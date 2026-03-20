from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    channel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channels.id"),
        nullable=False,
        index=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("open", "locked", name="thread_status"),
        default="open",
        nullable=False
    )
    locked_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="threads")
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by]
    )
    locker: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[locked_by]
    )
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="thread"
    )

    def __repr__(self) -> str:
        return f"Thread(id={self.id!r}, title={self.title!r}, status={self.status!r})"