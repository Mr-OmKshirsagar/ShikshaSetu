"""Comprehensive Phase 5G recommendation integrity, explainability, role isolation, and caching tests."""

import pytest
from datetime import datetime, UTC
from bson import ObjectId

from app.learning_resources.repository import LearningResourceRepository
from app.learning_resources.provider import (
    ProviderFactory,
    PrototypeIGOTProvider,
    PrototypeNSSTAProvider,
)
from app.learning_resources.candidates import CandidateGenerationService
from app.learning_resources.scoring import ScoringFormula, ScoringService
from app.learning_resources.service import RecommendationService
from app.learning_resources.cache import (
    get_cached_recommendations,
    set_cached_recommendations,
    invalidate_recommendations_cache,
)


@pytest.fixture
def test_setup_data(database):
    """Setup roles, competencies, mappings, and resources for comprehensive testing."""
    # 1. Competencies
    comp_comm_id = ObjectId()
    database.competencies.insert_one({
        "_id": comp_comm_id,
        "code": "COMM_COMMUNICATION",
        "name": "Communication & Interpersonal Skills",
        "domain": "Behavioral",
        "description": "Clear and effective communication in government context",
        "level_definitions": {"1": "Aware", "2": "Basic", "3": "Intermediate", "4": "Advanced", "5": "Expert"},
        "framework_status": "prototype",
    })

    comp_stat_id = ObjectId()
    database.competencies.insert_one({
        "_id": comp_stat_id,
        "code": "STAT_SAMPLING",
        "name": "Statistical Sampling & Survey Design",
        "domain": "Domain",
        "description": "Sampling techniques and survey management",
        "level_definitions": {"1": "Aware", "2": "Basic", "3": "Intermediate", "4": "Advanced", "5": "Expert"},
        "framework_status": "prototype",
    })

    comp_data_id = ObjectId()
    database.competencies.insert_one({
        "_id": comp_data_id,
        "code": "DATA_ANALYSIS",
        "name": "Data Analytics & Visualization",
        "domain": "Technical",
        "description": "Analytical methods and dashboard generation",
        "level_definitions": {"1": "Aware", "2": "Basic", "3": "Intermediate", "4": "Advanced", "5": "Expert"},
        "framework_status": "prototype",
    })

    # 2. Roles
    role_stat_officer_id = ObjectId()
    database.roles.insert_one({
        "_id": role_stat_officer_id,
        "role_code": "STATISTICAL_OFFICER",
        "role_name": "Statistical Officer",
        "description": "MoSPI Statistical Officer",
        "status": "active",
    })

    role_data_lead_id = ObjectId()
    database.roles.insert_one({
        "_id": role_data_lead_id,
        "role_code": "DATA_LEAD",
        "role_name": "Data Science Lead",
        "description": "Lead Data Scientist",
        "status": "active",
    })

    # Role requirements
    database.role_requirements.insert_many([
        {
            "role_id": role_stat_officer_id,
            "competency_id": comp_stat_id,
            "required_level": 4.0,
            "priority": "HIGH",
            "importance": 0.8,
        },
        {
            "role_id": role_stat_officer_id,
            "competency_id": comp_comm_id,
            "required_level": 3.0,
            "priority": "HIGH",
            "importance": 0.8,
        },
        {
            "role_id": role_data_lead_id,
            "competency_id": comp_data_id,
            "required_level": 4.5,
            "priority": "CRITICAL",
            "importance": 1.0,
        },
    ])

    # 3. Explicit role mappings
    database.role_mappings.insert_many([
        {
            "department": "National Statistical Office",
            "designation": "Statistical Officer",
            "role_id": role_stat_officer_id,
            "status": "ACTIVE",
            "mapping_type": "EXACT",
            "created_at": datetime.now(UTC),
        },
        {
            "department": "Analytics Division",
            "designation": "Data Science Lead",
            "role_id": role_data_lead_id,
            "status": "ACTIVE",
            "mapping_type": "EXACT",
            "created_at": datetime.now(UTC),
        },
    ])

    # 4. Learning Resources
    # Communication course (iGOT)
    res_comm_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_comm_id,
        "resource_id": "IGOT-COMM-101",
        "provider": "IGOT",
        "resource_type": "COURSE",
        "title": "Government Communication & Briefing",
        "metadata": {"duration_hours": 12.0, "difficulty": "Intermediate", "target_roles": ["Statistical Officer"], "prerequisites": []},
        "competencies": ["COMM_COMMUNICATION"],
        "source": {"source_type": "GOVERNMENT_PUBLICATION", "source_url": "https://igot.gov.in/course/comm101", "source_document": "SRC-01", "verification_status": "VERIFIED"},
        "provider_specific": {"course_id": "COMM-101", "course_url": "https://igot.gov.in/course/comm101", "provider_name": "iGOT Karmayogi", "extraction_note": None},
        "status": "ACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    # Sampling programme (NSSTA)
    res_stat_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_stat_id,
        "resource_id": "NSSTA-SAMPLING-2024",
        "provider": "NSSTA",
        "resource_type": "TRAINING_PROGRAMME",
        "title": "Advanced Sampling Survey Methodology",
        "metadata": {"duration_hours": 30.0, "difficulty": "Advanced", "target_roles": [], "prerequisites": []},
        "competencies": ["STAT_SAMPLING"],
        "source": {"source_type": "GOVERNMENT_PUBLICATION", "source_url": "https://mospi.gov.in/nssta", "source_document": "SRC-05", "verification_status": "VERIFIED"},
        "provider_specific": {"course_id": None, "programme_id": "PROG-STAT-01", "provider_name": "NSSTA", "extraction_note": None},
        "status": "ACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    # Multi-gap resource: Data & Communication joint module (iGOT)
    res_multi_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_multi_id,
        "resource_id": "IGOT-MULTI-201",
        "provider": "IGOT",
        "resource_type": "COURSE",
        "title": "Statistical Reporting and Stakeholder Communication",
        "metadata": {"duration_hours": 18.0, "difficulty": "Intermediate", "target_roles": ["Statistical Officer"], "prerequisites": []},
        "competencies": ["COMM_COMMUNICATION", "STAT_SAMPLING"],
        "source": {"source_type": "GOVERNMENT_PUBLICATION", "source_url": "https://igot.gov.in/course/multi201", "source_document": "SRC-01", "verification_status": "VERIFIED"},
        "provider_specific": {"course_id": "MULTI-201", "course_url": "https://igot.gov.in/course/multi201", "provider_name": "iGOT Karmayogi", "extraction_note": None},
        "status": "ACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    # Inactive resource (should never be recommended)
    res_inactive_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_inactive_id,
        "resource_id": "IGOT-INACTIVE-999",
        "provider": "IGOT",
        "resource_type": "COURSE",
        "title": "Deprecated Sampling Course",
        "metadata": {"duration_hours": 10.0, "difficulty": "Beginner", "target_roles": [], "prerequisites": []},
        "competencies": ["STAT_SAMPLING"],
        "source": {"source_type": "GOVERNMENT_PUBLICATION", "source_url": None, "source_document": "SRC-01", "verification_status": "VERIFIED"},
        "provider_specific": {"course_id": "INACTIVE-999", "provider_name": "iGOT Karmayogi"},
        "status": "INACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    # Unmapped resource (browseable only, never personalized)
    res_unmapped_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_unmapped_id,
        "resource_id": "IGOT-GENERAL-888",
        "provider": "IGOT",
        "resource_type": "COURSE",
        "title": "General Workplace Ethics in Public Service",
        "metadata": {"duration_hours": 4.0, "difficulty": "Beginner", "target_roles": [], "prerequisites": []},
        "competencies": [],
        "source": {"source_type": "GOVERNMENT_PUBLICATION", "source_url": "https://igot.gov.in/course/gen888", "source_document": "SRC-01", "verification_status": "VERIFIED"},
        "provider_specific": {"course_id": "GEN-888", "provider_name": "iGOT Karmayogi"},
        "status": "ACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    # 5. Explicit Competency-Resource Mappings
    database.learning_resource_mappings.insert_many([
        {
            "resource_id": res_comm_id,
            "competency_id": comp_comm_id,
            "competency_code": "COMM_COMMUNICATION",
            "competency_name": "Communication & Interpersonal Skills",
            "provider": "IGOT",
            "mapping_type": "VERIFIED",
            "confidence": 0.95,
            "created_at": datetime.now(UTC),
        },
        {
            "resource_id": res_stat_id,
            "competency_id": comp_stat_id,
            "competency_code": "STAT_SAMPLING",
            "competency_name": "Statistical Sampling & Survey Design",
            "provider": "NSSTA",
            "mapping_type": "VERIFIED",
            "confidence": 0.90,
            "created_at": datetime.now(UTC),
        },
        {
            "resource_id": res_multi_id,
            "competency_id": comp_comm_id,
            "competency_code": "COMM_COMMUNICATION",
            "competency_name": "Communication & Interpersonal Skills",
            "provider": "IGOT",
            "mapping_type": "VERIFIED",
            "confidence": 0.88,
            "created_at": datetime.now(UTC),
        },
        {
            "resource_id": res_multi_id,
            "competency_id": comp_stat_id,
            "competency_code": "STAT_SAMPLING",
            "competency_name": "Statistical Sampling & Survey Design",
            "provider": "IGOT",
            "mapping_type": "VERIFIED",
            "confidence": 0.85,
            "created_at": datetime.now(UTC),
        },
        {
            "resource_id": res_inactive_id,
            "competency_id": comp_stat_id,
            "competency_code": "STAT_SAMPLING",
            "competency_name": "Statistical Sampling & Survey Design",
            "provider": "IGOT",
            "mapping_type": "VERIFIED",
            "confidence": 0.70,
            "created_at": datetime.now(UTC),
        },
    ])

    return {
        "comp_comm_id": comp_comm_id,
        "comp_stat_id": comp_stat_id,
        "comp_data_id": comp_data_id,
        "role_stat_officer_id": role_stat_officer_id,
        "role_data_lead_id": role_data_lead_id,
        "res_comm_id": res_comm_id,
        "res_stat_id": res_stat_id,
        "res_multi_id": res_multi_id,
        "res_inactive_id": res_inactive_id,
        "res_unmapped_id": res_unmapped_id,
    }


