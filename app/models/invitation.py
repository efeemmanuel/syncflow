from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, UUID, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Invitation(Base):
    __tablename__ = "invitations"

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
    invited_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(
        Enum("team_lead", "member", name="invitation_role"),
        nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "expired", name="invitation_status"),
        default="pending",
        nullable=False
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=True
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="invitations")
    invited_by_user: Mapped["User"] = relationship(
        "User", back_populates="sent_invitations"
    )
    team: Mapped[Optional["Team"]] = relationship("Team")
    project: Mapped[Optional["Project"]] = relationship(
        "Project", back_populates="invitations"
    )

    def __repr__(self) -> str:
        return f"Invitation(id={self.id!r}, email={self.email!r}, status={self.status!r})"