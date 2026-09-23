"""
MongoDB indexes for optimized RAG retrieval performance.
"""

import logging
from pymongo.database import Database
from pymongo import IndexModel, ASCENDING, TEXT

logger = logging.getLogger(__name__)


def ensure_retrieval_indexes(database: Database) -> None:
    """
    Create optimized indexes for document chunk retrieval.
    Compound indexes significantly improve query performance.
    """
    chunks_collection = database["document_chunks"]
    
    indexes = [
        # Text index for keyword search
        IndexModel([("text", TEXT)], name="text_search_idx"),
        
        # Compound index for competency-scoped retrieval
        IndexModel(
            [
                ("competency_codes", ASCENDING),
                ("embedding_status", ASCENDING),
            ],
            name="competency_embedding_idx"
        ),
        
        # Compound index for material-based retrieval
        IndexModel(
            [
                ("material_id", ASCENDING),
                ("sequence", ASCENDING),
                ("embedding_status", ASCENDING),
            ],
            name="material_sequence_idx"
        ),
        
        # Index for vector search status
        IndexModel(
            [("embedding_status", ASCENDING)],
            name="embedding_status_idx"
        ),
        
        # Index for material lookup
        IndexModel(
            [("material_id", ASCENDING)],
            name="material_lookup_idx"
        ),
    ]
    
    try:
        # Create indexes if they don't exist
        existing_indexes = {idx["name"] for idx in chunks_collection.list_indexes()}
        
        for index_model in indexes:
            index_name = index_model.document["name"]
            if index_name not in existing_indexes:
                chunks_collection.create_indexes([index_model])
                logger.info(f"Created index: {index_name}")
            else:
                logger.debug(f"Index already exists: {index_name}")
        
        logger.info("Document chunk indexes ensured")
        
    except Exception as exc:
        logger.warning(f"Failed to create retrieval indexes: {exc}")


def ensure_learning_material_indexes(database: Database) -> None:
    """Create indexes for learning materials collection."""
    materials_collection = database["learning_materials"]
    
    indexes = [
        # Index for user's materials
        IndexModel(
            [("uploaded_by", ASCENDING), ("created_at", ASCENDING)],
            name="user_materials_idx"
        ),
        
        # Index for extraction status
        IndexModel(
            [("extraction_status", ASCENDING)],
            name="extraction_status_idx"
        ),
        
        # Index for competency-based lookup
        IndexModel(
            [("competency_codes", ASCENDING)],
            name="competency_lookup_idx"
        ),
    ]
    
    try:
        existing_indexes = {idx["name"] for idx in materials_collection.list_indexes()}
        
        for index_model in indexes:
            index_name = index_model.document["name"]
            if index_name not in existing_indexes:
                materials_collection.create_indexes([index_model])
                logger.info(f"Created material index: {index_name}")
        
        logger.info("Learning material indexes ensured")
        
    except Exception as exc:
        logger.warning(f"Failed to create material indexes: {exc}")
