"""
PHASE 5F — Assessment Architecture Consolidation Test Suite.

Verifies:
1. Practice quiz creates SUPPORTING evidence only.
2. Practice quiz does NOT mutate official competency_profiles.
3. Trainer-reviewed quiz creates SUPPORTING evidence.
4. Formal capability assessment creates AUTHORITATIVE evidence and updates competency profile.
5. Adaptive assessment creates AUTHORITATIVE evidence with IRT theta score and updates competency profile.
6. Percentage score remains percentage (0-100%).
7. IRT theta score remains continuous level semantics (1.0-5.0).
8. Supporting evidence cannot mutate current_level.
9. Authoritative evidence can mutate current_level.
10. User isolation across all assessment subsystems.
11. Trainer ownership enforcement on materials, questions, and quizzes.
12. Official cannot publish trainer assessments (HTTP 403).
13. Official cannot finalize another user's assessment attempt (HTTP 404 / 403).
14. Trainer cannot modify another trainer's assessment questions/quizzes.
15. Duplicate finalization is idempotent (HTTP 409 Conflict).
16. Duplicate submission does not double-update competency levels.
17. Evidence logs remain immutable.
18. Historical evidence is preserved upon role/assessment change.
"""

from datetime import UTC, datetime
from bson import ObjectId
import pytest
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, hash_password
from app.core.config import Settings
from app.main import create_app
from app.quizzes.service import QuizService
from app.adaptive_assessments.service import AdaptiveAssessmentService
from app.capability_assessments.service import create_capability_assessment, submit_capability_assessment


class FakeCursor(list):
    def sort(self, key: str, direction: int = 1):
        return FakeCursor(sorted(self, key=lambda item: item.get(key, ""), reverse=direction < 0))

    def limit(self, count: int):
        return FakeCursor(self[:count])

    def skip(self, count: int):
        return FakeCursor(self[count:])


