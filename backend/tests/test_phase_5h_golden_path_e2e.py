"""Phase 5H: Complete End-to-End Golden-Path Lifecycle Test for SIH Production Readiness.

Verifies the complete closed-loop lifecycle:
OFFICIAL
  -> Explicit Role Resolution
  -> Role Competency Requirements
  -> Formal Baseline Assessment
  -> Authoritative Competency Profile Mutation
  -> Skill Gap Calculation
  -> Personalized Recommendation with Grounded Explainability
  -> Learning Activity Start & Completion
  -> Supporting Evidence Recording (Preserving Authoritative Profile)
  -> Formal Capability Reassessment
  -> Authoritative Capability Level Increase
  -> Skill Gap Closure (NO_GAP)
  -> Recommendation Removal & Honest No-Gap Message
  -> Immutable Audit Trail & Historical Evidence Preservation
"""

from datetime import datetime, UTC
from bson import ObjectId
import pytest

from app.auth.security import create_access_token
from app.core.config import get_settings
from app.capability_assessments.models import CapabilityAssessmentStatus
from app.capability_assessments import service as cap_service
from app.capability_assessments.schemas import CapabilityAssessmentCreateRequest, CapabilityAssessmentSubmitRequest
from app.learning_resources.service import RecommendationService
from app.learning_activities.service import start_learning_activity, complete_learning_activity
from app.skill_gaps import service as gaps_service


@pytest.fixture
def golden_path_data(database):
    """Setup complete role, competency, question bank, mappings, and resources."""
    # 1. Competency
    comp_stat_id = ObjectId()
    database.competencies.insert_one({
        "_id": comp_stat_id,
        "code": "STAT_SAMPLING",
        "name": "Statistical Sampling & Survey Design",
        "domain": "Statistical Domain",
        "description": "Sampling theory and survey design",
        "level_definitions": {
            "1": "Aware",
            "2": "Basic",
            "3": "Intermediate",
            "4": "Advanced",
            "5": "Expert",
        },
        "framework_status": "official",
    })

    # 2. Role & Requirements
    role_stat_id = ObjectId()
    database.roles.insert_one({
        "_id": role_stat_id,
        "role_code": "STATISTICAL_OFFICER",
        "role_name": "Statistical Officer",
        "description": "MoSPI Statistical Officer",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "designations": ["Statistical Officer"],
        "status": "active",
    })

    database.role_requirements.insert_one({
        "role_id": role_stat_id,
        "competency_id": comp_stat_id,
        "required_level": 4.0,
        "priority": "HIGH",
        "importance": 0.85,
    })

    # 3. Explicit Role Mapping
    database.role_mappings.insert_one({
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "designation": "Statistical Officer",
        "role_id": role_stat_id,
        "status": "ACTIVE",
        "mapping_type": "EXACT",
        "created_at": datetime.now(UTC),
    })

    # 4. Question Bank for STAT_SAMPLING
    q1_id = ObjectId()
    q2_id = ObjectId()
    database.question_bank.insert_many([
        {
            "_id": q1_id,
            "question_id": "STAT_Q1",
            "competency_code": "STAT_SAMPLING",
            "question_type": "MCQ",
            "question_text": "What is stratified random sampling?",
            "options": ["Dividing population into strata", "Selecting purely at random", "Convenience sampling", "None of above"],
            "correct_answer": "Dividing population into strata",
            "difficulty": "Intermediate",
            "weight": 1.0,
            "status": "ACTIVE",
        },
        {
            "_id": q2_id,
            "question_id": "STAT_Q2",
            "competency_code": "STAT_SAMPLING",
            "question_type": "MCQ",
            "question_text": "What characterizes cluster sampling?",
            "options": ["Selecting intact groups", "Selecting every kth element", "Voluntary response", "Self-selection"],
            "correct_answer": "Selecting intact groups",
            "difficulty": "Advanced",
            "weight": 1.0,
            "status": "ACTIVE",
        },
    ])

    # 5. Assessment Configuration
    database.assessment_configurations.insert_one({
        "competency_code": "STAT_SAMPLING",
        "assessment_type": "CAPABILITY",
        "total_questions": 2,
        "passing_percentage": 60.0,
        "time_limit_minutes": 30,
        "question_ids": [str(q1_id), str(q2_id)],
        "status": "ACTIVE",
    })

    # 6. Learning Resource & Explicit Mapping
    res_sampling_id = ObjectId()
    database.learning_resources.insert_one({
        "_id": res_sampling_id,
        "resource_id": "NSSTA-SAMPLING-MASTERY",
        "provider": "NSSTA",
        "resource_type": "TRAINING_PROGRAMME",
        "title": "Comprehensive Survey Sampling and Methodology",
        "metadata": {
            "duration_hours": 20.0,
            "difficulty": "Advanced",
            "target_roles": ["Statistical Officer"],
            "prerequisites": [],
        },
        "competencies": ["STAT_SAMPLING"],
        "source": {
            "source_type": "GOVERNMENT_PUBLICATION",
            "source_url": "https://mospi.gov.in/nssta",
            "source_document": "SRC-05",
            "verification_status": "VERIFIED",
        },
        "provider_specific": {
            "course_id": None,
            "programme_id": "PROG-SAMPLING-01",
            "provider_name": "NSSTA",
        },
        "status": "ACTIVE",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    })

    database.learning_resource_mappings.insert_one({
        "resource_id": res_sampling_id,
        "competency_id": comp_stat_id,
        "competency_code": "STAT_SAMPLING",
        "competency_name": "Statistical Sampling & Survey Design",
        "provider": "NSSTA",
        "mapping_type": "VERIFIED",
        "confidence": 0.95,
        "created_at": datetime.now(UTC),
    })

    return {
        "comp_stat_id": comp_stat_id,
        "role_stat_id": role_stat_id,
        "res_sampling_id": res_sampling_id,
        "q1_id": q1_id,
        "q2_id": q2_id,
    }


