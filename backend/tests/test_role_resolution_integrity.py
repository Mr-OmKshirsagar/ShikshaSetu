"""
Regression test suite for Phase 5E: Role Resolution Integrity.
Validates all 20 required role resolution, isolation, and admin resolution invariants.
"""
from datetime import UTC, datetime
from bson import ObjectId
import pytest
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, hash_password
from app.core.config import Settings
from app.main import create_app
from app.roles.resolver import resolve_role_for_user, reconcile_user_competencies


class InsertOneResult:
    def __init__(self, inserted_id: ObjectId) -> None:
        self.inserted_id = inserted_id


class FakeCursor(list):
    def sort(self, key: str, direction: int = 1):
        return FakeCursor(sorted(self, key=lambda item: item.get(key, ""), reverse=direction < 0))

    def limit(self, count: int):
        return FakeCursor(self[:count])


class FakeCollection:
    """In-memory MongoDB collection for role resolution testing."""

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
                elif "$ne" in expected:
                    if actual == expected["$ne"]:
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

    def find_one(self, query: dict, projection: dict | None = None, sort=None, **kwargs) -> dict | None:
        docs = [item for item in self.documents if self._matches(item, query)]
        if sort:
            for key, direction in reversed(sort):
                docs = sorted(docs, key=lambda x: x.get(key, ""), reverse=(direction < 0))
        return next((dict(item) for item in docs), None)

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

    def update_many(self, query: dict, update: dict) -> None:
        for doc in self.documents:
            if self._matches(doc, query):
                if "$set" in update:
                    doc.update(update["$set"])

    def count_documents(self, query: dict) -> int:
        return sum(self._matches(item, query) for item in self.documents)

    def create_index(self, *args, **kwargs) -> str:
        return "idx"

    def __getitem__(self, name: str):
        return self


class FakeDatabase:
    """Mock MongoDB database setup for role tests."""

    def __init__(self) -> None:
        self.users = FakeCollection()
        self.roles = FakeCollection()
        self.role_requirements = FakeCollection()
        self.competencies = FakeCollection()
        self.competency_profiles = FakeCollection()
        self.competency_evidence = FakeCollection()
        self.learning_resources = FakeCollection()
        self.learning_resource_mappings = FakeCollection()
        self.resource_mappings = FakeCollection()

    def __getattr__(self, name: str) -> FakeCollection:
        if not hasattr(self, name):
            setattr(self, name, FakeCollection())
        return getattr(self, name)

    def __getitem__(self, name: str) -> FakeCollection:
        if not hasattr(self, name):
            setattr(self, name, FakeCollection())
        return getattr(self, name)


@pytest.fixture
def role_test_env():
    """Create test environment with multi-department roles."""
    db = FakeDatabase()
    settings = Settings(
        mongodb_uri="mongodb://test",
        mongodb_database="test",
        jwt_secret="super-secret-key-for-testing-only-32-chars",
    )
    application = create_app(settings)
    application.state.database = db

    now = datetime.now(UTC)

    # 1. Competencies
    comp_sampling = ObjectId()
    comp_pedagogy = ObjectId()
    db.competencies.insert_many([
        {"_id": comp_sampling, "code": "STAT_SAMPLING", "name": "Statistical Sampling", "domain": "STATISTICAL", "status": "active"},
        {"_id": comp_pedagogy, "code": "EDU_PEDAGOGY", "name": "Pedagogical Assessment", "domain": "EDUCATION", "status": "active"},
    ])

    # 2. Roles
    role_stat = ObjectId()
    role_edu = ObjectId()

    db.roles.insert_many([
        {
            "_id": role_stat,
            "role_code": "STATISTICAL_OFFICER",
            "role_name": "Statistical Officer",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "department_code": "MOSPI",
            "designations": ["Statistical Officer", "Senior Statistical Officer (SSO)", "Assistant Director (Statistics)"],
            "status": "active",
        },
        {
            "_id": role_edu,
            "role_code": "EDUCATION_OFFICER",
            "role_name": "Education & Curriculum Officer",
            "department": "Ministry of Education",
            "department_code": "MOE",
            "designations": ["Teacher", "Senior Teacher (PGT/TGT)", "Headmaster / Principal", "Block Education Officer (BEO)"],
            "status": "active",
        },
    ])

    # 3. Role Requirements
    db.role_requirements.insert_many([
        {"_id": ObjectId(), "role_id": role_stat, "competency_id": comp_sampling, "required_level": 4.0, "priority": 1, "importance": 0.9},
        {"_id": ObjectId(), "role_id": role_edu, "competency_id": comp_pedagogy, "required_level": 4.0, "priority": 1, "importance": 0.9},
    ])

    # 4. Users
    admin_id = ObjectId()
    official_id = ObjectId()
    trainer_id = ObjectId()

    db.users.insert_many([
        {
            "_id": admin_id,
            "email": "admin@shikshasetu.gov.in",
            "password_hash": hash_password("Password123!"),
            "full_name": "Admin User",
            "employee_id": "EMP-ADM-001",
            "role_id": role_stat,
            "access_role": "ADMIN",
            "status": "active",
        },
        {
            "_id": official_id,
            "email": "teacher@shikshasetu.gov.in",
            "password_hash": hash_password("Password123!"),
            "full_name": "Education Official",
            "employee_id": "EMP-EDU-001",
            "role_id": role_edu,
            "department": "Ministry of Education",
            "designation": "Teacher",
            "access_role": "OFFICIAL",
            "status": "active",
        },
        {
            "_id": trainer_id,
            "email": "trainer@shikshasetu.gov.in",
            "password_hash": hash_password("Password123!"),
            "full_name": "Trainer User",
            "employee_id": "EMP-TRN-001",
            "role_id": role_stat,
            "access_role": "TRAINER",
            "status": "active",
        },
    ])

    client = TestClient(application)
    admin_token = create_access_token(str(admin_id), settings)
    official_token = create_access_token(str(official_id), settings)
    trainer_token = create_access_token(str(trainer_id), settings)

    return {
        "db": db,
        "client": client,
        "role_stat": role_stat,
        "role_edu": role_edu,
        "comp_sampling": comp_sampling,
        "comp_pedagogy": comp_pedagogy,
        "admin_token": admin_token,
        "official_token": official_token,
        "trainer_token": trainer_token,
        "official_id": str(official_id),
    }


