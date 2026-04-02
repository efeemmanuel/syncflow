from pydantic import BaseModel, EmailStr

class CompanyRegister(BaseModel):
    name: str
    email: EmailStr
    admin_email: EmailStr
    password: str

class CompanyResponse(BaseModel):
    id: int
    name: str
    email: str
    is_verified: bool

    class Config:
        from_attributes = True


class AdminInviteAccept(BaseModel):
    full_name: str
    username: str
    password: str