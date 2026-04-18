from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.dependencies import get_db_session, get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserUpdate, UserResponse
from app.services.user import get_me, update_me, get_user, get_all_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me_route(
    db: Annotated[AsyncSession, Depends(get_db_session)],   # ← add db
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await get_me(current_user, db)   # ← pass db


@router.put("/me", response_model=UserResponse)
async def update_me_route(
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await update_me(db, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_route(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_user(db, user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[UserResponse])
async def get_all_users_route(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
    try:
        return await get_all_users(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))