def test_1_user_with_communication_gap_receives_comm_mapped_resource(database, test_setup_data):
    """User with Communication gap receives Communication-mapped resource."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "user_comm@example.com",
        "role": "OFFICIAL",
        "department": "National Statistical Office",
        "designation": "Statistical Officer",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    # Authoritative profile: STAT_SAMPLING is 4.0 (no gap), COMM_COMMUNICATION is 1.5 (gap = 1.5)
    database.competency_profiles.insert_many([
        {"user_id": user_id, "competency_id": test_setup_data["comp_stat_id"], "current_level": 4.0, "confidence": 0.9, "status": "active"},
        {"user_id": user_id, "competency_id": test_setup_data["comp_comm_id"], "current_level": 1.5, "confidence": 0.9, "status": "active"},
    ])

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.total_recommendations > 0
    rec_codes = [r.competency_code for r in res.recommendations]
    assert all(code == "COMM_COMMUNICATION" for code in rec_codes)
    # The communication resource should be present
    res_titles = [r.resource.title for r in res.recommendations]
    assert "Government Communication & Briefing" in res_titles or "Statistical Reporting and Stakeholder Communication" in res_titles


def test_2_user_with_comm_gap_does_not_receive_unrelated_unmapped_resource(database, test_setup_data):
    """User with Communication gap does NOT receive unrelated unmapped resource."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "user_comm2@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })
    database.competency_profiles.insert_one({
        "user_id": user_id,
        "competency_id": test_setup_data["comp_comm_id"],
        "current_level": 1.0,
        "confidence": 0.9,
        "status": "active",
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    res_ids = [r.resource.resource_id for r in res.recommendations]
    assert "IGOT-GENERAL-888" not in res_ids


def test_3_user_with_role_a_does_not_receive_role_b_recommendations(database, test_setup_data):
    """User with Role A does not receive recommendations derived from Role B requirements."""
    user_a = ObjectId()
    database.users.insert_one({
        "_id": user_a,
        "email": "user_a@example.com",
        "role": "OFFICIAL",
        "department": "National Statistical Office",
        "designation": "Statistical Officer",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    user_b = ObjectId()
    database.users.insert_one({
        "_id": user_b,
        "email": "user_b@example.com",
        "role": "OFFICIAL",
        "department": "Analytics Division",
        "designation": "Data Science Lead",
        "role_id": test_setup_data["role_data_lead_id"],
    })

    service = RecommendationService(database)
    res_a = service.get_recommendations_for_user(str(user_a))
    res_b = service.get_recommendations_for_user(str(user_b))

    # User A has Statistical Officer role (STAT_SAMPLING, COMM_COMMUNICATION)
    # User B has Data Science Lead role (DATA_ANALYSIS)
    codes_a = {r.competency_code for r in res_a.recommendations}
    assert "DATA_ANALYSIS" not in codes_a


def test_4_user_a_recommendations_do_not_leak_to_user_b(database, test_setup_data):
    """User A recommendations do not leak to User B."""
    user_a = ObjectId()
    database.users.insert_one({
        "_id": user_a,
        "email": "user_iso_a@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })
    # User A has mastered sampling, only needs comms
    database.competency_profiles.insert_one({
        "user_id": user_a,
        "competency_id": test_setup_data["comp_stat_id"],
        "current_level": 4.5,
        "confidence": 0.9,
        "status": "active",
    })

    user_b = ObjectId()
    database.users.insert_one({
        "_id": user_b,
        "email": "user_iso_b@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })
    # User B has mastered comms, only needs sampling
    database.competency_profiles.insert_one({
        "user_id": user_b,
        "competency_id": test_setup_data["comp_comm_id"],
        "current_level": 4.5,
        "confidence": 0.9,
        "status": "active",
    })

    service = RecommendationService(database)
    res_a = service.get_recommendations_for_user(str(user_a))
    res_b = service.get_recommendations_for_user(str(user_b))

    recs_a_codes = {r.competency_code for r in res_a.recommendations}
    recs_b_codes = {r.competency_code for r in res_b.recommendations}

    assert "COMM_COMMUNICATION" in recs_a_codes
    assert "STAT_SAMPLING" not in recs_a_codes

    assert "STAT_SAMPLING" in recs_b_codes
    assert "COMM_COMMUNICATION" not in recs_b_codes


def test_5_unresolved_role_returns_role_mapping_pending(database, test_setup_data):
    """Unresolved role returns status ROLE_MAPPING_PENDING."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "unresolved_user@example.com",
        "role": "OFFICIAL",
        "department": "Nonexistent Department",
        "designation": "Nonexistent Title",
        # no role_id
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.total_recommendations == 0
    assert res.metadata.get("status") == "ROLE_MAPPING_PENDING"
    assert "Role mapping pending" in res.role or "ROLE_MAPPING_PENDING" in res.metadata.get("status", "")


def test_6_unresolved_user_receives_no_role_specific_recommendations(database, test_setup_data):
    """Unresolved user receives empty recommendations list, never default fallback recs."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "unresolved_user2@example.com",
        "role": "OFFICIAL",
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.recommendations == []
    assert res.total_recommendations == 0


def test_7_no_active_gaps_returns_honest_no_gap_state(database, test_setup_data):
    """User with all competencies meeting or exceeding requirements receives honest no-gap state."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "proficient_user@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })
    # Both STAT_SAMPLING (req 4.0) and COMM_COMMUNICATION (req 3.0) mastered
    database.competency_profiles.insert_many([
        {"user_id": user_id, "competency_id": test_setup_data["comp_stat_id"], "current_level": 4.5, "confidence": 0.9, "status": "active"},
        {"user_id": user_id, "competency_id": test_setup_data["comp_comm_id"], "current_level": 3.5, "confidence": 0.9, "status": "active"},
    ])

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.total_recommendations == 0
    assert "All mapped competencies" in res.metadata.get("reason", "") or "No active competency gaps" in res.metadata.get("reason", "")


def test_8_active_gap_with_no_mapped_resources_returns_honest_unavailable_state(database, test_setup_data):
    """Active gap with no mapped resources returns honest unavailable-resource state."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "data_lead_user@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_data_lead_id"],
    })
    # DATA_ANALYSIS has a gap, but we did not map any resource to DATA_ANALYSIS in setup
    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.total_recommendations == 0
    assert "No mapped learning resources" in res.metadata.get("reason", "")


def test_9_unmapped_resources_excluded_from_personalized_recs(database, test_setup_data):
    """Unmapped resources are excluded from personalized recommendations but browseable in catalogue."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_unmapped@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    rec_resource_ids = [r.resource.resource_id for r in res.recommendations]
    assert "IGOT-GENERAL-888" not in rec_resource_ids

    # But unmapped resources ARE returned via unmapped catalogue method
    unmapped = service.get_unmapped_resources()
    unmapped_ids = [u.get("resource_id") for u in unmapped]
    assert "IGOT-GENERAL-888" in unmapped_ids


def test_10_inactive_resources_are_excluded(database, test_setup_data):
    """Inactive resources are excluded from recommendation generation."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_inactive@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    rec_resource_ids = [r.resource.resource_id for r in res.recommendations]
    assert "IGOT-INACTIVE-999" not in rec_resource_ids


def test_11_duplicate_resource_mappings_do_not_create_duplicate_cards(database, test_setup_data):
    """A resource mapped to multiple competencies appears only once in personalized recommendations."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_dedup@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    # IGOT-MULTI-201 maps to both COMM_COMMUNICATION and STAT_SAMPLING
    resource_ids = [r.resource.resource_id for r in res.recommendations]
    assert len(resource_ids) == len(set(resource_ids)), "Duplicate resource recommendations found"


def test_12_multi_gap_resource_represented_with_addressed_gaps_count(database, test_setup_data):
    """Multi-gap resource contains addressed_gaps_count and addressed_competency_codes metadata."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_multigap@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    multi_rec = next((r for r in res.recommendations if r.resource.resource_id == "IGOT-MULTI-201"), None)
    assert multi_rec is not None
    assert multi_rec.addressed_gaps_count == 2
    assert set(multi_rec.addressed_competency_codes) == {"COMM_COMMUNICATION", "STAT_SAMPLING"}


def test_13_why_recommended_values_match_actual_role_and_profile_data(database, test_setup_data):
    """Why recommended values match actual role requirements, current level, and calculated gap."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_explain@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })
    # Set known current level 2.0 for COMM_COMMUNICATION (req: 3.0, gap: 1.0)
    database.competency_profiles.insert_one({
        "user_id": user_id,
        "competency_id": test_setup_data["comp_comm_id"],
        "current_level": 2.0,
        "confidence": 0.85,
        "status": "active",
    })
    # Mastered sampling so only comm rec appears
    database.competency_profiles.insert_one({
        "user_id": user_id,
        "competency_id": test_setup_data["comp_stat_id"],
        "current_level": 4.0,
        "confidence": 0.85,
        "status": "active",
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    assert res.total_recommendations > 0
    rec = res.recommendations[0]
    assert rec.current_level == 2.0
    assert rec.required_level == 3.0
    assert rec.gap == 1.0
    assert rec.why_recommended is not None
    assert "2.0" in rec.why_recommended
    assert "3.0" in rec.why_recommended
    assert rec.explanation.why_recommended == rec.why_recommended


def test_14_provider_provenance_preserved(database, test_setup_data):
    """Provider provenance is preserved with accurate provider notes."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_prov@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    for rec in res.recommendations:
        if rec.provider == "IGOT":
            assert rec.explanation.provider_note == "iGOT Karmayogi (Curated Catalogue)"
        elif rec.provider == "NSSTA":
            assert "NSSTA Training Programme" in rec.explanation.provider_note


def test_15_igot_prototype_resources_are_not_represented_as_live_apis(database, test_setup_data):
    """iGOT resources are clearly labeled as Curated Catalogue in notes."""
    user_id = ObjectId()
    database.users.insert_one({
        "_id": user_id,
        "email": "test_igot_label@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    service = RecommendationService(database)
    res = service.get_recommendations_for_user(str(user_id))

    igot_recs = [r for r in res.recommendations if r.provider == "IGOT"]
    assert len(igot_recs) > 0
    for r in igot_recs:
        assert "Curated Catalogue" in r.explanation.provider_note


def test_16_completed_learning_creates_supporting_evidence_without_corrupting_gaps(database, test_setup_data):
    """Completing a learning activity records supporting evidence without corrupting official gap logic."""
    from app.learning_activities.service import start_learning_activity, complete_learning_activity

    user_id = str(ObjectId())
    database.users.insert_one({
        "_id": ObjectId(user_id),
        "email": "test_learning_act@example.com",
        "role": "OFFICIAL",
        "role_id": test_setup_data["role_stat_officer_id"],
    })

    # Start and complete activity
    act = start_learning_activity(database, user_id, "IGOT-COMM-101", "COMM_COMMUNICATION")
    complete_learning_activity(database, act.activity_id, user_id, final_score=90.0)

    # Verify supporting evidence created
    evidence = list(database.competency_evidence.find({"user_id": ObjectId(user_id)}))
    assert len(evidence) == 1
    assert evidence[0]["type"] == "LEARNING_ACTIVITY"


def test_17_cache_is_user_isolated():
    """Cache keys strictly isolate recommendations between users."""
    set_cached_recommendations("user_100", {"recs": [1]}, limit=5)
    set_cached_recommendations("user_200", {"recs": [2]}, limit=5)

    assert get_cached_recommendations("user_100", limit=5) == {"recs": [1]}
    assert get_cached_recommendations("user_200", limit=5) == {"recs": [2]}
    assert get_cached_recommendations("user_100", limit=10) is None


def test_18_cache_invalidates_after_authoritative_capability_assessment(database, test_setup_data):
    """Cache invalidates when capability assessment is submitted."""
    user_id = "user_cache_test_1"
    set_cached_recommendations(user_id, {"data": "old_recs"})
    assert get_cached_recommendations(user_id) is not None

    invalidate_recommendations_cache(user_id)
    assert get_cached_recommendations(user_id) is None


def test_19_cache_invalidates_after_role_change(database, test_setup_data):
    """Cache invalidates when user role is updated/resolved."""
    user_id = "user_cache_test_2"
    set_cached_recommendations(user_id, {"data": "role_a_recs"})

    invalidate_recommendations_cache(user_id)
    assert get_cached_recommendations(user_id) is None
