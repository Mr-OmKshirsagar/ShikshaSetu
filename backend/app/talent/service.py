"""
Government Talent & Opportunity Network - Business Logic
"""

from datetime import datetime
from typing import List, Optional, Tuple

from pymongo.database import Database
from bson import ObjectId

from app.talent.schemas import (
    TalentProfile,
    VerifiedCompetency,
    TalentPreferences,
    TalentProfileReadiness,
    MatchExplanation,
    MatchedCompetency,
    UserOpportunity,
    GovernmentOpportunity,
)
from app.talent.models import VisibilityLevel, OpportunityStatus


def _object_id(value: str) -> Optional[ObjectId]:
    """Convert string to ObjectId"""
    return ObjectId(value) if ObjectId.is_valid(value) else None


# ─── Talent Profile Construction ─────────────────────────────────────────────


def build_talent_profile(database: Database, user_id: str) -> Optional[TalentProfile]:
    """
    Build talent profile from existing verified ShikshaSetu data.
    Does NOT invent information - only uses database records.
    """
    user_oid = _object_id(user_id)
    if not user_oid:
        return None
    
    # Get user
    user = database.users.find_one({"_id": user_oid, "status": "active"})
    if not user:
        return None
    
    # Get user's role
    role = None
    role_name = None
    if user.get("role_id"):
        role_oid = _object_id(str(user["role_id"]))
        if role_oid:
            role = database.roles.find_one({"_id": role_oid})
            if role:
                role_name = role.get("role_name")
    
    # Fetch user competency profiles (supporting both active and standard profiles)
    competency_profiles = []
    if hasattr(database, "competency_profiles"):
        competency_profiles = list(database.competency_profiles.find({
            "user_id": user_oid
        }))
    
    # Build verified competencies
    verified_competencies = []
    total_confidence = 0.0

    raw_comp_ids = [p.get("competency_id") for p in competency_profiles if p.get("competency_id")]
    search_ids = []
    for cid in raw_comp_ids:
        search_ids.append(cid)
        if isinstance(cid, str):
            oid = _object_id(cid)
            if oid:
                search_ids.append(oid)
        elif isinstance(cid, ObjectId):
            search_ids.append(str(cid))

    # Batch fetch competencies
    competencies_map = {}
    if hasattr(database, "competencies") and search_ids:
        for c in database.competencies.find({"_id": {"$in": search_ids}}):
            competencies_map[c["_id"]] = c
            competencies_map[str(c["_id"])] = c

    # Batch fetch role requirements
    role_req_map = {}
    if role and hasattr(database, "role_requirements") and search_ids:
        for rr in database.role_requirements.find({
            "role_id": role["_id"],
            "competency_id": {"$in": search_ids}
        }):
            role_req_map[rr.get("competency_id")] = rr.get("required_level")
            role_req_map[str(rr.get("competency_id"))] = rr.get("required_level")

    for profile in competency_profiles:
        comp_id = profile.get("competency_id")
        if not comp_id:
            continue
        
        # Get competency details from batched map
        competency = competencies_map.get(comp_id) or competencies_map.get(str(comp_id))
        if not competency:
            continue
        
        # Get evidence count
        evidence_count = 0
        if hasattr(database, "competency_evidence"):
            evidence_count = database.competency_evidence.count_documents({
                "user_id": user_oid,
                "competency_id": comp_id
            })
        
        # Get required level from batched role requirements
        required_level = role_req_map.get(comp_id) or role_req_map.get(str(comp_id))
        
        raw_level = profile.get("current_level")
        if raw_level is None:
            raw_level = profile.get("level")
        current_level = float(raw_level or 0.0)
        
        raw_conf = profile.get("confidence")
        confidence = float(raw_conf or 0.0)
        total_confidence += confidence
        
        domain = competency.get("domain", "STATISTICAL")
        verified_competencies.append(VerifiedCompetency(
            competency_id=str(comp_id),
            competency_code=competency.get("code", ""),
            competency_name=competency.get("name", ""),
            domain=domain,
            current_level=current_level,
            required_level=required_level,
            confidence=confidence,
            evidence_count=evidence_count,
            verification_status="VERIFIED" if confidence >= 0.70 or evidence_count > 0 else "PARTIALLY_VERIFIED"
        ))
    
    # Calculate average confidence
    average_confidence = (
        total_confidence / len(competency_profiles)
        if competency_profiles else 0.0
    )
    
    # Real trainer experience & statistics from verified database
    trainer_experience = False
    training_materials_count = 0
    quizzes_authored_count = 0
    learners_trained_count = 0
    
    if hasattr(database, "learning_materials"):
        training_materials_count = database.learning_materials.count_documents({
            "$or": [{"uploaded_by": user_oid}, {"uploaded_by": str(user_oid)}]
        })
    
    if hasattr(database, "quizzes"):
        quizzes_authored_count = database.quizzes.count_documents({
            "$or": [{"trainer_id": user_oid}, {"trainer_id": str(user_oid)}]
        })
        if quizzes_authored_count > 0 and hasattr(database, "quiz_attempts"):
            trainer_quizzes = list(database.quizzes.find(
                {"$or": [{"trainer_id": user_oid}, {"trainer_id": str(user_oid)}]},
                {"_id": 1}
            ))
            tq_ids = [q["_id"] for q in trainer_quizzes] + [str(q["_id"]) for q in trainer_quizzes]
            learners_trained_count = len(database.quiz_attempts.distinct(
                "user_id", {"quiz_id": {"$in": tq_ids}}
            ))
            
    trainer_experience = (
        user.get("access_role") in ["TRAINER", "ADMIN"]
        or training_materials_count > 0
        or quizzes_authored_count > 0
    )
    
    # Completed learning activities
    completed_learning_count = 0
    if hasattr(database, "learning_activities"):
        completed_learning_count = database.learning_activities.count_documents({
            "user_id": user_oid,
            "status": "completed"
        })
        
    knowledge_domains = sorted(list({vc.domain for vc in verified_competencies if vc.domain}))
    
    # Get preferences
    preferences = None
    if hasattr(database, "talent_preferences"):
        prefs_doc = database.talent_preferences.find_one({"user_id": user_oid})
        if prefs_doc:
            preferences = TalentPreferences(
                user_id=str(user_oid),
                opt_in_enabled=prefs_doc.get("opt_in_enabled", False),
                visibility_level=prefs_doc.get("visibility_level", VisibilityLevel.PRIVATE),
                opportunity_types=prefs_doc.get("opportunity_types", []),
                available_for_opportunities=prefs_doc.get("available_for_opportunities", False),
                updated_at=prefs_doc.get("updated_at", datetime.utcnow())
            )
    
    # Default preferences if none saved (strictly Opt-In OFF and Private by default)
    if not preferences:
        preferences = TalentPreferences(
            user_id=str(user_oid),
            opt_in_enabled=False,
            visibility_level=VisibilityLevel.PRIVATE,
            opportunity_types=[],
            available_for_opportunities=False,
            updated_at=datetime.utcnow()
        )
    
    # Calculate profile readiness
    readiness = calculate_profile_readiness(
        has_role=role is not None or user.get("designation") is not None,
        competency_count=len(verified_competencies),
        average_confidence=average_confidence,
        has_evidence=any(vc.evidence_count > 0 for vc in verified_competencies) or average_confidence > 0.5
    )
    
    return TalentProfile(
        user_id=str(user_oid),
        full_name=user.get("full_name", ""),
        designation=user.get("designation", ""),
        department=user.get("department", ""),
        employee_id=user.get("employee_id", ""),
        role_id=str(role["_id"]) if role else None,
        role_name=role_name or user.get("role_name") or user.get("designation"),
        organization_id=user.get("organization_id"),
        organization_type=user.get("organization_type"),
        government_level=user.get("government_level"),
        state_ut=user.get("state_ut"),
        verified_competencies=verified_competencies,
        total_competencies=len(verified_competencies),
        average_confidence=average_confidence,
        years_experience=user.get("years_experience"),
        trainer_experience=trainer_experience,
        training_materials_count=training_materials_count,
        quizzes_authored_count=quizzes_authored_count,
        learners_trained_count=learners_trained_count,
        completed_learning_count=completed_learning_count,
        knowledge_domains=knowledge_domains,
        profile_readiness=readiness.overall_score,
        preferences=preferences
    )