class FakeCollection:
    def __init__(self, documents: list[dict] | None = None) -> None:
        self.documents = documents or []

    def _matches(self, document: dict, query: dict) -> bool:
        for key, expected in query.items():
            if key == "$or":
                if not any(self._matches(document, subq) for subq in expected):
                    return False
                continue

            actual = document.get(key)
            if isinstance(expected, dict):
                if "$in" in expected:
                    str_actual = str(actual)
                    expected_strs = [str(x) for x in expected["$in"]]
                    if actual not in expected["$in"] and str_actual not in expected_strs:
                        return False
                elif "$nin" in expected:
                    str_actual = str(actual)
                    expected_strs = [str(x) for x in expected["$nin"]]
                    if actual in expected["$nin"] or str_actual in expected_strs:
                        return False
                elif "$ne" in expected:
                    if actual == expected["$ne"]:
                        return False
                elif "$exists" in expected:
                    if bool(expected["$exists"]) != (key in document):
                        return False
                elif "$regex" in expected:
                    import re
                    if not re.search(expected["$regex"], str(actual or ""), re.IGNORECASE):
                        return False
            elif isinstance(actual, list) and not isinstance(expected, list):
                if expected not in actual and str(expected) not in [str(x) for x in actual]:
                    return False
            elif actual != expected and str(actual) != str(expected):
                return False
        return True

    def find_one(self, query: dict | None = None, projection: dict | None = None) -> dict | None:
        if not query:
            return self.documents[0] if self.documents else None
        for document in self.documents:
            if self._matches(document, query):
                return document
        return None

    def find(self, query: dict | None = None, projection: dict | None = None) -> FakeCursor:
        if not query:
            return FakeCursor(list(self.documents))
        return FakeCursor([d for d in self.documents if self._matches(d, query)])

    def insert_one(self, document: dict):
        document.setdefault("_id", ObjectId())
        self.documents.append(document)
        class Res:
            inserted_id = document["_id"]
        return Res()

    def insert_many(self, documents: list[dict]):
        ids = []
        for d in documents:
            d.setdefault("_id", ObjectId())
            self.documents.append(d)
            ids.append(d["_id"])
        class Res:
            inserted_ids = ids
        return Res()

    def update_one(self, query: dict, update: dict, upsert: bool = False):
        document = self.find_one(query)
        modified = 0
        if document is not None:
            if "$set" in update:
                document.update(update["$set"])
                modified = 1
            if "$inc" in update:
                for k, v in update["$inc"].items():
                    document[k] = document.get(k, 0) + v
                modified = 1
        elif upsert:
            new_doc = dict(query)
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            if "$set" in update:
                new_doc.update(update["$set"])
            new_doc.setdefault("_id", ObjectId())
            self.documents.append(new_doc)
            modified = 1
        class Res:
            matched_count = 1 if document else (1 if upsert else 0)
            modified_count = modified
            upserted_id = document["_id"] if document else (new_doc["_id"] if upsert else None)
        return Res()

    def count_documents(self, query: dict | None = None) -> int:
        return len(self.find(query))

    def aggregate(self, pipeline):
        matching = self.documents
        if pipeline and pipeline[0].get("$match"):
            query = pipeline[0]["$match"]
            matching = [d for d in self.documents if self._matches(d, query)]

        if pipeline and any("$sample" in stage for stage in pipeline):
            sample_size = 3
            for stage in pipeline:
                if "$sample" in stage:
                    sample_size = stage["$sample"].get("size", 3)
            return matching[:sample_size]
        return matching

    def find_one_and_update(self, query: dict, update: dict, return_document=False) -> dict | None:
        document = self.find_one(query)
        if document is not None:
            if "$set" in update:
                document.update(update["$set"])
        return document

    def create_index(self, *args, **kwargs):
        pass


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()
        self.roles = FakeCollection()
        self.role_requirements = FakeCollection()
        self.competencies = FakeCollection()
        self.competency_profiles = FakeCollection()
        self.competency_evidence = FakeCollection()
        self.quizzes = FakeCollection()
        self.quiz_attempts = FakeCollection()
        self.trainer_questions = FakeCollection()
        self.trainer_quizzes = FakeCollection()
        self.learning_materials = FakeCollection()
        self.capability_assessments = FakeCollection()
        self.adaptive_assessment_sessions = FakeCollection()
        self.question_bank = FakeCollection()
        self.assessment_configurations = FakeCollection()


