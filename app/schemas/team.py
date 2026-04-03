from pydantic import BaseModel
from typing import Optional


class TeamCreate(BaseModel):
    name: str
    team_lead_id: int


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    team_lead_id: Optional[int] = None


class TeamResponse(BaseModel):
    id: int
    name: str
    company_id: int
    team_lead_id: int

    model_config = {"from_attributes": True}