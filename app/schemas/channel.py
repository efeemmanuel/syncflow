from pydantic import BaseModel
from typing import Optional
from datetime import datetime



class ChannelCreate(BaseModel):
    name: str
    project_id: Optional[int] = None

class ChannelResponse(BaseModel):
    id: int
    name: str
    company_id: int
    project_id: Optional[int] = None
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str
    reply_to_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    channel_id: int
    sender_id: int
    sender_name: str
    content: str
    reply_to_id: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}