import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.middleware.rbac_middleware import require_roles
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/audit", tags=["Audit & Reporting"])


class AuditLogResponse(BaseModel):
    id: str
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    timestamp: datetime
    metadata_: Optional[dict]

    model_config = {"from_attributes": True}


@router.get("/logs", response_model=List[AuditLogResponse],
            summary="Immutable audit log with filters (Auditor)")
async def get_audit_logs(
    entity_id: Optional[str] = Query(None),
    actor_id: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("auditor", "org_admin", "system_admin")()),
):
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    if entity_id:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
    if actor_id:
        stmt = stmt.where(AuditLog.actor_id == actor_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/reports/export", summary="Export JSON proof report for a project (Admin)")
async def export_report(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("org_admin", "auditor", "system_admin")()),
):
    result = await db.execute(
        select(AuditLog).where(AuditLog.entity_id == project_id).order_by(AuditLog.timestamp)
    )
    logs = result.scalars().all()
    report = {
        "project_id": project_id,
        "exported_at": datetime.utcnow().isoformat(),
        "exported_by": current_user.user_id,
        "audit_trail": [
            {
                "id": l.id,
                "actor_id": l.actor_id,
                "action": l.action,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "timestamp": l.timestamp.isoformat(),
                "metadata": l.metadata_,
            }
            for l in logs
        ],
    }
    return JSONResponse(content=report, media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="proof_{project_id}.json"'})
