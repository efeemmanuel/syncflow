from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TaskSubmission(Base):
    __tablename__ = "task_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id"),
        nullable=False,
        index=True
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    task: Mapped["Task"] = relationship("Task", back_populates="submissions")
    submitter: Mapped["User"] = relationship("User")
    attachments: Mapped[List["TaskAttachment"]] = relationship(
        "TaskAttachment", back_populates="submission"
    )

    def __repr__(self) -> str:
        return f"TaskSubmission(id={self.id!r}, task_id={self.task_id!r})"