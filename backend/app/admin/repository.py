"""Repository layer for Admin organizational intelligence queries."""

from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo.database import Database


def get_all_users(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all users in the system."""
    return list(db.users.find({}))


def get_all_roles(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all professional roles."""
    return list(db.roles.find({}))


def get_all_competencies(db: Database) -> List[Dict[str, Any]]:
    """Retrieve full competency taxonomy."""
    return list(db.competencies.find({}))


def get_all_role_requirements(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all role-to-competency requirement mappings."""
    return list(db.role_requirements.find({}))


def get_all_competency_profiles(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all user competency profiles."""
    return list(db.competency_profiles.find({}))


def get_all_learning_activities(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all learning activities across all users."""
    return list(db.learning_activities.find({}))


def get_all_quizzes(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all trainer quizzes."""
    return list(db.quizzes.find({}))


def get_all_quiz_attempts(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all quiz attempt submissions."""
    return list(db.quiz_attempts.find({}))


def get_all_evidence_records(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all competency evidence ledger entries."""
    return list(db.competency_evidence.find({}))


def get_all_capability_assessments(db: Database) -> List[Dict[str, Any]]:
    """Retrieve all formal capability assessments."""
    return list(db.capability_assessments.find({}))


def get_all_learning_resources(db: Database) -> List[Dict[str, Any]]:
    """Retrieve catalog learning resources."""
    return list(db.learning_resources.find({}))


# ─── User-scoped queries (for individual workforce profile) ──────────────────


def get_user_by_id(db: Database, user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single user by string ID. Returns None if not found or invalid ID."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    return db.users.find_one({"_id": oid})


def get_user_learning_activities(
    db: Database, user_id: str, limit: int = 200
) -> List[Dict[str, Any]]:
    """Retrieve all learning activities for a specific user, most-recent first."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        oid = user_id  # type: ignore[assignment]
    return list(
        db.learning_activities.find({"user_id": oid})
        .sort("started_at", -1)
        .limit(limit)
    )


def get_user_capability_assessments(
    db: Database, user_id: str, limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieve all capability assessments for a specific user, most-recent first."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        oid = user_id  # type: ignore[assignment]
    # capability_assessments may store user_id as ObjectId or string
    docs = list(
        db.capability_assessments.find({"user_id": oid})
        .sort("started_at", -1)
        .limit(limit)
    )
    if not docs:
        # fallback: try string match
        docs = list(
            db.capability_assessments.find({"user_id": str(user_id)})
            .sort("started_at", -1)
            .limit(limit)
        )
    return docs


def get_user_evidence_records(
    db: Database, user_id: str, limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieve all competency evidence records for a specific user, most-recent first."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        oid = user_id  # type: ignore[assignment]
    docs = list(
        db.competency_evidence.find({"user_id": oid})
        .sort("recorded_at", -1)
        .limit(limit)
    )
    if not docs:
        docs = list(
            db.competency_evidence.find({"user_id": str(user_id)})
            .sort("recorded_at", -1)
            .limit(limit)
        )
    return docs


def get_user_competency_profiles(
    db: Database, user_id: str
) -> List[Dict[str, Any]]:
    """Retrieve all competency profiles for a specific user."""
    try:
        oid = ObjectId(user_id)
    except Exception:
        oid = user_id  # type: ignore[assignment]
    docs = list(db.competency_profiles.find({"user_id": oid}))
    if not docs:
        docs = list(db.competency_profiles.find({"user_id": str(user_id)}))
    return docs
