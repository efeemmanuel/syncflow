from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    priority: Optional[str] = "medium"
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    project_id: int
    company_id: int
    created_by: int
    status: str
    priority: str
    deadline: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}