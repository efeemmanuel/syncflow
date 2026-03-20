from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import UUID, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class ProjectLink(Base):
    __tablename__ = "project_links"

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
    linked_project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
        index=True
    )
    link_type: Mapped[str] = mapped_column(
        Enum("related", "depends_on", name="link_type"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    project: Mapped["Project"] = relationship(
        "Project", foreign_keys=[project_id], back_populates="source_links"
    )
    linked_project: Mapped["Project"] = relationship(
        "Project", foreign_keys=[linked_project_id], back_populates="linked_links"
    )

    def __repr__(self) -> str:
        return f"ProjectLink(project_id={self.project_id!r}, linked_project_id={self.linked_project_id!r}, type={self.link_type!r})"