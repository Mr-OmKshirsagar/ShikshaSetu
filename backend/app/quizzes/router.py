from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import get_current_user
from app.quizzes import repository as quiz_repo
from app.quizzes.service import QuizService, QuizServiceError
from app.quizzes.schemas import (
    QuizCreateRequest,
    QuizResponse,
    QuizSubmitRequest,
    QuizResultResponse,
    QuizQuestionResponse,
    RecommendedQuizItem,
    RecommendedQuizScoreBreakdown,
    QuizFeedResponse,
    QuizFeedMeta,
)
from app.trainer.repository import TrainerRepository


router = APIRouter(prefix="/quizzes", tags=["quizzes"])
CurrentUser = Annotated[dict, Depends(get_current_user)]


def _format_quiz_response(quiz: dict) -> QuizResponse:
    questions_response = []
    for q in quiz.get("questions", []):
        questions_response.append(QuizQuestionResponse(
            question_id=str(q.get("question_id", q.get("_id", ""))),
            question=q.get("question", ""),
            options=q.get("options", []),
            difficulty=q.get("difficulty", quiz.get("difficulty", "MEDIUM")),
            source_chunks=q.get("source_chunks", []),
        ))
    created_val = quiz.get("created_at")
    created_dt = created_val if isinstance(created_val, datetime) else datetime.now(UTC)
    assigned_val = quiz.get("assigned_at")
    assigned_dt = assigned_val if isinstance(assigned_val, datetime) else None
    return QuizResponse(
        _id=str(quiz["_id"]),
        title=quiz.get("title", ""),
        description=quiz.get("description"),
        competency_code=quiz.get("competency_code", ""),
        question_count=quiz.get("question_count", len(questions_response)),
        status=quiz.get("status", "PUBLISHED"),
        questions=questions_response,
        created_at=created_dt,
        relevance_reason=quiz.get("relevance_reason"),
        relevance_explanation=quiz.get("relevance_explanation"),
        priority=quiz.get("priority"),
        is_gap=quiz.get("is_gap"),
        gap_size=quiz.get("gap_size"),
        current_level=quiz.get("current_level"),
        required_level=quiz.get("required_level"),
        difficulty=quiz.get("difficulty", "MEDIUM"),
        target_competency_ids=quiz.get("target_competency_ids", []),
        target_role_ids=quiz.get("target_role_ids", []),
        target_designation_ids=quiz.get("target_designation_ids", []),
        assigned_at=assigned_dt,
        trainer_name=quiz.get("trainer_name"),
        is_also_recommended=quiz.get("is_also_recommended", False),
    )


def _format_recommended_item(r: dict) -> RecommendedQuizItem:
    q = r["quiz"]
    created_val = q.get("created_at")
    created_dt = created_val if isinstance(created_val, datetime) else datetime.now(UTC)

    cur_lvl = r.get("current_level")
    if cur_lvl is None:
        cur_lvl = q.get("current_level", 2.0)
    req_lvl = r.get("required_level")
    if req_lvl is None:
        req_lvl = q.get("required_level", 3.0)
    gap_val = r.get("gap")
    if gap_val is None:
        gap_val = q.get("gap_size", 0.0)

    score_val = r.get("recommendation_score", 0.8)

    return RecommendedQuizItem(
        _id=str(q.get("_id", "")),
        title=q.get("title", ""),
        competency_code=q.get("competency_code", r.get("primary_competency", "")),
        question_count=q.get("question_count", len(q.get("questions", []))),
        status=q.get("status", "PUBLISHED"),
        created_at=created_dt,
        recommendation_score=float(score_val),
        recommendation_source="COMPETENCY_GAP" if (gap_val and gap_val > 0) else "ROLE_PROFILE",
        primary_reason=r.get("reason") or q.get("relevance_explanation") or "Recommended for your role competency development.",
        current_level=float(cur_lvl),
        required_level=float(req_lvl),
        gap_size=float(gap_val or 0.0),
        is_gap=bool(gap_val and gap_val > 0),
        role_title=r.get("role_name"),
        difficulty=q.get("difficulty", "MEDIUM"),
        description=q.get("description"),
        score_breakdown=RecommendedQuizScoreBreakdown(
            gap_score=0.4 if (gap_val and gap_val > 0) else 0.2,
            role_score=0.25,
            severity_score=min(0.15, (gap_val or 0.0) / 3.0 * 0.15),
            difficulty_score=0.10,
            prereq_score=0.10,
            total_score=float(score_val),
        ),
    )


@router.get("/feed", response_model=QuizFeedResponse)
def get_quiz_feed(
    request: Request,
    current_user: CurrentUser,
    limit: int = 5,
) -> dict:
    """
    Get dual-source quiz feed separating Trainer Assignments from System Recommendations.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    user_id = str(current_user["_id"])
    service = QuizService(database)
    feed_data = service.get_official_quiz_feed(user_id, limit=limit)

    formatted_assigned = [_format_quiz_response(q) for q in feed_data["assigned"]]
    formatted_recommended = [_format_recommended_item(r) for r in feed_data["recommended"]]

    role_title = current_user.get("designation") or current_user.get("role_name") or current_user.get("role") or "Official"
    role_id = current_user.get("role_id") or current_user.get("role") or "OFFICIAL"

    return {
        "assigned": formatted_assigned,
        "recommended": formatted_recommended,
        "meta": QuizFeedMeta(
            user_id=user_id,
            role_id=str(role_id),
            role_title=str(role_title),
            total_assigned=len(formatted_assigned),
            total_recommended=len(formatted_recommended),
            active_gaps_count=sum(1 for r in formatted_recommended if r.is_gap),
        ),
    }


@router.get("/recommended", response_model=list[RecommendedQuizItem])
def get_recommended_quizzes(
    request: Request,
    current_user: CurrentUser,
    limit: int = 5,
) -> list[RecommendedQuizItem]:
    """
    List deterministic system-recommended quizzes based on role requirements and competency gaps.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    user_id = str(current_user["_id"])
    service = QuizService(database)
    recommended = service.recommend_quizzes_for_official(user_id, limit=limit)

    return [_format_recommended_item(r) for r in recommended]


