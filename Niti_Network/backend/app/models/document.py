import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class DocumentRegistry(Base):
    """Off-chain file registry — only SHA-256 hash goes on-chain."""
    __tablename__ = "document_registry"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    milestone_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    minio_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    tx_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Fabric transaction ID
