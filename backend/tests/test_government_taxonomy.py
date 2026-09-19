"""
Unit and Integration Tests for Government Organization & Designation Taxonomy.
Validates:
- Central Government Coverage (50+ Ministries grounded in Allocation of Business Rules 2026)
- 28 States and 8 Union Territories Coverage
- Local Government & Field Workforce Coverage (Talathi, Tehsil, BDO, Collectorate, Gram Panchayat)
- Designation Taxonomy across 12 domains + Aliases + Custom designation
- Backend Role Resolution via canonical taxonomy archetype
- Zero silent fallback for unknown arbitrary posts
- User Profile update and serialization with new taxonomy fields
- Idempotent Migration
"""

import pytest
from bson import ObjectId

from app.core.government_taxonomy import (
    CENTRAL_MINISTRIES,
    STATES_AND_UTS,
    STATE_DEPARTMENT_TEMPLATES,
    DESIGNATION_CATALOGUE,
    find_canonical_organization,
    find_canonical_designation,
    get_all_canonical_ministries,
    get_all_designations,
)
from app.roles.resolver import resolve_role_for_user
from app.scripts.migrate_user_taxonomy import migrate_user_taxonomy


class MockRolesCollection:
    """Mock roles collection simulating active roles in the database."""
    def __init__(self, roles):
        self._roles = roles

    def find(self, query=None):
        query = query or {}
        if query.get("status") == "active":
            return [r for r in self._roles if r.get("status") == "active"]
        return list(self._roles)


class MockUsersCollection:
    """Mock users collection simulating database.users."""
    def __init__(self, users):
        self._users = {str(u["_id"]): dict(u) for u in users}

    def find(self, query=None):
        return list(self._users.values())

    def update_one(self, filter_q, update_q):
        uid = str(filter_q["_id"])
        if uid in self._users:
            if "$set" in update_q:
                self._users[uid].update(update_q["$set"])


class MockDatabase:
    def __init__(self, roles, users=None):
        self.roles = MockRolesCollection(roles)
        self.users = MockUsersCollection(users or [])


