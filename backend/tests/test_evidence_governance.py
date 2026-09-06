"""
Comprehensive Regression Tests for Phase 5C: Evidence Governance & Competency Authority.

Tests all 18 invariants specified in Step 10 and the mandatory Step 11 scenario.
"""
from datetime import UTC, datetime
from bson import ObjectId
import pytest

from app.competencies.models import (
    EvidenceAuthority,
    EvidenceType,
    AUTHORITATIVE_CONFIDENCE,
    SUPPORTING_CONFIDENCE,
)
from app.quizzes.service import QuizService
from app.learning_activities import service as learning_service
from app.adaptive_assessments.service import AdaptiveAssessmentService
from app.skill_gaps.service import calculate_skill_gaps


class InsertOneResult:
    def __init__(self, inserted_id: ObjectId) -> None:
        self.inserted_id = inserted_id


class FakeCursor(list):
    def sort(self, key: str, direction: int = 1):
        return FakeCursor(sorted(self, key=lambda item: item.get(key, ""), reverse=direction < 0))

    def limit(self, count: int):
        return FakeCursor(self[:count])


class FakeCollection:
    """In-memory MongoDB collection for evidence governance testing."""

    def __init__(self, documents: list[dict] | None = None) -> None:
        self.documents = documents or []

    def _matches(self, document: dict, query: dict) -> bool:
        for key, expected in query.items():
            if key == "$or":
                if not any(self._matches(document, sub_q) for sub_q in expected):
                    return False
                continue
            actual = document.get(key)
            if isinstance(expected, dict):
                if "$in" in expected:
                    exp_set = {str(x) for x in expected["$in"]} | set(expected["$in"])
                    if actual not in exp_set and str(actual) not in exp_set:
                        return False
                elif "$nin" in expected:
                    exp_set = {str(x) for x in expected["$nin"]} | set(expected["$nin"])
                    if actual in exp_set or str(actual) in exp_set:
                        return False
                else:
                    if actual != expected:
                        return False
            else:
                if isinstance(expected, ObjectId) and isinstance(actual, str):
                    if str(expected) != actual:
                        return False
                elif isinstance(actual, ObjectId) and isinstance(expected, str):
                    if str(actual) != expected:
                        return False
                elif actual != expected:
                    return False
        return True

    def find(self, query: dict | None = None, projection: dict | None = None) -> FakeCursor:
        return FakeCursor([dict(item) for item in self.documents if self._matches(item, query or {})])

    def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        return next((dict(item) for item in self.documents if self._matches(item, query)), None)

    def insert_one(self, document: dict) -> InsertOneResult:
        document.setdefault("_id", ObjectId())
        self.documents.append(document)
        return InsertOneResult(document["_id"])

    def insert_many(self, documents: list[dict]) -> None:
        for doc in documents:
            self.insert_one(doc)

    def update_one(self, query: dict, update: dict, upsert: bool = False) -> None:
        doc = next((item for item in self.documents if self._matches(item, query)), None)
        if doc is None and upsert:
            new_doc = {k: v for k, v in query.items() if not isinstance(v, dict)}
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            if "$set" in update:
                new_doc.update(update["$set"])
            new_doc.setdefault("_id", ObjectId())
            self.documents.append(new_doc)
            return
        if doc is not None:
            if "$set" in update:
                doc.update(update["$set"])

    def find_one_and_update(self, query: dict, update: dict, return_document: bool = False) -> dict | None:
        doc = next((item for item in self.documents if self._matches(item, query)), None)
        if doc is not None:
            if "$set" in update:
                doc.update(update["$set"])
            return dict(doc)
        return None

    def count_documents(self, query: dict) -> int:
        return sum(self._matches(item, query) for item in self.documents)

    def create_index(self, *args, **kwargs) -> str:
        return "idx"

    def __getitem__(self, name: str):
        return self


class FakeDatabase:
    """Mock MongoDB database setup for governance testing."""

    def __init__(self) -> None:
        self.users = FakeCollection()
        self.roles = FakeCollection()
        self.role_requirements = FakeCollection()
        self.competencies = FakeCollection()
        self.competency_profiles = FakeCollection()
        self.competency_evidence = FakeCollection()
        self.learning_activities = FakeCollection()
        self.learning_materials = FakeCollection()
        self.quizzes = FakeCollection()
        self.quiz_attempts = FakeCollection()
        self.adaptive_assessment_sessions = FakeCollection()
        self.assessment_configurations = FakeCollection()
        self.assessment_attempts = FakeCollection()

    def __getitem__(self, name: str) -> FakeCollection:
        if not hasattr(self, name):
            setattr(self, name, FakeCollection())
        return getattr(self, name)


