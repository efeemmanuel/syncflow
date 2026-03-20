from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import UUID, DateTime, Text, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

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
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("threads.id"),
        nullable=True,
        index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    mentions: Mapped[Optional[List[uuid.UUID]]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # relationships
    channel: Mapped["Channel"] = relationship("Channel", back_populates="messages")
    thread: Mapped[Optional["Thread"]] = relationship("Thread", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, sender_id={self.sender_id!r})"