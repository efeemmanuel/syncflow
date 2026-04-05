from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.dependencies import get_db_session, require_admin_or_lead, get_current_user
from app.models.user import User
from app.schemas.project import ProjectRequest, ProjectResponse
from app.services.project import (
    create_project, get_projects, get_single_project,
    update_project, delete_project
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse)
async def create_project_route(
    data: ProjectRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await create_project(db, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[ProjectResponse])
async def get_projects_route(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_projects(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_single_project_route(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_single_project(db, project_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_route(
    project_id: int,
    data: ProjectRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await update_project(db, data, project_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{project_id}")
async def delete_project_route(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await delete_project(db, project_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))





from app.services.project import add_project_member, remove_project_member, get_project_members

@router.post("/{project_id}/members")
async def add_member_route(
    project_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await add_project_member(db, project_id, user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{project_id}/members/{user_id}")
async def remove_member_route(
    project_id: int,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await remove_project_member(db, project_id, user_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{project_id}/members")
async def get_members_route(
    project_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_admin_or_lead)]
):
    try:
        return await get_project_members(db, project_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))