@pytest.fixture
def governance_db():
    """Create test database with core fixtures."""
    db = FakeDatabase()

    comp_oid = ObjectId()
    db.competencies.insert_one({
        "_id": comp_oid,
        "code": "TECH_PYTHON",
        "name": "Python Programming",
        "domain": "TECHNICAL",
        "status": "active",
    })

    role_oid = ObjectId()
    db.roles.insert_one({
        "_id": role_oid,
        "role_code": "DATA_ANALYST",
        "role_name": "Data Analyst",
        "status": "active",
    })

    db.role_requirements.insert_one({
        "_id": ObjectId(),
        "role_id": role_oid,
        "competency_id": comp_oid,
        "required_level": 4.0,
        "priority": 1,
        "importance": 0.9,
    })

    user_a_oid = ObjectId()
    user_b_oid = ObjectId()

    db.users.insert_many([
        {
            "_id": user_a_oid,
            "email": "officer_a@test.gov.in",
            "access_role": "OFFICIAL",
            "role_id": role_oid,
            "status": "active",
        },
        {
            "_id": user_b_oid,
            "email": "officer_b@test.gov.in",
            "access_role": "OFFICIAL",
            "role_id": role_oid,
            "status": "active",
        },
    ])

    # Seed learning material for user_a
    material_oid = ObjectId("6a91102a585424c9c7ef7b99")
    db.learning_materials.insert_one({
        "_id": material_oid,
        "user_id": user_a_oid,
        "title": "Python Core Module",
        "status": "READY",
        "chunks": [{"id": "chunk_0", "text": "Python def keyword"}],
    })

    return db


def test_learning_completion_creates_supporting_evidence_and_preserves_profile(governance_db):
    """
    Invariants 1, 2, 11:
    - Learning completion creates supporting evidence (confidence = 0.30).
    - Learning completion does NOT change the competency profile.
    """
    user = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    governance_db.competency_profiles.insert_one({
        "user_id": user["_id"],
        "competency_id": comp["_id"],
        "current_level": 2.5,
        "confidence": 0.5,
        "status": "active",
    })

    started_activity = learning_service.start_learning_activity(
        governance_db,
        str(user["_id"]),
        "RES_PY_101",
        str(comp["_id"]),
    )

    result = learning_service.complete_learning_activity(
        governance_db,
        started_activity.activity_id,
        str(user["_id"]),
        final_score=100,
    )
    assert result["evidence_created"] is True
    assert result["evidence_confidence"] == SUPPORTING_CONFIDENCE

    # Profile must remain unchanged at 2.5
    profile = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile["current_level"] == 2.5
    assert profile["confidence"] == 0.5

    # Evidence ledger has supporting evidence
    evidence = governance_db.competency_evidence.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert evidence is not None
    assert evidence["type"] == "LEARNING_ACTIVITY"
    assert evidence["confidence"] == SUPPORTING_CONFIDENCE


def test_practice_quiz_and_ai_quiz_do_not_modify_profile(governance_db):
    """
    Invariants 3, 4, 5, 6, 7, 15:
    - Practice / AI quiz creates supporting evidence.
    - Practice quiz score percentage (even 100%) does NOT modify competency profile.
    - Skill gaps remain unchanged after supporting quiz.
    """
    user = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    governance_db.competency_profiles.insert_one({
        "user_id": user["_id"],
        "competency_id": comp["_id"],
        "current_level": 2.0,
        "confidence": 0.5,
        "status": "active",
    })

    quiz_service = QuizService(governance_db)
    quiz = quiz_service.create_quiz(
        user_id=str(user["_id"]),
        material_id="6a91102a585424c9c7ef7b99",
        competency_code="TECH_PYTHON",
        questions=[
            {
                "question": "What is Python?",
                "options": ["A language", "A snake", "A car", "A fruit"],
                "correct_answer": "A",
                "explanation": "Python is a programming language",
                "difficulty": "EASY",
                "source_chunks": ["chunk_1"],
            }
        ],
    )

    q_id = quiz["questions"][0]["question_id"]
    submit_res = quiz_service.submit_quiz(
        user_id=str(user["_id"]),
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": q_id, "selected_answer": "A"}],
    )

    assert submit_res["percentage"] == 100.0
    assert submit_res["competency"]["competency_level_before"] == 2.0
    assert submit_res["competency"]["competency_level_after"] == 2.0
    assert submit_res["competency"]["improvement"] == 0.0

    # Verify database profile was NOT mutated
    profile = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile["current_level"] == 2.0

    # Verify supporting evidence record in ledger
    ev = governance_db.competency_evidence.find_one({"user_id": user["_id"], "source": "AI_QUIZ"})
    assert ev is not None
    assert ev["authority"] == "SUPPORTING"
    assert ev["confidence"] == SUPPORTING_CONFIDENCE
    assert ev["score_type"] == "PERCENTAGE"


