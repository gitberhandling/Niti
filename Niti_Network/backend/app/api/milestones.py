from typing import Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.middleware.rbac_middleware import require_roles
from app.services.fabric_client import FabricClient
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/projects", tags=["Milestones"])


class AddMilestoneRequest(BaseModel):
    milestone_id: str
    title: str


class UpdateMilestoneRequest(BaseModel):
    status: str  # pending | verified | rejected
    completion_percentage: Optional[int] = None


@router.post("/{project_id}/milestones", response_model=dict, status_code=201,
             summary="Add a milestone to a project (Admin only)")
async def add_milestone(
    project_id: str,
    body: AddMilestoneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("org_admin", "system_admin")()),
):
    fabric = FabricClient()
    tx_id = await fabric.invoke_chaincode(
        "AddMilestone",
        [project_id, body.milestone_id, body.title],
    )
    return {"project_id": project_id, "milestone_id": body.milestone_id, "tx_id": tx_id}


@router.patch("/{project_id}/milestones/{milestone_id}", response_model=dict,
              summary="Update a milestone status (Auditor/Admin)")
async def update_milestone(
    project_id: str,
    milestone_id: str,
    body: UpdateMilestoneRequest,
    current_user: CurrentUser = Depends(require_roles("org_admin", "auditor", "system_admin")()),
):
    fabric = FabricClient()
    tx_id = await fabric.invoke_chaincode(
        "UpdateMilestoneStatus",
        [milestone_id, body.status, current_user.user_id],
    )
    return {"milestone_id": milestone_id, "status": body.status, "tx_id": tx_id}
