from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.middleware.auth_middleware import get_current_user, CurrentUser
from app.middleware.rbac_middleware import require_roles
from app.models.document import DocumentRegistry
from app.services.minio_service import MinioService
from app.services.hash_service import compute_sha256
from app.services.fabric_client import FabricClient
from app.core.exceptions import NotFoundError, HashMismatchError

router = APIRouter(prefix="/documents", tags=["Documents"])


class UploadUrlRequest(BaseModel):
    project_id: str
    milestone_id: Optional[str] = None
    filename: str
    content_type: str = "application/octet-stream"


class UploadUrlResponse(BaseModel):
    signed_url: str
    document_id: str
    minio_key: str
    expires_in_seconds: int = 900  # 15 minutes


class VerifyDocumentRequest(BaseModel):
    document_id: str
    project_id: str
    milestone_id: Optional[str] = None
    minio_key: str


class DocumentResponse(BaseModel):
    id: str
    project_id: str
    milestone_id: Optional[str]
    sha256_hash: str
    minio_key: str
    uploaded_by: str
    uploaded_at: datetime
    tx_id: Optional[str]

    model_config = {"from_attributes": True}


@router.post("/upload-url", response_model=UploadUrlResponse,
             summary="Generate 15-min signed MinIO URL (Contractor)")
async def get_upload_url(
    body: UploadUrlRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("contractor", "org_admin", "system_admin")()),
):
    minio = MinioService()
    document_id, signed_url, minio_key = await minio.generate_presigned_put(
        project_id=body.project_id,
        filename=body.filename,
        content_type=body.content_type,
    )
    # Pre-register so we can track even before verify
    doc = DocumentRegistry(
        id=document_id,
        project_id=body.project_id,
        milestone_id=body.milestone_id,
        minio_key=minio_key,
        sha256_hash="",  # filled in on verify
        uploaded_by=current_user.user_id,
    )
    db.add(doc)
    return UploadUrlResponse(signed_url=signed_url, document_id=document_id, minio_key=minio_key)


@router.post("/verify", response_model=dict, summary="Compute SHA-256 and anchor hash on-chain")
async def verify_document(
    body: VerifyDocumentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_roles("contractor", "org_admin", "system_admin")()),
):
    minio = MinioService()
    file_bytes = await minio.download_object(body.minio_key)
    sha256_hash = compute_sha256(file_bytes)

    # Update registry
    result = await db.execute(select(DocumentRegistry).where(DocumentRegistry.id == body.document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document", body.document_id)
    doc.sha256_hash = sha256_hash

    # Anchor on Fabric
    fabric = FabricClient()
    tx_id = await fabric.invoke_chaincode(
        "AnchorDocumentHash",
        [body.document_id, body.project_id, sha256_hash],
    )
    doc.tx_id = tx_id

    return {"document_id": body.document_id, "sha256_hash": sha256_hash, "tx_id": tx_id}


@router.get("/{document_id}", response_model=DocumentResponse, summary="Get document metadata + on-chain hash")
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(select(DocumentRegistry).where(DocumentRegistry.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document", document_id)
    return doc
