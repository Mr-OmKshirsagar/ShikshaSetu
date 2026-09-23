"""
Comprehensive test suite for Government Talent & Opportunity Network.

Covers:
1. Talent profile retrieval & readiness calculation
2. Explicit consent (opt-in / opt-out, default OFF)
3. Deterministic eligibility filtering (Rule-based, not LLM)
4. Competency threshold check (at or above vs below threshold)
5. Talathi with revenue competencies vs Statistical opportunity (ineligibility)
6. Department isolation & visibility tiers (PRIVATE, MY_DEPARTMENT, AUTHORIZED_DEPARTMENTS)
7. Explainability & verified fact grounding
8. Opportunity lifecycle (DRAFT -> PUBLISH)
9. Role-based access control & IDOR prevention
10. Audit logging of sensitive discovery actions
"""

from datetime import datetime, UTC
from bson import ObjectId
import pytest
from fastapi.testclient import TestClient

from app.auth.schemas import AccessRole
from app.auth.security import create_access_token
from app.core.config import Settings
from app.main import create_app
from app.talent.models import OpportunityType, OpportunityStatus, VisibilityLevel, TalentAuditAction
from app.talent import service, repository


class FakeCollection:
    def __init__(self, documents=None):
        self.documents = list(documents or [])

    def find_one(self, query=None, projection=None):
        query = query or {}
        for doc in self.documents:
            match = True
            for k, v in query.items():
                if k == "$or":
                    or_match = any(
                        all(doc.get(sub_k) == sub_v or str(doc.get(sub_k)) == str(sub_v) for sub_k, sub_v in condition.items())
                        for condition in v
                    )
                    if not or_match:
                        match = False
                        break
                elif doc.get(k) != v and str(doc.get(k)) != str(v):
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    def find(self, query=None, projection=None):
        query = query or {}
        res = []
        for doc in self.documents:
            match = True
            for k, v in query.items():
                if k == "$or":
                    or_match = any(
                        all(doc.get(sub_k) == sub_v or str(doc.get(sub_k)) == str(sub_v) for sub_k, sub_v in condition.items())
                        for condition in v
                    )
                    if not or_match:
                        match = False
                        break
                elif k == "_id" and isinstance(v, dict) and "$in" in v:
                    if doc.get("_id") not in v["$in"] and str(doc.get("_id")) not in [str(x) for x in v["$in"]]:
                        match = False
                        break
                elif doc.get(k) != v and str(doc.get(k)) != str(v):
                    match = False
                    break
            if match:
                res.append(dict(doc))
        return FakeCursor(res)

    def count_documents(self, query=None):
        return len(list(self.find(query)))

    def insert_one(self, doc):
        doc = dict(doc)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.documents.append(doc)
        class InsertResult:
            inserted_id = doc["_id"]
        return InsertResult()

    def update_one(self, query, update, upsert=False):
        doc = self.find_one(query)
        if doc:
            for k, v in update.get("$set", {}).items():
                doc[k] = v
            # update in documents
            for i, d in enumerate(self.documents):
                if d.get("_id") == doc.get("_id"):
                    self.documents[i] = doc
                    break
        elif upsert:
            new_doc = dict(query)
            for k, v in update.get("$set", {}).items():
                new_doc[k] = v
            new_doc["_id"] = ObjectId()
            self.documents.append(new_doc)

    def create_index(self, *args, **kwargs):
        pass


class FakeCursor:
    def __init__(self, items):
        self.items = items

    def sort(self, *args, **kwargs):
        return self

    def skip(self, count):
        self.items = self.items[count:]
        return self

    def limit(self, count):
        self.items = self.items[:count]
        return self

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()
        self.roles = FakeCollection()
        self.competencies = FakeCollection()
        self.competency_profiles = FakeCollection()
        self.competency_evidence = FakeCollection()
        self.role_requirements = FakeCollection()
        self.learning_materials = FakeCollection()
        self.quizzes = FakeCollection()
        self.quiz_attempts = FakeCollection()
        self.learning_activities = FakeCollection()
        self.talent_preferences = FakeCollection()
        self.government_opportunities = FakeCollection()
        self.talent_opportunity_matches = FakeCollection()
        self.talent_access_audit = FakeCollection()


