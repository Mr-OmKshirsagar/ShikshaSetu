"""
Government Talent & Opportunity Network - API Router
"""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.database import Database
from bson import ObjectId

from app.auth.dependencies import require_official, require_admin
from app.talent.service import (
    build_talent_profile,
    get_user_eligible_opportunities,
    match_opportunity_to_talent_pool,
)
from app.talent.repository import (
    update_talent_preferences,
    create_opportunity,
    get_opportunity_by_id,
    update_opportunity,
    get_all_opportunities,
    publish_opportunity,
    archive_opportunity,
    delete_opportunity,
    log_audit_event,
)
from app.talent.schemas import (
    TalentProfile,
    TalentPreferencesUpdate,
    GovernmentOpportunity,
    OpportunityCreate,
    OpportunityUpdate,
    OpportunityListResponse,
    OpportunityMatchResponse,
    UserOpportunityListResponse,
    AuditLogListResponse,
)
from app.talent.models import OpportunityStatus, TalentAuditAction

router = APIRouter(prefix="/talent", tags=["Talent Network"])


# ─── Helper Functions ────────────────────────────────────────────────────────


def get_database(request: Request) -> Database:
    """Get database from app state"""
    database = getattr(request.app.state, "database", None)
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not available"
        )
    return database


def _object_id(value: str) -> ObjectId | None:
    """Convert string to ObjectId"""
    return ObjectId(value) if ObjectId.is_valid(value) else None


async def _log_audit(
    database: Database,
    action: str,
    current_user: dict,
    target_user_id: str | None = None,
    target_opportunity_id: str | None = None,
    details: dict | None = None
):
    """Log audit event"""
    try:
        log_audit_event(
            database=database,
            action=action,
            performed_by=str(current_user["_id"]),
            performed_by_name=current_user.get("full_name", "Unknown"),
            performed_by_department=current_user.get("department", "Unknown"),
            target_user_id=target_user_id,
            target_opportunity_id=target_opportunity_id,
            details=details or {}
        )
    except Exception:
        pass  # Don't fail request if audit logging fails


# ─── Talent Profile Endpoints (Official Users) ───────────────────────────────