@router.get("/assigned", response_model=list[QuizResponse])
def get_assigned_quizzes(
    request: Request,
    current_user: CurrentUser,
) -> list[dict]:
    """
    List quizzes explicitly assigned to the current official by a trainer or admin.
    Does NOT depend on recommendation scoring.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    user_id = str(current_user["_id"])
    service = QuizService(database)
    quizzes = service.get_explicitly_assigned_quizzes(user_id)
    return [_format_quiz_response(q) for q in quizzes]


@router.get("/relevant", response_model=list[QuizResponse])
def get_relevant_quizzes(
    request: Request,
    current_user: CurrentUser,
) -> list[dict]:
    """Legacy alias returning role/competency-personalized quizzes."""
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    user_id = str(current_user["_id"])
    service = QuizService(database)
    quizzes = service.list_relevant_quizzes_for_official(user_id)
    return [_format_quiz_response(q) for q in quizzes]



@router.post("", response_model=QuizResponse)
def create_quiz(
    request: Request,
    payload: QuizCreateRequest,
    current_user: CurrentUser,
) -> dict:
    """
    Create a quiz from learning material.
    
    The quiz will have questions generated from the material using Phase 6.
    Correct answers are hidden until submission.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    
    # Initialize quiz indexes
    quiz_repo.create_quiz_indexes(database)
    quiz_repo.create_quiz_attempt_indexes(database)

    service = QuizService(database)
    
    try:
        quiz = service.create_quiz(
            user_id=str(current_user["_id"]),
            material_id=payload.material_id,
            competency_code=payload.competency_code,
            questions=[{
                "question": q.question,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "difficulty": q.difficulty,
                "source_chunks": q.source_chunks,
            } for q in payload.questions],
        )

        # Convert questions to response schema (hide correct answers)
        questions_response = []
        for q in quiz["questions"]:
            questions_response.append(QuizQuestionResponse(
                question_id=q["question_id"],
                question=q["question"],
                options=q["options"],
                difficulty=q["difficulty"],
                source_chunks=q.get("source_chunks", []),
            ))

        return QuizResponse(
            _id=str(quiz["_id"]),
            title=quiz["title"],
            competency_code=quiz["competency_code"],
            question_count=quiz["question_count"],
            status=quiz["status"],
            questions=questions_response,
            created_at=quiz["created_at"],
        )

    except QuizServiceError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quiz",
        )


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    request: Request,
    quiz_id: str,
    current_user: CurrentUser,
) -> dict:
    """
    Retrieve a quiz by ID.
    
    Correct answers are hidden before submission.
    User can only retrieve their own quizzes.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    
    service = QuizService(database)
    
    try:
        quiz = service.get_quiz(
            user_id=str(current_user["_id"]),
            quiz_id=quiz_id,
        )

        # Convert questions to response schema (hide correct answers)
        questions_response = []
        for q in quiz["questions"]:
            questions_response.append(QuizQuestionResponse(
                question_id=q["question_id"],
                question=q["question"],
                options=q["options"],
                difficulty=q["difficulty"],
                source_chunks=q.get("source_chunks", []),
            ))

        return QuizResponse(
            _id=str(quiz["_id"]),
            title=quiz["title"],
            competency_code=quiz["competency_code"],
            question_count=quiz["question_count"],
            status=quiz["status"],
            questions=questions_response,
            created_at=quiz["created_at"],
        )

    except QuizServiceError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve quiz",
        )


@router.post("/{quiz_id}/submit", response_model=QuizResultResponse)
def submit_quiz(
    request: Request,
    quiz_id: str,
    payload: QuizSubmitRequest,
    current_user: CurrentUser,
) -> dict:
    """
    Submit quiz answers.
    
    Server calculates score server-side (client score is ignored).
    Correct answers are revealed in the response.
    Competency profile is updated deterministically.
    Evidence is created and linked to the quiz attempt.
    """
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not available",
        )
    
    service = QuizService(database)
    
    try:
        result = service.submit_quiz(
            user_id=str(current_user["_id"]),
            quiz_id=quiz_id,
            answers=[{"question_id": a.question_id, "selected_answer": a.selected_answer} for a in payload.answers],
        )

        return QuizResultResponse(
            _id=str(result["_id"]),
            quiz_id=result["quiz_id"],
            score=result["score"],
            percentage=result["percentage"],
            correct_count=result["correct_count"],
            total_questions=result["total_questions"],
            competency=result["competency"],
            skill_gap=result["skill_gap"],
            explanations=result["explanations"],
            submitted_at=result["submitted_at"],
        )

    except QuizServiceError as e:
        if "already submitted" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit quiz",
        )
