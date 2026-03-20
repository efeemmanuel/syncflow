from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import String, UUID, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TaskIntegration(Base):
    __tablename__ = "task_integrations"

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
    integration_type: Mapped[str] = mapped_column(
        Enum(
            "github",
            "figma",
            "notion",
            "google_drive",
            "loom",
            "custom_link",
            name="integration_type"
        ),
        nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    task: Mapped["Task"] = relationship("Task", back_populates="integrations")

    def __repr__(self) -> str:
        return f"TaskIntegration(id={self.id!r}, type={self.integration_type!r}, label={self.label!r})"