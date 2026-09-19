"""
Automated unit and integration test suite for ShikshaSetu Recommended Quiz Engine.

Verifies:
1. test_assigned_quizzes_isolated_from_recommended:
   Trainer-assigned quizzes appear in assigned list; unassigned recommended quizzes do NOT appear in assigned.
2. test_talathi_unrelated_quizzes_not_recommended:
   Talathi does NOT see Statistical Sampling, Survey Design, Data Visualization, or Python under recommended.
3. test_talathi_sees_revenue_recommendations:
   Talathi sees Land Records under recommended due to competency gap.
4. test_statistical_officer_sees_statistical_sampling:
   Statistical Officer sees Statistical Sampling under recommended when gap exists.
5. test_critical_gap_ranked_higher_than_minor_gap:
   Larger gap receives higher recommendation score than smaller gap.
6. test_deduplication_assigned_and_recommended:
   When a quiz is both assigned and recommended, it is retained under assigned with is_also_recommended=True,
   and omitted from recommended.
7. test_feed_endpoint_structure:
   GET /api/v1/quizzes/feed returns { assigned: [...], recommended: [...], meta: {...} }.
8. test_recommended_endpoint_structure:
   GET /api/v1/quizzes/recommended returns list[RecommendedQuizItem].
9. test_assigned_endpoint_backward_compatible:
   GET /api/v1/quizzes/assigned returns list[QuizResponse] of only explicitly assigned quizzes.
10. test_recommendation_explainability:
    Recommended items have primary_reason, current_level, required_level, gap_size, score_breakdown.
11. test_rajesh_golden_demo_retention:
    Rajesh Sharma (Statistical Officer) maintains critical gap recommendation for Statistical Sampling.
12. test_draft_or_archived_quizzes_excluded:
    Only PUBLISHED quizzes can be recommended.
13. test_top_5_limit_respected:
    recommend_quizzes_for_official respects limit query param (default 5).
14. test_ineligible_quiz_access_prevented:
    Official cannot fetch an unrelated/ineligible quiz via GET /quizzes/{id} (returns 404).
15. test_trainer_quiz_assignment_flow_unaffected:
    Explicit assignment via POST /trainer/quizzes/{id}/assign immediately reflects in assigned quizzes.
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
            if "$addToSet" in update:
                for k, v in update["$addToSet"].items():
                    if isinstance(v, dict) and "$each" in v:
                        items = v["$each"]
                    else:
                        items = [v]
                    lst = document.setdefault(k, [])
                    for it in items:
                        if it not in lst:
                            lst.append(it)
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
def engine_env():
    db = FakeDatabase()
    settings = Settings(
        mongodb_uri="mongodb://test",
        mongodb_database="test_recommended_quiz_engine_db",
        jwt_secret="super-secret-key-for-testing-only-32-chars",
    )
    app = create_app(settings)
    app.state.database = db
    client = TestClient(app)

    now = datetime.now(UTC)

    # 1. Roles
    stat_role_id = "STATISTICAL_OFFICER"
    revenue_role_id = "REVENUE_ADMINISTRATION_OFFICER"

    db.roles.insert_many([
        {
            "_id": ObjectId(),
            "role_id": stat_role_id,
            "role_code": stat_role_id,
            "role_name": "Statistical Officer",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "designations": ["Statistical Officer", "Assistant Director (Statistics)"],
        },
        {
            "_id": ObjectId(),
            "role_id": revenue_role_id,
            "role_code": revenue_role_id,
            "role_name": "Revenue Administration Officer",
            "department": "Department of Revenue & Land Records",
            "designations": ["Talathi", "Patwari", "Village Revenue Officer"],
        },
    ])

    # 2. Competencies
    db.competencies.insert_many([
        {"_id": ObjectId(), "code": "STAT_SAMPLING", "competency_id": "STAT_SAMPLING", "name": "Statistical Sampling", "competency_name": "Statistical Sampling", "category": "Domain"},
        {"_id": ObjectId(), "code": "SURV_DESIGN", "competency_id": "SURV_DESIGN", "name": "Survey Design", "competency_name": "Survey Design", "category": "Domain"},
        {"_id": ObjectId(), "code": "DATA_VIZ", "competency_id": "DATA_VIZ", "name": "Data Visualization", "competency_name": "Data Visualization", "category": "Technical"},
        {"_id": ObjectId(), "code": "PYTHON_PROG", "competency_id": "PYTHON_PROG", "name": "Python Programming", "competency_name": "Python Programming", "category": "Technical"},
        {"_id": ObjectId(), "code": "LAND_REC", "competency_id": "LAND_REC", "name": "Land Records Management", "competency_name": "Land Records Management", "category": "Domain"},
        {"_id": ObjectId(), "code": "REV_ADMIN", "competency_id": "REV_ADMIN", "name": "Revenue Administration", "competency_name": "Revenue Administration", "category": "Domain"},
    ])

    # 3. Role Requirements (individual docs as queried by service)
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
            "competency_id": "SURV_DESIGN",
            "competency_code": "SURV_DESIGN",
            "required_level": 3.0,
            "priority": "MANDATORY",
            "criticality": "MEDIUM",
        },
        {
            "role_id": revenue_role_id,
            "competency_id": "LAND_REC",
            "competency_code": "LAND_REC",
            "required_level": 4.0,
            "priority": "MANDATORY",
            "criticality": "HIGH",
        },
        {
            "role_id": revenue_role_id,
            "competency_id": "REV_ADMIN",
            "competency_code": "REV_ADMIN",
            "required_level": 3.5,
            "priority": "MANDATORY",
            "criticality": "MEDIUM",
        },
    ])

    # 4. Users
    rajesh_id = ObjectId()
    talathi_id = ObjectId()
    trainer_id = ObjectId()

    db.users.insert_many([
        {
            "_id": rajesh_id,
            "email": "rajesh.sharma@mospi.gov.in",
            "hashed_password": hash_password("pass123"),
            "full_name": "Rajesh Sharma",
            "access_role": "OFFICIAL",
            "role": stat_role_id,
            "role_id": stat_role_id,
            "government_role_id": stat_role_id,
            "designation": "Statistical Officer",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "status": "active",
            "is_active": True,
            "created_at": now,
        },
        {
            "_id": talathi_id,
            "email": "talathi.pune@maharashtra.gov.in",
            "hashed_password": hash_password("pass123"),
            "full_name": "Suresh Talathi",
            "access_role": "OFFICIAL",
            "role": revenue_role_id,
            "role_id": revenue_role_id,
            "government_role_id": revenue_role_id,
            "designation": "Talathi",
            "department": "Department of Revenue & Land Records",
            "status": "active",
            "is_active": True,
            "created_at": now,
        },
        {
            "_id": trainer_id,
            "email": "trainer.admin@shikshasetu.gov.in",
            "hashed_password": hash_password("pass123"),
            "full_name": "Dr. Trainer",
            "access_role": "TRAINER",
            "role": "TRAINER",
            "role_id": "TRAINER",
            "status": "active",
            "is_active": True,
            "created_at": now,
        },
    ])

    # 5. Competency Profiles
    # Rajesh: STAT_SAMPLING level 2.0 (req 4.0 -> gap 2.0 = CRITICAL), SURV_DESIGN level 3.0 (no gap)
    db.competency_profiles.insert_many([
        {
            "user_id": str(rajesh_id),
            "competency_id": "STAT_SAMPLING",
            "competency_code": "STAT_SAMPLING",
            "current_level": 2.0,
            "last_assessed_at": now,
        },
        {
            "user_id": str(rajesh_id),
            "competency_id": "SURV_DESIGN",
            "competency_code": "SURV_DESIGN",
            "current_level": 3.0,
            "last_assessed_at": now,
        },
        # Suresh Talathi: LAND_REC level 2.5 (req 4.0 -> gap 1.5), REV_ADMIN level 3.5 (req 3.5 -> gap 0)
        {
            "user_id": str(talathi_id),
            "competency_id": "LAND_REC",
            "competency_code": "LAND_REC",
            "current_level": 2.5,
            "last_assessed_at": now,
        },
        {
            "user_id": str(talathi_id),
            "competency_id": "REV_ADMIN",
            "competency_code": "REV_ADMIN",
            "current_level": 3.5,
            "last_assessed_at": now,
        },
    ])

    # 6. Published Quizzes
    quiz_stat_id = ObjectId()
    quiz_surv_id = ObjectId()
    quiz_python_id = ObjectId()
    quiz_land_id = ObjectId()
    quiz_rev_id = ObjectId()

    questions = [
        {
            "question_id": f"q_{i}",
            "question": f"Question {i}?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "difficulty": "INTERMEDIATE",
            "explanation": "Exp",
        }
        for i in range(3)
    ]

    db.quizzes.insert_many([
        {
            "_id": quiz_stat_id,
            "title": "Statistical Sampling Methods",
            "competency_code": "STAT_SAMPLING",
            "target_competency_ids": ["STAT_SAMPLING"],
            "target_role_ids": [stat_role_id],
            "status": "PUBLISHED",
            "published": True,
            "difficulty": "INTERMEDIATE",
            "questions": questions,
            "assigned_to": [],
            "created_at": now,
        },
        {
            "_id": quiz_surv_id,
            "title": "Survey Design Fundamentals",
            "competency_code": "SURV_DESIGN",
            "target_competency_ids": ["SURV_DESIGN"],
            "target_role_ids": [stat_role_id],
            "status": "PUBLISHED",
            "published": True,
            "difficulty": "BEGINNER",
            "questions": questions,
            "assigned_to": [],
            "created_at": now,
        },
        {
            "_id": quiz_python_id,
            "trainer_id": str(trainer_id),
            "title": "Python Data Science",
            "competency_code": "PYTHON_PROG",
            "target_competency_ids": ["PYTHON_PROG"],
            "target_role_ids": ["SOFTWARE_ENGINEER"],
            "status": "PUBLISHED",
            "published": True,
            "difficulty": "ADVANCED",
            "questions": questions,
            "assigned_to": [],
            "created_at": now,
        },
        {
            "_id": quiz_land_id,
            "title": "Land Records Verification & Mutations",
            "competency_code": "LAND_REC",
            "target_competency_ids": ["LAND_REC"],
            "target_role_ids": [revenue_role_id],
            "status": "PUBLISHED",
            "published": True,
            "difficulty": "INTERMEDIATE",
            "questions": questions,
            "assigned_to": [],
            "created_at": now,
        },
        {
            "_id": quiz_rev_id,
            "title": "Revenue Administration Act",
            "competency_code": "REV_ADMIN",
            "target_competency_ids": ["REV_ADMIN"],
            "target_role_ids": [revenue_role_id],
            "status": "PUBLISHED",
            "published": True,
            "difficulty": "BEGINNER",
            "questions": questions,
            "assigned_to": [],
            "created_at": now,
        },
    ])

    return {
        "db": db,
        "client": client,
        "rajesh_id": rajesh_id,
        "talathi_id": talathi_id,
        "trainer_id": trainer_id,
        "quiz_stat_id": quiz_stat_id,
        "quiz_land_id": quiz_land_id,
        "quiz_python_id": quiz_python_id,
        "quiz_surv_id": quiz_surv_id,
        "quiz_rev_id": quiz_rev_id,
        "rajesh_token": create_access_token(str(rajesh_id), settings),
        "talathi_token": create_access_token(str(talathi_id), settings),
        "trainer_token": create_access_token(str(trainer_id), settings),
    }


def test_assigned_quizzes_isolated_from_recommended(engine_env):
    """1. Trainer-assigned quiz appears in assigned array; unassigned recommended quiz does NOT appear in assigned."""
    client = engine_env["client"]
    db = engine_env["db"]
    rajesh_id = engine_env["rajesh_id"]
    quiz_surv_id = engine_env["quiz_surv_id"]

    # Explicitly assign Survey Design to Rajesh
    db.quizzes.update_one({"_id": quiz_surv_id}, {"$set": {"assigned_to": [str(rajesh_id)]}})

    resp = client.get(
        "/api/v1/quizzes/feed",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    feed = resp.json()

    assigned_titles = [q["title"] for q in feed["assigned"]]
    assert "Survey Design Fundamentals" in assigned_titles

    # Statistical Sampling is recommended (due to gap) but NOT assigned
    assert "Statistical Sampling Methods" not in assigned_titles
    recommended_titles = [q["title"] for q in feed["recommended"]]
    assert "Statistical Sampling Methods" in recommended_titles


def test_talathi_unrelated_quizzes_not_recommended(engine_env):
    """2. Talathi does NOT see Statistical Sampling, Python Programming, Survey Design under recommended."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['talathi_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()

    rec_competencies = [item["competency_code"] for item in items]
    assert "STAT_SAMPLING" not in rec_competencies
    assert "SURV_DESIGN" not in rec_competencies
    assert "PYTHON_PROG" not in rec_competencies


