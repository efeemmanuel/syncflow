from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserUpdate

from app.models.company import Company

async def get_me(current_user: User, db: AsyncSession):
    company = await db.get(Company, current_user.company_id)
    # return as dict so company_name is included
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "company_id": current_user.company_id,
        "company_name": company.name if company else None,
        "team_id": current_user.team_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }

async def update_me(db: AsyncSession, data: UserUpdate, current_user: User):
    # check username not already taken
    if data.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        existing = result.scalar_one_or_none()
        if existing and existing.id != current_user.id:
            raise ValueError("Username already taken")
        current_user.username = data.username

    if data.full_name:
        current_user.full_name = data.full_name

    await db.commit()
    await db.refresh(current_user)
    return current_user


async def get_user(db: AsyncSession, user_id: int, current_user: User):
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    return user


async def get_all_users(db: AsyncSession, current_user: User):
    result = await db.execute(
        select(User).where(User.company_id == current_user.company_id)
    )
    return result.scalars().all()