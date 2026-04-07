from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    username: Optional[str] = None
    role: str
    company_id: int
    team_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}