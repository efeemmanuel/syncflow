from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

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
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_type: Mapped[str] = mapped_column(
        Enum("team", "company", name="project_type"),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "on_hold", "completed", "cancelled", name="project_status"),
        default="draft",
        nullable=False
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="projects")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="projects")
    creator: Mapped["User"] = relationship("User", back_populates="created_projects")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project")
    project_teams: Mapped[List["ProjectTeam"]] = relationship(
        "ProjectTeam", back_populates="project"
    )
    source_links: Mapped[List["ProjectLink"]] = relationship(
        "ProjectLink", foreign_keys="ProjectLink.project_id", back_populates="project"
    )
    linked_links: Mapped[List["ProjectLink"]] = relationship(
        "ProjectLink", foreign_keys="ProjectLink.linked_project_id", back_populates="linked_project"
    )
    channels: Mapped[List["Channel"]] = relationship("Channel", back_populates="project")
    invitations: Mapped[List["Invitation"]] = relationship(
        "Invitation", back_populates="project"
    )

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, title={self.title!r}, type={self.project_type!r})"