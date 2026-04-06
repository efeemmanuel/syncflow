from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate


async def add_comment(db: AsyncSession, task_id: int, data: CommentCreate, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    comment = Comment(
        content=data.content,
        task_id=task_id,
        user_id=current_user.id,
        company_id=current_user.company_id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(db: AsyncSession, task_id: int, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(Comment).where(Comment.task_id == task_id)
    )
    return result.scalars().all()


async def delete_comment(db: AsyncSession, task_id: int, comment_id: int, current_user: User):
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(Comment).where(Comment.id == comment_id, Comment.task_id == task_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise ValueError("Comment not found")

    # only comment owner or admin can delete
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise ValueError("Access denied")

    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}