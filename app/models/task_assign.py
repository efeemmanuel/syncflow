from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Enum,Boolean, DateTime, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class TaskAssignees(Base):
    __tablename__ = "task_assignees"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    task: Mapped["Task"] = relationship(back_populates="assignees")
    user: Mapped["User"] = relationship()