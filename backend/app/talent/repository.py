"""
Government Talent & Opportunity Network - Repository Layer
"""

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo.database import Database

from app.talent.models import OpportunityStatus, VisibilityLevel, TalentAuditAction


def _object_id(value: str) -> Optional[ObjectId]:
    """Convert string to ObjectId"""
    return ObjectId(value) if ObjectId.is_valid(value) else None


# ─── Talent Preferences ──────────────────────────────────────────────────────


def get_talent_preferences(database: Database, user_id: str) -> Optional[dict]:
    """Get user's talent preferences"""
    user_oid = _object_id(user_id)
    if not user_oid:
        return None
    return database.talent_preferences.find_one({"user_id": user_oid})


def upsert_talent_preferences(
    database: Database,
    user_id: str,
    updates: dict
) -> dict:
    """Create or update talent preferences"""
    user_oid = _object_id(user_id)
    if not user_oid:
        raise ValueError("Invalid user_id")
    
    updates["updated_at"] = datetime.utcnow()
    
    database.talent_preferences.update_one(
        {"user_id": user_oid},
        {"$set": updates},
        upsert=True
    )
    
    return get_talent_preferences(database, user_id)


def update_talent_preferences(database: Database, user_id: str, updates) -> bool:
    """Update talent preferences from Pydantic model"""
    from app.talent.schemas import TalentPreferencesUpdate
    
    user_oid = _object_id(user_id)
    if not user_oid:
        return False
    
    updates_dict = updates.model_dump(exclude_none=True) if hasattr(updates, "model_dump") else updates.dict(exclude_none=True)
    updates_dict["updated_at"] = datetime.utcnow()
    
    result = database.talent_preferences.update_one(
        {"user_id": user_oid},
        {"$set": updates_dict},
        upsert=True
    )
    
    if result is None:
        return True
    return getattr(result, "modified_count", 0) > 0 or getattr(result, "upserted_id", None) is not None


def get_opted_in_users(
    database: Database,
    department: Optional[str] = None
) -> List[dict]:
    """Get users who have opted into opportunity discovery"""
    query = {
        "opt_in_enabled": True,
        "available_for_opportunities": True
    }
    
    if department:
        # Get users from specific department
        user_ids = [
            p["user_id"] for p in 
            database.talent_preferences.find(query, {"user_id": 1})
        ]
        users = list(database.users.find({
            "_id": {"$in": user_ids},
            "department": department,
            "status": "active"
        }))
        return users
    
    # Get all opted-in users
    user_ids = [
        p["user_id"] for p in 
        database.talent_preferences.find(query, {"user_id": 1})
    ]
    return list(database.users.find({
        "_id": {"$in": user_ids},
        "status": "active"
    }))


# ─── Government Opportunities ────────────────────────────────────────────────


def create_opportunity(database: Database, opportunity_data, created_by: str) -> Optional[str]:
    """Create new government opportunity"""
    from app.talent.schemas import OpportunityCreate
    
    # Convert Pydantic to dict
    opp_dict = opportunity_data.model_dump() if hasattr(opportunity_data, "model_dump") else opportunity_data.dict()
    
    opp_dict["created_at"] = datetime.utcnow()
    opp_dict["updated_at"] = datetime.utcnow()
    opp_dict["status"] = OpportunityStatus.DRAFT
    
    # Convert created_by to ObjectId
    created_by_oid = _object_id(created_by)
    if created_by_oid:
        opp_dict["created_by"] = created_by_oid
    
    result = database.government_opportunities.insert_one(opp_dict)
    return str(result.inserted_id)


def get_opportunity(database: Database, opportunity_id: str) -> Optional[dict]:
    """Get opportunity by ID"""
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return None
    return database.government_opportunities.find_one({"_id": opp_oid})


