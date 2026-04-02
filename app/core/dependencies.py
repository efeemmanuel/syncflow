from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import sessionmanager

from typing import Annotated
from fastapi import Depends
from app.models.user import User
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.core.security import verify_token, oauth2_scheme
from sqlalchemy import select


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session





async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db_session)]
):
    token_data = await verify_token(token)
    result = await db.execute(select(User).where(User.id == token_data["user_id"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return current_user


async def require_team_lead(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "team_lead":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Team lead required")
    return current_user


async def require_admin_or_lead(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role not in ["admin", "team_lead"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or team lead required")
    return current_user



async def require_same_company(
    company_id: int,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied"
        )
    return current_user