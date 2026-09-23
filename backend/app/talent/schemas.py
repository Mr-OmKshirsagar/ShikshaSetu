"""
Government Talent & Opportunity Network - Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.talent.models import OpportunityType, OpportunityStatus, VisibilityLevel


# ─── Talent Preferences ──────────────────────────────────────────────────────


class TalentPreferences(BaseModel):
    """User's talent profile preferences"""
    user_id: str
    opt_in_enabled: bool = Field(default=False, description="Opted into opportunity discovery")
    visibility_level: VisibilityLevel = Field(default=VisibilityLevel.PRIVATE)
    opportunity_types: List[OpportunityType] = Field(default_factory=list)
    available_for_opportunities: bool = Field(default=False)
    updated_at: datetime


class TalentPreferencesUpdate(BaseModel):
    """Update talent preferences"""
    opt_in_enabled: Optional[bool] = None
    visibility_level: Optional[VisibilityLevel] = None
    opportunity_types: Optional[List[OpportunityType]] = None
    available_for_opportunities: Optional[bool] = None


# ─── Talent Profile ──────────────────────────────────────────────────────────


class VerifiedCompetency(BaseModel):
    """Verified competency information"""
    competency_id: str
    competency_code: str
    competency_name: str
    domain: Optional[str] = None
    current_level: float
    required_level: Optional[float] = None
    confidence: float
    evidence_count: int = 0
    verification_status: str = "VERIFIED"


class TalentProfile(BaseModel):
    """Derived government talent profile"""
    model_config = ConfigDict(from_attributes=True)
    
    # Identity
    user_id: str
    full_name: str
    designation: str
    department: str
    employee_id: str
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    
    # Organization
    organization_id: Optional[str] = None
    organization_type: Optional[str] = None
    government_level: Optional[str] = None
    state_ut: Optional[str] = None
    
    # Verified capabilities
    verified_competencies: List[VerifiedCompetency]
    total_competencies: int
    average_confidence: float
    
    # Professional experience
    years_experience: Optional[int] = None
    trainer_experience: bool = False
    training_materials_count: int = 0
    quizzes_authored_count: int = 0
    learners_trained_count: int = 0
    completed_learning_count: int = 0
    knowledge_domains: List[str] = Field(default_factory=list)
    
    # Profile completeness
    profile_readiness: float = Field(ge=0.0, le=1.0)
    
    # Preferences
    preferences: Optional[TalentPreferences] = None


class TalentProfileReadiness(BaseModel):
    """Profile readiness calculation"""
    overall_score: float = Field(ge=0.0, le=1.0)
    has_verified_competencies: bool
    has_role: bool
    has_evidence: bool
    competency_count: int
    average_confidence: float


# ─── Government Opportunity ──────────────────────────────────────────────────


class OpportunityRequirement(BaseModel):
    """Competency requirement for opportunity"""
    competency_code: str
    minimum_level: float = Field(ge=1.0, le=5.0)
    importance: float = Field(default=1.0, ge=0.0, le=1.0)


class GovernmentOpportunity(BaseModel):
    """Government opportunity model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    description: str
    
    # Department/Ministry
    department_id: Optional[str] = None
    department_name: str
    ministry_id: Optional[str] = None
    ministry_name: Optional[str] = None
    
    # Opportunity details
    opportunity_type: OpportunityType
    location: Optional[str] = None
    is_remote: bool = False
    
    # Requirements
    required_roles: List[str] = Field(default_factory=list)
    required_designations: List[str] = Field(default_factory=list)
    required_competencies: List[OpportunityRequirement] = Field(default_factory=list)
    minimum_experience_years: Optional[int] = None
    
    # Timeline
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None
    
    # Status
    status: OpportunityStatus = OpportunityStatus.DRAFT
    
    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None


class OpportunityCreate(BaseModel):
    """Create new opportunity"""
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    department_name: str = Field(min_length=1, max_length=200)
    ministry_name: Optional[str] = Field(None, max_length=200)
    opportunity_type: OpportunityType
    location: Optional[str] = Field(None, max_length=200)
    is_remote: bool = False
    required_roles: List[str] = Field(default_factory=list)
    required_designations: List[str] = Field(default_factory=list)
    required_competencies: List[OpportunityRequirement] = Field(default_factory=list)
    minimum_experience_years: Optional[int] = Field(None, ge=0, le=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None


class OpportunityUpdate(BaseModel):
    """Update existing opportunity"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    department_name: Optional[str] = Field(None, min_length=1, max_length=200)
    ministry_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    is_remote: Optional[bool] = None
    required_roles: Optional[List[str]] = None
    required_designations: Optional[List[str]] = None
    required_competencies: Optional[List[OpportunityRequirement]] = None
    minimum_experience_years: Optional[int] = Field(None, ge=0, le=50)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    application_deadline: Optional[datetime] = None


class OpportunityListResponse(BaseModel):
    """List of opportunities"""
    total: int
    opportunities: List[GovernmentOpportunity]


# ─── Opportunity Matching ────────────────────────────────────────────────────


class MatchedCompetency(BaseModel):
    """Matched competency details"""
    competency_code: str
    competency_name: str
    required_level: float
    current_level: float
    gap: float
    meets_requirement: bool


class MatchExplanation(BaseModel):
    """Explainable match information"""
    eligible: bool
    match_score: float = Field(ge=0.0, le=1.0)
    matched_competencies: List[MatchedCompetency]
    missing_competencies: List[str] = Field(default_factory=list)
    eligibility_reasons: List[str]
    match_reasons: List[str]
    evidence_confidence: float


class TalentMatch(BaseModel):
    """Matched talent for opportunity"""
    user_id: str
    full_name: str
    designation: str
    department: str
    match_score: float = Field(ge=0.0, le=1.0)
    competency_match_count: int
    evidence_confidence: float
    eligible: bool
    profile_readiness: Optional[float] = 0.0
    explanation: MatchExplanation


class OpportunityMatchResponse(BaseModel):
    """Opportunity match results"""
    opportunity_id: str
    opportunity_title: str
    total_eligible: int
    matches: List[TalentMatch]


# ─── User-Facing Opportunity ─────────────────────────────────────────────────


class UserOpportunity(BaseModel):
    """Opportunity from user's perspective"""
    opportunity: GovernmentOpportunity
    match_explanation: Optional[MatchExplanation] = None
    is_eligible: bool


class UserOpportunityListResponse(BaseModel):
    """User's eligible opportunities"""
    total: int
    opportunities: List[UserOpportunity]


# ─── Audit Log ───────────────────────────────────────────────────────────────


class TalentAuditLog(BaseModel):
    """Audit log entry"""
    action: str
    performed_by: str
    performed_by_name: str
    performed_by_department: str
    target_user_id: Optional[str] = None
    target_opportunity_id: Optional[str] = None
    details: dict = Field(default_factory=dict)
    timestamp: datetime


class AuditLogListResponse(BaseModel):
    """Audit log entries"""
    total: int
    logs: List[TalentAuditLog]
