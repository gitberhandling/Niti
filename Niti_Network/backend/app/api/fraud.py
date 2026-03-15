from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.middleware.rbac_middleware import require_roles
from app.models.fraud_alert import FraudAlert
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


class AlertResponse(BaseModel):
    id: str
    project_id: str
    contractor_id: str
    severity: str
    reason: str
    rule_id: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved_by: Optional[str]
    resolution: Optional[str]

    model_config = {"from_attributes": True}


class ResolveAlertRequest(BaseModel):
    resolution: str  # approved | escalated


@router.get("/alerts", response_model=List[AlertResponse], summary="List fraud alerts (Auditor, Admin)")
async def list_alerts(
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("auditor", "org_admin", "system_admin")()),
):
    stmt = select(FraudAlert).order_by(FraudAlert.created_at.desc())
    if severity:
        stmt = stmt.where(FraudAlert.severity == severity)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/alerts/{alert_id}", response_model=AlertResponse, summary="Alert detail")
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("auditor", "org_admin", "system_admin")()),
):
    result = await db.execute(select(FraudAlert).where(FraudAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("FraudAlert", alert_id)
    return alert


@router.patch("/alerts/{alert_id}/resolve", response_model=dict, summary="Resolve a fraud alert (Auditor)")
async def resolve_alert(
    alert_id: str,
    body: ResolveAlertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("auditor", "org_admin", "system_admin")()),
):
    result = await db.execute(select(FraudAlert).where(FraudAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise NotFoundError("FraudAlert", alert_id)
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.user_id
    alert.resolution = body.resolution
    return {"alert_id": alert_id, "resolution": body.resolution, "resolved_by": current_user.user_id}
