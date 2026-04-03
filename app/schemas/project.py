from pydantic import BaseModel
from typing import Optional




class ProjectRequest(BaseModel):
    title: str
    description: str
    company_id: int
    team_id: id