def calculate_profile_readiness(
    has_role: bool,
    competency_count: int,
    average_confidence: float,
    has_evidence: bool
) -> TalentProfileReadiness:
    """Calculate talent profile readiness score"""
    score = 0.0
    
    # Has role/designation (20%)
    if has_role:
        score += 0.20
    
    # Has competencies (30%)
    if competency_count > 0:
        comp_score = min(competency_count / 5.0, 1.0) * 0.30
        score += comp_score
    
    # Average confidence (30%)
    score += average_confidence * 0.30
    
    # Has evidence / verification (20%)
    if has_evidence:
        score += 0.20
    
    return TalentProfileReadiness(
        overall_score=round(min(score, 1.0), 2),
        has_verified_competencies=competency_count > 0,
        has_role=has_role,
        has_evidence=has_evidence,
        competency_count=competency_count,
        average_confidence=round(average_confidence, 2)
    )


# ─── Opportunity Matching Engine ─────────────────────────────────────────────


def check_eligibility_and_match(
    database: Database,
    opportunity: dict,
    user_id: str,
    profile: Optional[TalentProfile] = None
) -> Tuple[bool, float, MatchExplanation]:
    """
    Deterministic eligibility check and scoring.
    
    HARD FILTERS:
    1. Opt-in enabled (User consent)
    2. Availability enabled
    3. User account is active
    4. Visibility level checks (PRIVATE / MY_DEPARTMENT / AUTHORIZED_DEPARTMENTS)
    5. Opportunity type preferences check
    6. Role / Designation requirements
    7. Minimum experience
    8. Competency requirements & minimum levels
    
    Returns:
        (eligible, match_score, explanation)
    """
    user_oid = _object_id(user_id)
    if not user_oid:
        return False, 0.0, None
    
    # Get talent profile (reuse provided profile to avoid redundant DB builds)
    if profile is None:
        profile = build_talent_profile(database, user_id)
    if not profile:
        return False, 0.0, None
    
    eligibility_reasons = []
    match_reasons = []
    matched_competencies = []
    missing_competencies = []
    
    # ── HARD FILTER 1: Opt-in check (Strict User Consent) ────────────────────
    if not profile.preferences or not profile.preferences.opt_in_enabled:
        return False, 0.0, MatchExplanation(
            eligible=False,
            match_score=0.0,
            matched_competencies=[],
            missing_competencies=[],
            eligibility_reasons=["User has not opted into opportunity discovery"],
            match_reasons=[],
            evidence_confidence=0.0
        )
    
    eligibility_reasons.append("✓ Opted into opportunity discovery")
    
    # ── HARD FILTER 2: Availability check ────────────────────────────────────
    if not profile.preferences.available_for_opportunities:
        return False, 0.0, MatchExplanation(
            eligible=False,
            match_score=0.0,
            matched_competencies=[],
            missing_competencies=[],
            eligibility_reasons=eligibility_reasons + ["User currently marked as unavailable for opportunities"],
            match_reasons=[],
            evidence_confidence=0.0
        )
    
    eligibility_reasons.append("✓ Available for eligible opportunities")
    
    # ── HARD FILTER 3: Visibility Tier & Department Isolation ────────────────
    visibility = profile.preferences.visibility_level
    if visibility == VisibilityLevel.PRIVATE:
        return False, 0.0, MatchExplanation(
            eligible=False,
            match_score=0.0,
            matched_competencies=[],
            missing_competencies=[],
            eligibility_reasons=eligibility_reasons + ["Talent profile visibility is restricted to Private"],
            match_reasons=[],
            evidence_confidence=0.0
        )
    
    opp_dept = opportunity.get("department_name") or opportunity.get("department") or ""
    user_dept = profile.department or ""
    
    if visibility == VisibilityLevel.MY_DEPARTMENT:
        if opp_dept and user_dept and opp_dept.lower().strip() != user_dept.lower().strip():
            return False, 0.0, MatchExplanation(
                eligible=False,
                match_score=0.0,
                matched_competencies=[],
                missing_competencies=[],
                eligibility_reasons=eligibility_reasons + [
                    f"Opportunity from outside department ('{opp_dept}'). Profile restricted to 'My Department Only'."
                ],
                match_reasons=[],
                evidence_confidence=profile.average_confidence
            )
        eligibility_reasons.append(f"✓ Department eligibility satisfied ({user_dept})")
    else:
        eligibility_reasons.append("✓ Authorized government department discovery enabled")
    
    # ── HARD FILTER 4: Opportunity Type Preferences ──────────────────────────
    opp_type = opportunity.get("opportunity_type")
    if profile.preferences.opportunity_types and opp_type:
        if opp_type not in profile.preferences.opportunity_types:
            return False, 0.0, MatchExplanation(
                eligible=False,
                match_score=0.0,
                matched_competencies=[],
                missing_competencies=[],
                eligibility_reasons=eligibility_reasons + [
                    f"Opportunity type '{opp_type}' is not in user's selected preferences"
                ],
                match_reasons=[],
                evidence_confidence=profile.average_confidence
            )
        eligibility_reasons.append(f"✓ Opportunity preference matches: {opp_type}")
    
    # ── HARD FILTER 5: Role requirements ──────────────────────────────────────
    eligible = True
    required_roles = opportunity.get("required_roles", [])
    if required_roles:
        candidate_role = (profile.role_name or "").lower().strip()
        candidate_desig = (profile.designation or "").lower().strip()
        has_role_match = any(
            req.lower().strip() in (candidate_role, candidate_desig)
            or candidate_role in req.lower()
            or candidate_desig in req.lower()
            for req in required_roles
        )
        if not has_role_match:
            eligible = False
            eligibility_reasons.append(f"Required role not met (needs one of: {', '.join(required_roles)})")
        else:
            eligibility_reasons.append(f"✓ Role requirement satisfied: {profile.role_name or profile.designation}")
    
    # ── HARD FILTER 6: Designation requirements ───────────────────────────────
    required_designations = opportunity.get("required_designations", [])
    if required_designations:
        candidate_desig = (profile.designation or "").lower().strip()
        has_desig_match = any(
            req.lower().strip() in candidate_desig or candidate_desig in req.lower().strip()
            for req in required_designations
        )
        if not has_desig_match:
            eligible = False
            eligibility_reasons.append(f"Required designation not met (needs one of: {', '.join(required_designations)})")
        else:
            eligibility_reasons.append(f"✓ Designation requirement satisfied: {profile.designation}")
    
    # ── HARD FILTER 7: Minimum experience ─────────────────────────────────────
    min_experience = opportunity.get("minimum_experience_years")
    if min_experience and profile.years_experience is not None:
        if profile.years_experience < min_experience:
            eligible = False
            eligibility_reasons.append(f"Minimum experience not met (requires {min_experience} years, has {profile.years_experience})")
        else:
            eligibility_reasons.append(f"✓ Experience requirement satisfied: {profile.years_experience} years")
    
    # ── HARD FILTER 8: Competency requirements & Minimum Levels ───────────────
    required_competencies = opportunity.get("required_competencies", [])
    competency_score = 0.0
    total_importance = 0.0
    
    for req in required_competencies:
        comp_code = req.get("competency_code") if isinstance(req, dict) else getattr(req, "competency_code", "")
        min_level = float(req.get("minimum_level", 1.0) if isinstance(req, dict) else getattr(req, "minimum_level", 1.0))
        importance = float(req.get("importance", 1.0) if isinstance(req, dict) else getattr(req, "importance", 1.0))
        total_importance += importance
        
        # Match candidate competency
        user_comp = next(
            (vc for vc in profile.verified_competencies if vc.competency_code.upper() == comp_code.upper()),
            None
        )
        
        if not user_comp:
            missing_competencies.append(comp_code)
            eligible = False
        elif user_comp.current_level < min_level:
            gap = round(min_level - user_comp.current_level, 2)
            matched_competencies.append(MatchedCompetency(
                competency_code=comp_code,
                competency_name=user_comp.competency_name,
                required_level=min_level,
                current_level=user_comp.current_level,
                gap=gap,
                meets_requirement=False
            ))
            eligible = False
        else:
            matched_competencies.append(MatchedCompetency(
                competency_code=comp_code,
                competency_name=user_comp.competency_name,
                required_level=min_level,
                current_level=user_comp.current_level,
                gap=0.0,
                meets_requirement=True
            ))
            level_score = min(user_comp.current_level / 5.0, 1.0)
            competency_score += level_score * importance
    
    if not eligible:
        reasons = list(eligibility_reasons)
        if missing_competencies:
            reasons.append(f"Missing required competencies: {', '.join(missing_competencies)}")
        unmet = [mc for mc in matched_competencies if not mc.meets_requirement]
        for mc in unmet:
            reasons.append(f"Competency below threshold: {mc.competency_name} (Current: {mc.current_level}, Required: {mc.required_level})")
            
        return False, 0.0, MatchExplanation(
            eligible=False,
            match_score=0.0,
            matched_competencies=matched_competencies,
            missing_competencies=missing_competencies,
            eligibility_reasons=reasons,
            match_reasons=[],
            evidence_confidence=profile.average_confidence
        )
    
    if required_competencies:
        eligibility_reasons.append(f"✓ All {len(required_competencies)} required competencies verified at or above threshold")
    
    # ── RELEVANCE SCORING (Only for ELIGIBLE candidates) ──────────────────────
    if total_importance > 0:
        competency_match_score = competency_score / total_importance
    else:
        competency_match_score = 1.0
    
    # Role relevance (10%)
    role_score = 0.10 if profile.role_name and required_roles else 0.05
    
    # Evidence confidence (20%)
    confidence_score = profile.average_confidence * 0.20
    
    # Experience match (10%)
    experience_score = 0.05
    if min_experience and profile.years_experience:
        experience_score = min(profile.years_experience / min_experience, 2.0) * 0.05
    
    # Trainer experience bonus (10% for trainer opportunities)
    trainer_bonus = 0.0
    if opportunity.get("opportunity_type") == "TRAINER" and profile.trainer_experience:
        trainer_bonus = 0.10
        match_reasons.append(f"✓ Verified trainer experience ({profile.training_materials_count} materials, {profile.quizzes_authored_count} quizzes)")
    
    match_score = round(
        (competency_match_score * 0.50) +
        role_score +
        confidence_score +
        experience_score +
        trainer_bonus,
        2
    )
    match_score = min(match_score, 1.0)
    
    # Build detailed explainability match reasons
    for mc in matched_competencies:
        match_reasons.append(f"✓ {mc.competency_name} — Level {mc.current_level:.1f} (Required: {mc.required_level:.1f})")
    
    match_reasons.append(f"✓ Evidence confidence: {profile.average_confidence:.0%}")
    if profile.years_experience:
        match_reasons.append(f"✓ {profile.years_experience} years relevant experience")
    if profile.department:
        match_reasons.append(f"✓ Department: {profile.department}")
    
    return True, match_score, MatchExplanation(
        eligible=True,
        match_score=match_score,
        matched_competencies=matched_competencies,
        missing_competencies=[],
        eligibility_reasons=eligibility_reasons,
        match_reasons=match_reasons,
        evidence_confidence=round(profile.average_confidence, 2)
    )