def test_talathi_sees_revenue_recommendations(engine_env):
    """3. Talathi sees Land Records under recommended due to role competency gap."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['talathi_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()

    rec_competencies = [item["competency_code"] for item in items]
    assert "LAND_REC" in rec_competencies
    land_rec_item = next(item for item in items if item["competency_code"] == "LAND_REC")
    assert land_rec_item["is_gap"] is True
    assert land_rec_item["gap_size"] == 1.5


def test_statistical_officer_sees_statistical_sampling(engine_env):
    """4. Statistical Officer sees Statistical Sampling under recommended when gap exists."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()

    stat_item = next((item for item in items if item["competency_code"] == "STAT_SAMPLING"), None)
    assert stat_item is not None
    assert stat_item["is_gap"] is True
    assert stat_item["gap_size"] == 2.0


def test_critical_gap_ranked_higher_than_minor_gap(engine_env):
    """5. Critical gap (larger gap size) receives higher recommendation score than smaller gap or no gap."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()

    # In Rajesh's profile: STAT_SAMPLING gap=2.0, SURV_DESIGN gap=0.0
    stat_item = next((item for item in items if item["competency_code"] == "STAT_SAMPLING"), None)
    surv_item = next((item for item in items if item["competency_code"] == "SURV_DESIGN"), None)

    assert stat_item is not None
    if surv_item:
        assert stat_item["recommendation_score"] > surv_item["recommendation_score"]


def test_deduplication_assigned_and_recommended(engine_env):
    """6. When a quiz is both assigned AND recommended, it is retained under assigned with is_also_recommended=True, and omitted from recommended."""
    client = engine_env["client"]
    db = engine_env["db"]
    rajesh_id = engine_env["rajesh_id"]
    quiz_stat_id = engine_env["quiz_stat_id"]

    # Explicitly assign Statistical Sampling to Rajesh
    db.quizzes.update_one({"_id": quiz_stat_id}, {"$set": {"assigned_to": [str(rajesh_id)]}})

    resp = client.get(
        "/api/v1/quizzes/feed",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    feed = resp.json()

    # 1. Appears in assigned
    assigned_stat = next((q for q in feed["assigned"] if q["competency_code"] == "STAT_SAMPLING"), None)
    assert assigned_stat is not None
    assert assigned_stat.get("is_also_recommended") is True

    # 2. Omitted from recommended
    rec_stat = next((q for q in feed["recommended"] if q["competency_code"] == "STAT_SAMPLING"), None)
    assert rec_stat is None


def test_feed_endpoint_structure(engine_env):
    """7. GET /api/v1/quizzes/feed returns { assigned: [...], recommended: [...], meta: {...} }."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/feed",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "assigned" in data and isinstance(data["assigned"], list)
    assert "recommended" in data and isinstance(data["recommended"], list)
    assert "meta" in data
    assert data["meta"]["role_id"] == "STATISTICAL_OFFICER"
    assert data["meta"]["role_title"] == "Statistical Officer"


