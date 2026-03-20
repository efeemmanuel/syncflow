from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

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
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="teams")
    lead: Mapped["User"] = relationship(
        "User", foreign_keys=[lead_id], back_populates="led_teams"
    )
    members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", back_populates="team"
    )
    projects: Mapped[List["Project"]] = relationship(
        "Project", back_populates="team"
    )
    project_teams: Mapped[List["ProjectTeam"]] = relationship(
        "ProjectTeam", back_populates="team"
    )
    channels: Mapped[List["Channel"]] = relationship(
        "Channel", back_populates="team"
    )

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, name={self.name!r})"