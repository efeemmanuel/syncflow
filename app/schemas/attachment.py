from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AttachmentCreate(BaseModel):
    file_url: str
    file_type: str


class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    company_id: int
    file_url: str
    file_type: str
    created_at: datetime

    model_config = {"from_attributes": True}