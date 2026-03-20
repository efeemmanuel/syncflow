from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    submission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task_submissions.id"),
        nullable=False,
        index=True
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    submission: Mapped["TaskSubmission"] = relationship(
        "TaskSubmission", back_populates="attachments"
    )

    def __repr__(self) -> str:
        return f"TaskAttachment(id={self.id!r}, file_name={self.file_name!r})"