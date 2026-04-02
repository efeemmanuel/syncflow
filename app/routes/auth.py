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
from fastapi.security import OAuth2PasswordRequestForm

from app.services.company import invite_team_lead, accept_team_lead_invite
from app.core.dependencies import require_admin
from app.models.user import User

from app.services.company import invite_member, accept_member_invite
from app.core.dependencies import require_team_lead

from app.services.company import refresh_access_token, logout
from app.core.dependencies import get_current_user


from app.services.company import forgot_password, reset_password
from app.core.security import oauth2_scheme


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=CompanyResponse)
async def register(data: CompanyRegister, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        company = await register_company(db, data)
        otp = generate_otp()
        await save_otp(company.email, otp)
        await send_otp_email(company.email, otp)
        await send_admin_invite(db, company.id, data.admin_email)
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
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    try:
        return await login_company(db, form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))







@router.post("/refresh")
async def refresh(refresh_token: str):
    try:
        return await refresh_access_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
async def logout_route(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await logout(current_user.id, token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



@router.post("/send-admin-invite")
async def admin_invite(
    company_id: int,
    admin_email: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
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
    




@router.post("/invite-team-lead")
async def invite_lead(
    email: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
    try:
        return await invite_team_lead(db, current_user.company_id, email, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/accept-team-lead-invite")
async def accept_lead_invite(token: str, data: AdminInviteAccept, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await accept_team_lead_invite(db, token, data.full_name, data.username, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    





@router.post("/invite-member")
async def invite_mem(
    email: str,
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_team_lead)]
):
    try:
        return await invite_member(db, current_user.company_id, email, team_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/accept-member-invite")
async def accept_mem_invite(token: str, data: AdminInviteAccept, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await accept_member_invite(db, token, data.full_name, data.username, data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    




@router.post("/forgot-password")
async def forgot_pass(email: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await forgot_password(db, email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/reset-password")
async def reset_pass(email: str, otp: str, new_password: str, db: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        return await reset_password(db, email, otp, new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))