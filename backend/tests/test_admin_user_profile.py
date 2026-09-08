"""
Tests for GET /api/v1/admin/users/{user_id}/profile

Covers:
 1.  Admin can retrieve a user's workforce profile
 2.  Non-admin (OFFICIAL) cannot retrieve it — 403
 3.  Non-admin (TRAINER) cannot retrieve it — 403
 4.  Unauthenticated request returns 401
 5.  Non-existent user_id returns 404
 6.  Correct user's learning activities are returned (not another user's)
 7.  Learning activities are not mixed between users
 8.  Completed activity is shown with status "completed"
 9.  In-progress activity shows correct stored progress_percent
10.  Not-started activity is represented with status "not_started"
11.  User with no learning activity returns empty list and honest summary
12.  Supporting evidence is distinguished from authoritative evidence
13.  Practice quiz results are NOT presented as authoritative evidence
14.  Historical evidence records remain unchanged after profile fetch
15.  Skill gaps correspond to the selected user's role requirements, not another user's
"""

import pytest
from bson import ObjectId
from datetime import datetime, UTC
from fastapi.testclient import TestClient

from app.auth.security import create_access_token, hash_password
from app.core.config import Settings
from app.main import create_app


# ─── Fake DB infrastructure (reuse pattern from test_admin.py) ───────────────

class FakeCollection:
    def __init__(self, documents=None):
        self._docs = list(documents or [])

    def find(self, query=None, projection=None):
        if not query:
            return _FakeCursor(self._docs)
        results = [d for d in self._docs if self._match(d, query)]
        return _FakeCursor(results)

    def find_one(self, query, projection=None):
        for d in self._docs:
            if self._match(d, query):
                return d
        return None

    def insert_one(self, document):
        if "_id" not in document:
            document["_id"] = ObjectId()
        self._docs.append(document)
        return type("InsertResult", (), {"inserted_id": document["_id"]})()

    def update_one(self, query, update, **kwargs):
        for d in self._docs:
            if self._match(d, query):
                if "$set" in update:
                    d.update(update["$set"])
                return type("UpdateResult", (), {"matched_count": 1, "modified_count": 1})()
        return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})()

    def delete_one(self, query):
        for i, d in enumerate(self._docs):
            if self._match(d, query):
                self._docs.pop(i)
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

    @staticmethod
    def _match(doc, query):
        for k, v in query.items():
            if doc.get(k) != v:
                return False
        return True


class _FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, *args, **kwargs):
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __iter__(self):
        return iter(self._docs)

    def __len__(self):
        return len(self._docs)


class FakeDatabase:
    def __init__(self):
        self.users                = FakeCollection()
        self.roles                = FakeCollection()
        self.role_requirements    = FakeCollection()
        self.competencies         = FakeCollection()
        self.competency_profiles  = FakeCollection()
        self.competency_evidence  = FakeCollection()
        self.learning_activities  = FakeCollection()
        self.quizzes              = FakeCollection()
        self.quiz_attempts        = FakeCollection()
        self.capability_assessments = FakeCollection()
        self.learning_resources   = FakeCollection()


# ─── Fixture ──────────────────────────────────────────────────────────────────