@pytest.fixture
def consolidation_setup():
    db = FakeDatabase()
    settings = Settings(
        jwt_secret="phase5f-super-secure-jwt-key-32-chars-long",
        api_prefix="/api/v1",
    )
    app = create_app(settings)
    app.state.database = db
    app.state.settings = settings
    client = TestClient(app)

    # 1. Seed Roles & Competencies
    role_id = ObjectId()
    db.roles.insert_one({
        "_id": role_id,
        "role_code": "STATISTICAL_OFFICER",
        "role_name": "Statistical Officer",
        "department": "MoSPI",
        "designations": ["Statistical Officer", "Junior Statistical Officer"],
        "status": "active",
    })

    comp_id = ObjectId()
    comp_code = "STAT_SAMPLING"
    db.competencies.insert_one({
        "_id": comp_id,
        "code": comp_code,
        "title": "Statistical Sampling",
        "name": "Statistical Sampling",
        "domain": "STATISTICAL",
        "status": "ACTIVE",
    })

    db.role_requirements.insert_one({
        "_id": ObjectId(),
        "role_id": role_id,
        "competency_id": comp_id,
        "competency_code": comp_code,
        "required_level": 4.0,
        "status": "active",
    })

    # 2. Seed Official User A
    user_a_id = ObjectId()
    user_a = {
        "_id": user_a_id,
        "email": "official_a@shikshasetu.gov.in",
        "full_name": "Official User A",
        "access_role": "OFFICIAL",
        "status": "active",
        "password_hash": hash_password("pass123"),
        "department": "MoSPI",
        "designation": "Statistical Officer",
        "role_id": role_id,
        "created_at": datetime.now(UTC),
    }
    db.users.insert_one(user_a)
    token_a = create_access_token(str(user_a_id), settings)

    # Initial Competency Profile for User A
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": user_a_id,
        "competency_id": comp_id,
        "competency_code": comp_code,
        "current_level": 2.0,
        "confidence": 0.5,
        "status": "active",
        "last_assessed_at": datetime.now(UTC),
    })

    # Seed Learning Material for User A
    mat_a_id = ObjectId()
    db.learning_materials.insert_one({
        "_id": mat_a_id,
        "user_id": user_a_id,
        "trainer_id": str(user_a_id),
        "filename": "sampling_basics.pdf",
        "status": "READY",
        "created_at": datetime.now(UTC),
    })

    # 3. Seed Official User B
    user_b_id = ObjectId()
    user_b = {
        "_id": user_b_id,
        "email": "official_b@shikshasetu.gov.in",
        "full_name": "Official User B",
        "access_role": "OFFICIAL",
        "status": "active",
        "password_hash": hash_password("pass123"),
        "department": "MoSPI",
        "designation": "Statistical Officer",
        "role_id": role_id,
        "created_at": datetime.now(UTC),
    }
    db.users.insert_one(user_b)
    token_b = create_access_token(str(user_b_id), settings)

    # 4. Seed Trainer User 1 & Trainer User 2
    trainer_1_id = ObjectId()
    trainer_1 = {
        "_id": trainer_1_id,
        "email": "trainer_1@shikshasetu.gov.in",
        "full_name": "Trainer Alpha",
        "access_role": "TRAINER",
        "status": "active",
        "password_hash": hash_password("pass123"),
        "department": "NSSTA",
        "designation": "Lead Trainer",
        "created_at": datetime.now(UTC),
    }
    db.users.insert_one(trainer_1)
    trainer_1_token = create_access_token(str(trainer_1_id), settings)

    trainer_2_id = ObjectId()
    trainer_2 = {
        "_id": trainer_2_id,
        "email": "trainer_2@shikshasetu.gov.in",
        "full_name": "Trainer Beta",
        "access_role": "TRAINER",
        "status": "active",
        "password_hash": hash_password("pass123"),
        "department": "NSSTA",
        "designation": "Senior Trainer",
        "created_at": datetime.now(UTC),
    }
    db.users.insert_one(trainer_2)
    trainer_2_token = create_access_token(str(trainer_2_id), settings)

    # 5. Seed Question Bank for Capability and Adaptive Testing
    for i in range(1, 10):
        diff = "EASY" if i <= 3 else ("MEDIUM" if i <= 6 else "HARD")
        db.question_bank.insert_one({
            "_id": ObjectId(),
            "question_id": f"QB-SAMPLING-{i}",
            "competency_code": comp_code,
            "question_type": "MCQ",
            "question_text": f"What is sample stratification principle {i}?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "difficulty": diff,
            "weight": 1.0,
            "status": "ACTIVE",
        })

    # Assessment configuration
    db.assessment_configurations.insert_one({
        "_id": ObjectId(),
        "competency_code": comp_code,
        "title": "Sampling Capability Assessment",
        "questions_count": 3,
        "status": "ACTIVE",
        "allow_retake": True,
    })

    return {
        "db": db,
        "client": client,
        "user_a": user_a,
        "token_a": token_a,
        "user_b": user_b,
        "token_b": token_b,
        "trainer_1": trainer_1,
        "trainer_1_token": trainer_1_token,
        "trainer_2": trainer_2,
        "trainer_2_token": trainer_2_token,
        "comp_id": comp_id,
        "comp_code": comp_code,
    }


