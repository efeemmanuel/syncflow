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
from app.utils.email import send_admin_invite_email, send_invite_email
import uuid
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.redis import redis_client
import jwt
from app.utils.otp import generate_otp, save_otp, verify_otp
from app.utils.email import send_otp_email



async def register_company(db: AsyncSession, data: CompanyRegister):
    result = await db.execute(select(Company).where(Company.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("Company with this email already exists")

    company = Company(
        name=data.name,
        email=data.email,
        slug=data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8],
    )
    db.add(company)
    await db.flush()

    
    admin = User(
    full_name=data.name,
    email=data.admin_email,
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

    company_result = await db.execute(select(Company).where(Company.id == user.company_id))
    company = company_result.scalar_one_or_none()
    if not company.is_verified:
        raise ValueError("Company not verified")

    access_token = create_access_token(
        data={"user_id": user.id, "company_id": user.company_id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = create_refresh_token(
        data={"user_id": user.id, "company_id": user.company_id, "role": user.role}
    )

    await redis_client.setex(f"refresh:{user.id}", 604800, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}






async def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("user_id")
        stored = await redis_client.get(f"refresh:{user_id}")
        if not stored or stored != refresh_token:
            raise ValueError("Invalid refresh token")
        access_token = create_access_token(
            data={"user_id": user_id, "company_id": payload.get("company_id"), "role": payload.get("role")}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception:
        raise ValueError("Invalid refresh token")


async def logout(user_id: int, token: str):
    # blacklist access token
    await redis_client.setex(f"blacklist:{token}", 1800, "blacklisted")
    # delete refresh token
    await redis_client.delete(f"refresh:{user_id}")
    return {"message": "Logged out successfully"}





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





async def invite_team_lead(db: AsyncSession, company_id: int, email: str, current_user: User):
    # check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("User with this email already exists")

    # create team lead user
    team_lead = User(
        email=email,
        role="team_lead",
        company_id=company_id,
    )
    db.add(team_lead)
    await db.flush()

    # generate and send invite token
    token = await save_invite_token(email, company_id, "team_lead")
    await send_invite_email(email, token, "team_lead")
    await db.commit()
    return {"message": "Team lead invited successfully"}


async def accept_team_lead_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
    token_data = await verify_invite_token(token)

    result = await db.execute(select(User).where(User.email == token_data["email"]))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    user.full_name = full_name
    user.username = username
    user.hashed_password = get_password_hash(password)
    user.invite_accepted = True
    user.is_active = True
    user.joined_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)
    return user




async def invite_member(db: AsyncSession, company_id: int, email: str, team_id: int):
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("User with this email already exists")

    member = User(
        email=email,
        role="member",
        company_id=company_id,
        team_id=team_id,
    )
    db.add(member)
    await db.flush()

    token = await save_invite_token(email, company_id, "member")
    await send_invite_email(email, token, "member")
    await db.commit()
    return {"message": "Member invited successfully"}


async def accept_member_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
    token_data = await verify_invite_token(token)

    result = await db.execute(select(User).where(User.email == token_data["email"]))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    user.full_name = full_name
    user.username = username
    user.hashed_password = get_password_hash(password)
    user.invite_accepted = True
    user.is_active = True
    user.joined_at = datetime.utcnow()

    await db.commit()
    await db.refresh(user)
    return user




async def forgot_password(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    otp = generate_otp()
    await save_otp(email, otp)
    await send_otp_email(email, otp)
    return {"message": "OTP sent to your email"}


async def reset_password(db: AsyncSession, email: str, otp: str, new_password: str):
    is_valid = await verify_otp(email, otp)
    if not is_valid:
        raise ValueError("Invalid or expired OTP")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    user.hashed_password = get_password_hash(new_password)
    await db.commit()
    return {"message": "Password reset successfully"}