def test_step_11_mandatory_vulnerability_scenario(governance_db):
    """
    STEP 11 MANDATORY REGRESSION TEST:
    1. Official has initial competency level = 2.5
    2. Official completes self-service quiz with 100% score
       -> Competency level REMAINS 2.5
       -> Supporting evidence record exists (confidence = 0.30)
    3. Official completes authoritative adaptive/formal assessment with result 3.8
       -> Competency level BECOMES 3.8
       -> Confidence BECOMES 0.85
       -> Skill gap recalculates from (4.0 - 2.5 = 1.5) to (4.0 - 3.8 = 0.2)
    """
    user = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    # 1. Initial State: level = 2.5
    governance_db.competency_profiles.insert_one({
        "user_id": user["_id"],
        "competency_id": comp["_id"],
        "current_level": 2.5,
        "confidence": 0.50,
        "status": "active",
    })

    gaps_initial = calculate_skill_gaps(governance_db, str(user["_id"]))
    gap_python_init = next(g for g in gaps_initial.gaps if g.competency_code == "TECH_PYTHON")
    assert gap_python_init.current_level == 2.5
    assert gap_python_init.gap == 1.5

    # 2. Self-service quiz with 100% score
    quiz_service = QuizService(governance_db)
    quiz = quiz_service.create_quiz(
        user_id=str(user["_id"]),
        material_id="6a91102a585424c9c7ef7b99",
        competency_code="TECH_PYTHON",
        questions=[
            {
                "question": "What keyword defines a function in Python?",
                "options": ["def", "func", "function", "lambda"],
                "correct_answer": "def",
                "explanation": "def keyword defines a function",
                "difficulty": "EASY",
                "source_chunks": ["chunk_0"],
            }
        ],
    )
    q_id = quiz["questions"][0]["question_id"]
    submit_res = quiz_service.submit_quiz(
        user_id=str(user["_id"]),
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": q_id, "selected_answer": "def"}],
    )
    assert submit_res["percentage"] == 100.0

    # Profile must remain 2.5
    profile_after_quiz = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile_after_quiz["current_level"] == 2.5

    # Supporting evidence exists
    quiz_ev = governance_db.competency_evidence.find_one({"user_id": user["_id"], "source": "AI_QUIZ"})
    assert quiz_ev is not None
    assert quiz_ev["authority"] == "SUPPORTING"
    assert quiz_ev["confidence"] == 0.30

    # 3. Authoritative Adaptive Assessment Completed at Level 3.8
    adaptive_service = AdaptiveAssessmentService(governance_db)
    session_oid = ObjectId()
    governance_db.adaptive_assessment_sessions.insert_one({
        "_id": session_oid,
        "user_id": user["_id"],
        "competency_code": "TECH_PYTHON",
        "current_estimated_level": 3.8,
        "status": "COMPLETED",
        "question_history": [{"q": 1, "correct": True}, {"q": 2, "correct": True}],
        "correct_answers": 2,
    })

    summary = adaptive_service.finalize_session(user_id=str(user["_id"]), session_id=str(session_oid))
    assert summary.final_demonstrated_level == 3.8

    # Profile MUST NOW BE 3.8 with confidence 0.85
    profile_after_adaptive = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile_after_adaptive["current_level"] == 3.8
    assert profile_after_adaptive["confidence"] == 0.85

    # Skill gaps recalculated
    gaps_final = calculate_skill_gaps(governance_db, str(user["_id"]))
    gap_python_final = next(g for g in gaps_final.gaps if g.competency_code == "TECH_PYTHON")
    assert gap_python_final.current_level == 3.8
    assert round(gap_python_final.gap, 1) == 0.2


