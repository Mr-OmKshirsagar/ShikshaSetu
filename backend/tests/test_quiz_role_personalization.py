"""
Automated unit and integration test suite for Quiz Role & Competency Personalization.

Verifies:
1. Statistical Officer sees Statistical Sampling quiz (matching role/gap).
2. Statistical Officer does NOT see Land Records quiz (targeted to Revenue).
3. Talathi sees Land Records / Revenue Administration quiz.
4. Talathi does NOT see Statistical Sampling quiz.
5. Explicitly assigned quiz by trainer is visible to any learner at Priority 1 (ASSIGNED_BY_TRAINER).
6. Trainer can manage and access question and quiz pools without official competency restrictions.
7. Unauthorized official cannot fetch ineligible quiz via GET /quizzes/{id} (returns 404).
8. Golden demo persona (Rajesh Sharma) retains Statistical Sampling as CRITICAL_GAP at Priority 2.
9. Non-gap role-required competency remains available as REQUIRED_COMPETENCY at Priority 6.
10. Role-targeted quiz is visible as ROLE_TARGETED (Priority 5).
"""

from datetime import UTC, datetime
from bson import ObjectId
import pytest
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, hash_password
from app.core.config import Settings
from app.main import create_app


class FakeCursor(list):
    def sort(self, key: str, direction: int = 1):
        return FakeCursor(sorted(self, key=lambda item: item.get(key, ""), reverse=direction < 0))

    def limit(self, count: int):
        return FakeCursor(self[:count])


class FakeCollection:
    """In-memory collection supporting queries, insertions, and updates."""

    def __init__(self, documents: list[dict] | None = None) -> None:
        self.documents = documents or []

    def _matches(self, document: dict, query: dict) -> bool:
        for key, expected in query.items():
            if key == "$or":
                if not any(self._matches(document, subq) for subq in expected):
                    return False
                continue
            if key == "$and":
                if not all(self._matches(document, subq) for subq in expected):
                    return False
                continue

            actual = document.get(key)
            if isinstance(expected, dict):
                if "$in" in expected:
                    str_actual = str(actual)
                    expected_strs = [str(x) for x in expected["$in"]]
                    if actual not in expected["$in"] and str_actual not in expected_strs:
                        return False
                elif "$ne" in expected:
                    if actual == expected["$ne"]:
                        return False
                elif "$exists" in expected:
                    if bool(expected["$exists"]) != (key in document):
                        return False
            elif isinstance(actual, list) and not isinstance(expected, list):
                if expected not in actual and str(expected) not in [str(x) for x in actual]:
                    return False
            elif actual != expected and str(actual) != str(expected):
                return False
        return True

    def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        for document in self.documents:
            if self._matches(document, query):
                return dict(document)
        return None

    def find(self, query: dict | None = None, projection: dict | None = None) -> FakeCursor:
        if not query:
            return FakeCursor([dict(d) for d in self.documents])
        return FakeCursor([dict(d) for d in self.documents if self._matches(d, query)])

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
        document = None
        for d in self.documents:
            if self._matches(d, query):
                document = d
                break
        if document is not None:
            if "$set" in update:
                document.update(update["$set"])
        elif upsert:
            new_doc = dict(query)
            if "$setOnInsert" in update:
                new_doc.update(update["$setOnInsert"])
            if "$set" in update:
                new_doc.update(update["$set"])
            new_doc.setdefault("_id", ObjectId())
            self.documents.append(new_doc)

    def count_documents(self, query: dict) -> int:
        return sum(1 for d in self.documents if self._matches(d, query))

    def create_index(self, *args, **kwargs) -> str:
        return "idx"


class FakeDatabase:
    """Mock MongoDB database setup for isolated quiz personalization tests."""

    def __init__(self) -> None:
        self.users = FakeCollection()
        self.roles = FakeCollection()
        self.role_requirements = FakeCollection()
        self.competencies = FakeCollection()
        self.competency_profiles = FakeCollection()
        self.competency_evidence = FakeCollection()
        self.quizzes = FakeCollection()
        self.quiz_attempts = FakeCollection()
        self.trainer_questions = FakeCollection()
        self.learning_materials = FakeCollection()


