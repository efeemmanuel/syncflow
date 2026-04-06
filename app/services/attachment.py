from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.attachment import Attachment
from app.models.task import Task
from app.models.user import User
from app.schemas.attachment import AttachmentCreate


async def add_attachment(db: AsyncSession, task_id: int, data: AttachmentCreate, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    attachment = Attachment(
        file_url=data.file_url,
        file_type=data.file_type,
        task_id=task_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)
    return attachment


async def get_attachments(db: AsyncSession, task_id: int, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(Attachment).where(Attachment.task_id == task_id)
    )
    return result.scalars().all()


async def delete_attachment(db: AsyncSession, task_id: int, attachment_id: int, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(Attachment).where(Attachment.id == attachment_id, Attachment.task_id == task_id)
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise ValueError("Attachment not found")

    # only attachment owner or admin can delete
    if attachment.user_id != current_user.id and current_user.role != "admin":
        raise ValueError("Access denied")

    await db.delete(attachment)
    await db.commit()
    return {"message": "Attachment deleted successfully"}