def test_recommended_endpoint_structure(engine_env):
    """8. GET /api/v1/quizzes/recommended returns list[RecommendedQuizItem]."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    if items:
        item = items[0]
        assert "recommendation_score" in item
        assert "primary_reason" in item
        assert "current_level" in item
        assert "required_level" in item


def test_assigned_endpoint_backward_compatible(engine_env):
    """9. GET /api/v1/quizzes/assigned returns pure list[QuizResponse] of explicitly assigned quizzes only."""
    client = engine_env["client"]
    db = engine_env["db"]
    rajesh_id = engine_env["rajesh_id"]
    quiz_stat_id = engine_env["quiz_stat_id"]

    # Before assignment, list should be empty
    resp = client.get(
        "/api/v1/quizzes/assigned",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []

    # Assign quiz
    db.quizzes.update_one({"_id": quiz_stat_id}, {"$set": {"assigned_to": [str(rajesh_id)]}})

    resp2 = client.get(
        "/api/v1/quizzes/assigned",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp2.status_code == 200
    assigned_list = resp2.json()
    assert isinstance(assigned_list, list)
    assert len(assigned_list) == 1
    assert assigned_list[0]["competency_code"] == "STAT_SAMPLING"


def test_recommendation_explainability(engine_env):
    """10. Explainability: recommended items contain human-readable reason and breakdown."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    stat_item = next((item for item in items if item["competency_code"] == "STAT_SAMPLING"), None)
    assert stat_item is not None
    assert "competency gap" in stat_item["primary_reason"].lower()
    assert "score_breakdown" in stat_item
    assert "gap_score" in stat_item["score_breakdown"]
    assert "role_score" in stat_item["score_breakdown"]


