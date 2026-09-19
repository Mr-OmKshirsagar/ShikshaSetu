"""
Idempotent User Organization & Designation Taxonomy Migration Script.

Safely annotates existing users with canonical taxonomy IDs without
modifying their competency profiles, evidence records, or assessment results.
"""

import logging
from datetime import datetime, UTC
from typing import Dict, Any

from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import get_settings
from app.core.government_taxonomy import (
    find_canonical_organization,
    find_canonical_designation,
)

logger = logging.getLogger("taxonomy_migration")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def migrate_user_taxonomy(database: Database) -> Dict[str, Any]:
    """
    Idempotently scans all users in the database and adds canonical
    taxonomy fields (organization_id, designation_id, government_level, etc.)
    while strictly preserving existing department/designation strings,
    role assignments, and competency profiles.
    """
    users = list(database.users.find({}))
    migrated_count = 0
    already_canonical = 0

    now = datetime.now(UTC)

    for u in users:
        updates: Dict[str, Any] = {}
        dept = u.get("department") or ""
        desig = u.get("designation") or ""

        # 1. Organization canonicalization
        if not u.get("organization_id") and dept:
            canon_org = find_canonical_organization(dept)
            if canon_org:
                updates["organization_id"] = canon_org["id"]
                updates["organization_type"] = canon_org.get("organization_type", "MINISTRY")
                updates["government_level"] = canon_org.get("level", "CENTRAL")
                if canon_org.get("level") == "CENTRAL":
                    updates["state_ut"] = None
            else:
                # Default fallback for unmapped legacy departments
                updates["organization_id"] = "GOI-GEN"
                updates["organization_type"] = "DEPARTMENT"
                updates["government_level"] = "CENTRAL"

        # 2. Designation canonicalization
        if not u.get("designation_id") and desig:
            canon_desig = find_canonical_designation(desig)
            if canon_desig:
                updates["designation_id"] = canon_desig["id"]
                updates["government_designation"] = canon_desig["title"]
            else:
                updates["designation_id"] = "DESIG-CUSTOM"
                updates["government_designation"] = desig

        # 3. Application role mirroring
        if not u.get("application_role") and u.get("access_role"):
            updates["application_role"] = str(u["access_role"])

        if updates:
            updates["updated_at"] = now
            database.users.update_one({"_id": u["_id"]}, {"$set": updates})
            migrated_count += 1
        else:
            already_canonical += 1

    logger.info(
        f"Taxonomy Migration Complete: {migrated_count} users updated, "
        f"{already_canonical} users already had canonical metadata (Total: {len(users)})."
    )

    return {
        "total_users": len(users),
        "migrated": migrated_count,
        "already_canonical": already_canonical,
    }


if __name__ == "__main__":
    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=15000,
        socketTimeoutMS=20000,
    )
    db = client[settings.mongodb_database]
    result = migrate_user_taxonomy(db)
    print("Migration Result:", result)
    client.close()
