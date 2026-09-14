"""
Dedicated Golden Demo Reset Script for ShikshaSetu.

Restores ONLY the primary demo persona (official@shikshasetu.gov.in) to the
exact MoSPI Statistical Officer golden baseline for SIH rehearsal.

Safety & Invariants:
- Scoped strictly to official@shikshasetu.gov.in.
- Does NOT delete or alter other users, departments, roles, or competencies.
- Does NOT delete or alter learning materials, trainer questions, quizzes, or question_bank.
- Does NOT expose or print database connection credentials.
- 100% idempotent: running repeatedly yields the exact same deterministic state.
"""

import os
import sys
import logging
from datetime import datetime, UTC
from bson import ObjectId

# Configure DNS fallback if running on network where MongoDB Atlas SRV fails
try:
    import dns.resolver
    _custom_resolver = dns.resolver.Resolver()
    _custom_resolver.nameservers = ["8.8.8.8", "8.8.4.4"]
    dns.resolver.default_resolver = _custom_resolver
except Exception:
    pass

from pymongo import MongoClient
from pymongo.database import Database

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("demo_reset")

PRIMARY_DEMO_EMAIL = "official@shikshasetu.gov.in"
TARGET_FULL_NAME = "Rajesh Sharma"
TARGET_DEPARTMENT = "Ministry of Statistics & Programme Implementation (MoSPI)"
TARGET_DESIGNATION = "Statistical Officer"
TARGET_ROLE_CODE = "STATISTICAL_OFFICER"

CANONICAL_BASELINE_SPECS = [
    ("STAT_SAMPLING", 2.45, 0.75, "Baseline knowledge assessment (Sampling theory, stratification, PPS)"),
    ("STAT_SURVEY_DESIGN", 3.00, 0.70, "Baseline evaluation (Questionnaire design & protocols)"),
    ("STAT_DATA_QUALITY_FRAMEWORKS", 3.20, 0.70, "Baseline evaluation (NDQS data validation rules)"),
    ("TECH_PYTHON", 2.80, 0.70, "Baseline evaluation (Pandas & data wrangling)"),
    ("TECH_DATA_VISUALIZATION", 3.00, 0.70, "Baseline evaluation (Official charts & dashboards)"),
    ("BEH_ETHICS", 3.50, 0.75, "Baseline evaluation (DoPT conduct rules & public integrity)"),
]


def _get_database() -> tuple[MongoClient, Database]:
    """Connect to MongoDB securely using application configuration without logging credentials."""
    from app.core.config import get_settings

    settings = get_settings()
    client = MongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=15000,
        socketTimeoutMS=20000,
    )
    db = client[settings.mongodb_database]
    db.command("ping")
    return client, db