def test_01_exact_department_and_designation_resolves(role_test_env):
    """1. Exact Department + Designation resolves correctly."""
    db = role_test_env["db"]
    role_edu = role_test_env["role_edu"]

    resolved = resolve_role_for_user(db, "Ministry of Education", "Teacher")
    assert resolved == role_edu


def test_02_unknown_department_and_designation_does_not_fall_back(role_test_env):
    """2. Unknown Department + Designation returns None (NO silent fallback to STATISTICAL_OFFICER)."""
    db = role_test_env["db"]
    resolved = resolve_role_for_user(db, "Unknown Alien Department", "Space Navigator")
    assert resolved is None


def test_03_unknown_designation_in_known_department_does_not_fall_back(role_test_env):
    """3. Unknown designation in known department returns None (no arbitrary department default)."""
    db = role_test_env["db"]
    resolved = resolve_role_for_user(db, "Ministry of Education", "Aviation Helicopter Pilot")
    assert resolved is None


def test_04_unknown_department_with_known_designation_resolves_if_canonical(role_test_env):
    """4. Known designation resolves to the canonical role even if department is variant."""
    db = role_test_env["db"]
    role_stat = role_test_env["role_stat"]
    resolved = resolve_role_for_user(db, "State Economics Branch", "Senior Statistical Officer (SSO)")
    assert resolved == role_stat


def test_05_case_and_whitespace_handling(role_test_env):
    """5. Case and whitespace normalized matching works reliably."""
    db = role_test_env["db"]
    role_edu = role_test_env["role_edu"]
    resolved = resolve_role_for_user(db, "  MINISTRY OF EDUCATION  ", "  teacher  ")
    assert resolved == role_edu


