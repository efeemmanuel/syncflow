from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Channel(Base):
    __tablename__ = "channels"

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
    channel_type: Mapped[str] = mapped_column(
        Enum("company", "team", "project", name="channel_type"),
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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="channels")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="channels")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="channels")
    members: Mapped[List["ChannelMember"]] = relationship(
        "ChannelMember", back_populates="channel"
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="channel"
    )
    threads: Mapped[List["Thread"]] = relationship(
        "Thread", back_populates="channel"
    )

    def __repr__(self) -> str:
        return f"Channel(id={self.id!r}, name={self.name!r}, type={self.channel_type!r})"