def match_opportunity_to_talent_pool(
    database: Database,
    opportunity_id: str
) -> List[dict]:
    """
    Match an opportunity to all eligible talent in the pool.
    Enforces opt-in and visibility boundaries.
    Returns list of matches with scores and explanations.
    """
    opp_oid = _object_id(opportunity_id)
    if not opp_oid:
        return []
    
    opportunity = database.government_opportunities.find_one({"_id": opp_oid})
    if not opportunity:
        return []
    
    # Get all opted-in users
    opted_in_prefs = []
    if hasattr(database, "talent_preferences"):
        opted_in_prefs = list(database.talent_preferences.find({
            "opt_in_enabled": True,
            "available_for_opportunities": True
        }))
    
    user_ids = [str(p["user_id"]) for p in opted_in_prefs]
    matches = []
    
    for uid in user_ids:
        u_profile = build_talent_profile(database, uid)
        if not u_profile:
            continue

        eligible, match_score, explanation = check_eligibility_and_match(
            database, opportunity, uid, profile=u_profile
        )
        
        if eligible:
            u_oid = _object_id(uid)
            user = database.users.find_one({"_id": u_oid}) if u_oid else None
            if user:
                u_readiness = u_profile.profile_readiness

                matches.append({
                    "user_id": uid,
                    "full_name": user.get("full_name", "Officer"),
                    "designation": user.get("designation", ""),
                    "department": user.get("department", ""),
                    "match_score": match_score,
                    "competency_match_count": len(explanation.matched_competencies) if explanation else 0,
                    "evidence_confidence": explanation.evidence_confidence if explanation else 0.0,
                    "eligible": True,
                    "profile_readiness": u_readiness,
                    "explanation": explanation.model_dump() if hasattr(explanation, "model_dump") else explanation.dict()
                })
    
    # Sort by match score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches


