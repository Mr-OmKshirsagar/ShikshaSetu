"""
Schema migration + embedding back-fill for pre-P0 document_chunks.

Problem:
  Document chunks inserted before the P0 RAG upgrade have:
    - embedding: None           (field present but null)
    - no embedding_status field (field absent)

  DocumentChunkRepository.get_chunks_with_embeddings() queries:
    {embedding_status: "EMBEDDED"}
  …and finds 0 results, so EmbeddingIndexManager builds empty numpy indexes
  and all vector search returns nothing.

This script:
  1. Marks all chunks with embedding==None or missing embedding_status as PENDING.
  2. Calls embed_and_persist_chunks() to generate real Gemini embeddings.
  3. Rebuilds all material indexes in EmbeddingIndexManager.
  4. Prints a before/after summary.

Run once:
  python -m app.scripts.migrate_embed_backfill
"""

import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("embed_backfill")


def run_backfill() -> dict:
    from app.core.config import get_settings
    from app.core.database import initialize_database, close_database
    from app.ai.repository import DocumentChunkRepository, LearningMaterialRepository
    from app.ai.models import DocumentChunk
    from app.rag.embedding_index import embed_and_persist_chunks, EmbeddingIndexManager

    s = get_settings()
    logger.info("Connecting to MongoDB: %s / %s", s.mongodb_uri[:40] + "...", s.mongodb_database)
    client, db = initialize_database(s.mongodb_uri, s.mongodb_database)

    try:
        # ── 1. Find chunks that need migration ────────────────────────────────
        # Pre-P0 chunks: embedding field exists but is None, no embedding_status
        needs_migration = list(db.document_chunks.find({
            "$or": [
                {"embedding_status": {"$exists": False}},
                {"embedding_status": {"$in": ["PENDING", "FAILED", None]}},
            ]
        }))

        already_embedded = db.document_chunks.count_documents({"embedding_status": "EMBEDDED"})
        total_chunks = db.document_chunks.count_documents({})

        logger.info(
            "Chunk summary — total: %d | already EMBEDDED: %d | need migration: %d",
            total_chunks, already_embedded, len(needs_migration),
        )

        if not needs_migration:
            logger.info("All chunks already have real embeddings. Nothing to do.")
            return {"status": "already_complete", "embedded": already_embedded, "total": total_chunks}

        # ── 2. Mark all needing migration as PENDING ──────────────────────────
        migration_ids = [c["_id"] for c in needs_migration]
        db.document_chunks.update_many(
            {"_id": {"$in": migration_ids}},
            {"$set": {"embedding_status": "PENDING"}},
        )
        logger.info("Marked %d chunks as PENDING", len(migration_ids))

        # ── 3. Initialise embedding provider ─────────────────────────────────
        api_key = s.embedding_api_key or s.llm_api_key
        embedding_model = s.embedding_model

        if not api_key:
            logger.error("No embedding API key configured. Set EMBEDDING_API_KEY or LLM_API_KEY.")
            return {"status": "error", "reason": "no api key"}

        try:
            from app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider
            provider = GeminiEmbeddingProvider(api_key=api_key, model=embedding_model)
            if not provider.is_available():
                raise RuntimeError("Provider unavailable after init")
            logger.info("Gemini embedding provider ready — model: %s", embedding_model)
        except Exception as exc:
            logger.error("Embedding provider init failed: %s", exc)
            return {"status": "error", "reason": str(exc)}

        # ── 4. Embed per material ─────────────────────────────────────────────
        materials = list(db.learning_materials.find({"status": "READY"}))
        total_embedded = 0
        total_failed = 0

        for mat in materials:
            mat_id = str(mat["_id"])
            original_filename = mat.get("original_filename", mat_id)

            # Load chunks needing embedding for this material
            raw_chunks = list(db.document_chunks.find({
                "material_id": mat_id,
                "embedding_status": {"$in": ["PENDING", "FAILED"]},
            }))

            if not raw_chunks:
                logger.info("  %s: no chunks to embed", original_filename)
                continue

            logger.info("  %s: embedding %d chunk(s)…", original_filename, len(raw_chunks))

            # Convert to DocumentChunk models
            doc_chunks = []
            for c in raw_chunks:
                c["_id"] = str(c["_id"])
                c["id"] = c["_id"]
                doc_chunks.append(DocumentChunk(**c))

            t0 = time.time()
            embedded, failed = embed_and_persist_chunks(
                database=db,
                chunks=doc_chunks,
                embedding_provider=provider,
                model_name=embedding_model,
            )
            elapsed_ms = int((time.time() - t0) * 1000)

            total_embedded += embedded
            total_failed += failed
            logger.info(
                "  %s: embedded=%d  failed=%d  time=%dms",
                original_filename, embedded, failed, elapsed_ms,
            )

        # ── 5. Rebuild in-memory indexes ──────────────────────────────────────
        logger.info("Rebuilding EmbeddingIndexManager indexes…")
        manager = EmbeddingIndexManager.get_instance()
        manager._indexes.clear()
        rebuilt = manager.load_all_ready_materials(db)
        logger.info("Rebuilt %d material indexes", rebuilt)

        # ── 6. Final verification ─────────────────────────────────────────────
        final_embedded = db.document_chunks.count_documents({"embedding_status": "EMBEDDED"})
        final_pending  = db.document_chunks.count_documents({"embedding_status": "PENDING"})
        final_failed   = db.document_chunks.count_documents({"embedding_status": "FAILED"})

        summary = {
            "status": "complete",
            "chunks_embedded_this_run": total_embedded,
            "chunks_failed_this_run":   total_failed,
            "total_embedded_in_db":     final_embedded,
            "total_pending_in_db":      final_pending,
            "total_failed_in_db":       final_failed,
            "indexes_rebuilt":          rebuilt,
        }
        logger.info("Back-fill complete: %s", summary)
        return summary

    finally:
        close_database(client)


if __name__ == "__main__":
    result = run_backfill()
    if result.get("status") == "error":
        sys.exit(1)
