from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.middleware.rbac_middleware import require_roles
from app.models.project import ProjectMirror
from app.services.fabric_client import FabricClient
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/projects", tags=["Projects"])


# ─── Pydantic Schemas ──────────────────────────────────────

class CreateProjectRequest(BaseModel):
    project_id: str
    name: str
    department: str
    budget: float


class UpdateStatusRequest(BaseModel):
    status: str  # active | closed


class ProjectResponse(BaseModel):
    id: str
    chain_project_id: str
    name: str
    status: str
    budget: float
    dept_id: Optional[str]
    last_synced: datetime

    model_config = {"from_attributes": True}


# ─── Endpoints ─────────────────────────────────────────────

@router.get("", response_model=List[ProjectResponse], summary="List all projects")
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by status: active | closed"),
    dept: Optional[str] = Query(None, description="Filter by department"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    stmt = select(ProjectMirror)
    if status:
        stmt = stmt.where(ProjectMirror.status == status)
    if dept:
        stmt = stmt.where(ProjectMirror.dept_id == dept)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=dict, status_code=201, summary="Create a new project on-chain")
async def create_project(
    body: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("org_admin", "system_admin")()),
):
    fabric = FabricClient()
    tx_id = await fabric.invoke_chaincode(
        "CreateProject",
        [body.project_id, body.name, body.department, str(body.budget)],
    )
    # Mirror to PostgreSQL
    mirror = ProjectMirror(
        chain_project_id=body.project_id,
        name=body.name,
        status="active",
        budget=body.budget,
        dept_id=body.department,
    )
    db.add(mirror)
    return {"project_id": body.project_id, "tx_id": tx_id, "status": "created"}


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project detail")
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectMirror).where(ProjectMirror.chain_project_id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)
    return project


@router.patch("/{project_id}/status", response_model=dict, summary="Update project status")
async def update_project_status(
    project_id: str,
    body: UpdateStatusRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("org_admin", "system_admin")()),
):
    result = await db.execute(
        select(ProjectMirror).where(ProjectMirror.chain_project_id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", project_id)
    project.status = body.status
    fabric = FabricClient()
    tx_id = await fabric.invoke_chaincode("UpdateProjectStatus", [project_id, body.status])
    return {"project_id": project_id, "status": body.status, "tx_id": tx_id}