@pytest.fixture
def personalization_env():
    """Create test client, fake database, and seed standard roles, quizzes, and users."""
    db = FakeDatabase()
    settings = Settings(
        mongodb_uri="mongodb://test",
        mongodb_database="test_personalization_db",
        jwt_secret="super-secret-key-for-testing-only-32-chars",
    )
    app = create_app(settings)
    app.state.database = db
    client = TestClient(app)

    now = datetime.now(UTC)

    # 1. Seed Roles
    stat_role_id = "STATISTICAL_OFFICER"
    revenue_role_id = "REVENUE_ADMINISTRATION_OFFICER"
    stat_role_oid = ObjectId()
    revenue_role_oid = ObjectId()

    db.roles.insert_many([
        {
            "_id": stat_role_oid,
            "role_id": stat_role_id,
            "role_code": stat_role_id,
            "role_name": "Statistical Officer",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "designations": ["Statistical Officer", "Assistant Director (Statistics)", "Research Officer"],
        },
        {
            "_id": revenue_role_oid,
            "role_id": revenue_role_id,
            "role_code": revenue_role_id,
            "role_name": "Revenue Administration Officer",
            "department": "Department of Revenue & Land Records",
            "designations": ["Talathi", "Patwari", "Lekhpal", "Village Revenue Officer", "Tahsildar"],
        },
    ])

    # 2. Seed Role Requirements
    db.role_requirements.insert_many([
        {
            "role_id": stat_role_id,
            "competency_id": "STAT_SAMPLING",
            "competency_code": "STAT_SAMPLING",
            "required_level": 4.0,
            "priority": "MANDATORY",
            "criticality": "HIGH",
        },
        {
            "role_id": stat_role_id,
            "competency_id": "TECH_DATA_VISUALIZATION",
            "competency_code": "TECH_DATA_VISUALIZATION",
            "required_level": 3.0,
            "priority": "RECOMMENDED",
            "criticality": "MEDIUM",
        },
        {
            "role_id": revenue_role_id,
            "competency_id": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE",
            "competency_code": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE",
            "required_level": 4.0,
            "priority": "MANDATORY",
            "criticality": "HIGH",
        },
        {
            "role_id": revenue_role_id,
            "competency_id": "DIGOV_DIGITAL_SIGNATURES",
            "competency_code": "DIGOV_DIGITAL_SIGNATURES",
            "required_level": 3.0,
            "priority": "MANDATORY",
            "criticality": "MEDIUM",
        },
    ])

    # 3. Seed Competencies
    db.competencies.insert_many([
        {"_id": ObjectId(), "code": "STAT_SAMPLING", "competency_id": "STAT_SAMPLING", "competency_name": "Statistical Sampling", "name": "Statistical Sampling", "category": "DOMAIN"},
        {"_id": ObjectId(), "code": "TECH_DATA_VISUALIZATION", "competency_id": "TECH_DATA_VISUALIZATION", "competency_name": "Data Visualization", "name": "Data Visualization", "category": "DOMAIN"},
        {"_id": ObjectId(), "code": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE", "competency_id": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE", "competency_name": "Digital Public Infrastructure", "name": "Digital Public Infrastructure", "category": "DOMAIN"},
        {"_id": ObjectId(), "code": "DIGOV_DIGITAL_SIGNATURES", "competency_id": "DIGOV_DIGITAL_SIGNATURES", "competency_name": "Digital Signatures", "name": "Digital Signatures", "category": "DOMAIN"},
    ])

    # 4. Seed Users
    # 4a. Rajesh Sharma (Statistical Officer)
    stat_user_id = ObjectId()
    db.users.insert_one({
        "_id": stat_user_id,
        "email": "rajesh.sharma@mospi.gov.in",
        "hashed_password": hash_password("Demo@1234"),
        "full_name": "Rajesh Sharma",
        "access_role": "OFFICIAL",
        "role": stat_role_id,
        "role_id": stat_role_id,
        "designation": "Statistical Officer",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "status": "active",
        "is_active": True,
        "created_at": now,
    })

    # 4b. Suresh Talathi (Revenue Official / Talathi)
    talathi_user_id = ObjectId()
    db.users.insert_one({
        "_id": talathi_user_id,
        "email": "suresh.talathi@revenue.gov.in",
        "hashed_password": hash_password("Demo@1234"),
        "full_name": "Suresh Talathi",
        "access_role": "OFFICIAL",
        "role": revenue_role_id,
        "role_id": revenue_role_id,
        "designation": "Talathi",
        "department": "Department of Revenue & Land Records",
        "status": "active",
        "is_active": True,
        "created_at": now,
    })

    # 4c. Trainer User
    trainer_user_id = ObjectId()
    db.users.insert_one({
        "_id": trainer_user_id,
        "email": "trainer.kapoor@lba.gov.in",
        "hashed_password": hash_password("Demo@1234"),
        "full_name": "Dr. Sunita Kapoor",
        "access_role": "TRAINER",
        "role": "CURRICULUM_TRAINER",
        "role_id": "CURRICULUM_TRAINER",
        "designation": "Master Trainer",
        "department": "Lal Bahadur Shastri National Academy of Administration (LBSNAA)",
        "status": "active",
        "is_active": True,
        "created_at": now,
    })

    # 5. Competency Profiles
    # Rajesh Sharma has a critical gap in STAT_SAMPLING: required 4.0, current 2.0 (gap = 2.0)
    # And has met TECH_DATA_VISUALIZATION: required 3.0, current 3.5 (no gap)
    db.competency_profiles.insert_many([
        {
            "user_id": str(stat_user_id),
            "competency_id": "STAT_SAMPLING",
            "current_level": 2.0,
            "last_assessed_at": now,
        },
        {
            "user_id": str(stat_user_id),
            "competency_id": "TECH_DATA_VISUALIZATION",
            "current_level": 3.5,
            "last_assessed_at": now,
        },
        # Suresh Talathi has gap in DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE: required 4.0, current 1.5 (gap = 2.5)
        {
            "user_id": str(talathi_user_id),
            "competency_id": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE",
            "current_level": 1.5,
            "last_assessed_at": now,
        },
    ])

    # 6. Seed Quizzes
    quiz_stat_id = ObjectId()
    quiz_revenue_id = ObjectId()
    quiz_assigned_id = ObjectId()

    db.quizzes.insert_many([
        {
            "_id": quiz_stat_id,
            "title": "iGOT: Statistical Sampling, Estimation & Survey Design",
            "description": "Probability sampling and estimation methods.",
            "competency_code": "STAT_SAMPLING",
            "trainer_id": str(trainer_user_id),
            "status": "PUBLISHED",
            "published": True,
            "assigned_to": [],
            "target_competency_ids": ["STAT_SAMPLING"],
            "target_role_ids": ["STATISTICAL_OFFICER"],
            "difficulty": "HARD",
            "question_count": 2,
            "questions": [
                {
                    "question_id": "q-stat-1",
                    "question": "What is stratified sampling?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "explanation": "Stratification divides population into homogeneous groups.",
                    "difficulty": "HARD",
                }
            ],
            "created_at": now,
        },
        {
            "_id": quiz_revenue_id,
            "title": "Revenue Administration, Land Records (7/12 & RoR) & Mutation Procedures",
            "description": "Land records maintenance and mutation procedures.",
            "competency_code": "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE",
            "trainer_id": str(trainer_user_id),
            "status": "PUBLISHED",
            "published": True,
            "assigned_to": [],
            "target_competency_ids": ["DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE"],
            "target_role_ids": ["REVENUE_ADMINISTRATION_OFFICER"],
            "target_designation_ids": ["Talathi", "Patwari", "Lekhpal"],
            "difficulty": "HARD",
            "question_count": 2,
            "questions": [
                {
                    "question_id": "q-rev-1",
                    "question": "Which authority approves contested mutation?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "B",
                    "explanation": "Tahsildar approves contested mutation entries.",
                    "difficulty": "HARD",
                }
            ],
            "created_at": now,
        },
        {
            "_id": quiz_assigned_id,
            "title": "Special Mandatory Training on Civil Service Ethics",
            "description": "Mandatory ethics quiz assigned directly by trainer.",
            "competency_code": "BEH_ETHICS",
            "trainer_id": str(trainer_user_id),
            "status": "ASSIGNED",
            "published": True,
            "assigned_to": [str(stat_user_id)],  # Explicitly assigned to Rajesh Sharma only
            "target_competency_ids": ["BEH_ETHICS"],
            "target_role_ids": [],
            "difficulty": "MEDIUM",
            "question_count": 1,
            "questions": [
                {
                    "question_id": "q-eth-1",
                    "question": "Public service ethics principle:",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Integrity is non-negotiable.",
                    "difficulty": "MEDIUM",
                }
            ],
            "created_at": now,
        },
    ])

    stat_token = create_access_token(str(stat_user_id), settings)
    talathi_token = create_access_token(str(talathi_user_id), settings)
    trainer_token = create_access_token(str(trainer_user_id), settings)

    return {
        "client": client,
        "db": db,
        "stat_user_id": str(stat_user_id),
        "talathi_user_id": str(talathi_user_id),
        "stat_token": stat_token,
        "talathi_token": talathi_token,
        "trainer_token": trainer_token,
        "quiz_stat_id": str(quiz_stat_id),
        "quiz_revenue_id": str(quiz_revenue_id),
        "quiz_assigned_id": str(quiz_assigned_id),
    }