@router.get("/profile", response_model=TalentProfile)
async def get_talent_profile(
    current_user: Annotated[dict, Depends(require_official)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Get current user's talent profile.
    
    **Access:** OFFICIAL, TRAINER, ADMIN
    
    Returns talent profile constructed from verified ShikshaSetu data:
    - Verified competencies from assessments
    - Role and designation
    - Trainer experience and statistics
    - Profile readiness score
    - Privacy preferences
    """
    user_id = str(current_user["_id"])
    profile = build_talent_profile(database, user_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent profile not available. Complete competency assessments to build your profile."
        )
    
    await _log_audit(
        database=database,
        action="VIEW_PROFILE",
        current_user=current_user,
        target_user_id=user_id
    )
    
    return profile


@router.patch("/preferences", response_model=TalentProfile)
async def update_preferences(
    preferences: TalentPreferencesUpdate,
    current_user: Annotated[dict, Depends(require_official)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Update talent profile preferences.
    
    **Access:** OFFICIAL, TRAINER, ADMIN
    
    Allows users to:
    - Opt into/out of opportunity discovery
    - Set visibility level (PRIVATE / MY_DEPARTMENT / AUTHORIZED_DEPARTMENTS)
    - Select opportunity types of interest
    - Mark availability for opportunities
    
    **Privacy:** All changes require explicit user consent. Defaults to opt-out and private.
    """
    user_id = str(current_user["_id"])
    
    # Update preferences
    success = update_talent_preferences(
        database=database,
        user_id=user_id,
        updates=preferences
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )
    
    # Log audit
    await _log_audit(
        database=database,
        action="UPDATE_PREFERENCES",
        current_user=current_user,
        target_user_id=user_id,
        details=preferences.model_dump(exclude_none=True)
    )
    
    # Return updated profile
    profile = build_talent_profile(database, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return profile


@router.get("/opportunities", response_model=UserOpportunityListResponse)
async def get_eligible_opportunities(
    current_user: Annotated[dict, Depends(require_official)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Get opportunities the user is eligible for.
    
    **Access:** OFFICIAL, TRAINER, ADMIN
    
    Returns:
    - Only published opportunities
    - Only opportunities user is eligible for (based on opt-in, competencies, role)
    - Includes match explanation (eligibility reasons, match score, gaps)
    - Sorted by eligibility and match score
    
    **Privacy:** Respects user's opt-in and visibility preferences.
    """
    user_id = str(current_user["_id"])
    
    opportunities = get_user_eligible_opportunities(database, user_id)
    
    await _log_audit(
        database=database,
        action="VIEW_OPPORTUNITIES",
        current_user=current_user,
        target_user_id=user_id,
        details={"eligible_count": sum(1 for o in opportunities if o.is_eligible)}
    )
    
    return UserOpportunityListResponse(
        total=len(opportunities),
        opportunities=opportunities
    )


# ─── Opportunity Management (Admin Only) ─────────────────────────────────────


@router.post("/opportunities", response_model=GovernmentOpportunity, status_code=status.HTTP_201_CREATED)
async def create_new_opportunity(
    opportunity: OpportunityCreate,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Create new government opportunity.
    
    **Access:** ADMIN only
    
    Creates opportunity in DRAFT status. Must be explicitly published.
    """
    user_id = str(current_user["_id"])
    
    opportunity_id = create_opportunity(
        database=database,
        opportunity_data=opportunity,
        created_by=user_id
    )
    
    if not opportunity_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create opportunity"
        )
    
    await _log_audit(
        database=database,
        action="CREATE_OPPORTUNITY",
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details={"title": opportunity.title, "type": opportunity.opportunity_type}
    )
    
    created = get_opportunity_by_id(database, opportunity_id)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity created but not found"
        )
    
    return created


@router.get("/opportunities/{opportunity_id}", response_model=GovernmentOpportunity)
async def get_opportunity(
    opportunity_id: str,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Get opportunity details.
    
    **Access:** ADMIN only
    """
    opportunity = get_opportunity_by_id(database, opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return opportunity


@router.patch("/opportunities/{opportunity_id}", response_model=GovernmentOpportunity)
async def update_existing_opportunity(
    opportunity_id: str,
    updates: OpportunityUpdate,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Update opportunity details.
    
    **Access:** ADMIN only
    
    Can only update opportunities in DRAFT status.
    """
    # Check exists
    existing = get_opportunity_by_id(database, opportunity_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    # Only allow updates to DRAFT opportunities
    if existing.status != OpportunityStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update opportunity in {existing.status} status. Only DRAFT opportunities can be modified."
        )
    
    success = update_opportunity(
        database=database,
        opportunity_id=opportunity_id,
        updates=updates
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update opportunity"
        )
    
    await _log_audit(
        database=database,
        action="UPDATE_OPPORTUNITY",
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details=updates.model_dump(exclude_none=True)
    )
    
    updated = get_opportunity_by_id(database, opportunity_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found after update"
        )
    
    return updated


@router.post("/opportunities/{opportunity_id}/publish", response_model=GovernmentOpportunity)
async def publish_existing_opportunity(
    opportunity_id: str,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Publish opportunity to make it visible to eligible talent.
    
    **Access:** ADMIN only
    
    Changes status from DRAFT to PUBLISHED.
    """
    existing = get_opportunity_by_id(database, opportunity_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    if existing.status != OpportunityStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish opportunity in {existing.status} status"
        )
    
    success = publish_opportunity(database, opportunity_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish opportunity"
        )
    
    await _log_audit(
        database=database,
        action="PUBLISH_OPPORTUNITY",
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details={"title": existing.title}
    )
    
    published = get_opportunity_by_id(database, opportunity_id)
    return published


@router.post("/opportunities/{opportunity_id}/archive", response_model=GovernmentOpportunity)
async def archive_existing_opportunity(
    opportunity_id: str,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Archive opportunity (no longer visible to talent).
    
    **Access:** ADMIN only
    """
    existing = get_opportunity_by_id(database, opportunity_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    success = archive_opportunity(database, opportunity_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive opportunity"
        )
    
    await _log_audit(
        database=database,
        action="ARCHIVE_OPPORTUNITY",
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details={"title": existing.title}
    )
    
    archived = get_opportunity_by_id(database, opportunity_id)
    return archived


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_opportunity(
    opportunity_id: str,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Permanently delete a government opportunity and its cached matches.
    
    **Access:** ADMIN only
    """
    existing = get_opportunity_by_id(database, opportunity_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    success = delete_opportunity(database, opportunity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete opportunity"
        )
    
    await _log_audit(
        database=database,
        action="DELETE_OPPORTUNITY",
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details={"title": existing.title}
    )
    return None


@router.get("/admin/opportunities", response_model=OpportunityListResponse)
async def list_all_opportunities(
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
    status_filter: OpportunityStatus | None = None,
):
    """
    List all opportunities (admin view).
    
    **Access:** ADMIN only
    
    Optional filters:
    - status: Filter by opportunity status (DRAFT, PUBLISHED, ARCHIVED)
    """
    opportunities = get_all_opportunities(database, status_filter)
    
    return OpportunityListResponse(
        total=len(opportunities),
        opportunities=opportunities
    )


@router.get("/opportunities/{opportunity_id}/matches", response_model=OpportunityMatchResponse)
async def get_opportunity_matches(
    opportunity_id: str,
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
):
    """
    Get all eligible talent matches for an opportunity.
    
    **Access:** ADMIN only
    
    Returns:
    - All talent that meet eligibility criteria
    - Match scores and explanations
    - Competency gaps and matches
    - Evidence confidence levels
    
    **Privacy:** Only shows profiles that have opted in with appropriate visibility.
    """
    opportunity = get_opportunity_by_id(database, opportunity_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    matches = match_opportunity_to_talent_pool(database, opportunity_id)
    
    await _log_audit(
        database=database,
        action=TalentAuditAction.OPPORTUNITY_MATCHES_VIEWED.value,
        current_user=current_user,
        target_opportunity_id=opportunity_id,
        details={
            "title": opportunity.title,
            "eligible_count": len(matches)
        }
    )
    
    return OpportunityMatchResponse(
        opportunity_id=opportunity_id,
        opportunity_title=opportunity.title,
        total_eligible=len(matches),
        matches=matches
    )


# ─── Audit Log (Admin Only) ──────────────────────────────────────────────────


@router.get("/admin/audit-logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    current_user: Annotated[dict, Depends(require_admin)],
    database: Annotated[Database, Depends(get_database)],
    limit: int = 100,
):
    """
    Get talent network audit logs.
    
    **Access:** ADMIN only
    
    Returns recent audit events (profile views, preference changes, opportunity actions).
    """
    if not hasattr(database, "talent_access_audit"):
        return AuditLogListResponse(total=0, logs=[])
    
    logs = list(database.talent_access_audit.find()
                .sort("timestamp", -1)
                .limit(limit))
    
    audit_logs = []
    for log in logs:
        log_dict = dict(log)
        log_dict.pop("_id", None)
        if "timestamp" not in log_dict:
            log_dict["timestamp"] = datetime.utcnow()
        audit_logs.append(log_dict)
    
    return AuditLogListResponse(
        total=len(audit_logs),
        logs=audit_logs
    )
