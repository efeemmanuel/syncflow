from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Enum,Boolean, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime





class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    plan: Mapped[str] = mapped_column(Enum("freemium", "premium", name="plan_status"), default="freemium", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_attempts: Mapped[int] = mapped_column(default=0, nullable=False)

    projects: Mapped[List["Project"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    members: Mapped[List["User"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    channels: Mapped[List["Channel"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    teams: Mapped[List["Team"]] = relationship(back_populates="company", cascade="all, delete-orphan")
