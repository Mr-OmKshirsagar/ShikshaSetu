from fastapi import APIRouter, Request

from app.competencies import service
from app.competencies.schemas import RoleRequirementResponse, RoleResponse
from app.core.database import get_or_reconnect_database

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleResponse])
def get_roles(request: Request) -> list[dict]:
    db = get_or_reconnect_database(request.app)
    return service.list_roles(db)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(request: Request, role_id: str) -> dict:
    db = get_or_reconnect_database(request.app)
    return service.get_role(db, role_id)


@router.get("/{role_id}/requirements", response_model=list[RoleRequirementResponse])
def get_role_requirements(request: Request, role_id: str) -> list[dict]:
    db = get_or_reconnect_database(request.app)
    return service.list_role_requirements(db, role_id)
