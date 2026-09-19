import logging

from pymongo import ASCENDING, TEXT
from pymongo.database import Database

logger = logging.getLogger(__name__)


def ensure_framework_indexes(database: Database) -> None:
    database.assessments.create_index([("assessment_key", ASCENDING)], unique=True, name="uq_assessment_key")
    database.assessment_attempts.create_index([("user_id", ASCENDING)], name="ix_attempt_user")
    database.assessment_attempts.create_index([("assessment_id", ASCENDING)], name="ix_attempt_assessment")
    database.assessment_attempts.create_index(
        [("user_id", ASCENDING), ("assessment_id", ASCENDING)],
        name="ix_attempt_user_assessment",
    )
    database.users.create_index([("email", ASCENDING)], unique=True, name="uq_user_email")
    database.users.create_index([("employee_id", ASCENDING)], unique=True, name="uq_employee_id")
    database.users.create_index([("role_id", ASCENDING)], name="ix_user_role")
    database.competencies.create_index([("code", ASCENDING)], unique=True, name="uq_competency_code")
    database.roles.create_index([("role_code", ASCENDING)], unique=True, name="uq_role_code")
    database.role_requirements.create_index(
        [("role_id", ASCENDING), ("competency_id", ASCENDING)],
        unique=True,
        name="uq_role_competency",
    )
    database.competency_profiles.create_index(
        [("user_id", ASCENDING), ("competency_id", ASCENDING)],
        unique=True,
        name="uq_user_competency_profile",
    )
    database.competency_evidence.create_index(
        [("user_id", ASCENDING), ("competency_id", ASCENDING)],
        name="ix_user_competency_evidence",
    )
    database.adaptive_assessment_sessions.create_index(
        [("user_id", ASCENDING), ("status", ASCENDING), ("completed_at", -1)],
        name="ix_adaptive_sessions_user_status_date",
    )

    # ── RAG / Document Intelligence indexes ──────────────────────────────────

    # learning_materials: fast lookup by user (ownership check on every request)
    database.learning_materials.create_index(
        [("user_id", ASCENDING)], name="ix_lm_user_id"
    )
    # learning_materials: status filter (e.g. find all READY materials)
    database.learning_materials.create_index(
        [("status", ASCENDING)], name="ix_lm_status"
    )

    # document_chunks: primary lookup — every retrieval filters by material_id
    database.document_chunks.create_index(
        [("material_id", ASCENDING)], name="ix_dc_material_id"
    )
    # document_chunks: compound for metadata-filtered retrieval
    database.document_chunks.create_index(
        [("material_id", ASCENDING), ("competency_code", ASCENDING)],
        name="ix_dc_material_competency",
    )
    # document_chunks: embedding_status — needed to queue re-embedding jobs
    database.document_chunks.create_index(
        [("embedding_status", ASCENDING)], name="ix_dc_embedding_status"
    )
    # document_chunks: full-text search for keyword retrieval branch
    # create_index raises OperationFailure if a conflicting text index already
    # exists; wrap individually so other indexes are not blocked on failure.
    try:
        database.document_chunks.create_index(
            [("text", TEXT), ("source_section", TEXT)],
            name="ix_dc_text_fulltext",
            default_language="english",
        )
    except Exception as exc:
        logger.warning("Could not create text index on document_chunks: %s", exc)

    # ── Adaptive Assessment / Question Bank indexes ───────────────────────────

    # question_bank: every _select_next_question call filters by competency_code + status
    database.question_bank.create_index(
        [("competency_code", ASCENDING), ("status", ASCENDING)],
        name="ix_qb_competency_status",
    )
    # question_bank: also filter by difficulty within a competency
    database.question_bank.create_index(
        [("competency_code", ASCENDING), ("status", ASCENDING), ("difficulty", ASCENDING)],
        name="ix_qb_competency_status_difficulty",
    )

    # ── RAG Dataset collections indexes ──────────────────────────────────────

    # rag_glossary: fast term lookup
    try:
        database.rag_glossary.create_index([("term", ASCENDING)], unique=True, name="uq_glossary_term")
        database.rag_glossary.create_index([("domain", ASCENDING)], name="ix_glossary_domain")
        database.rag_glossary.create_index(
            [("term", TEXT), ("definition", TEXT)],
            name="ix_glossary_fulltext",
            default_language="english",
        )
    except Exception as exc:
        logger.warning("Could not create glossary indexes: %s", exc)

    # rag_synonyms: canonical term lookup + alias search
    try:
        database.rag_synonyms.create_index(
            [("canonical_term", ASCENDING)], unique=True, name="uq_synonym_canonical"
        )
    except Exception as exc:
        logger.warning("Could not create synonym indexes: %s", exc)

    # rag_eval_set: golden Q&A
    try:
        database.rag_eval_set.create_index([("query_type", ASCENDING)], name="ix_eval_qtype")
        database.rag_eval_set.create_index([("difficulty", ASCENDING)], name="ix_eval_difficulty")
    except Exception as exc:
        logger.warning("Could not create eval set indexes: %s", exc)

    # rag_refusal_set: out-of-scope test
    try:
        database.rag_refusal_set.create_index(
            [("expected_behavior", ASCENDING)], name="ix_refusal_behavior"
        )
    except Exception as exc:
        logger.warning("Could not create refusal set indexes: %s", exc)

    # rag_feedback: append-only feedback log
    try:
        database.rag_feedback.create_index([("session_id", ASCENDING)], name="ix_feedback_session")
        database.rag_feedback.create_index([("timestamp", ASCENDING)], name="ix_feedback_ts")
        database.rag_feedback.create_index([("resolved", ASCENDING)], name="ix_feedback_resolved")
    except Exception as exc:
        logger.warning("Could not create feedback indexes: %s", exc)

    # rag_entity_registry: entity lookup
    try:
        database.rag_entity_registry.create_index(
            [("entity_name", ASCENDING)], name="ix_entity_name"
        )
        database.rag_entity_registry.create_index(
            [("entity_type", ASCENDING)], name="ix_entity_type"
        )
    except Exception as exc:
        logger.warning("Could not create entity registry indexes: %s", exc)

    # rag_terminology_hi_en: bilingual lookup
    try:
        database.rag_terminology_hi_en.create_index(
            [("term_en", ASCENDING)], unique=True, name="uq_term_en"
        )
    except Exception as exc:
        logger.warning("Could not create terminology indexes: %s", exc)
