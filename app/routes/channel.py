from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List
from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.schemas.channel import ChannelResponse, MessageCreate, MessageResponse
from app.services.channel import get_channels, get_channel_messages, send_message, delete_message
from app.schemas.channel import ChannelCreate

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("/", response_model=List[ChannelResponse])
async def get_channels_route(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_channels(db, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{channel_id}/messages")
async def get_messages_route(
    channel_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await get_channel_messages(db, channel_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{channel_id}/messages")
async def send_message_route(
    channel_id: int,
    data: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await send_message(db, channel_id, data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{channel_id}/messages/{message_id}")
async def delete_message_route(
    channel_id: int,
    message_id: int,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return await delete_message(db, channel_id, message_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    





@router.post("/", response_model=ChannelResponse)
async def create_channel_route(
    data: ChannelCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    from app.models.channels import Channel
    channel = Channel(
        name=data.name,
        company_id=current_user.company_id,
        project_id=data.project_id,
        is_default=False,
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    return channel