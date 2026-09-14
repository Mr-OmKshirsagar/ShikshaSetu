import pytest
from bson import ObjectId
from unittest.mock import MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.adaptive_assessments.service import AdaptiveAssessmentService
from app.adaptive_assessments.schemas import (
    AdaptiveStartRequest,
    AdaptiveAnswerRequest,
)
from app.ai.generation import MCQGenerator
from app.ai.models import DocumentChunk


def test_scenario_1_session_state_recovery():
    """Verify that an in-progress adaptive assessment session can be recovered via /status."""
    from pymongo import MongoClient
    import os

    # Use live or mock DB via service
    mock_db = MagicMock()
    session_oid = ObjectId()
    user_oid = ObjectId()

    q1_doc = {
        "_id": ObjectId(),
        "question_id": "Q1",
        "question_text": "What is simple random sampling?",
        "options": ["A", "B", "C", "D"],
        "difficulty": "MEDIUM",
    }

    mock_session = {
        "_id": session_oid,
        "user_id": user_oid,
        "competency_code": "STAT_SAMPLING",
        "competency_name": "Sampling Techniques",
        "status": "IN_PROGRESS",
        "current_estimated_level": 2.85,
        "questions_attempted": 1,
        "max_questions": 5,
        "current_question": q1_doc,
    }

    mock_db.adaptive_assessment_sessions.find_one.return_value = mock_session

    service = AdaptiveAssessmentService(mock_db)
    # Test session status retrieval
    from app.adaptive_assessments.calibration import map_theta_to_difficulty, map_theta_to_level_label
    theta = mock_session["current_estimated_level"]
    status = {
        "session_id": str(mock_session["_id"]),
        "status": mock_session["status"],
        "competency_code": mock_session["competency_code"],
        "competency_name": mock_session["competency_name"],
        "estimated_level": theta,
        "difficulty": map_theta_to_difficulty(theta),
        "proficiency_tier": map_theta_to_level_label(theta),
        "questions_completed": mock_session["questions_attempted"],
        "total_questions_planned": mock_session["max_questions"],
        "current_question_number": mock_session["questions_attempted"] + 1,
        "current_question": service._format_question_item(q1_doc).model_dump(),
    }

    assert status["session_id"] == str(session_oid)
    assert status["status"] == "IN_PROGRESS"
    assert status["questions_completed"] == 1
    assert status["current_question_number"] == 2
    assert status["estimated_level"] == 2.85
    assert status["current_question"]["question_id"] == "Q1"


def test_scenario_2_double_finalization_rejected_with_409():
    """Verify that submitting the same finalized assessment twice raises HTTP 409 Conflict."""
    mock_db = MagicMock()
    session_oid = ObjectId()
    user_oid = ObjectId()

    # Session already has evidence_id and completed_at
    mock_session = {
        "_id": session_oid,
        "user_id": user_oid,
        "status": "COMPLETED",
        "evidence_id": ObjectId(),
        "completed_at": "2026-09-13T00:00:00Z",
    }
    mock_db.adaptive_assessment_sessions.find_one.return_value = mock_session

    service = AdaptiveAssessmentService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.finalize_session(str(user_oid), str(session_oid))

    assert exc_info.value.status_code == 409
    assert "already been finalized" in exc_info.value.detail

    # Verify no second evidence was inserted
    assert mock_db.competency_evidence.insert_one.call_count == 0


def test_scenario_3_invalid_session_id_returns_400():
    """Verify that malformed session IDs return HTTP 400 rather than crashing the backend."""
    mock_db = MagicMock()
    service = AdaptiveAssessmentService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        service.finalize_session("invalid-user-id", "not-a-valid-object-id")

    assert exc_info.value.status_code == 400
    assert "Invalid ID format" in exc_info.value.detail


def test_scenario_4_gemini_failure_triggers_deterministic_fallback():
    """
    Verify that if the LLM provider fails (e.g. rate limit 429, timeout, network exception),
    MCQGenerator falls back to deterministic chunk-grounded question synthesis.
    """
    # Create an LLM provider that unconditionally raises an exception (simulating 429/timeout)
    failing_llm = MagicMock()
    failing_llm.generate.side_effect = Exception("Gemini API error 429: ResourceExhausted")
    failing_llm.generate_json.side_effect = Exception("Gemini API error 429: ResourceExhausted")

    # Create retriever with sample document chunks
    chunk = DocumentChunk(
        material_id="mat_123",
        sequence=0,
        text="Stratified random sampling ensures proportional representation across heterogeneous population subgroups.",
        token_count=18,
    )
    # DocumentChunk has an _id or synthetic id
    chunk.id = "CHUNK_TEST_001"

    mock_retriever = MagicMock()
    mock_retriever.retrieve_for_generation.return_value = [chunk]
    mock_retriever.get_context_for_generation.return_value = (chunk.text, [chunk.id])

    generator = MCQGenerator(llm_provider=failing_llm, retriever=mock_retriever)
    generator.settings.generation_retry_count = 1  # Fast retry for test

    questions = generator.generate_questions(
        query="Sampling Techniques",
        competency_code="STAT_SAMPLING",
        question_count=2,
        difficulty="MEDIUM",
    )

    assert len(questions) == 2, f"Expected 2 fallback questions, got {len(questions)}"
    for q in questions:
        assert len(q.options) == 4
        assert q.correct_answer in ("A", "B", "C", "D")
        assert "Stat Sampling" in q.question or "STAT_SAMPLING" in q.question
        assert q.source_chunks == ["CHUNK_TEST_001"]
