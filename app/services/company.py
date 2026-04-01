from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyRegister
from app.core.security import get_password_hash
from app.utils.otp import verify_otp
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings

from app.core.security import save_invite_token
from app.core.security import verify_invite_token
from datetime import datetime, timedelta
from app.utils.email import send_admin_invite_email
import uuid




# create the company and admin then go to otp.py to generate otp
async def register_company(db: AsyncSession, data: CompanyRegister):
    # check if company email already exists
    result = await db.execute(select(Company).where(Company.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Company with this email already exists")

    # create company
    company = Company(
        name=data.name,
        email=data.email,
        slug=data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8],
        
    )
    db.add(company)
    await db.flush()  # gets the company id without committing

    # create admin user for the company
    admin = User(
        full_name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role="admin",
        company_id=company.id,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(company)
    return company






# Company submits email + OTP code
# Verify function checks Redis → marks company active
async def verify_company_otp(db: AsyncSession, email: str, otp: str):
    # verify otp from redis
    is_valid = await verify_otp(email, otp)
    if not is_valid:
        raise ValueError("Invalid or expired OTP")

    # get company by email
    result = await db.execute(select(Company).where(Company.email == email))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError("Company not found")

    # mark company as verified and active
    company.is_verified = True
    company.is_active = True
    await db.commit()
    await db.refresh(company)
    return company





# company log in with email and password
async def login_company(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    # query company directly instead of user.company.is_verified
    company_result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = company_result.scalar_one_or_none()
    if not company.is_verified:
        raise ValueError("Company not verified")

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "company_id": user.company_id,
            "role": user.role
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    return {"access_token": access_token, "token_type": "bearer"}






async def send_admin_invite(db: AsyncSession, company_id: int, admin_email: str):
    # check if company exists
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError("Company not found")

    # generate and save invite token
    token = await save_invite_token(admin_email, company_id, "admin")

    # send invite email
    await send_admin_invite_email(admin_email, token, company.name)
    return {"message": "Invite sent successfully"}





async def accept_admin_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
    # verify token from redis
    token_data = await verify_invite_token(token)

    # check if user already exists
    result = await db.execute(select(User).where(User.email == token_data["email"]))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # update user account
    user.full_name = full_name
    user.username = username
    user.hashed_password = get_password_hash(password)
    user.invite_accepted = True
    user.is_active = True
    user.joined_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)
    return user