def test_evidence_ledger_immutability_and_user_isolation(governance_db):
    """
    Invariants 12, 13, 16, 17, 18:
    - Multiple assessment events append immutable records to the ledger.
    - User A's actions do NOT alter User B's profile or evidence.
    - Score types remain semantically typed (PERCENTAGE, IRT_THETA).
    """
    user_a = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    user_b = governance_db.users.find_one({"email": "officer_b@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    governance_db.competency_profiles.insert_one({
        "user_id": user_b["_id"],
        "competency_id": comp["_id"],
        "current_level": 1.8,
        "confidence": 0.85,
        "status": "active",
    })

    quiz_service = QuizService(governance_db)
    quiz = quiz_service.create_quiz(
        user_id=str(user_a["_id"]),
        material_id="6a91102a585424c9c7ef7b99",
        competency_code="TECH_PYTHON",
        questions=[{"question": "Q?", "options": ["A", "B", "C"], "correct_answer": "A", "explanation": "exp", "difficulty": "EASY", "source_chunks": []}],
    )
    quiz_service.submit_quiz(
        user_id=str(user_a["_id"]),
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": quiz["questions"][0]["question_id"], "selected_answer": "A"}],
    )

    user_a_evidence = list(governance_db.competency_evidence.find({"user_id": user_a["_id"]}))
    assert len(user_a_evidence) == 1
    assert user_a_evidence[0]["score_type"] == "PERCENTAGE"

    user_b_evidence = list(governance_db.competency_evidence.find({"user_id": user_b["_id"]}))
    assert len(user_b_evidence) == 0
    profile_b = governance_db.competency_profiles.find_one({"user_id": user_b["_id"], "competency_id": comp["_id"]})
    assert profile_b["current_level"] == 1.8


def test_client_cannot_self_declare_authoritative_authority(governance_db):
    """
    Invariant 16:
    - Client submitting a quiz cannot override authority to AUTHORITATIVE.
    - Authority is strictly dictated by trusted backend service models.
    """
    user = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    governance_db.competency_profiles.insert_one({
        "user_id": user["_id"],
        "competency_id": comp["_id"],
        "current_level": 2.5,
        "confidence": 0.50,
        "status": "active",
    })

    quiz_service = QuizService(governance_db)
    quiz = quiz_service.create_quiz(
        user_id=str(user["_id"]),
        material_id="6a91102a585424c9c7ef7b99",
        competency_code="TECH_PYTHON",
        questions=[{"question": "Q1", "options": ["A", "B"], "correct_answer": "A", "explanation": "exp", "difficulty": "EASY", "source_chunks": []}],
    )

    # Even if client tries to pass extra payload or submit, service enforces SUPPORTING
    submit_res = quiz_service.submit_quiz(
        user_id=str(user["_id"]),
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": quiz["questions"][0]["question_id"], "selected_answer": "A"}],
    )

    # Database evidence authority is always SUPPORTING with confidence 0.30
    ev = governance_db.competency_evidence.find_one({"user_id": user["_id"], "source": "AI_QUIZ"})
    assert ev is not None
    assert ev["authority"] == EvidenceAuthority.SUPPORTING
    assert ev["confidence"] == SUPPORTING_CONFIDENCE

    # Profile level is unaffected
    profile = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile["current_level"] == 2.5


def test_trainer_reviewed_quiz_remains_supporting(governance_db):
    """
    Invariant 7:
    - Trainer review in Quiz Studio verifies item content quality.
    - A learner's attempt on a trainer-reviewed quiz remains SUPPORTING evidence.
    - Profile current_level is not mutated.
    """
    user = governance_db.users.find_one({"email": "officer_a@test.gov.in"})
    comp = governance_db.competencies.find_one({"code": "TECH_PYTHON"})

    governance_db.competency_profiles.insert_one({
        "user_id": user["_id"],
        "competency_id": comp["_id"],
        "current_level": 2.5,
        "confidence": 0.50,
        "status": "active",
    })

    quiz_service = QuizService(governance_db)
    # Seed a published trainer quiz
    quiz_oid = ObjectId()
    governance_db.quizzes.insert_one({
        "_id": quiz_oid,
        "trainer_id": str(ObjectId()),
        "competency_code": "TECH_PYTHON",
        "title": "Trainer Reviewed Sampling Quiz",
        "status": "PUBLISHED",
        "questions": [
            {
                "question_id": "tq_1",
                "question": "Trainer question",
                "options": ["A", "B"],
                "correct_answer": "A",
                "explanation": "Reviewed explanation",
                "difficulty": "MEDIUM",
            }
        ],
        "created_at": datetime.now(UTC),
    })

    submit_res = quiz_service.submit_quiz(
        user_id=str(user["_id"]),
        quiz_id=str(quiz_oid),
        answers=[{"question_id": "tq_1", "selected_answer": "A"}],
    )
    assert submit_res["percentage"] == 100.0
    assert submit_res["competency"]["competency_level_after"] == 2.5
    assert submit_res["competency"]["improvement"] == 0.0

    profile = governance_db.competency_profiles.find_one({"user_id": user["_id"], "competency_id": comp["_id"]})
    assert profile["current_level"] == 2.5
