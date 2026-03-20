
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, UUID, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base




# id          → UUID, primary key
# company_id  → UUID, FK to companies.id
# lead_id     → UUID, FK to users.id (the team lead)
# name        → String(255), required
# description → Text, optional
# created_at  → DateTime
# updated_at  → DateTime