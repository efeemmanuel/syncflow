from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Enum,Boolean, DateTime, Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime





class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(Enum("active", "completed", "on_hold", name="project_status"), default="active", nullable=False)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="projects")
    team: Mapped[Optional["Team"]] = relationship()
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    tasks: Mapped[List["Task"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    channels: Mapped[List["Channel"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    members: Mapped[List["ProjectMembers"]] = relationship(back_populates="project")