@pytest.fixture
def setup():
    db       = FakeDatabase()
    settings = Settings(jwt_secret="test-secret-key-32-chars-long-abc", api_prefix="/api/v1")
    app      = create_app(settings)
    app.state.database = db
    app.state.settings = settings
    client   = TestClient(app)

    # ── Users ──────────────────────────────────────────────────────────────────
    admin_id   = ObjectId()
    official_id = ObjectId()
    other_id   = ObjectId()
    trainer_id = ObjectId()

    role_id = ObjectId()

    db.users.insert_one({
        "_id": admin_id,
        "email": "admin@test.com",
        "full_name": "Admin User",
        "access_role": "ADMIN",
        "status": "active",
        "password_hash": hash_password("pass"),
        "department": "DoPT",
        "designation": "Director",
        "employee_id": "ADM001",
        "role_id": role_id,
        "created_at": datetime.now(UTC),
    })

    db.users.insert_one({
        "_id": official_id,
        "email": "official@test.com",
        "full_name": "Ravi Kumar",
        "access_role": "OFFICIAL",
        "status": "active",
        "password_hash": hash_password("pass"),
        "department": "MoSPI",
        "designation": "Statistical Officer",
        "employee_id": "OFF001",
        "role_id": role_id,
        "created_at": datetime.now(UTC),
    })

    db.users.insert_one({
        "_id": other_id,
        "email": "other@test.com",
        "full_name": "Another Officer",
        "access_role": "OFFICIAL",
        "status": "active",
        "password_hash": hash_password("pass"),
        "department": "NSSO",
        "designation": "Deputy Director",
        "employee_id": "OFF002",
        "role_id": role_id,
        "created_at": datetime.now(UTC),
    })

    db.users.insert_one({
        "_id": trainer_id,
        "email": "trainer@test.com",
        "full_name": "Trainer User",
        "access_role": "TRAINER",
        "status": "active",
        "password_hash": hash_password("pass"),
        "department": "CBC",
        "designation": "Lead Trainer",
        "employee_id": "TRN001",
        "created_at": datetime.now(UTC),
    })

    # ── Role + competency ──────────────────────────────────────────────────────
    comp_id = ObjectId()
    db.competencies.insert_one({
        "_id": comp_id,
        "code": "STAT_DATA",
        "name": "Statistical Data Analysis",
        "domain": "Statistical",
    })

    db.roles.insert_one({
        "_id": role_id,
        "role_name": "Statistical Officer",
        "role_code": "STAT_OFFICER",
    })

    db.role_requirements.insert_one({
        "_id": ObjectId(),
        "role_id": role_id,
        "competency_id": comp_id,
        "required_level": 4.0,
    })

    # ── Competency profile for official (current_level 2.5, gap 1.5 = CRITICAL) ──
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": official_id,
        "competency_id": comp_id,
        "current_level": 2.5,
    })

    # ── Competency profile for other user (different level) ──
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": other_id,
        "competency_id": comp_id,
        "current_level": 3.9,
    })

    # ── Learning activities for official only ──────────────────────────────────
    completed_act_id = ObjectId()
    db.learning_activities.insert_one({
        "_id": completed_act_id,
        "user_id": official_id,
        "resource_id": "res-sql-basics",
        "competency_id": str(comp_id),
        "status": "completed",
        "progress_percent": 100.0,
        "duration_minutes": 90.0,
        "started_at": datetime(2026, 9, 1, 9, 0, tzinfo=UTC),
        "completed_at": datetime(2026, 9, 3, 11, 0, tzinfo=UTC),
        "last_accessed_at": datetime(2026, 9, 3, 11, 0, tzinfo=UTC),
        "notes": "Completed SQL fundamentals",
    })

    inprogress_act_id = ObjectId()
    db.learning_activities.insert_one({
        "_id": inprogress_act_id,
        "user_id": official_id,
        "resource_id": "res-python-data",
        "competency_id": str(comp_id),
        "status": "in_progress",
        "progress_percent": 45.0,
        "duration_minutes": 30.0,
        "started_at": datetime(2026, 9, 5, 10, 0, tzinfo=UTC),
        "completed_at": None,
        "last_accessed_at": datetime(2026, 9, 6, 8, 0, tzinfo=UTC),
        "notes": None,
    })

    notstarted_act_id = ObjectId()
    db.learning_activities.insert_one({
        "_id": notstarted_act_id,
        "user_id": official_id,
        "resource_id": "res-r-statistics",
        "competency_id": str(comp_id),
        "status": "not_started",
        "progress_percent": 0.0,
        "duration_minutes": 0.0,
        "started_at": datetime(2026, 9, 7, 0, 0, tzinfo=UTC),
        "completed_at": None,
        "last_accessed_at": datetime(2026, 9, 7, 0, 0, tzinfo=UTC),
        "notes": None,
    })

    # ── Learning activity for OTHER user (must not appear in official's profile) ──
    db.learning_activities.insert_one({
        "_id": ObjectId(),
        "user_id": other_id,
        "resource_id": "res-other-only",
        "competency_id": str(comp_id),
        "status": "completed",
        "progress_percent": 100.0,
        "duration_minutes": 60.0,
        "started_at": datetime(2026, 9, 2, 0, 0, tzinfo=UTC),
        "completed_at": datetime(2026, 9, 4, 0, 0, tzinfo=UTC),
        "last_accessed_at": datetime(2026, 9, 4, 0, 0, tzinfo=UTC),
        "notes": None,
    })

    # ── Evidence: supporting (LEARNING_ACTIVITY) for official ─────────────────
    supporting_ev_id = ObjectId()
    db.competency_evidence.insert_one({
        "_id": supporting_ev_id,
        "user_id": official_id,
        "competency_id": str(comp_id),
        "type": "LEARNING_ACTIVITY",
        "confidence": 0.30,
        "score": 100.0,
        "recorded_at": datetime(2026, 9, 3, 11, 0, tzinfo=UTC),
        "source": {"activity_id": completed_act_id, "resource_id": "res-sql-basics"},
        "notes": "Completed SQL Basics",
    })

    # ── Evidence: authoritative (CAPABILITY_ASSESSMENT) for official ──────────
    auth_ev_id = ObjectId()
    db.competency_evidence.insert_one({
        "_id": auth_ev_id,
        "user_id": official_id,
        "competency_id": str(comp_id),
        "type": "CAPABILITY_ASSESSMENT",
        "confidence": 0.85,
        "score": 3.2,
        "recorded_at": datetime(2026, 9, 6, 14, 0, tzinfo=UTC),
        "source": {"assessment_id": ObjectId()},
        "notes": "Formal capability assessment",
    })

    # ── Capability assessment for official ────────────────────────────────────
    capability_ass_id = ObjectId()
    db.capability_assessments.insert_one({
        "_id": capability_ass_id,
        "user_id": official_id,
        "competency_code": "STAT_DATA",
        "status": "SUBMITTED",
        "score": 3.2,
        "percentage": 64.0,
        "started_at": datetime(2026, 9, 6, 13, 0, tzinfo=UTC),
        "submitted_at": datetime(2026, 9, 6, 14, 0, tzinfo=UTC),
    })

    # Tokens
    admin_token   = create_access_token(str(admin_id),   settings)
    official_token = create_access_token(str(official_id), settings)
    trainer_token = create_access_token(str(trainer_id), settings)

    return {
        "client":         client,
        "db":             db,
        "admin_token":    admin_token,
        "official_token": official_token,
        "trainer_token":  trainer_token,
        "admin_id":       admin_id,
        "official_id":    official_id,
        "other_id":       other_id,
        "trainer_id":     trainer_id,
        "comp_id":        comp_id,
        "role_id":        role_id,
        "supporting_ev_id": supporting_ev_id,
        "auth_ev_id":     auth_ev_id,
    }


