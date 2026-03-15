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
from app.services.biometric_service import BiometricService

router = APIRouter(prefix="/biometric", tags=["Biometric"])


class BiometricVerifyRequest(BaseModel):
    contractor_id: str
    project_id: str
    frame_base64: str  # Base64-encoded camera frame
    id_photo_base64: str  # Base64-encoded ID document photo


class BiometricVerifyResponse(BaseModel):
    status: str  # green | amber | red
    match_score: float
    is_duplicate: bool
    alert_id: Optional[str]
    detail: str


@router.post("/verify", response_model=BiometricVerifyResponse,
             summary="1:1 face match + 1:N duplicate check (Contractor)")
async def verify_biometric(
    body: BiometricVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("contractor", "org_admin", "system_admin")()),
):
    service = BiometricService()
    result = await service.verify(
        frame_base64=body.frame_base64,
        id_photo_base64=body.id_photo_base64,
        contractor_id=body.contractor_id,
    )

    # Persist fraud alert if amber/red
    alert_id = None
    if result["status"] in ("amber", "red"):
        alert = FraudAlert(
            project_id=body.project_id,
            contractor_id=body.contractor_id,
            severity=result["status"],
            reason=result["detail"],
            rule_id="R001" if result["is_duplicate"] else "R006",
        )
        db.add(alert)
        await db.flush()
        alert_id = alert.id

    return BiometricVerifyResponse(
        status=result["status"],
        match_score=result["match_score"],
        is_duplicate=result["is_duplicate"],
        alert_id=alert_id,
        detail=result["detail"],
    )


@router.get("/status/{contractor_id}", response_model=dict,
            summary="Get biometric verification status for a contractor")
async def get_biometric_status(
    contractor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(FraudAlert)
        .where(FraudAlert.contractor_id == contractor_id)
        .order_by(FraudAlert.created_at.desc())
    )
    alerts = result.scalars().all()
    if not alerts:
        return {"contractor_id": contractor_id, "status": "green", "alerts": []}
    worst = "green"
    for a in alerts:
        if a.severity == "red":
            worst = "red"
            break
        if a.severity == "amber":
            worst = "amber"
    return {"contractor_id": contractor_id, "status": worst, "alert_count": len(alerts)}