def test_statistical_officer_sees_statistical_sampling(personalization_env):
    """Test 1: Statistical Officer sees Statistical Sampling quiz."""
    client = personalization_env["client"]
    token = personalization_env["stat_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    quiz_codes = [q["competency_code"] for q in quizzes]
    assert "STAT_SAMPLING" in quiz_codes

    stat_quiz = next(q for q in quizzes if q["competency_code"] == "STAT_SAMPLING")
    assert stat_quiz["relevance_reason"] == "CRITICAL_GAP"
    assert stat_quiz["is_gap"] is True
    assert stat_quiz["gap_size"] == 2.0
    assert stat_quiz["priority"] == 2


def test_statistical_officer_does_not_see_land_records(personalization_env):
    """Test 2: Statistical Officer does NOT see Land Records quiz."""
    client = personalization_env["client"]
    token = personalization_env["stat_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    quiz_codes = [q["competency_code"] for q in quizzes]
    assert "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE" not in quiz_codes
    assert not any("Land Records" in q["title"] for q in quizzes)


def test_talathi_sees_revenue_administration_quiz(personalization_env):
    """Test 3: Talathi sees Revenue Administration / Land Records quiz."""
    client = personalization_env["client"]
    token = personalization_env["talathi_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    quiz_codes = [q["competency_code"] for q in quizzes]
    assert "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE" in quiz_codes

    rev_quiz = next(q for q in quizzes if q["competency_code"] == "DIGOV_DIGITAL_PUBLIC_INFRASTRUCTURE")
    assert rev_quiz["relevance_reason"] == "CRITICAL_GAP"
    assert rev_quiz["is_gap"] is True
    assert rev_quiz["gap_size"] == 2.5


def test_talathi_does_not_see_statistical_sampling(personalization_env):
    """Test 4: Talathi does NOT see Statistical Sampling quiz."""
    client = personalization_env["client"]
    token = personalization_env["talathi_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    quiz_codes = [q["competency_code"] for q in quizzes]
    assert "STAT_SAMPLING" not in quiz_codes


def test_assigned_by_trainer_visible_to_any_learner(personalization_env):
    """Test 5: Explicitly assigned quiz is visible to the assigned learner at Priority 1."""
    client = personalization_env["client"]
    token = personalization_env["stat_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/assigned", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    assigned_quiz = next(q for q in quizzes if q["competency_code"] == "BEH_ETHICS")
    assert assigned_quiz["relevance_reason"] == "ASSIGNED_BY_TRAINER"
    assert assigned_quiz["priority"] == 1
    # Check that Priority 1 appears first in the returned list
    assert quizzes[0]["_id"] == personalization_env["quiz_assigned_id"]


def test_trainer_can_access_quizzes_and_questions(personalization_env):
    """Test 6: Trainer can list quizzes in Trainer Studio without competency filtering."""
    client = personalization_env["client"]
    token = personalization_env["trainer_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/trainer/quizzes", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()
    assert len(quizzes) >= 2


def test_unauthorized_official_cannot_fetch_ineligible_quiz_by_id(personalization_env):
    """Test 7: Ineligible quiz returns 404 to an unauthorized official."""
    client = personalization_env["client"]
    talathi_token = personalization_env["talathi_token"]
    headers = {"Authorization": f"Bearer {talathi_token}"}

    # Talathi attempts to directly fetch the Statistical Sampling quiz
    stat_quiz_id = personalization_env["quiz_stat_id"]
    resp = client.get(f"/api/v1/quizzes/{stat_quiz_id}", headers=headers)
    assert resp.status_code == 404
    assert "Quiz not found" in resp.json()["detail"]


def test_rajesh_sharma_golden_demo_retention(personalization_env):
    """Test 8: Golden demo persona retains STAT_SAMPLING as a critical gap at priority 2."""
    client = personalization_env["client"]
    token = personalization_env["stat_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    stat_quiz = next(q for q in quizzes if q["competency_code"] == "STAT_SAMPLING")
    assert stat_quiz["priority"] == 2
    assert stat_quiz["current_level"] == 2.0
    assert stat_quiz["required_level"] == 4.0
    assert stat_quiz["gap_size"] == 2.0


def test_non_gap_required_competency_remains_available(personalization_env):
    """Test 9: Non-gap required competency remains eligible as REQUIRED_COMPETENCY."""
    client = personalization_env["client"]
    db = personalization_env["db"]
    token = personalization_env["stat_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Insert a quiz for TECH_DATA_VISUALIZATION (where Rajesh has level 3.5 >= required 3.0)
    now = datetime.now(UTC)
    db.quizzes.insert_one({
        "_id": ObjectId(),
        "title": "iGOT: Data Visualization & Official Statistics",
        "description": "Visualizing complex government statistics.",
        "competency_code": "TECH_DATA_VISUALIZATION",
        "trainer_id": "trainer-id",
        "status": "PUBLISHED",
        "published": True,
        "assigned_to": [],
        "target_competency_ids": ["TECH_DATA_VISUALIZATION"],
        "target_role_ids": ["STATISTICAL_OFFICER"],
        "difficulty": "MEDIUM",
        "question_count": 1,
        "questions": [
            {
                "question_id": "q-vis-1",
                "question": "Best chart for distributions?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "Histogram.",
                "difficulty": "MEDIUM",
            }
        ],
        "created_at": now,
    })

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    vis_quiz = next((q for q in quizzes if q["competency_code"] == "TECH_DATA_VISUALIZATION"), None)
    assert vis_quiz is not None
    assert vis_quiz["relevance_reason"] == "REQUIRED_COMPETENCY"
    assert vis_quiz["is_gap"] is False
    assert vis_quiz["priority"] == 6


def test_role_targeted_quiz_visible_as_role_targeted(personalization_env):
    """Test 10: Quiz targeted to role is visible as ROLE_TARGETED (Priority 5) even without profile."""
    client = personalization_env["client"]
    db = personalization_env["db"]
    token = personalization_env["talathi_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add a quiz explicitly targeted to REVENUE_ADMINISTRATION_OFFICER with no profile entry
    now = datetime.now(UTC)
    db.quizzes.insert_one({
        "_id": ObjectId(),
        "title": "Village Administration & Citizen Grievance Portal Procedures",
        "description": "Procedures for handling rural grievances.",
        "competency_code": "PUB_GRIEVANCE_HANDLING",
        "trainer_id": "trainer-id",
        "status": "PUBLISHED",
        "published": True,
        "assigned_to": [],
        "target_competency_ids": ["PUB_GRIEVANCE_HANDLING"],
        "target_role_ids": ["REVENUE_ADMINISTRATION_OFFICER"],
        "difficulty": "EASY",
        "question_count": 1,
        "questions": [
            {
                "question_id": "q-grv-1",
                "question": "Time limit for portal resolution?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Citizen charter timeline.",
                "difficulty": "EASY",
            }
        ],
        "created_at": now,
    })

    resp = client.get("/api/v1/quizzes/relevant", headers=headers)
    assert resp.status_code == 200
    quizzes = resp.json()

    grv_quiz = next((q for q in quizzes if q["competency_code"] == "PUB_GRIEVANCE_HANDLING"), None)
    assert grv_quiz is not None
    assert grv_quiz["relevance_reason"] == "ROLE_TARGETED"
    assert grv_quiz["priority"] == 5
