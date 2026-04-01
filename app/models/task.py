from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Enum,Boolean, DateTime, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime





class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum("todo", "in_progress", "completed", "blocked", name="task_status"), default="todo", nullable=False)
    priority: Mapped[str] = mapped_column(Enum("low", "medium", "high", name="task_priority"), default="medium", nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    assignees: Mapped[List["TaskAssignees"]] = relationship(back_populates="task")