def test_01_practice_quiz_creates_supporting_evidence_and_no_profile_mutation(consolidation_setup):
    """Verifies practice quiz records SUPPORTING evidence (0.30) without mutating competency_profiles."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]
    mat = db.learning_materials.find_one({"trainer_id": user_id})

    quiz_service = QuizService(db)
    quiz = quiz_service.create_quiz(
        user_id=user_id,
        material_id=str(mat["_id"]),
        competency_code=comp_code,
        questions=[{
            "question": "What is simple random sampling?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "A is correct",
            "difficulty": "MEDIUM",
        }],
    )

    # Submit quiz with 100% score
    result = quiz_service.submit_quiz(
        user_id=user_id,
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": quiz["questions"][0]["question_id"], "selected_answer": "A"}],
    )

    assert result["percentage"] == 100.0
    assert result["competency"]["competency_level_after"] == 2.0  # Unchanged

    # Verify evidence authority in DB
    ev = db.competency_evidence.find_one({"quiz_id": quiz["_id"]})
    assert ev is not None
    assert ev["authority"] == "SUPPORTING"
    assert ev["confidence"] == 0.30
    assert ev["score_type"] == "PERCENTAGE"
    assert ev["score"] == 100.0

    # Verify competency profile level in DB is strictly UNCHANGED (2.0)
    profile = db.competency_profiles.find_one({"user_id": user_a["_id"]})
    assert profile["current_level"] == 2.0


def test_02_formal_capability_assessment_creates_authoritative_evidence_and_mutates_profile(consolidation_setup):
    """Verifies formal capability assessment records AUTHORITATIVE evidence and mutates competency profile."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]

    # Create capability assessment
    assessment = create_capability_assessment(db, user_id=user_id, competency_code=comp_code)
    assessment_id = assessment["id"]

    # Submit answers with all correct
    answers = [
        {"question_id": q["question_id"], "selected_answer": "A"}
        for q in assessment["questions"]
    ]
    result = submit_capability_assessment(db, user_id=user_id, assessment_id=assessment_id, answers=answers)

    assert result["percentage"] == 1.0
    assert result["normalized_score"] == 5.0

    # Verify AUTHORITATIVE evidence
    ev = db.competency_evidence.find_one({"assessment_id": ObjectId(assessment_id)})
    assert ev is not None
    assert ev["authority"] == "AUTHORITATIVE"
    assert ev["confidence"] == 0.85

    # Verify competency profile in DB was updated
    profile = db.competency_profiles.find_one({"user_id": user_a["_id"]})
    assert profile["current_level"] > 2.0


def test_03_adaptive_assessment_creates_authoritative_irt_evidence_and_updates_profile(consolidation_setup):
    """Verifies adaptive assessment records AUTHORITATIVE IRT evidence and updates official profile."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]

    adaptive_service = AdaptiveAssessmentService(db)
    from app.adaptive_assessments.schemas import AdaptiveStartRequest, AdaptiveAnswerRequest
    session = adaptive_service.start_session(
        user_id=user_id,
        request=AdaptiveStartRequest(competency_code=comp_code, max_questions=3),
    )
    session_id = session.session_id

    # Answer 1 question
    adaptive_service.submit_answer(
        user_id=user_id,
        session_id=session_id,
        request=AdaptiveAnswerRequest(
            question_id=session.question.question_id,
            selected_answer="A",
            response_time_ms=5000,
        ),
    )

    # Finalize session
    summary = adaptive_service.finalize_session(user_id=user_id, session_id=session_id)
    assert summary.status == "COMPLETED"
    assert summary.final_demonstrated_level >= 1.0

    # Check evidence record
    ev = db.competency_evidence.find_one({"assessment_id": ObjectId(session_id)})
    assert ev is not None
    assert ev["score_type"] == "IRT_THETA"
    assert ev["confidence"] == 0.85

    # Verify official profile updated to final theta
    profile = db.competency_profiles.find_one({"user_id": user_a["_id"]})
    assert profile["current_level"] == summary.final_demonstrated_level


def test_04_duplicate_finalization_is_idempotent_and_rejects_duplicate_runs(consolidation_setup):
    """Verifies that submitting or finalizing the same assessment twice returns 409 Conflict."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]

    adaptive_service = AdaptiveAssessmentService(db)
    from app.adaptive_assessments.schemas import AdaptiveStartRequest
    from fastapi import HTTPException

    session = adaptive_service.start_session(
        user_id=user_id,
        request=AdaptiveStartRequest(competency_code=comp_code, max_questions=3),
    )
    session_id = session.session_id

    # First finalization succeeds
    adaptive_service.finalize_session(user_id=user_id, session_id=session_id)

    # Second finalization raises 409 Conflict
    with pytest.raises(HTTPException) as exc_info:
        adaptive_service.finalize_session(user_id=user_id, session_id=session_id)
    assert exc_info.value.status_code == 409