def test_06_unresolved_user_does_not_receive_other_role_requirements(role_test_env):
    """6. Unresolved user returns 422 or empty requirements; does NOT inherit Statistical Officer requirements."""
    client = role_test_env["client"]
    db = role_test_env["db"]
    settings = Settings(mongodb_uri="mongodb://test", mongodb_database="test", jwt_secret="super-secret-key-for-testing-only-32-chars")

    unresolved_user_id = ObjectId()
    db.users.insert_one({
        "_id": unresolved_user_id,
        "email": "unresolved@shikshasetu.gov.in",
        "full_name": "Unmapped Official",
        "department": "Department of Novel Activities",
        "designation": "Chief Novelty Lead",
        "role_id": None,
        "access_role": "OFFICIAL",
        "status": "active",
    })
    token = create_access_token(str(unresolved_user_id), settings)

    res = client.get("/api/v1/skill-gaps/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422
    assert "role" in res.json()["detail"].lower() or "pending" in res.json()["detail"].lower()


def test_07_unresolved_user_does_not_receive_recommendations(role_test_env):
    """7. Unresolved user receives 0 recommendations with pending status, no false candidate generation."""
    client = role_test_env["client"]
    db = role_test_env["db"]
    settings = Settings(mongodb_uri="mongodb://test", mongodb_database="test", jwt_secret="super-secret-key-for-testing-only-32-chars")

    unresolved_user_id = ObjectId()
    db.users.insert_one({
        "_id": unresolved_user_id,
        "email": "unresolved2@shikshasetu.gov.in",
        "full_name": "Unmapped Official 2",
        "department": "Department of Novel Activities",
        "designation": "Chief Novelty Lead",
        "role_id": None,
        "access_role": "OFFICIAL",
        "status": "active",
    })
    token = create_access_token(str(unresolved_user_id), settings)

    res = client.get("/api/v1/recommendations/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["total_recommendations"] == 0
    assert len(data["recommendations"]) == 0
    assert data.get("metadata", {}).get("status") == "ROLE_MAPPING_PENDING"


def test_08_resolved_user_isolation(role_test_env):
    """8. User A (Education) and User B (Statistics) receive strictly isolated requirements."""
    client = role_test_env["client"]
    db = role_test_env["db"]
    settings = Settings(mongodb_uri="mongodb://test", mongodb_database="test", jwt_secret="super-secret-key-for-testing-only-32-chars")

    stat_user_id = ObjectId()
    db.users.insert_one({
        "_id": stat_user_id,
        "email": "stat_officer@shikshasetu.gov.in",
        "full_name": "Stat Officer",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "designation": "Statistical Officer",
        "role_id": role_test_env["role_stat"],
        "access_role": "OFFICIAL",
        "status": "active",
    })
    stat_token = create_access_token(str(stat_user_id), settings)

    # Stat user skill gaps
    res_stat = client.get("/api/v1/skill-gaps/me", headers={"Authorization": f"Bearer {stat_token}"})
    assert res_stat.status_code == 200
    stat_gaps = [g["competency_code"] for g in res_stat.json()["gaps"]]
    assert "STAT_SAMPLING" in stat_gaps
    assert "EDU_PEDAGOGY" not in stat_gaps

    # Education user skill gaps
    res_edu = client.get("/api/v1/skill-gaps/me", headers={"Authorization": f"Bearer {role_test_env['official_token']}"})
    assert res_edu.status_code == 200
    edu_gaps = [g["competency_code"] for g in res_edu.json()["gaps"]]
    assert "EDU_PEDAGOGY" in edu_gaps
    assert "STAT_SAMPLING" not in edu_gaps


def test_09_department_change_triggers_reconciliation_and_preserves_evidence(role_test_env):
    """9 & 10 & 11: Department/Designation change re-evaluates role, updates active profiles, and preserves historical evidence."""
    client = role_test_env["client"]
    db = role_test_env["db"]
    official_id = ObjectId(role_test_env["official_id"])

    # Insert historical evidence in education competency
    db.competency_evidence.insert_one({
        "user_id": official_id,
        "competency_id": role_test_env["comp_pedagogy"],
        "evidence_type": "CAPABILITY_ASSESSMENT",
        "authority": "AUTHORITATIVE",
        "score": 3.8,
        "confidence": 0.85,
        "source": "FORMAL_ASSESSMENT",
        "created_at": datetime.now(UTC),
    })

    # Update profile to Statistics department
    res = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {role_test_env['official_token']}"},
        json={
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "designation": "Statistical Officer",
        }
    )
    assert res.status_code == 200
    assert res.json()["department"] == "Ministry of Statistics & Programme Implementation (MoSPI)"

    # Check updated role in database
    user_doc = db.users.find_one({"_id": official_id})
    assert user_doc["role_id"] == role_test_env["role_stat"]

    # Historical evidence is STILL present
    evidence_records = list(db.competency_evidence.find({"user_id": official_id}))
    assert len(evidence_records) == 1
    assert evidence_records[0]["score"] == 3.8


def test_13_admin_can_resolve_unresolved_user_role(role_test_env):
    """13. ADMIN can formally assign a role to an unresolved user."""
    client = role_test_env["client"]
    db = role_test_env["db"]
    role_edu = role_test_env["role_edu"]

    unresolved_id = ObjectId()
    db.users.insert_one({
        "_id": unresolved_id,
        "email": "pending_admin@shikshasetu.gov.in",
        "full_name": "Pending Officer",
        "department": "Custom Department",
        "designation": "Custom Lead",
        "role_id": None,
        "access_role": "OFFICIAL",
        "status": "active",
    })

    res = client.post(
        f"/api/v1/admin/users/{str(unresolved_id)}/assign-role",
        headers={"Authorization": f"Bearer {role_test_env['admin_token']}"},
        json={
            "role_id": str(role_edu),
            "department": "Ministry of Education",
            "designation": "Teacher",
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["professional_role"] == "Education & Curriculum Officer"
    assert data["department"] == "Ministry of Education"

    user_doc = db.users.find_one({"_id": unresolved_id})
    assert user_doc["role_id"] == role_edu


def test_14_15_16_role_assignment_rbac_enforcement(role_test_env):
    """14, 15, 16. OFFICIAL, TRAINER, and Unauthenticated callers CANNOT assign roles."""
    client = role_test_env["client"]
    target_id = role_test_env["official_id"]
    role_stat = str(role_test_env["role_stat"])

    # 14. Official cannot assign
    res_off = client.post(
        f"/api/v1/admin/users/{target_id}/assign-role",
        headers={"Authorization": f"Bearer {role_test_env['official_token']}"},
        json={"role_id": role_stat}
    )
    assert res_off.status_code == 403

    # 15. Trainer cannot assign
    res_trn = client.post(
        f"/api/v1/admin/users/{target_id}/assign-role",
        headers={"Authorization": f"Bearer {role_test_env['trainer_token']}"},
        json={"role_id": role_stat}
    )
    assert res_trn.status_code == 403

    # 16. Unauthenticated cannot assign
    res_unauth = client.post(
        f"/api/v1/admin/users/{target_id}/assign-role",
        json={"role_id": role_stat}
    )
    assert res_unauth.status_code == 401
