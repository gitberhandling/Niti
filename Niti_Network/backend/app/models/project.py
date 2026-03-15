import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class ProjectMirror(Base):
    """Read-optimised mirror of on-chain project state in PostgreSQL."""
    __tablename__ = "projects_mirror"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain_project_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")  # active | closed
    budget: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    dept_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
