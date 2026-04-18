"""
PASTE THIS INTO: app/services/company.py

Changes from original:
1. register_company() now auto-creates a default Channel for the company
2. Everything else is unchanged

Only the register_company function is modified — copy/replace just that function,
or replace the whole file with this content.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.company import Company
from app.models.user import User
from app.models.team import Team
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
from app.models.channels import Channel  # NEW IMPORT


async def register_company(db: AsyncSession, data: CompanyRegister):
    # check if company email already exists
    result = await db.execute(select(Company).where(Company.email == data.email))
    if result.scalar_one_or_none():
        raise ValueError("Company with this email already exists")

    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ValueError("User with this email already exists")

    company = Company(
        name=data.name,
        email=data.email,
        slug=data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8],
    )
    db.add(company)
    await db.flush()

    admin = User(
        full_name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role="admin",
        company_id=company.id,
        is_active=True,
        invite_accepted=True,
    )
    db.add(admin)
    await db.flush()

    # AUTO-CREATE default general channel for the company
    general_channel = Channel(
        name="general",
        company_id=company.id,
        project_id=None,
        is_default=True,
    )
    db.add(general_channel)

    await db.commit()
    await db.refresh(company)
    return company


# ── Everything below is UNCHANGED from the original ──────────────────────────

async def verify_company_otp(db: AsyncSession, email: str, otp: str):
    is_valid = await verify_otp(email, otp)
    if not is_valid:
        raise ValueError("Invalid or expired OTP")

    result = await db.execute(select(Company).where(Company.email == email))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError("Company not found")

    company.is_verified = True
    company.is_active = True
    await db.commit()
    await db.refresh(company)
    return company


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
    await redis_client.setex(f"blacklist:{token}", 1800, "blacklisted")
    await redis_client.delete(f"refresh:{user_id}")
    return {"message": "Logged out successfully"}


async def send_admin_invite(db: AsyncSession, company_id: int, admin_email: str):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise ValueError("Company not found")

    token = await save_invite_token(admin_email, company_id, "admin")
    await send_admin_invite_email(admin_email, token, company.name)
    return {"message": "Invite sent successfully"}


async def accept_admin_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
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


async def invite_team_lead(db: AsyncSession, company_id: int, email: str, team_id: int, current_user: User):
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise ValueError("User with this email already exists")

    team_lead = User(
        email=email,
        full_name="Invited User",
        role="team_lead",
        company_id=company_id,
        team_id=team_id,
    )
    db.add(team_lead)
    await db.flush()

    team.team_lead_id = team_lead.id

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

    await db.flush()

    if user.team_id:
        from app.models.team_members import TeamMembers
        existing = await db.execute(
            select(TeamMembers).where(
                TeamMembers.team_id == user.team_id,
                TeamMembers.user_id == user.id
            )
        )
        if not existing.scalar_one_or_none():
            team_member = TeamMembers(team_id=user.team_id, user_id=user.id)
            db.add(team_member)

    await db.commit()
    await db.refresh(user)
    return user


async def invite_member(db: AsyncSession, company_id: int, email: str, team_id: int):
    result = await db.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()

    if existing:
        if existing.company_id == company_id:
            existing.team_id = team_id
            existing.is_active = True

            from app.models.team_members import TeamMembers
            team_member_check = await db.execute(
                select(TeamMembers).where(
                    TeamMembers.team_id == team_id,
                    TeamMembers.user_id == existing.id
                )
            )
            if not team_member_check.scalar_one_or_none():
                team_member = TeamMembers(team_id=team_id, user_id=existing.id)
                db.add(team_member)

            await db.commit()
            return {"message": "Member re-added to team successfully"}
        else:
            raise ValueError("User with this email already exists in another company")

    member = User(
        email=email,
        full_name="Invited User",
        role="member",
        company_id=company_id,
        team_id=team_id,
    )
    db.add(member)
    await db.flush()

    token = await save_invite_token(email, company_id, "member")
    await send_invite_email(email, token, "member")
    await db.commit()
    return {"message": "Invite sent successfully"}


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

    await db.flush()

    if user.team_id:
        from app.models.team_members import TeamMembers
        existing = await db.execute(
            select(TeamMembers).where(
                TeamMembers.team_id == user.team_id,
                TeamMembers.user_id == user.id
            )
        )
        if not existing.scalar_one_or_none():
            team_member = TeamMembers(team_id=user.team_id, user_id=user.id)
            db.add(team_member)

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


















# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.models.company import Company
# from app.models.user import User
# from app.models.team import Team
# from app.schemas.company import CompanyRegister
# from app.core.security import get_password_hash
# from app.utils.otp import verify_otp
# from app.core.security import verify_password, create_access_token
# from datetime import timedelta
# from app.core.config import settings

# from app.core.security import save_invite_token
# from app.core.security import verify_invite_token
# from datetime import datetime, timedelta
# from app.utils.email import send_admin_invite_email, send_invite_email
# import uuid
# from app.core.security import verify_password, create_access_token, create_refresh_token
# from app.core.redis import redis_client
# import jwt
# from app.utils.otp import generate_otp, save_otp, verify_otp
# from app.utils.email import send_otp_email



# # async def register_company(db: AsyncSession, data: CompanyRegister):
# #     result = await db.execute(select(Company).where(Company.email == data.email))
# #     existing = result.scalar_one_or_none()
# #     if existing:
# #         raise ValueError("Company with this email already exists")

# #     company = Company(
# #         name=data.name,
# #         email=data.email,
# #         slug=data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8],
# #     )
# #     db.add(company)
# #     await db.flush()

    
# #     admin = User(
# #     full_name=data.name,
# #     email=data.admin_email,
# #     hashed_password=get_password_hash(data.password),
# #     role="admin",
# #     company_id=company.id,
# #     )
# #     db.add(admin)
# #     await db.commit()
# #     await db.refresh(company)
# #     return company


# async def register_company(db: AsyncSession, data: CompanyRegister):
#     # check if company email already exists
#     result = await db.execute(select(Company).where(Company.email == data.email))
#     if result.scalar_one_or_none():
#         raise ValueError("Company with this email already exists")

#     # check if user with company email already exists
#     result = await db.execute(select(User).where(User.email == data.email))
#     if result.scalar_one_or_none():
#         raise ValueError("User with this email already exists")

#     # create company
#     company = Company(
#         name=data.name,
#         email=data.email,
#         slug=data.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8],
#     )
#     db.add(company)
#     await db.flush()

#     # create admin user with COMPANY email and password
#     admin = User(
#         full_name=data.name,
#         email=data.email,  # company email is the login email
#         hashed_password=get_password_hash(data.password),
#         role="admin",
#         company_id=company.id,
#         is_active=True,
#         invite_accepted=True,
#     )
#     db.add(admin)
#     await db.commit()
#     await db.refresh(company)
#     return company



# # Company submits email + OTP code
# # Verify function checks Redis → marks company active
# async def verify_company_otp(db: AsyncSession, email: str, otp: str):
#     # verify otp from redis
#     is_valid = await verify_otp(email, otp)
#     if not is_valid:
#         raise ValueError("Invalid or expired OTP")

#     # get company by email
#     result = await db.execute(select(Company).where(Company.email == email))
#     company = result.scalar_one_or_none()
#     if not company:
#         raise ValueError("Company not found")

#     # mark company as verified and active
#     company.is_verified = True
#     company.is_active = True
#     await db.commit()
#     await db.refresh(company)
#     return company





# # company log in with email and password

# async def login_company(db: AsyncSession, email: str, password: str):
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("Invalid credentials")

#     if not verify_password(password, user.hashed_password):
#         raise ValueError("Invalid credentials")

#     company_result = await db.execute(select(Company).where(Company.id == user.company_id))
#     company = company_result.scalar_one_or_none()
#     if not company.is_verified:
#         raise ValueError("Company not verified")

#     access_token = create_access_token(
#         data={"user_id": user.id, "company_id": user.company_id, "role": user.role},
#         expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
#     )
#     refresh_token = create_refresh_token(
#         data={"user_id": user.id, "company_id": user.company_id, "role": user.role}
#     )

#     await redis_client.setex(f"refresh:{user.id}", 604800, refresh_token)

#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}






# async def refresh_access_token(refresh_token: str):
#     try:
#         payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
#         user_id = payload.get("user_id")
#         stored = await redis_client.get(f"refresh:{user_id}")
#         if not stored or stored != refresh_token:
#             raise ValueError("Invalid refresh token")
#         access_token = create_access_token(
#             data={"user_id": user_id, "company_id": payload.get("company_id"), "role": payload.get("role")}
#         )
#         return {"access_token": access_token, "token_type": "bearer"}
#     except Exception:
#         raise ValueError("Invalid refresh token")


# async def logout(user_id: int, token: str):
#     # blacklist access token
#     await redis_client.setex(f"blacklist:{token}", 1800, "blacklisted")
#     # delete refresh token
#     await redis_client.delete(f"refresh:{user_id}")
#     return {"message": "Logged out successfully"}





# async def send_admin_invite(db: AsyncSession, company_id: int, admin_email: str):
#     # check if company exists
#     result = await db.execute(select(Company).where(Company.id == company_id))
#     company = result.scalar_one_or_none()
#     if not company:
#         raise ValueError("Company not found")

#     # generate and save invite token
#     token = await save_invite_token(admin_email, company_id, "admin")

#     # send invite email
#     await send_admin_invite_email(admin_email, token, company.name)
#     return {"message": "Invite sent successfully"}





# async def accept_admin_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
#     # verify token from redis
#     token_data = await verify_invite_token(token)

#     # check if user already exists
#     result = await db.execute(select(User).where(User.email == token_data["email"]))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found")

#     # update user account
#     user.full_name = full_name
#     user.username = username
#     user.hashed_password = get_password_hash(password)
#     user.invite_accepted = True
#     user.is_active = True
#     user.joined_at = datetime.utcnow()

#     await db.commit()
#     await db.refresh(user)
#     return user




# async def invite_team_lead(db: AsyncSession, company_id: int, email: str, team_id: int, current_user: User):
#     # check team exists
#     result = await db.execute(
#         select(Team).where(Team.id == team_id, Team.company_id == company_id)
#     )
#     team = result.scalar_one_or_none()
#     if not team:
#         raise ValueError("Team not found")

#     # check email not already in use
#     result = await db.execute(select(User).where(User.email == email))
#     if result.scalar_one_or_none():
#         raise ValueError("User with this email already exists")

#     # create team lead user
#     team_lead = User(
#         email=email,
#         full_name="Invited User",
#         role="team_lead",
#         company_id=company_id,
#         team_id=team_id,
#     )
#     db.add(team_lead)
#     await db.flush()

#     # update team with this team lead
#     team.team_lead_id = team_lead.id

#     # generate and send invite token
#     token = await save_invite_token(email, company_id, "team_lead")
#     await send_invite_email(email, token, "team_lead")
#     await db.commit()
#     return {"message": "Team lead invited successfully"}




# async def accept_team_lead_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
#     token_data = await verify_invite_token(token)

#     result = await db.execute(select(User).where(User.email == token_data["email"]))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found")

#     user.full_name = full_name
#     user.username = username
#     user.hashed_password = get_password_hash(password)
#     user.invite_accepted = True
#     user.is_active = True
#     user.joined_at = datetime.utcnow()

#     await db.flush()

#     # add team lead to their team
#     if user.team_id:
#         from app.models.team_members import TeamMembers
#         existing = await db.execute(
#             select(TeamMembers).where(
#                 TeamMembers.team_id == user.team_id,
#                 TeamMembers.user_id == user.id
#             )
#         )
#         if not existing.scalar_one_or_none():
#             team_member = TeamMembers(team_id=user.team_id, user_id=user.id)
#             db.add(team_member)

#     await db.commit()
#     await db.refresh(user)
#     return user




# async def invite_member(db: AsyncSession, company_id: int, email: str, team_id: int):
#     result = await db.execute(select(User).where(User.email == email))
#     existing = result.scalar_one_or_none()
    
#     if existing:
#         # if user exists but was removed from team, reassign them
#         if existing.company_id == company_id:
#             existing.team_id = team_id
#             existing.is_active = True
            
#             # add back to team members
#             from app.models.team_members import TeamMembers
#             team_member_check = await db.execute(
#                 select(TeamMembers).where(
#                     TeamMembers.team_id == team_id,
#                     TeamMembers.user_id == existing.id
#                 )
#             )
#             if not team_member_check.scalar_one_or_none():
#                 team_member = TeamMembers(team_id=team_id, user_id=existing.id)
#                 db.add(team_member)
            
#             await db.commit()
#             return {"message": "Member re-added to team successfully"}
#         else:
#             raise ValueError("User with this email already exists in another company")

#     member = User(
#         email=email,
#         full_name="Invited User",
#         role="member",
#         company_id=company_id,
#         team_id=team_id,
#     )
#     db.add(member)
#     await db.flush()

#     token = await save_invite_token(email, company_id, "member")
#     await send_invite_email(email, token, "member")
#     await db.commit()
#     return {"message": "Invite sent successfully"}




# async def accept_member_invite(db: AsyncSession, token: str, full_name: str, username: str, password: str):
#     token_data = await verify_invite_token(token)

#     result = await db.execute(select(User).where(User.email == token_data["email"]))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found")

#     user.full_name = full_name
#     user.username = username
#     user.hashed_password = get_password_hash(password)
#     user.invite_accepted = True
#     user.is_active = True
#     user.joined_at = datetime.utcnow()

#     await db.flush()

#     # add user to their team
#     if user.team_id:
#         from app.models.team_members import TeamMembers
#         existing = await db.execute(
#             select(TeamMembers).where(
#                 TeamMembers.team_id == user.team_id,
#                 TeamMembers.user_id == user.id
#             )
#         )
#         if not existing.scalar_one_or_none():
#             team_member = TeamMembers(team_id=user.team_id, user_id=user.id)
#             db.add(team_member)

#     await db.commit()
#     await db.refresh(user)
#     return user


# async def forgot_password(db: AsyncSession, email: str):
#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found")

#     otp = generate_otp()
#     await save_otp(email, otp)
#     await send_otp_email(email, otp)
#     return {"message": "OTP sent to your email"}


# async def reset_password(db: AsyncSession, email: str, otp: str, new_password: str):
#     is_valid = await verify_otp(email, otp)
#     if not is_valid:
#         raise ValueError("Invalid or expired OTP")

#     result = await db.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found")

#     user.hashed_password = get_password_hash(new_password)
#     await db.commit()
#     return {"message": "Password reset successfully"}