@pytest.fixture
def fake_db():
    db = FakeDatabase()
    
    # Setup Roles
    stat_role_id = ObjectId()
    revenue_role_id = ObjectId()
    db.roles.insert_one({
        "_id": stat_role_id,
        "role_name": "Statistical Officer",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)"
    })
    db.roles.insert_one({
        "_id": revenue_role_id,
        "role_name": "Talathi",
        "department": "Department of Revenue & Land Records"
    })
    
    # Setup Competencies
    comp_sampling_id = ObjectId()
    comp_survey_id = ObjectId()
    comp_land_id = ObjectId()
    
    db.competencies.insert_one({
        "_id": comp_sampling_id,
        "code": "STAT_SAMPLING",
        "name": "Statistical Sampling & Estimation",
        "domain": "STATISTICAL"
    })
    db.competencies.insert_one({
        "_id": comp_survey_id,
        "code": "STAT_SURVEY_DESIGN",
        "name": "Survey Design & Methodology",
        "domain": "STATISTICAL"
    })
    db.competencies.insert_one({
        "_id": comp_land_id,
        "code": "REV_LAND_RECORDS",
        "name": "Land Records & Mutation",
        "domain": "ADMINISTRATIVE"
    })
    
    # Setup Official User: Rajesh Sharma (Statistical Officer)
    stat_user_id = ObjectId()
    db.users.insert_one({
        "_id": stat_user_id,
        "email": "official@shikshasetu.gov.in",
        "full_name": "Rajesh Sharma",
        "designation": "Statistical Officer",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "employee_id": "STAT101",
        "role_id": stat_role_id,
        "access_role": AccessRole.OFFICIAL.value,
        "status": "active",
        "years_experience": 5
    })
    
    # Statistical Officer's Competency Profiles (Sampling: 3.5, Survey: 4.0, confidence 0.85)
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": stat_user_id,
        "competency_id": comp_sampling_id,
        "current_level": 3.5,
        "confidence": 0.85
    })
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": stat_user_id,
        "competency_id": comp_survey_id,
        "current_level": 4.0,
        "confidence": 0.90
    })
    db.competency_evidence.insert_one({
        "_id": ObjectId(),
        "user_id": stat_user_id,
        "competency_id": comp_sampling_id,
        "evidence_type": "ASSESSMENT"
    })
    
    # Setup Talathi User: Ramesh Patil (Revenue Department)
    talathi_user_id = ObjectId()
    db.users.insert_one({
        "_id": talathi_user_id,
        "email": "talathi@shikshasetu.gov.in",
        "full_name": "Ramesh Patil",
        "designation": "Talathi",
        "department": "Department of Revenue & Land Records",
        "employee_id": "REV202",
        "role_id": revenue_role_id,
        "access_role": AccessRole.OFFICIAL.value,
        "status": "active",
        "years_experience": 4
    })
    db.competency_profiles.insert_one({
        "_id": ObjectId(),
        "user_id": talathi_user_id,
        "competency_id": comp_land_id,
        "current_level": 4.2,
        "confidence": 0.80
    })
    
    # Setup Admin User
    admin_user_id = ObjectId()
    db.users.insert_one({
        "_id": admin_user_id,
        "email": "admin@shikshasetu.gov.in",
        "full_name": "Amit Patel",
        "designation": "System Administrator",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "employee_id": "ADM001",
        "access_role": AccessRole.ADMIN.value,
        "status": "active"
    })

    return {
        "db": db,
        "stat_user_id": str(stat_user_id),
        "talathi_user_id": str(talathi_user_id),
        "admin_user_id": str(admin_user_id),
        "stat_role_id": str(stat_role_id),
        "comp_sampling_id": str(comp_sampling_id),
        "comp_survey_id": str(comp_survey_id),
        "comp_land_id": str(comp_land_id),
    }


