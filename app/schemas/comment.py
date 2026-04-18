from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    task_id: int
    user_id: int
    user_name: Optional[str] = None
    company_id: int
    created_at: datetime

    model_config = {"from_attributes": True}