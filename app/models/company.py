from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC", nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="company")
    teams: Mapped[List["Team"]] = relationship("Team", back_populates="company")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="company")
    channels: Mapped[List["Channel"]] = relationship("Channel", back_populates="company")
    invitations: Mapped[List["Invitation"]] = relationship("Invitation", back_populates="company")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="company")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="company")

    def __repr__(self) -> str:
        return f"Company(id={self.id!r}, name={self.name!r}, slug={self.slug!r})"