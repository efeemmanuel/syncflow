from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base






class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("companies.id"), 
        nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum('company_admin', 'team_lead', 'member', name='user_role'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # company: Mapped[List["Company"]] = relationship(back_populates="user")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


    # relationships
    company: Mapped["Company"] = relationship("Company", back_populates="users")
    team_memberships: Mapped[List["TeamMember"]] = relationship("TeamMember", back_populates="user")
    created_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    assigned_tasks: Mapped[List["Task"]] = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    sent_messages: Mapped[List["Message"]] = relationship("Message", back_populates="sender")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r}, role={self.role!r})"



# company         → many-to-one back to Company
# team_memberships → one-to-many to TeamMember
# created_tasks   → one-to-many to Task (tasks this user created)
# assigned_tasks  → one-to-many to Task (tasks assigned to this user)
# sent_messages   → one-to-many to Message
