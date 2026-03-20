from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, Boolean, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )
    assigned_to: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("pending", "ongoing", "in_review", "completed", "cancelled", name="task_status"),
        default="pending",
        nullable=False
    )
    priority: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", "critical", name="task_priority"),
        default="medium",
        nullable=False
    )
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    approval_status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "changes_requested", name="approval_status"),
        default="pending",
        nullable=False
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    assignee: Mapped["User"] = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_tasks"
    )
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by], back_populates="created_tasks"
    )
    approver: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[approved_by]
    )
    submissions: Mapped[List["TaskSubmission"]] = relationship(
        "TaskSubmission", back_populates="task"
    )
    comments: Mapped[List["TaskComment"]] = relationship(
        "TaskComment", back_populates="task"
    )
    integrations: Mapped[List["TaskIntegration"]] = relationship(
        "TaskIntegration", back_populates="task"
    )

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r}, status={self.status!r})"