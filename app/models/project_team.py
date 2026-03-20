from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import UUID, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProjectTeam(Base):
    __tablename__ = "project_teams"

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
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=False,
        index=True
    )
    added_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    project: Mapped["Project"] = relationship("Project", back_populates="project_teams")
    team: Mapped["Team"] = relationship("Team", back_populates="project_teams")
    added_by_user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"ProjectTeam(project_id={self.project_id!r}, team_id={self.team_id!r})"