from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.schemas.attachment import AttachmentCreate, AttachmentResponse
from app.services.attachment import add_attachment, get_attachments, delete_attachment

router = APIRouter(prefix="/tasks", tags=["attachments"])


@router.post("/{task_id}/attachments", response_model=AttachmentResponse)
async def add_attachment_route(
    task_id: int,
    data: AttachmentCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await add_attachment(db, task_id, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{task_id}/attachments", response_model=list[AttachmentResponse])
async def get_attachments_route(
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_attachments(db, task_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{task_id}/attachments/{attachment_id}")
async def delete_attachment_route(
    task_id: int,
    attachment_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await delete_attachment(db, task_id, attachment_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))