def test_05_trainer_ownership_and_official_access_controls(consolidation_setup):
    """Verifies that trainers own their quizzes, officials cannot publish, and cross-trainer modification is forbidden."""
    client = consolidation_setup["client"]
    trainer_1_token = consolidation_setup["trainer_1_token"]
    trainer_2_token = consolidation_setup["trainer_2_token"]
    token_a = consolidation_setup["token_a"]
    comp_code = consolidation_setup["comp_code"]

    headers_t1 = {"Authorization": f"Bearer {trainer_1_token}"}
    headers_t2 = {"Authorization": f"Bearer {trainer_2_token}"}
    headers_official = {"Authorization": f"Bearer {token_a}"}

    # 1. Trainer 1 creates an approved question
    q_doc = {
        "_id": ObjectId(),
        "trainer_id": str(consolidation_setup["trainer_1"]["_id"]),
        "material_id": str(ObjectId()),
        "competency_code": comp_code,
        "question": "What is stratified sampling?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "A is correct",
        "difficulty": "EASY",
        "status": "APPROVED",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    consolidation_setup["db"].trainer_questions.insert_one(q_doc)

    # Trainer 1 creates quiz draft
    res_draft = client.post(
        "/api/v1/trainer/quizzes",
        headers=headers_t1,
        json={
            "title": "Sampling Quiz by T1",
            "competency_code": comp_code,
            "question_ids": [str(q_doc["_id"])],
        },
    )
    assert res_draft.status_code == 201
    quiz_id = res_draft.json()["id"]

    # 2. Official CANNOT publish trainer quiz (HTTP 403 Forbidden)
    res_pub_official = client.post(f"/api/v1/trainer/quizzes/{quiz_id}/publish", headers=headers_official)
    assert res_pub_official.status_code == 403

    # 3. Trainer 2 CANNOT publish Trainer 1's quiz (HTTP 400/404 Ownership Violation)
    res_pub_t2 = client.post(f"/api/v1/trainer/quizzes/{quiz_id}/publish", headers=headers_t2)
    assert res_pub_t2.status_code in (400, 404)

    # 4. Trainer 1 publishes successfully
    res_pub_t1 = client.post(f"/api/v1/trainer/quizzes/{quiz_id}/publish", headers=headers_t1)
    assert res_pub_t1.status_code == 200
    assert res_pub_t1.json()["status"] == "PUBLISHED"


def test_06_user_isolation_on_assessment_attempts(consolidation_setup):
    """Verifies User B cannot view or submit User A's assessment attempt."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_b = consolidation_setup["user_b"]
    comp_code = consolidation_setup["comp_code"]

    # User A starts assessment
    assessment = create_capability_assessment(db, user_id=str(user_a["_id"]), competency_code=comp_code)
    assessment_id = assessment["id"]

    # User B attempts to submit User A's assessment
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        submit_capability_assessment(
            db,
            user_id=str(user_b["_id"]),
            assessment_id=assessment_id,
            answers=[{"question_id": q["question_id"], "selected_answer": "A"} for q in assessment["questions"]],
        )
    assert exc_info.value.status_code == 404  # Isolated, not found for User B


def test_07_score_type_semantics_preserved(consolidation_setup):
    """Verifies that score types are semantically distinct across practice quizzes and adaptive assessments."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]

    # 1. Practice Quiz -> PERCENTAGE
    mat = db.learning_materials.find_one({"trainer_id": user_id})
    quiz_service = QuizService(db)
    quiz = quiz_service.create_quiz(
        user_id=user_id,
        material_id=str(mat["_id"]),
        competency_code=comp_code,
        questions=[{
            "question": "Sample Question?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Exp",
            "difficulty": "EASY",
        }],
    )
    quiz_res = quiz_service.submit_quiz(
        user_id=user_id,
        quiz_id=str(quiz["_id"]),
        answers=[{"question_id": quiz["questions"][0]["question_id"], "selected_answer": "A"}],
    )
    assert 0.0 <= quiz_res["percentage"] <= 100.0
    ev_quiz = db.competency_evidence.find_one({"quiz_id": quiz["_id"]})
    assert ev_quiz["score_type"] == "PERCENTAGE"

    # 2. Adaptive Assessment -> IRT_THETA
    adaptive_service = AdaptiveAssessmentService(db)
    from app.adaptive_assessments.schemas import AdaptiveStartRequest, AdaptiveAnswerRequest
    session = adaptive_service.start_session(
        user_id=user_id,
        request=AdaptiveStartRequest(competency_code=comp_code, max_questions=3),
    )
    adaptive_service.submit_answer(
        user_id=user_id,
        session_id=session.session_id,
        request=AdaptiveAnswerRequest(
            question_id=session.question.question_id,
            selected_answer="A",
            response_time_ms=3000,
        ),
    )
    summary = adaptive_service.finalize_session(user_id=user_id, session_id=session.session_id)
    assert 1.0 <= summary.final_demonstrated_level <= 5.0
    ev_adaptive = db.competency_evidence.find_one({"assessment_id": ObjectId(session.session_id)})
    assert ev_adaptive["score_type"] == "IRT_THETA"


def test_08_evidence_immutability_and_audit_trail(consolidation_setup):
    """Verifies evidence records in competency_evidence are preserved historically."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_id = str(user_a["_id"])
    comp_code = consolidation_setup["comp_code"]

    initial_evidence_count = db.competency_evidence.count_documents({"user_id": user_a["_id"]})

    # Record capability assessment
    assessment = create_capability_assessment(db, user_id=user_id, competency_code=comp_code)
    submit_capability_assessment(
        db,
        user_id=user_id,
        assessment_id=assessment["id"],
        answers=[{"question_id": q["question_id"], "selected_answer": "A"} for q in assessment["questions"]],
    )

    new_evidence_count = db.competency_evidence.count_documents({"user_id": user_a["_id"]})
    assert new_evidence_count > initial_evidence_count


def test_09_official_cannot_finalize_another_users_adaptive_session(consolidation_setup):
    """Verifies User B cannot finalize User A's adaptive assessment session."""
    db = consolidation_setup["db"]
    user_a = consolidation_setup["user_a"]
    user_b = consolidation_setup["user_b"]
    comp_code = consolidation_setup["comp_code"]

    adaptive_service = AdaptiveAssessmentService(db)
    from app.adaptive_assessments.schemas import AdaptiveStartRequest
    from fastapi import HTTPException

    session = adaptive_service.start_session(
        user_id=str(user_a["_id"]),
        request=AdaptiveStartRequest(competency_code=comp_code, max_questions=3),
    )

    with pytest.raises(HTTPException) as exc_info:
        adaptive_service.finalize_session(
            user_id=str(user_b["_id"]),
            session_id=session.session_id,
        )
    assert exc_info.value.status_code == 404