def _profile_url(user_id):
    return f"/api/v1/admin/users/{user_id}/profile"


# ─── Test 1: Admin can retrieve a user's workforce profile ───────────────────

def test_admin_can_retrieve_user_profile(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["user"]["full_name"] == "Ravi Kumar"
    assert data["user"]["department"] == "MoSPI"


# ─── Test 2: Official cannot retrieve another user's profile — 403 ───────────

def test_official_cannot_retrieve_user_profile(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['official_token']}"},
    )
    assert res.status_code == 403, res.text


# ─── Test 3: Trainer cannot retrieve workforce profiles — 403 ────────────────

def test_trainer_cannot_retrieve_user_profile(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['trainer_token']}"},
    )
    assert res.status_code == 403, res.text


# ─── Test 4: Unauthenticated request returns 401 ────────────────────────────

def test_unauthenticated_returns_401(setup):
    res = setup["client"].get(_profile_url(setup["official_id"]))
    assert res.status_code == 401, res.text


# ─── Test 5: Non-existent user_id returns 404 ───────────────────────────────

def test_nonexistent_user_returns_404(setup):
    fake_id = str(ObjectId())
    res = setup["client"].get(
        _profile_url(fake_id),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 404, res.text


# ─── Test 6: Correct user's learning activities are returned ────────────────

def test_correct_user_activities_returned(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    activities = res.json()["learning_activities"]
    resource_ids = [a["resource_id"] for a in activities]
    assert "res-sql-basics"   in resource_ids
    assert "res-python-data"  in resource_ids
    assert "res-r-statistics" in resource_ids


# ─── Test 7: Another user's activities are NOT mixed in ─────────────────────

def test_other_user_activities_not_mixed(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    activities = res.json()["learning_activities"]
    resource_ids = [a["resource_id"] for a in activities]
    assert "res-other-only" not in resource_ids, (
        "Other user's activity must not appear in official's profile"
    )


# ─── Test 8: Completed activity shows status "completed" ─────────────────────

def test_completed_activity_status(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    activities = res.json()["learning_activities"]
    completed = [a for a in activities if a["resource_id"] == "res-sql-basics"]
    assert len(completed) == 1
    assert completed[0]["status"] == "completed"
    assert completed[0]["progress_percent"] == 100.0
    assert completed[0]["completed_at"] is not None


# ─── Test 9: In-progress activity shows stored progress_percent ──────────────

def test_inprogress_activity_progress(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    activities = res.json()["learning_activities"]
    inprog = [a for a in activities if a["resource_id"] == "res-python-data"]
    assert len(inprog) == 1
    assert inprog[0]["status"] == "in_progress"
    assert inprog[0]["progress_percent"] == 45.0, (
        "progress_percent must be the stored value (45.0), not derived"
    )
    assert inprog[0]["completed_at"] is None


# ─── Test 10: Not-started activity is represented correctly ──────────────────

def test_notstarted_activity_representation(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    activities = res.json()["learning_activities"]
    notstarted = [a for a in activities if a["resource_id"] == "res-r-statistics"]
    assert len(notstarted) == 1
    assert notstarted[0]["status"] == "not_started"
    assert notstarted[0]["progress_percent"] == 0.0
    assert notstarted[0]["completed_at"] is None


# ─── Test 11: No learning activity → empty list and honest summary ────────────

def test_no_learning_activity_returns_empty_and_honest_summary(setup):
    # Admin user has no learning activities seeded
    res = setup["client"].get(
        _profile_url(setup["admin_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["learning_activities"] == []
    ls = data["learning_summary"]
    assert ls["total_activities"] == 0
    assert ls["completed"] == 0
    assert ls["in_progress"] == 0
    assert ls["not_started"] == 0
    # overall_learning_progress_pct must be null, not fabricated
    assert ls["overall_learning_progress_pct"] is None, (
        "Must not fabricate a progress value when there are no activities"
    )


# ─── Test 12: Supporting vs authoritative evidence are distinguished ──────────

def test_supporting_and_authoritative_evidence_distinguished(setup):
    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    data = res.json()
    ev_summary = data["evidence_summary"]
    assert ev_summary["supporting_count"] >= 1
    assert ev_summary["authoritative_count"] >= 1

    evidence = data["evidence"]
    types = {e["evidence_type"] for e in evidence}
    assert "LEARNING_ACTIVITY"    in types, "Supporting evidence must be present"
    assert "CAPABILITY_ASSESSMENT" in types, "Authoritative evidence must be present"

    supporting   = [e for e in evidence if e["evidence_type"] == "LEARNING_ACTIVITY"]
    authoritative = [e for e in evidence if e["evidence_type"] == "CAPABILITY_ASSESSMENT"]

    for e in supporting:
        assert e["confidence"] is not None
        assert e["confidence"] <= 0.35, (
            f"Supporting evidence confidence should be ~0.30, got {e['confidence']}"
        )
    for e in authoritative:
        assert e["confidence"] is not None
        assert e["confidence"] >= 0.80, (
            f"Authoritative evidence confidence should be ~0.85, got {e['confidence']}"
        )


# ─── Test 13: Practice quiz results not shown as authoritative capability ─────

def test_quiz_results_not_presented_as_authoritative(setup):
    # Insert a quiz attempt — must NOT appear as authoritative evidence
    db = setup["db"]
    db.quiz_attempts.insert_one({
        "_id": ObjectId(),
        "user_id": setup["official_id"],
        "quiz_id": ObjectId(),
        "score": 4.0,
        "percentage": 80.0,
        "status": "SUBMITTED",
        "submitted_at": datetime.now(UTC),
    })

    res = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res.status_code == 200
    data = res.json()

    # Quiz attempts must not appear in the assessments list
    # (assessments list contains only formal capability assessments)
    for ass in data["assessments"]:
        assert ass["assessment_type"] != "QUIZ", (
            "Practice quiz must not appear in formal assessments list"
        )

    # evidence types must not include raw "QUIZ" type
    evidence_types = {e["evidence_type"] for e in data["evidence"]}
    assert "QUIZ" not in evidence_types


# ─── Test 14: Historical evidence remains unchanged after profile fetch ───────

def test_evidence_unchanged_after_profile_fetch(setup):
    db = setup["db"]

    # Record count before
    count_before = len(db.competency_evidence._docs)

    # Fetch profile (read-only)
    setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )

    # Record count after — must be identical
    count_after = len(db.competency_evidence._docs)
    assert count_after == count_before, (
        "Profile fetch must not write, alter, or delete any evidence records"
    )

    # The supporting evidence record is still intact
    ev = db.competency_evidence.find_one({"_id": setup["supporting_ev_id"]})
    assert ev is not None
    assert ev["confidence"] == 0.30
    assert ev["type"] == "LEARNING_ACTIVITY"


# ─── Test 15: Skill gaps correspond to selected user's role, not another's ───

def test_skill_gaps_match_selected_user_role(setup):
    """
    Official has current_level=2.5, required=4.0 → gap=1.5 → HIGH
    (service threshold: CRITICAL >= 2.0, HIGH >= 1.0, MEDIUM > 0.0).
    Other user has current_level=3.9, required=4.0 → gap=0.1 → MEDIUM.
    Fetching official's profile must show official's own gap values, not other's.
    """
    res_official = setup["client"].get(
        _profile_url(setup["official_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res_official.status_code == 200
    gaps_official = res_official.json()["active_gaps"]
    assert len(gaps_official) >= 1
    stat_gap = next(
        (g for g in gaps_official if g["competency_code"] == "STAT_DATA"), None
    )
    assert stat_gap is not None
    assert stat_gap["current_level"] == pytest.approx(2.5, abs=0.01)
    assert stat_gap["gap"] == pytest.approx(1.5, abs=0.01)
    # gap=1.5: CRITICAL threshold is >=2.0, HIGH threshold is >=1.0
    assert stat_gap["gap_category"] == "HIGH"

    res_other = setup["client"].get(
        _profile_url(setup["other_id"]),
        headers={"Authorization": f"Bearer {setup['admin_token']}"},
    )
    assert res_other.status_code == 200
    gaps_other = res_other.json()["active_gaps"]
    stat_gap_other = next(
        (g for g in gaps_other if g["competency_code"] == "STAT_DATA"), None
    )
    # other user has current 3.9 vs required 4.0 → gap=0.1 → MEDIUM
    if stat_gap_other:
        assert stat_gap_other["gap_category"] == "MEDIUM", (
            "Other user's gap should be MEDIUM (0.1), not HIGH"
        )
        assert stat_gap_other["current_level"] == pytest.approx(3.9, abs=0.01), (
            "Other user's current_level must not bleed into official's profile"
        )
        # Key isolation check: official's gap must differ from other's gap
        assert stat_gap["gap"] != stat_gap_other["gap"], (
            "Gaps must reflect each user's own competency profile"
        )