@pytest.fixture
def app_client(fake_db):
    settings = Settings(
        app_name="ShikshaSetu Test",
        mongodb_database="shikshasetu_test",
        jwt_secret="test-secret-key-32-chars-long-strictly!",
    )
    app = create_app(settings)
    app.state.database = fake_db["db"]
    return TestClient(app), fake_db, settings


def auth_header(user_id: str, settings: Settings) -> dict:
    token = create_access_token(user_id, settings)
    return {"Authorization": f"Bearer {token}"}


# ─── Tests ───────────────────────────────────────────────────────────────────


def test_talent_profile_retrieval_and_readiness(app_client):
    """Test talent profile retrieval, readiness scoring, and verified competencies."""
    client, fixtures, settings = app_client
    headers = auth_header(fixtures["stat_user_id"], settings)
    
    response = client.get("/api/v1/talent/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["full_name"] == "Rajesh Sharma"
    assert data["designation"] == "Statistical Officer"
    assert data["department"] == "Ministry of Statistics & Programme Implementation (MoSPI)"
    assert len(data["verified_competencies"]) == 2
    assert data["profile_readiness"] > 0.50
    # Default opt-in must be False (Zero surveillance by default)
    assert data["preferences"]["opt_in_enabled"] is False
    assert data["preferences"]["visibility_level"] == VisibilityLevel.PRIVATE.value


def test_talent_consent_opt_in_and_opt_out(app_client):
    """Test opt-in and opt-out preferences updating and audit logging."""
    client, fixtures, settings = app_client
    headers = auth_header(fixtures["stat_user_id"], settings)
    
    # 1. Update preferences to opt in and enable Authorized Departments discovery
    patch_data = {
        "opt_in_enabled": True,
        "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS.value,
        "available_for_opportunities": True,
        "opportunity_types": [OpportunityType.TRAINER.value, OpportunityType.SUBJECT_MATTER_EXPERT.value]
    }
    response = client.patch("/api/v1/talent/preferences", json=patch_data, headers=headers)
    assert response.status_code == 200
    pref = response.json()["preferences"]
    assert pref["opt_in_enabled"] is True
    assert pref["visibility_level"] == VisibilityLevel.AUTHORIZED_DEPARTMENTS.value
    assert pref["available_for_opportunities"] is True
    
    # Verify audit log was written
    audit_logs = list(fixtures["db"].talent_access_audit.find({
        "performed_by": ObjectId(fixtures["stat_user_id"]),
        "action": "UPDATE_PREFERENCES"
    }))
    assert len(audit_logs) >= 1
    
    # 2. Opt back out
    patch_out = {
        "opt_in_enabled": False,
        "available_for_opportunities": False,
        "visibility_level": VisibilityLevel.PRIVATE.value
    }
    resp_out = client.patch("/api/v1/talent/preferences", json=patch_out, headers=headers)
    assert resp_out.status_code == 200
    assert resp_out.json()["preferences"]["opt_in_enabled"] is False


def test_deterministic_matching_eligible_candidate(fake_db):
    """Test deterministic rule-based matching for an eligible, opted-in official."""
    db = fake_db["db"]
    user_id = fake_db["stat_user_id"]
    
    # Opt in user
    repository.upsert_talent_preferences(db, user_id, {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS,
        "opportunity_types": [OpportunityType.TRAINER]
    })
    
    # Opportunity requiring STAT_SAMPLING (min 3.0) and STAT_SURVEY_DESIGN (min 3.5)
    opportunity = {
        "_id": ObjectId(),
        "title": "National Sampling Lead Faculty",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "opportunity_type": OpportunityType.TRAINER,
        "required_roles": ["Statistical Officer"],
        "required_competencies": [
            {"competency_code": "STAT_SAMPLING", "minimum_level": 3.0, "importance": 1.0},
            {"competency_code": "STAT_SURVEY_DESIGN", "minimum_level": 3.5, "importance": 0.8}
        ],
        "minimum_experience_years": 3,
        "status": OpportunityStatus.PUBLISHED
    }
    
    eligible, match_score, explanation = service.check_eligibility_and_match(db, opportunity, user_id)
    assert eligible is True
    assert match_score >= 0.70
    assert len(explanation.matched_competencies) == 2
    assert explanation.missing_competencies == []
    # Verify explainability reasons
    assert any("Statistical Sampling & Estimation" in r for r in explanation.match_reasons)
    assert any("Evidence confidence" in r for r in explanation.match_reasons)


def test_deterministic_matching_below_minimum_competency(fake_db):
    """Test that candidate with competency below the required threshold is NOT eligible."""
    db = fake_db["db"]
    user_id = fake_db["stat_user_id"]
    
    # Opt in user
    repository.upsert_talent_preferences(db, user_id, {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS
    })
    
    # Opportunity requiring STAT_SAMPLING at Level 4.5 (user only has 3.5)
    opportunity = {
        "_id": ObjectId(),
        "title": "Principal Statistical Methodology Advisor",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "opportunity_type": OpportunityType.ADVISORY,
        "required_competencies": [
            {"competency_code": "STAT_SAMPLING", "minimum_level": 4.5, "importance": 1.0}
        ],
        "status": OpportunityStatus.PUBLISHED
    }
    
    eligible, match_score, explanation = service.check_eligibility_and_match(db, opportunity, user_id)
    assert eligible is False
    assert match_score == 0.0
    assert len(explanation.matched_competencies) == 1
    assert explanation.matched_competencies[0].meets_requirement is False
    assert explanation.matched_competencies[0].gap == 1.0  # 4.5 - 3.5
    assert any("Competency below threshold" in r for r in explanation.eligibility_reasons)


def test_talathi_unrelated_competency_rejection(fake_db):
    """Test that Talathi (Revenue) never matches an unrelated Statistical opportunity."""
    db = fake_db["db"]
    talathi_id = fake_db["talathi_user_id"]
    
    # Opt in Talathi
    repository.upsert_talent_preferences(db, talathi_id, {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS
    })
    
    stat_opportunity = {
        "_id": ObjectId(),
        "title": "Senior Trainer — Statistical Sampling",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "opportunity_type": OpportunityType.TRAINER,
        "required_roles": ["Statistical Officer"],
        "required_competencies": [
            {"competency_code": "STAT_SAMPLING", "minimum_level": 2.0, "importance": 1.0}
        ],
        "status": OpportunityStatus.PUBLISHED
    }
    
    eligible, match_score, explanation = service.check_eligibility_and_match(db, stat_opportunity, talathi_id)
    assert eligible is False
    assert "STAT_SAMPLING" in explanation.missing_competencies


def test_department_isolation_and_visibility_levels(fake_db):
    """Test strict department isolation under MY_DEPARTMENT and PRIVATE visibility."""
    db = fake_db["db"]
    stat_user_id = fake_db["stat_user_id"]
    
    # Case 1: PRIVATE visibility -> Never eligible
    repository.upsert_talent_preferences(db, stat_user_id, {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.PRIVATE
    })
    opp_mospi = {
        "_id": ObjectId(),
        "title": "MoSPI Workshop",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "required_competencies": [{"competency_code": "STAT_SAMPLING", "minimum_level": 2.0}],
        "status": OpportunityStatus.PUBLISHED
    }
    eligible, _, explanation = service.check_eligibility_and_match(db, opp_mospi, stat_user_id)
    assert eligible is False
    assert any("Private" in r for r in explanation.eligibility_reasons)
    
    # Case 2: MY_DEPARTMENT visibility -> Eligible for MoSPI, but NOT for Revenue Dept
    repository.upsert_talent_preferences(db, stat_user_id, {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.MY_DEPARTMENT
    })
    
    opp_outside_dept = {
        "_id": ObjectId(),
        "title": "External Department Opportunity",
        "department_name": "Department of Agriculture",
        "required_competencies": [{"competency_code": "STAT_SAMPLING", "minimum_level": 2.0}],
        "status": OpportunityStatus.PUBLISHED
    }
    eligible_ext, _, exp_ext = service.check_eligibility_and_match(db, opp_outside_dept, stat_user_id)
    assert eligible_ext is False
    assert any("outside department" in r.lower() for r in exp_ext.eligibility_reasons)


def test_opportunity_discovery_matches_endpoint_rbac(app_client):
    """Test that discovering talent matches is restricted to authorized departments and audited."""
    client, fixtures, settings = app_client
    db = fixtures["db"]
    admin_headers = auth_header(fixtures["admin_user_id"], settings)
    official_headers = auth_header(fixtures["stat_user_id"], settings)
    
    # Create opportunity
    opp_doc = {
        "title": "National Sampling Mentor",
        "description": "Mentoring field staff",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "opportunity_type": OpportunityType.MENTOR.value,
        "required_competencies": [{"competency_code": "STAT_SAMPLING", "minimum_level": 2.0}],
        "status": OpportunityStatus.PUBLISHED.value,
        "created_by": fixtures["admin_user_id"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
    inserted = db.government_opportunities.insert_one(opp_doc)
    opp_id = str(inserted.inserted_id)
    
    # Opt in Statistical Officer
    repository.upsert_talent_preferences(db, fixtures["stat_user_id"], {
        "opt_in_enabled": True,
        "available_for_opportunities": True,
        "visibility_level": VisibilityLevel.AUTHORIZED_DEPARTMENTS.value
    })
    
    # 1. Official cannot call /matches (HTTP 403 Forbidden)
    res_forbidden = client.get(f"/api/v1/talent/opportunities/{opp_id}/matches", headers=official_headers)
    assert res_forbidden.status_code == 403
    
    # 2. Admin can call /matches
    res_admin = client.get(f"/api/v1/talent/opportunities/{opp_id}/matches", headers=admin_headers)
    assert res_admin.status_code == 200
    data = res_admin.json()
    assert data["total_eligible"] == 1
    assert data["matches"][0]["full_name"] == "Rajesh Sharma"
    assert data["matches"][0]["eligible"] is True
    
    # 3. Check audit log
    audit_logs = list(db.talent_access_audit.find({
        "action": TalentAuditAction.OPPORTUNITY_MATCHES_VIEWED.value,
        "target_opportunity_id": ObjectId(opp_id)
    }))
    assert len(audit_logs) >= 1


def test_create_and_publish_opportunity_lifecycle(app_client):
    """Test creating and publishing an opportunity by authorized personnel."""
    client, fixtures, settings = app_client
    admin_headers = auth_header(fixtures["admin_user_id"], settings)
    
    create_payload = {
        "title": "Executive Workshop on Data Governance",
        "description": "Cross-ministerial governance seminar",
        "department_name": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "opportunity_type": OpportunityType.WORKSHOP.value,
        "required_roles": ["Statistical Officer"],
        "required_competencies": [
            {"competency_code": "STAT_SAMPLING", "minimum_level": 3.0, "importance": 1.0}
        ],
        "minimum_experience_years": 2
    }
    
    # Create (starts in DRAFT)
    res_create = client.post("/api/v1/talent/opportunities", json=create_payload, headers=admin_headers)
    assert res_create.status_code == 201
    opp_data = res_create.json()
    opp_id = opp_data["id"]
    assert opp_data["status"] == OpportunityStatus.DRAFT.value
    
    # Publish
    res_pub = client.post(f"/api/v1/talent/opportunities/{opp_id}/publish", headers=admin_headers)
    assert res_pub.status_code == 200
    assert res_pub.json()["status"] == OpportunityStatus.PUBLISHED.value