def get_user_eligible_opportunities(
    database: Database,
    user_id: str
) -> List[UserOpportunity]:
    """
    Find all published opportunities that the user is eligible for,
    along with transparent explainability.
    """
    if not hasattr(database, "government_opportunities"):
        return []
    
    published_opps = list(database.government_opportunities.find({
        "status": OpportunityStatus.PUBLISHED
    }).sort("created_at", -1))
    
    if not published_opps:
        return []

    # Build talent profile ONCE and reuse across all opportunity checks
    profile = build_talent_profile(database, user_id)
    if not profile:
        return []

    results = []
    for opp in published_opps:
        opp_id = str(opp["_id"])
        eligible, match_score, explanation = check_eligibility_and_match(
            database, opp, user_id, profile=profile
        )
        
        # Build GovernmentOpportunity schema
        opp_doc = dict(opp)
        opp_doc["id"] = opp_id
        if "_id" in opp_doc:
            del opp_doc["_id"]
        if "created_by" in opp_doc and isinstance(opp_doc["created_by"], ObjectId):
            opp_doc["created_by"] = str(opp_doc["created_by"])
            
        try:
            gov_opp = GovernmentOpportunity(**opp_doc)
            results.append(UserOpportunity(
                opportunity=gov_opp,
                match_explanation=explanation,
                is_eligible=eligible
            ))
        except Exception:
            continue
            
    # Sort eligible opportunities first, then by match score
    results.sort(
        key=lambda x: (
            1 if x.is_eligible else 0,
            x.match_explanation.match_score if x.match_explanation else 0.0
        ),
        reverse=True
    )
    return results
