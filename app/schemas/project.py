from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None
    team_id: Optional[int] = None
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    company_id: int
    team_id: Optional[int] = None
    created_by: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}