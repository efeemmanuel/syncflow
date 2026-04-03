from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.dependencies import get_db_session, require_admin, require_admin_or_lead
from app.models.user import User
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from app.services.team import (
    create_team, get_teams, get_team,
    update_team, delete_team,
    add_team_member, remove_team_member, get_team_members
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse)
async def create_team_route(
    data: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
    try:
        return await create_team(db, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[TeamResponse])
async def get_teams_route(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await get_teams(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team_route(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await get_team(db, team_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team_route(
    team_id: int,
    data: TeamUpdate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
    try:
        return await update_team(db, team_id, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{team_id}")
async def delete_team_route(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin)]
):
    try:
        return await delete_team(db, team_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{team_id}/members")
async def add_member_route(
    team_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await add_team_member(db, team_id, user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{team_id}/members/{user_id}")
async def remove_member_route(
    team_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await remove_team_member(db, team_id, user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
@router.get("/{team_id}/members")
async def get_members_route(
    team_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await get_team_members(db, team_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))