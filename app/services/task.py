from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.task import Task
from app.models.project import Project
from app.models.user import User
from app.models.task_assign import TaskAssignees
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task_assign import TaskAssignees
from app.models.comment import Comment
from app.models.attachment import Attachment
from sqlalchemy import delete


async def create_task(db: AsyncSession, data: TaskCreate, current_user: User):
    # check project exists in company
    result = await db.execute(
        select(Project).where(Project.id == data.project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    # team lead can only create tasks for their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("You can only create tasks for your own team project")

    task = Task(
        title=data.title,
        description=data.description,
        project_id=data.project_id,
        company_id=current_user.company_id,
        created_by=current_user.id,
        priority=data.priority,
        deadline=data.deadline
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks(db: AsyncSession, current_user: User):
    if current_user.role == "admin":
        # admin sees all company tasks
        result = await db.execute(
            select(Task).where(Task.company_id == current_user.company_id)
        )
    elif current_user.role == "team_lead":
        # team lead sees only tasks in their team projects
        result = await db.execute(
            select(Task).join(Project, Project.id == Task.project_id)
            .where(Project.team_id == current_user.team_id)
        )
    else:
        # member sees only tasks assigned to them
        result = await db.execute(
            select(Task).join(TaskAssignees, TaskAssignees.task_id == Task.id)
            .where(TaskAssignees.user_id == current_user.id)
        )
    return result.scalars().all()


async def get_single_task(db: AsyncSession, task_id: int, current_user: User):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    # team lead can only see tasks in their team projects
    if current_user.role == "team_lead":
        result = await db.execute(
            select(Project).where(Project.id == task.project_id, Project.team_id == current_user.team_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Access denied")

    # member can only see tasks assigned to them
    if current_user.role == "member":
        result = await db.execute(
            select(TaskAssignees).where(
                TaskAssignees.task_id == task_id,
                TaskAssignees.user_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise ValueError("Access denied")

    return task


async def update_task(db: AsyncSession, task_id: int, data: TaskUpdate, current_user: User):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    # members can only update status of their assigned tasks
    if current_user.role == "member":
        
        result = await db.execute(
            select(TaskAssignees).where(
                TaskAssignees.task_id == task_id,
                TaskAssignees.user_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise ValueError("You are not assigned to this task")
        # member can only update status
        if data.status:
            task.status = data.status
        await db.commit()
        await db.refresh(task)
        return task

    # admin/team lead can update everything
    if current_user.role == "team_lead":
        result = await db.execute(
            select(Project).where(Project.id == task.project_id, Project.team_id == current_user.team_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Access denied")

    if data.title:
        task.title = data.title
    if data.description:
        task.description = data.description
    if data.status:
        task.status = data.status
    if data.priority:
        task.priority = data.priority
    if data.deadline:
        task.deadline = data.deadline

    await db.commit()
    await db.refresh(task)
    return task







async def delete_task(db: AsyncSession, task_id: int, current_user: User):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    if current_user.role == "team_lead":
        result = await db.execute(
            select(Project).where(Project.id == task.project_id, Project.team_id == current_user.team_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Access denied")

    # delete related records first
    await db.execute(delete(TaskAssignees).where(TaskAssignees.task_id == task_id))
    await db.execute(delete(Comment).where(Comment.task_id == task_id))
    await db.execute(delete(Attachment).where(Attachment.task_id == task_id))

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}






async def assign_task(db: AsyncSession, task_id: int, user_id: int, current_user: User):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise ValueError("Task not found")

    # check user exists in company
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found in this company")

    # auto add to project members if not already there
    from app.models.project_member import ProjectMembers
    result = await db.execute(
        select(ProjectMembers).where(
            ProjectMembers.project_id == task.project_id,
            ProjectMembers.user_id == user_id
        )
    )
    if not result.scalar_one_or_none():
        project_member = ProjectMembers(project_id=task.project_id, user_id=user_id)
        db.add(project_member)


    result = await db.execute(
        select(TaskAssignees).where(
            TaskAssignees.task_id == task_id,
            TaskAssignees.user_id == user_id
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("User is already assigned to this task")

    assignee = TaskAssignees(task_id=task_id, user_id=user_id)
    db.add(assignee)
    await db.commit()
    return {"message": "Task assigned successfully"}

async def get_task_assignees(db: AsyncSession, task_id: int, current_user: User):
    
    # check task exists in company
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.company_id == current_user.company_id)
    )
    if not result.scalar_one_or_none():
        raise ValueError("Task not found")

    result = await db.execute(
        select(User).join(TaskAssignees, TaskAssignees.user_id == User.id)
        .where(TaskAssignees.task_id == task_id)
    )
    return result.scalars().all()







# In get_comments — enrich with user name
async def get_comments(db: AsyncSession, task_id: int, current_user: User):
    result = await db.execute(
        select(Comment).where(Comment.task_id == task_id)
    )
    comments = result.scalars().all()
    
    output = []
    for c in comments:
        sender = await db.get(User, c.user_id)
        output.append({
            "id": c.id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "user_name": sender.full_name if sender else "Unknown",
            "content": c.content,
            "created_at": c.created_at,
        })
    return output