def update_opportunity(
    database: Database,
    opportunity_id: str,
    updates
) -> bool:
    """Update opportunity"""
    from app.talent.schemas import OpportunityUpdate
    
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return False
    
    updates_dict = updates.model_dump(exclude_none=True) if hasattr(updates, "model_dump") else updates.dict(exclude_none=True)
    updates_dict["updated_at"] = datetime.utcnow()
    
    result = database.government_opportunities.update_one(
        {"_id": opp_oid},
        {"$set": updates_dict}
    )
    
    if result is None:
        return True
    return getattr(result, "modified_count", 0) > 0


def publish_opportunity(database: Database, opportunity_id: str) -> bool:
    """Publish opportunity"""
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return False
    
    result = database.government_opportunities.update_one(
        {"_id": opp_oid},
        {"$set": {
            "status": OpportunityStatus.PUBLISHED,
            "published_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result is None:
        return True
    return getattr(result, "modified_count", 0) > 0


def archive_opportunity(database: Database, opportunity_id: str) -> bool:
    """Archive opportunity"""
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return False
    
    result = database.government_opportunities.update_one(
        {"_id": opp_oid},
        {"$set": {
            "status": OpportunityStatus.ARCHIVED,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result is None:
        return True
    return getattr(result, "modified_count", 0) > 0


def delete_opportunity(database: Database, opportunity_id: str) -> bool:
    """Delete opportunity and associated match cache"""
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return False
    
    # Remove cached matches
    database.talent_opportunity_matches.delete_many({"opportunity_id": opp_oid})
    
    # Remove opportunity
    result = database.government_opportunities.delete_one({"_id": opp_oid})
    if result is None:
        return True
    return getattr(result, "deleted_count", 0) > 0


def get_opportunity_by_id(database: Database, opportunity_id: str):
    """Get opportunity by ID and convert to schema"""
    from app.talent.schemas import GovernmentOpportunity
    
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return None
    
    opp = database.government_opportunities.find_one({"_id": opp_oid})
    if not opp:
        return None
    
    # Convert to schema
    opp_dict = dict(opp)
    opp_dict["id"] = str(opp["_id"])
    if "_id" in opp_dict:
        del opp_dict["_id"]
    if "created_by" in opp_dict and isinstance(opp_dict["created_by"], ObjectId):
        opp_dict["created_by"] = str(opp_dict["created_by"])
    
    try:
        return GovernmentOpportunity(**opp_dict)
    except Exception:
        return None


def get_all_opportunities(database: Database, status_filter=None):
    """Get all opportunities"""
    from app.talent.schemas import GovernmentOpportunity
    
    query = {}
    if status_filter:
        query["status"] = status_filter
    
    opps = list(database.government_opportunities.find(query).sort("created_at", -1))
    
    results = []
    for opp in opps:
        opp_dict = dict(opp)
        opp_dict["id"] = str(opp["_id"])
        if "_id" in opp_dict:
            del opp_dict["_id"]
        if "created_by" in opp_dict and isinstance(opp_dict["created_by"], ObjectId):
            opp_dict["created_by"] = str(opp_dict["created_by"])
        
        try:
            results.append(GovernmentOpportunity(**opp_dict))
        except Exception:
            continue
    
    return results


def log_audit_event(
    database: Database,
    action: str,
    performed_by: str,
    performed_by_name: str,
    performed_by_department: str,
    target_user_id: Optional[str] = None,
    target_opportunity_id: Optional[str] = None,
    details: Optional[dict] = None
) -> None:
    """Create audit log entry"""
    performed_by_oid = _object_id(performed_by)
    if not performed_by_oid:
        return
    
    log_entry = {
        "action": action,
        "performed_by": performed_by_oid,
        "performed_by_name": performed_by_name,
        "performed_by_department": performed_by_department,
        "timestamp": datetime.utcnow(),
        "details": details or {}
    }
    
    if target_user_id:
        target_oid = _object_id(target_user_id)
        if target_oid:
            log_entry["target_user_id"] = target_oid
    
    if target_opportunity_id:
        opp_oid = _object_id(target_opportunity_id)
        if opp_oid:
            log_entry["target_opportunity_id"] = opp_oid
    
    database.talent_access_audit.insert_one(log_entry)


def list_opportunities(
    database: Database,
    status: Optional[OpportunityStatus] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> tuple[List[dict], int]:
    """List opportunities with filters"""
    query = {}
    
    if status:
        query["status"] = status
    
    if department:
        query["department_name"] = department
    
    total = database.government_opportunities.count_documents(query)
    opportunities = list(
        database.government_opportunities
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    
    return opportunities, total


def get_published_opportunities(database: Database) -> List[dict]:
    """Get all published opportunities"""
    return list(database.government_opportunities.find({
        "status": OpportunityStatus.PUBLISHED
    }).sort("created_at", -1))


# ─── Opportunity Matches ─────────────────────────────────────────────────────


def save_opportunity_match(
    database: Database,
    opportunity_id: str,
    user_id: str,
    match_data: dict
) -> None:
    """Save opportunity match result"""
    opp_oid = _object_id(opportunity_id)
    user_oid = _object_id(user_id)
    
    if not opp_oid or not user_oid:
        return
    
    match_data["opportunity_id"] = opp_oid
    match_data["user_id"] = user_oid
    match_data["calculated_at"] = datetime.utcnow()
    
    database.talent_opportunity_matches.update_one(
        {"opportunity_id": opp_oid, "user_id": user_oid},
        {"$set": match_data},
        upsert=True
    )


def get_opportunity_matches(
    database: Database,
    opportunity_id: str,
    min_score: float = 0.0
) -> List[dict]:
    """Get matches for opportunity"""
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return []
    
    return list(database.talent_opportunity_matches.find({
        "opportunity_id": opp_oid,
        "match_score": {"$gte": min_score},
        "eligible": True
    }).sort("match_score", -1))


def get_user_opportunity_match(
    database: Database,
    opportunity_id: str,
    user_id: str
) -> Optional[dict]:
    """Get specific user's match for opportunity"""
    opp_oid = _object_id(opportunity_id)
    user_oid = _object_id(user_id)
    
    if not opp_oid or not user_oid:
        return None
    
    return database.talent_opportunity_matches.find_one({
        "opportunity_id": opp_oid,
        "user_id": user_oid
    })


# ─── Audit Logging ───────────────────────────────────────────────────────────


def get_audit_logs(
    database: Database,
    target_user_id: Optional[str] = None,
    target_opportunity_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[dict], int]:
    """Get audit logs"""
    query = {}
    
    if target_user_id:
        user_oid = _object_id(target_user_id)
        if user_oid:
            query["target_user_id"] = user_oid
    
    if target_opportunity_id:
        opp_oid = _object_id(target_opportunity_id)
        if opp_oid:
            query["target_opportunity_id"] = opp_oid
    
    total = database.talent_access_audit.count_documents(query)
    logs = list(
        database.talent_access_audit
        .find(query)
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )
    
    return logs, total


# ─── Database Indexes ────────────────────────────────────────────────────────


def ensure_talent_indexes(database: Database) -> None:
    """Create indexes for talent collections"""
    # Talent preferences
    database.talent_preferences.create_index("user_id", unique=True)
    database.talent_preferences.create_index([("opt_in_enabled", 1), ("available_for_opportunities", 1)])
    
    # Government opportunities
    database.government_opportunities.create_index("status")
    database.government_opportunities.create_index("department_name")
    database.government_opportunities.create_index("opportunity_type")
    database.government_opportunities.create_index("created_at")
    
    # Opportunity matches
    database.talent_opportunity_matches.create_index([("opportunity_id", 1), ("user_id", 1)], unique=True)
    database.talent_opportunity_matches.create_index([("opportunity_id", 1), ("match_score", -1)])
    database.talent_opportunity_matches.create_index([("user_id", 1)])
    
    # Audit logs
    database.talent_access_audit.create_index("timestamp")
    database.talent_access_audit.create_index("target_user_id")
    database.talent_access_audit.create_index("target_opportunity_id")
    database.talent_access_audit.create_index("performed_by")
