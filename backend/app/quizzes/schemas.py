"""Pydantic schemas for Quiz API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class QuizQuestionRequest(BaseModel):
    """Question structure for quiz creation."""
    question_id: str
    question: str
    options: list[str] = Field(min_length=3, max_length=5)
    correct_answer: str
    explanation: str
    difficulty: str = Field(pattern="^(EASY|MEDIUM|HARD)$")
    source_chunks: list[str] = Field(default_factory=list)


class QuizCreateRequest(BaseModel):
    """Request to create a quiz from pre-generated MCQs."""
    material_id: str = Field(..., description="ID of the learning material")
    competency_code: str = Field(..., description="Competency code (e.g., TECH_SQL)")
    questions: list[QuizQuestionRequest] = Field(..., description="Pre-generated MCQs from Phase 6")


class QuizQuestionResponse(BaseModel):
    """Quiz question response - correct_answer HIDDEN before submission."""
    question_id: str
    question: str
    options: list[str]
    difficulty: str
    source_chunks: list[str] = Field(default_factory=list)


class QuizResponse(BaseModel):
    """Quiz retrieval response - before submission."""
    quiz_id: str = Field(alias="_id")
    title: str
    competency_code: str
    question_count: int
    status: str
    questions: list[QuizQuestionResponse] = Field(default_factory=list)
    created_at: datetime
    description: Optional[str] = None
    relevance_reason: Optional[str] = None
    relevance_explanation: Optional[str] = None
    priority: Optional[int] = None
    is_gap: Optional[bool] = None
    gap_size: Optional[float] = None
    current_level: Optional[float] = None
    required_level: Optional[float] = None
    difficulty: Optional[str] = None
    target_competency_ids: list[str] = Field(default_factory=list)
    target_role_ids: list[str] = Field(default_factory=list)
    target_designation_ids: list[str] = Field(default_factory=list)
    assigned_at: Optional[datetime] = None
    trainer_name: Optional[str] = None
    is_also_recommended: Optional[bool] = False

    model_config = {"populate_by_name": True}


class RecommendedQuizItem(BaseModel):
    """Recommended quiz item with pedagogical explainability."""
    quiz: QuizResponse
    primary_competency: str
    current_level: Optional[float] = None
    required_level: Optional[float] = None
    gap: Optional[float] = None
    recommendation_score: float
    reason: str
    role_name: Optional[str] = None


class QuizFeedMeta(BaseModel):
    """Metadata for official quiz feed."""
    total_assigned: int
    total_recommended: int
    recommendation_reasoning: bool = True


class QuizFeedResponse(BaseModel):
    """Dual-source response separating Trainer Assignments from System Recommendations."""
    assigned: list[QuizResponse] = Field(default_factory=list)
    recommended: list[RecommendedQuizItem] = Field(default_factory=list)
    meta: QuizFeedMeta


class QuizAnswerRequest(BaseModel):
    """Single answer in submission."""
    question_id: str
    selected_answer: str = Field(pattern="^[A-E]$")


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers."""
    answers: list[QuizAnswerRequest] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_no_duplicates(self) -> "QuizSubmitRequest":
        question_ids = [a.question_id for a in self.answers]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("duplicate question_id in answers")
        return self


class CompetencyResultResponse(BaseModel):
    """Competency result after quiz submission."""
    competency_code: str
    competency_level_before: float = Field(ge=1, le=5)
    competency_level_after: float = Field(ge=1, le=5)
    confidence_before: float = Field(ge=0, le=1)
    confidence_after: float = Field(ge=0, le=1)
    improvement: float


class SkillGapResultResponse(BaseModel):
    """Skill gap result after competency update."""
    competency_code: str
    current_level: float = Field(ge=1, le=5)
    required_level: float = Field(ge=1, le=5)
    gap_before: float
    gap_after: float


class QuestionExplanation(BaseModel):
    """Question with explanation after submission."""
    question_id: str
    question: str
    options: list[str]
    your_answer: str
    correct_answer: str
    explanation: str
    difficulty: str
    source_chunks: list[str]
    is_correct: bool


class QuizResultResponse(BaseModel):
    """Quiz submission result response."""
    attempt_id: str = Field(alias="_id")
    quiz_id: str
    score: int
    percentage: float
    correct_count: int
    total_questions: int
    competency: CompetencyResultResponse
    skill_gap: SkillGapResultResponse
    explanations: list[QuestionExplanation]
    submitted_at: datetime

    model_config = {"populate_by_name": True}


class RecommendedQuizScoreBreakdown(BaseModel):
    gap_score: float = 0.0
    role_score: float = 0.0
    severity_score: float = 0.0
    difficulty_score: float = 0.0
    prereq_score: float = 0.0
    total_score: float = 0.0


class RecommendedQuizItem(BaseModel):
    quiz_id: str = Field(alias="_id")
    title: str
    competency_code: str
    question_count: int
    status: str
    created_at: datetime
    recommendation_score: float
    recommendation_source: str
    primary_reason: str
    current_level: float
    required_level: float
    gap_size: float
    is_gap: bool
    role_title: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None
    score_breakdown: Optional[RecommendedQuizScoreBreakdown] = None

    model_config = {"populate_by_name": True}


class QuizFeedMeta(BaseModel):
    user_id: str
    role_id: str
    role_title: str
    total_assigned: int
    total_recommended: int
    active_gaps_count: int


class QuizFeedResponse(BaseModel):
    assigned: list[QuizResponse]
    recommended: list[RecommendedQuizItem]
    meta: QuizFeedMeta