@pytest.fixture
def mock_db():
    roles = [
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667a"),
            "role_code": "EDUCATION_OFFICER",
            "role_name": "Education & Curriculum Officer",
            "department": "Ministry of Education",
            "department_code": "MOE",
            "designations": ["Teacher", "Headmaster / Principal", "Block Education Officer (BEO)"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667b"),
            "role_code": "STATISTICAL_OFFICER",
            "role_name": "Statistical Officer",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "department_code": "MOSPI",
            "designations": ["Statistical Officer", "Senior Statistical Officer (SSO)", "Assistant Director (Statistics)"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667c"),
            "role_code": "DIGITAL_GOVERNANCE_ARCHITECT",
            "role_name": "Digital Governance & e-Gov Architect",
            "department": "Ministry of Electronics and Information Technology (MeitY)",
            "department_code": "MEITY",
            "designations": ["Informatics Officer / Scientist 'B'", "Technical Director (e-Gov)"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667d"),
            "role_code": "RURAL_DEVELOPMENT_OFFICER",
            "role_name": "Rural Schemes & Grassroots Governance Officer",
            "department": "Ministry of Rural Development & Panchayati Raj",
            "department_code": "MORD",
            "designations": ["Block Development Officer (BDO)", "Panchayat Secretary"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667e"),
            "role_code": "PUBLIC_FINANCIAL_MANAGEMENT_OFFICER",
            "role_name": "Financial Management & Audit Officer",
            "department": "Ministry of Finance",
            "department_code": "MOF",
            "designations": ["Accounts Officer (AAO / AO)", "Audit Officer"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e7667f"),
            "role_code": "PUBLIC_HEALTH_DATA_OFFICER",
            "role_name": "Public Health & Epidemiological Data Officer",
            "department": "Ministry of Health and Family Welfare (MoHFW)",
            "department_code": "MOHFW",
            "designations": ["Medical Officer (Public Health)", "Surveillance Officer"],
            "status": "active",
        },
        {
            "_id": ObjectId("6a8ff00dbda6ad0866e76680"),
            "role_code": "CAPACITY_BUILDING_OFFICER",
            "role_name": "Civil Services Capacity Building Officer",
            "department": "Department of Personnel and Training (DoPT)",
            "department_code": "DOPT",
            "designations": ["Under Secretary", "Section Officer (SO)"],
            "status": "active",
        },
    ]
    return MockDatabase(roles)


def test_central_ministries_coverage():
    """Verify that Central Government coverage includes all required Union ministries."""
    ministries = get_all_canonical_ministries()
    assert len(ministries) >= 50, f"Expected 50+ central ministries, got {len(ministries)}"

    names = [m["name"].lower() for m in ministries]
    aliases = [a.lower() for m in ministries for a in m.get("aliases", [])]
    all_text = " ".join(names + aliases)

    required_keywords = [
        "agriculture", "ayush", "chemicals", "civil aviation", "coal",
        "commerce", "communications", "consumer affairs", "cooperation",
        "corporate affairs", "culture", "defence", "education",
        "electronics and information technology", "environment", "external affairs",
        "finance", "health", "home affairs", "housing and urban affairs",
        "jal shakti", "labour", "law and justice", "msme", "mines",
        "panchayati raj", "personnel", "petroleum", "railways",
        "rural development", "statistics", "textiles", "tribal",
        "women and child", "youth affairs",
    ]

    for kw in required_keywords:
        assert kw in all_text, f"Missing expected Central Government domain: '{kw}'"


def test_states_and_uts_coverage():
    """Verify all 28 States and 8 Union Territories are covered."""
    states = [s for s in STATES_AND_UTS if s["type"] == "STATE"]
    uts = [u for u in STATES_AND_UTS if u["type"] == "UT"]

    assert len(states) == 28, f"Expected 28 States, got {len(states)}"
    assert len(uts) == 8, f"Expected 8 Union Territories, got {len(uts)}"

    state_names = {s["name"] for s in states}
    assert "Maharashtra" in state_names
    assert "Uttar Pradesh" in state_names
    assert "Tamil Nadu" in state_names
    assert "West Bengal" in state_names
    assert "Gujarat" in state_names

    ut_names = {u["name"] for u in uts}
    assert "Delhi" in ut_names
    assert "Jammu and Kashmir" in ut_names
    assert "Ladakh" in ut_names
    assert "Puducherry" in ut_names


def test_local_government_and_field_offices_coverage():
    """Verify field administration templates include Tehsil, Talathi, BDO, and local government bodies."""
    templates = STATE_DEPARTMENT_TEMPLATES
    assert len(templates) >= 8

    office_names = [
        off["name"].lower()
        for tmpl in templates
        for off in tmpl.get("field_offices", [])
    ]
    all_offices = " ".join(office_names)

    assert "tehsil" in all_offices or "taluka" in all_offices
    assert "talathi" in all_offices or "patwari" in all_offices
    assert "collectorate" in all_offices or "district administration" in all_offices
    assert "block development" in all_offices
    assert "gram panchayat" in all_offices
    assert "municipal corporation" in all_offices
    assert "district treasury" in all_offices


def test_designation_catalogue_coverage():
    """Verify designation catalogue contains realistic civil services, field roles, and custom option."""
    designations = get_all_designations()
    assert len(designations) >= 40

    titles = [d["title"].lower() for d in designations]
    aliases = [a.lower() for d in designations for a in d.get("aliases", [])]
    all_titles = " ".join(titles + aliases)

    # Key field posts
    assert "talathi" in all_titles
    assert "patwari" in all_titles
    assert "lekhpal" in all_titles
    assert "tehsildar" in all_titles or "tahsildar" in all_titles
    assert "statistical officer" in all_titles
    assert "teacher" in all_titles
    assert "medical officer" in all_titles
    assert "police inspector" in all_titles
    assert "accounts officer" in all_titles
    assert "clerk" in all_titles

    # Other / Custom option
    custom_item = find_canonical_designation("Other")
    assert custom_item is not None
    assert custom_item["id"] == "DESIG-OTHER"


def test_canonical_normalization_lookups():
    """Test find_canonical_organization and find_canonical_designation."""
    # Central org exact and alias
    mospi = find_canonical_organization("Ministry of Statistics & Programme Implementation (MoSPI)")
    assert mospi is not None
    assert mospi["id"] == "GOI-MOSPI"

    moe = find_canonical_organization("Ministry of Education")
    assert moe is not None
    assert moe["id"] == "GOI-MOE"

    # Field organization
    talathi_off = find_canonical_organization("Talathi / Patwari Office (Village Revenue Saja)")
    assert talathi_off is not None
    assert "TALATHI" in talathi_off["id"]

    # Designation exact & alias
    talathi_des = find_canonical_designation("Talathi")
    assert talathi_des is not None
    assert talathi_des["id"] == "DESIG-REV-TALATHI"

    tehsildar_des = find_canonical_designation("Tehsildar")
    assert tehsildar_des is not None
    assert tehsildar_des["id"] == "DESIG-ADM-TEHSILDAR"


def test_role_resolution_for_canonical_designations(mock_db):
    """Test that canonical designations resolve cleanly to archetype roles."""
    # 1. Exact MoSPI + Statistical Officer (Existing user flow)
    oid = resolve_role_for_user(mock_db, "Ministry of Statistics & Programme Implementation (MoSPI)", "Statistical Officer")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667b")

    # 2. MoE + Teacher (Existing user flow)
    oid = resolve_role_for_user(mock_db, "Ministry of Education", "Teacher")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667a")

    # 3. Field workforce: Talathi resolves to Rural Development archetype
    oid = resolve_role_for_user(mock_db, "Revenue Department, Maharashtra", "Talathi")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667d")

    # 4. Field workforce: Tahsildar resolves to Rural Development archetype
    oid = resolve_role_for_user(mock_db, "Tehsil Office", "Tahsildar")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667d")

    # 5. Education: District Education Officer resolves to Education Officer
    oid = resolve_role_for_user(mock_db, "School Education Department", "District Education Officer")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667a")

    # 6. Health: Medical Officer resolves to Public Health Officer
    oid = resolve_role_for_user(mock_db, "District Hospital", "Medical Officer")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667f")

    # 7. Finance: Accounts Officer resolves to Financial Management Officer
    oid = resolve_role_for_user(mock_db, "District Treasury", "Accounts Officer")
    assert oid == ObjectId("6a8ff00dbda6ad0866e7667e")


def test_no_silent_fallback_for_unknown_posts(mock_db):
    """Ensure arbitrary unknown posts NEVER receive a silent fallback role."""
    oid = resolve_role_for_user(mock_db, "Alien Space Directorate", "Starship Commander")
    assert oid is None

    oid = resolve_role_for_user(mock_db, "Ministry of Education", "Helicopter Pilot")
    assert oid is None


def test_idempotent_user_taxonomy_migration():
    """Test that existing user records are cleanly migrated without data loss."""
    users = [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "email": "official@shikshasetu.gov.in",
            "full_name": "Rajesh Sharma",
            "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
            "designation": "Statistical Officer",
            "access_role": "OFFICIAL",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "email": "talathi.demo@maharashtra.gov.in",
            "full_name": "Sanjay Patil",
            "department": "Revenue and Land Administration Department",
            "designation": "Talathi",
            "access_role": "OFFICIAL",
        },
    ]

    mock_db = MockDatabase([], users)
    result = migrate_user_taxonomy(mock_db)

    assert result["total_users"] == 2
    assert result["migrated"] == 2

    # Check Rajesh Sharma (Golden Demo)
    rajesh = mock_db.users._users[str(users[0]["_id"])]
    assert rajesh["organization_id"] == "GOI-MOSPI"
    assert rajesh["designation_id"] == "DESIG-STAT-OFFICER"
    assert rajesh["government_level"] == "CENTRAL"
    assert rajesh["department"] == "Ministry of Statistics & Programme Implementation (MoSPI)"
    assert rajesh["designation"] == "Statistical Officer"
    assert rajesh["application_role"] == "OFFICIAL"

    # Check Sanjay Patil (Field Talathi)
    patil = mock_db.users._users[str(users[1]["_id"])]
    assert patil["organization_id"] == "STATE-REV"
    assert patil["designation_id"] == "DESIG-REV-TALATHI"
    assert patil["government_level"] == "STATE"
    assert patil["application_role"] == "OFFICIAL"

    # Running migration again should be a no-op (idempotent)
    second_run = migrate_user_taxonomy(mock_db)
    assert second_run["migrated"] == 0
    assert second_run["already_canonical"] == 2
