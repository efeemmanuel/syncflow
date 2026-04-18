from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.channels import Channel
from app.models.channel_message import ChannelMessage
from app.models.project_member import ProjectMembers
from app.models.user import User
from app.schemas.channel import MessageCreate


async def get_channels(db: AsyncSession, current_user: User):
    """Return all channels visible to the user:
    - Default company channel: everyone
    - Project channels: only project members
    """
    result = await db.execute(
        select(Channel).where(Channel.company_id == current_user.company_id)
    )
    all_channels = result.scalars().all()

    visible = []
    for ch in all_channels:
        if ch.is_default:
            visible.append(ch)
        elif ch.project_id:
            # admin and team lead see all project channels in their company
            if current_user.role in ("admin", "team_lead"):
                visible.append(ch)
            else:
                # member: only if assigned to project
                pm = await db.execute(
                    select(ProjectMembers).where(
                        ProjectMembers.project_id == ch.project_id,
                        ProjectMembers.user_id == current_user.id
                    )
                )
                if pm.scalar_one_or_none():
                    visible.append(ch)

    return visible


async def get_channel_messages(db: AsyncSession, channel_id: int, current_user: User):
    # verify user can access this channel
    channel = await _get_accessible_channel(db, channel_id, current_user)
    if not channel:
        raise ValueError("Channel not found or access denied")

    result = await db.execute(
        select(ChannelMessage)
        .where(ChannelMessage.channel_id == channel_id)
        .order_by(ChannelMessage.created_at.asc())
    )
    messages = result.scalars().all()

    # enrich with sender name
    output = []
    for msg in messages:
        sender = await db.get(User, msg.sender_id)
        output.append({
            "id": msg.id,
            "channel_id": msg.channel_id,
            "sender_id": msg.sender_id,
            "sender_name": sender.full_name if sender else "Unknown",
            "content": msg.content,
            "reply_to_id": msg.reply_to_id,
            "created_at": msg.created_at,
        })
    return output


async def send_message(db: AsyncSession, channel_id: int, data: MessageCreate, current_user: User):
    channel = await _get_accessible_channel(db, channel_id, current_user)
    if not channel:
        raise ValueError("Channel not found or access denied")

    message = ChannelMessage(
        channel_id=channel_id,
        sender_id=current_user.id,
        content=data.content,
        reply_to_id=data.reply_to_id,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return {
        "id": message.id,
        "channel_id": message.channel_id,
        "sender_id": message.sender_id,
        "sender_name": current_user.full_name,
        "content": message.content,
        "reply_to_id": message.reply_to_id,
        "created_at": message.created_at,
    }


async def delete_message(db: AsyncSession, channel_id: int, message_id: int, current_user: User):
    result = await db.execute(
        select(ChannelMessage).where(
            ChannelMessage.id == message_id,
            ChannelMessage.channel_id == channel_id
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise ValueError("Message not found")

    if message.sender_id != current_user.id and current_user.role != "admin":
        raise ValueError("Access denied")

    await db.delete(message)
    await db.commit()
    return {"message": "Message deleted"}


async def _get_accessible_channel(db: AsyncSession, channel_id: int, current_user: User):
    result = await db.execute(
        select(Channel).where(
            Channel.id == channel_id,
            Channel.company_id == current_user.company_id
        )
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return None

    if channel.is_default:
        return channel

    if current_user.role in ("admin", "team_lead"):
        return channel

    # member: check project membership
    if channel.project_id:
        pm = await db.execute(
            select(ProjectMembers).where(
                ProjectMembers.project_id == channel.project_id,
                ProjectMembers.user_id == current_user.id
            )
        )
        if pm.scalar_one_or_none():
            return channel

    return None