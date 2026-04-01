from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session
from app.schemas.company import CompanyRegister, CompanyResponse
from app.services.company import register_company, verify_company_otp, login_company
from app.utils.otp import generate_otp, save_otp
from app.utils.email import send_otp_email
from typing import Annotated

from app.services.company import send_admin_invite, accept_admin_invite
from app.schemas.company import AdminInviteAccept

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=CompanyResponse)
async def register(data: CompanyRegister, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        company = await register_company(db, data)
        otp = generate_otp()
        await save_otp(company.email, otp)
        await send_otp_email(company.email, otp)
        return company
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/verify-otp")
async def verify_otp_route(email: str, otp: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        company = await verify_company_otp(db, email, otp)
        return {"message": "Company verified successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
async def login(email: str, password: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await login_company(db, email, password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.post("/send-admin-invite")
async def admin_invite(company_id: int, admin_email: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await send_admin_invite(db, company_id, admin_email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/accept-invite")
async def accept_invite(token: str, data: AdminInviteAccept, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await accept_admin_invite(db, token, data.full_name, data.username, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))