def test_rajesh_golden_demo_retention(engine_env):
    """11. Golden demo persona (Rajesh Sharma) retains Statistical Sampling as top recommendation."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    # Top recommendation must be Statistical Sampling
    top_item = items[0]
    assert top_item["competency_code"] == "STAT_SAMPLING"
    assert top_item["gap_size"] == 2.0


def test_draft_or_archived_quizzes_excluded(engine_env):
    """12. Draft or archived quizzes are never recommended (only PUBLISHED)."""
    client = engine_env["client"]
    db = engine_env["db"]
    draft_quiz_id = ObjectId()

    db.quizzes.insert_one({
        "_id": draft_quiz_id,
        "title": "Draft Sampling Quiz",
        "competency_code": "STAT_SAMPLING",
        "target_competency_ids": ["STAT_SAMPLING"],
        "target_role_ids": ["STATISTICAL_OFFICER"],
        "status": "DRAFT",
        "published": False,
        "questions": [],
        "assigned_to": [],
        "created_at": datetime.now(UTC),
    })

    resp = client.get(
        "/api/v1/quizzes/recommended",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    titles = [item["title"] for item in items]
    assert "Draft Sampling Quiz" not in titles


def test_top_5_limit_respected(engine_env):
    """13. Recommendations respect the limit parameter (default 5)."""
    client = engine_env["client"]
    resp = client.get(
        "/api/v1/quizzes/recommended?limit=1",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) <= 1


def test_ineligible_quiz_access_prevented(engine_env):
    """14. Official cannot fetch an ineligible quiz via GET /quizzes/{id} (returns 404)."""
    client = engine_env["client"]
    quiz_stat_id = engine_env["quiz_stat_id"]

    # Suresh Talathi tries to access Statistical Sampling quiz
    resp = client.get(
        f"/api/v1/quizzes/{quiz_stat_id}",
        headers={"Authorization": f"Bearer {engine_env['talathi_token']}"},
    )
    assert resp.status_code == 404
    assert "not authorized" in resp.json()["detail"].lower() or "not found" in resp.json()["detail"].lower()


def test_trainer_quiz_assignment_flow_unaffected(engine_env):
    """15. Trainer assignment endpoint POST /trainer/quizzes/{id}/assign immediately reflects in assigned quizzes."""
    client = engine_env["client"]
    quiz_python_id = engine_env["quiz_python_id"]
    rajesh_id = str(engine_env["rajesh_id"])

    # Trainer assigns Python quiz to Rajesh
    resp = client.post(
        f"/api/v1/trainer/quizzes/{quiz_python_id}/assign",
        json={"learner_ids": [rajesh_id]},
        headers={"Authorization": f"Bearer {engine_env['trainer_token']}"},
    )
    assert resp.status_code == 200

    # Rajesh checks assigned quizzes
    assigned_resp = client.get(
        "/api/v1/quizzes/assigned",
        headers={"Authorization": f"Bearer {engine_env['rajesh_token']}"},
    )
    assert assigned_resp.status_code == 200
    assigned_quizzes = assigned_resp.json()
    assert any(q["title"] == "Python Data Science" for q in assigned_quizzes)
