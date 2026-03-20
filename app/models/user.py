from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("company_admin", "team_lead", "member", name="user_role"),
        nullable=False
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password_reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    password_reset_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    led_teams: Mapped[List["Team"]] = relationship(
        "Team", foreign_keys="Team.lead_id", back_populates="lead"
    )
    team_memberships: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", back_populates="user"
    )
    created_tasks: Mapped[List["Task"]] = relationship(
        "Task", foreign_keys="Task.created_by", back_populates="creator"
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", foreign_keys="Task.assigned_to", back_populates="assignee"
    )
    sent_messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="sender"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user"
    )
    sent_invitations: Mapped[List["Invitation"]] = relationship(
        "Invitation", back_populates="invited_by_user"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", back_populates="user"
    )
    created_projects: Mapped[List["Project"]] = relationship(
    "Project", foreign_keys="Project.created_by", back_populates="creator"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"