def reset_demo_official(db: Database) -> dict:
    """
    Idempotently restores official@shikshasetu.gov.in to golden baseline.
    Returns a summary dict of operations performed.
    """
    now = datetime.now(UTC)

    # 1. Resolve primary demo user
    user = db.users.find_one({"email": PRIMARY_DEMO_EMAIL})
    if not user:
        raise RuntimeError(f"Primary demo user '{PRIMARY_DEMO_EMAIL}' not found in database.")

    user_oid = user["_id"]
    user_id_str = str(user_oid)

    # 2. Resolve STATISTICAL_OFFICER role
    role_doc = db.roles.find_one({
        "$or": [
            {"role_code": TARGET_ROLE_CODE},
            {"code": TARGET_ROLE_CODE},
            {"role_name": "Statistical Officer"},
        ]
    })
    if not role_doc:
        raise RuntimeError(f"Canonical role '{TARGET_ROLE_CODE}' not found in database.")
    role_oid = role_doc["_id"]

    # 3. Resolve competency ObjectIds
    comp_map: dict[str, ObjectId] = {}
    for code, _, _, _ in CANONICAL_BASELINE_SPECS:
        c_doc = db.competencies.find_one({"code": code})
        if c_doc:
            comp_map[code] = c_doc["_id"]
        else:
            raise RuntimeError(f"Canonical competency '{code}' not found in database.")

    # 4. Restore User Profile Metadata
    from app.auth.security import hash_password
    db.users.update_one(
        {"_id": user_oid},
        {"$set": {
            "full_name": TARGET_FULL_NAME,
            "department": TARGET_DEPARTMENT,
            "designation": TARGET_DESIGNATION,
            "role_id": role_oid,
            "access_role": "OFFICIAL",
            "status": "active",
            "password_hash": hash_password("Password123!"),
            "updated_at": now,
        }}
    )

    # 5. Clean rehearsal session/attempt data strictly for this user
    user_filter = {"$or": [{"user_id": user_oid}, {"user_id": user_id_str}]}
    
    del_adaptive = db.adaptive_assessment_sessions.delete_many(user_filter).deleted_count
    del_quiz_attempts = db.quiz_attempts.delete_many(user_filter).deleted_count
    del_capability_assessments = db.capability_assessments.delete_many(user_filter).deleted_count
    del_assessment_attempts = db.assessment_attempts.delete_many(user_filter).deleted_count
    del_learning_activities = db.learning_activities.delete_many(user_filter).deleted_count

    # 6. Reset Competency Evidence strictly to canonical baseline
    del_evidence = db.competency_evidence.delete_many(user_filter).deleted_count

    new_evidence_docs = []
    for code, level, conf, desc in CANONICAL_BASELINE_SPECS:
        c_oid = comp_map[code]
        new_evidence_docs.append({
            "user_id": user_oid,
            "competency_id": c_oid,
            "competency_code": code,
            "evidence_type": "KNOWLEDGE_TEST",
            "authority": "AUTHORITATIVE",
            "score": level,
            "confidence": conf,
            "source_type": "PROTOTYPE",
            "source_reference": "MoSPI Official Baseline Evaluation 2026",
            "assessment_type": "BASELINE_ASSESSMENT",
            "description": desc,
            "status": "ACTIVE",
            "recorded_at": now,
            "created_at": now,
            "updated_at": now,
        })
    if new_evidence_docs:
        db.competency_evidence.insert_many(new_evidence_docs)

    # 7. Reset Competency Profiles strictly to canonical baseline
    # Remove any non-canonical profiles for this user
    canonical_comp_ids = list(comp_map.values())
    del_stray_profiles = db.competency_profiles.delete_many({
        "user_id": user_oid,
        "competency_id": {"$nin": canonical_comp_ids}
    }).deleted_count

    for code, level, conf, _ in CANONICAL_BASELINE_SPECS:
        c_oid = comp_map[code]
        db.competency_profiles.update_one(
            {"user_id": user_oid, "competency_id": c_oid},
            {
                "$set": {
                    "user_id": user_oid,
                    "competency_id": c_oid,
                    "current_level": level,
                    "level": level,
                    "confidence": conf,
                    "status": "active",
                    "last_assessed_at": now,
                    "updated_at": now,
                },
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

    # 8. Invalidate recommendation cache
    try:
        from app.learning_resources.cache import invalidate_recommendations_cache
        invalidate_recommendations_cache(user_id_str)
    except Exception:
        pass

    # 9. Verify Safety: count preserved collections
    preserved_summary = {
        "total_users": db.users.count_documents({}),
        "total_roles": db.roles.count_documents({}),
        "total_competencies": db.competencies.count_documents({}),
        "total_question_bank": db.question_bank.count_documents({}),
        "total_trainer_materials": db.learning_materials.count_documents({}),
        "total_trainer_questions": db.trainer_questions.count_documents({}),
        "total_learning_resources": db.learning_resources.count_documents({}),
    }

    return {
        "status": "SUCCESS",
        "user_email": PRIMARY_DEMO_EMAIL,
        "user_role": TARGET_ROLE_CODE,
        "department": TARGET_DEPARTMENT,
        "deleted_rehearsal_sessions": {
            "adaptive_assessment_sessions": del_adaptive,
            "quiz_attempts": del_quiz_attempts,
            "capability_assessments": del_capability_assessments,
            "assessment_attempts": del_assessment_attempts,
            "learning_activities": del_learning_activities,
            "previous_evidence_records": del_evidence,
            "stray_competency_profiles": del_stray_profiles,
        },
        "restored_baseline_evidence": len(new_evidence_docs),
        "restored_competency_profiles": len(CANONICAL_BASELINE_SPECS),
        "target_gap_stat_sampling": {
            "current": 2.45,
            "required": 4.00,
            "gap": 1.55,
            "priority": "CRITICAL",
        },
        "preserved_system_data": preserved_summary,
    }


def main():
    print("=" * 70)
    print("ShikshaSetu — Dedicated Golden Demo Persona Reset")
    print(f"Target Persona: {PRIMARY_DEMO_EMAIL}")
    print("=" * 70)

    try:
        client, db = _get_database()
        result = reset_demo_official(db)
        client.close()

        print("\n[OK] RESET COMPLETED SUCCESSFULLY")
        print(f"  User: {result['user_email']}")
        print(f"  Department: {result['department']}")
        print(f"  Role: {result['user_role']}")
        print("\nRehearsal Sessions Cleared:")
        for k, v in result["deleted_rehearsal_sessions"].items():
            print(f"  - {k}: {v}")
        print("\nCanonical Profiles Restored:")
        print(f"  - Evidence records: {result['restored_baseline_evidence']}")
        print(f"  - Competency profiles: {result['restored_competency_profiles']}")
        print(f"  - STAT_SAMPLING: Current 2.45 / 4.00 (Gap: 1.55, CRITICAL)")
        print("\nPreserved Collections (Untouched):")
        for k, v in result["preserved_system_data"].items():
            print(f"  - {k}: {v}")
        print("=" * 70)
    except Exception as exc:
        print(f"\n[ERROR] RESET FAILED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
