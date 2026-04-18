from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate


async def add_comment(db: AsyncSession, task_id: int, data: CommentCreate, current_user: User):
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

    # return enriched dict so user_name is included
    return {
        "id": comment.id,
        "content": comment.content,
        "task_id": comment.task_id,
        "user_id": comment.user_id,
        "user_name": current_user.full_name,
        "company_id": comment.company_id,
        "created_at": comment.created_at,
    }


async def get_comments(db: AsyncSession, task_id: int, current_user: User):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()

    output = []
    for c in comments:
        sender = await db.get(User, c.user_id)
        output.append({
            "id": c.id,
            "content": c.content,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "user_name": sender.full_name if sender else "Unknown",
            "company_id": c.company_id,
            "created_at": c.created_at,
        })
    return output


async def delete_comment(db: AsyncSession, task_id: int, comment_id: int, current_user: User):
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

    if comment.user_id != current_user.id and current_user.role != "admin":
        raise ValueError("Access denied")

    await db.delete(comment)
    await db.commit()
    return {"message": "Comment deleted successfully"}