def test_complete_golden_path_closed_loop_lifecycle(database, golden_path_data):
    """
    Complete Golden-Path E2E Test:
    User -> Resolution -> Baseline Assessment -> Gaps -> Recommendation ->
    Learning Activity -> Supporting Evidence -> Reassessment -> Authoritative Update -> Gap Closure
    """
    settings = get_settings()
    user_oid = ObjectId()
    user_id = str(user_oid)

    # 1. User Registration & Explicit Role Resolution
    database.users.insert_one({
        "_id": user_oid,
        "email": "golden_path_official@shikshasetu.gov.in",
        "full_name": "Golden Path Official",
        "department": "Ministry of Statistics & Programme Implementation (MoSPI)",
        "designation": "Statistical Officer",
        "role_id": golden_path_data["role_stat_id"],
        "access_role": "OFFICIAL",
        "status": "active",
    })

    token = create_access_token(user_id, settings)
    assert token is not None

    # Verify initial skill gaps before formal assessment
    gap_resp_0 = gaps_service.calculate_skill_gaps(database, user_id)
    assert gap_resp_0.role["name"] == "Statistical Officer"
    assert len(gap_resp_0.gaps) == 1
    assert gap_resp_0.gaps[0].competency_code == "STAT_SAMPLING"
    assert gap_resp_0.gaps[0].required_level == 4.0
    assert gap_resp_0.gaps[0].current_level is None  # Unassessed baseline
    assert gap_resp_0.gaps[0].gap == 4.0

    # 2. Formal Baseline Capability Assessment (Official answers 1/2 correct = 50% => normalized level 2.5)
    created_assessment = cap_service.create_capability_assessment(database, user_id, "STAT_SAMPLING")
    assessment_id = created_assessment["id"]
    assert created_assessment["status"] == CapabilityAssessmentStatus.IN_PROGRESS

    submit_answers_1 = [
        {"question_id": "STAT_Q1", "selected_answer": "Dividing population into strata"},  # Correct
        {"question_id": "STAT_Q2", "selected_answer": "Voluntary response"},               # Incorrect
    ]
    submit_res_1 = cap_service.submit_capability_assessment(database, user_id, assessment_id, submit_answers_1)
    assert submit_res_1["status"] == CapabilityAssessmentStatus.SUBMITTED
    assert submit_res_1["percentage"] == 0.5
    baseline_score = submit_res_1["competency_results"][0]["score"]
    assert 2.0 <= baseline_score <= 3.0

    # Verify Authoritative Evidence is recorded
    evidence_list = list(database.competency_evidence.find({"user_id": user_oid}))
    assert len(evidence_list) == 1
    assert evidence_list[0]["authority"] == "AUTHORITATIVE"
    assert evidence_list[0]["evidence_type"] == "KNOWLEDGE_TEST"

    # Verify Authoritative Profile is updated
    profile = database.competency_profiles.find_one({"user_id": user_oid, "competency_id": golden_path_data["comp_stat_id"]})
    assert profile is not None
    assert profile["current_level"] == baseline_score

    # 3. Calculate Skill Gaps after Baseline Assessment
    gap_resp_1 = gaps_service.calculate_skill_gaps(database, user_id)
    gap_item = gap_resp_1.gaps[0]
    assert gap_item.competency_code == "STAT_SAMPLING"
    assert gap_item.current_level == baseline_score
    assert gap_item.gap > 0.0
    assert gap_item.gap_category in ("HIGH", "CRITICAL", "MEDIUM")

    # 4. Generate Personalized Recommendations
    rec_service = RecommendationService(database)
    rec_res_1 = rec_service.get_recommendations_for_user(user_id)
    assert rec_res_1.total_recommendations == 1
    rec_1 = rec_res_1.recommendations[0]
    assert rec_1.resource.resource_id == "NSSTA-SAMPLING-MASTERY"
    assert rec_1.competency_code == "STAT_SAMPLING"
    assert rec_1.current_level == baseline_score
    assert rec_1.required_level == 4.0
    assert rec_1.why_recommended is not None
    assert "Statistical Sampling & Survey Design" in rec_1.why_recommended
    assert "NSSTA" in rec_1.why_recommended

    # 5. Start and Complete Learning Activity
    learning_act = start_learning_activity(database, user_id, "NSSTA-SAMPLING-MASTERY", "STAT_SAMPLING")
    assert learning_act.status.value == "in_progress"

    complete_learning_activity(database, learning_act.activity_id, user_id, final_score=95.0, notes="Mastered sampling formulas")

    # Invariant: Learning activity completion creates SUPPORTING evidence only (does not alter authoritative capability)
    all_evidence = list(database.competency_evidence.find({"user_id": user_oid}))
    assert len(all_evidence) == 2
    supporting_evidence = next((e for e in all_evidence if e.get("type") == "LEARNING_ACTIVITY"), None)
    assert supporting_evidence is not None
    assert supporting_evidence["confidence"] == 0.3  # Supporting only

    # Authoritative profile remains at baseline level
    profile_after_learning = database.competency_profiles.find_one({"user_id": user_oid, "competency_id": golden_path_data["comp_stat_id"]})
    assert profile_after_learning["current_level"] == baseline_score

    # 6. Formal Reassessment (Official scores 100% => normalized level 5.0)
    reassessment = cap_service.create_capability_assessment(database, user_id, "STAT_SAMPLING")
    reassessment_id = reassessment["id"]

    submit_answers_2 = [
        {"question_id": "STAT_Q1", "selected_answer": "Dividing population into strata"},  # Correct
        {"question_id": "STAT_Q2", "selected_answer": "Selecting intact groups"},          # Correct
    ]
    submit_res_2 = cap_service.submit_capability_assessment(database, user_id, reassessment_id, submit_answers_2)
    assert submit_res_2["status"] == CapabilityAssessmentStatus.SUBMITTED
    assert submit_res_2["percentage"] == 1.0
    reassessed_score = submit_res_2["competency_results"][0]["score"]
    assert reassessed_score >= 4.0

    # 7. Verify Gap Closure
    gap_resp_2 = gaps_service.calculate_skill_gaps(database, user_id)
    final_gap_item = gap_resp_2.gaps[0]
    assert final_gap_item.current_level >= 4.0
    assert final_gap_item.gap <= 0.0
    assert final_gap_item.gap_category == "NO_GAP"

    # 8. Verify Recommendation Disappears (Honest No-Gap State)
    rec_res_2 = rec_service.get_recommendations_for_user(user_id)
    assert rec_res_2.total_recommendations == 0
    assert "All mapped competencies" in rec_res_2.metadata.get("reason", "")

    # 9. Verify Append-Only Evidence Immutability & Complete Audit Trail
    final_evidence_trail = list(database.competency_evidence.find({"user_id": user_oid}))
    assert len(final_evidence_trail) == 3
    auth_evidence = [e for e in final_evidence_trail if e.get("authority") == "AUTHORITATIVE" or e.get("evidence_type") == "KNOWLEDGE_TEST"]
    supp_evidence = [e for e in final_evidence_trail if e.get("type") == "LEARNING_ACTIVITY"]
    assert len(auth_evidence) == 2
    assert len(supp_evidence) == 1
    assert supp_evidence[0]["confidence"] == 0.3
