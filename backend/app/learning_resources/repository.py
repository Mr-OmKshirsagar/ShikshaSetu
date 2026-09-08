"""Repository layer for learning resources database access."""

from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo.database import Database

from .models import LearningResource, Competency, ResourceMapping


class LearningResourceRepository:
    """Repository for learning resources queries."""

    def __init__(self, database: Database):
        self.db = database
        self.resources = database.learning_resources
        self.competencies = database.competencies
        self.mappings = database.learning_resource_mappings

    def get_resource_by_id(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a resource by its resource_id string (e.g., 'IGOT-123', 'NSSTA-PROTO-xxx')."""
        return self.resources.find_one({"resource_id": resource_id})

    def get_resource_by_mongo_id(self, mongo_id: str) -> Optional[Dict[str, Any]]:
        """Get a resource by its MongoDB ObjectId."""
        try:
            obj_id = ObjectId(mongo_id)
            return self.resources.find_one({"_id": obj_id})
        except Exception:
            return None

    def get_resources_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get all resources from a specific provider."""
        return list(self.resources.find({"provider": provider, "status": "ACTIVE"}))

    def get_resources_by_competency(self, competency_code: str) -> List[Dict[str, Any]]:
        """Get all resources mapped to a specific competency."""
        # Get mappings for this competency
        mappings = list(self.mappings.find({"competency_code": competency_code}))

        resources = []
        for mapping in mappings:
            resource = self.get_resource_by_mongo_id(str(mapping["resource_id"]))
            if resource:
                resources.append(resource)

        return resources

    def get_resources_by_competency_and_provider(
        self, competency_code: str, provider: str
    ) -> List[Dict[str, Any]]:
        """Get resources for a competency from a specific provider in a single batched query."""
        mappings = list(
            self.mappings.find(
                {"competency_code": competency_code, "provider": provider}
            )
        )
        if not mappings:
            return []

        # Batch fetch all resources in ONE query instead of N individual roundtrips
        raw_ids = [m["resource_id"] for m in mappings if "resource_id" in m]
        query_ids = []
        for rid in raw_ids:
            if isinstance(rid, ObjectId):
                query_ids.append(rid)
            elif ObjectId.is_valid(str(rid)):
                query_ids.append(ObjectId(str(rid)))
            query_ids.append(str(rid))

        resources = list(
            self.resources.find(
                {"_id": {"$in": query_ids}, "provider": provider}
            )
        )
        return resources

    def get_competency_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a competency by its code."""
        return self.competencies.find_one({"code": code})

    def get_all_competencies(self) -> List[Dict[str, Any]]:
        """Get all competencies."""
        return list(self.competencies.find())

    def get_mapping(
        self, resource_id: str, competency_code: str
    ) -> Optional[Dict[str, Any]]:
        """Get mapping between a resource and competency."""
        oid = ObjectId(resource_id) if ObjectId.is_valid(resource_id) else None
        return self.mappings.find_one(
            {"$or": [{"resource_id": oid}, {"resource_id": str(resource_id)}], "competency_code": competency_code}
        )

    def get_mappings_for_resource(self, resource_id: str) -> List[Dict[str, Any]]:
        """Get all competency mappings for a resource."""
        oid = ObjectId(resource_id) if ObjectId.is_valid(resource_id) else None
        return list(self.mappings.find({"$or": [{"resource_id": oid}, {"resource_id": str(resource_id)}]}))

    def get_mappings_for_competency(self, competency_code: str) -> List[Dict[str, Any]]:
        """Get all resource mappings for a competency."""
        return list(self.mappings.find({"competency_code": competency_code}))

    def count_resources_by_provider(self, provider: str) -> int:
        """Count resources by provider."""
        return self.resources.count_documents({"provider": provider, "status": "ACTIVE"})

    def count_mapped_competencies(self) -> int:
        """Count competencies that have at least one resource mapping."""
        unique_codes = self.mappings.distinct("competency_code")
        return len(unique_codes)

    def get_resources_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """Get resources by difficulty level."""
        return list(
            self.resources.find(
                {"metadata.difficulty": difficulty, "status": "ACTIVE"}
            )
        )

    def get_iGOT_resources(self) -> List[Dict[str, Any]]:
        """Get all iGOT resources."""
        return self.get_resources_by_provider("IGOT")

    def get_NSSTA_resources(self) -> List[Dict[str, Any]]:
        """Get all NSSTA resources."""
        return self.get_resources_by_provider("NSSTA")
