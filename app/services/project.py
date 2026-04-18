from app.schemas.project import ProjectRequest
from app.models.project import Project
from app.models.user import User
from app.core.dependencies import get_db_session, require_admin, require_admin_or_lead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.team import Team
from app.models.project_member import ProjectMembers
from app.models.task import Task
from app.schemas.project import ProjectRequest, ProjectUpdate
from sqlalchemy import delete
from app.models.task_assign import TaskAssignees
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.project_member import ProjectMembers
from app.models.channels import Channel


async def create_project(db: AsyncSession, data: ProjectRequest, current_user: User):
    result = await db.execute(
        select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
    )
    if result.scalar_one_or_none():
        raise ValueError("A project with this title already exists")

    # auto assign team lead's team
    team_id = data.team_id
    if current_user.role == "team_lead":
        if not current_user.team_id:
            raise ValueError("You are not assigned to a team yet")
        team_id = current_user.team_id

    # for admin creating a multi-team project, use first team_id or None
    if current_user.role == "admin" and data.team_ids and not team_id:
        team_id = data.team_ids[0] if data.team_ids else None

    project = Project(
        title=data.title,
        description=data.description,
        company_id=current_user.company_id,
        team_id=team_id,
        created_by=current_user.id
    )
    db.add(project)
    await db.flush()  # get project.id before creating channel

    # auto-create a channel for this project
    channel = Channel(
        name=data.title,
        company_id=current_user.company_id,
        project_id=project.id,
        is_default=False,
    )
    db.add(channel)

    await db.commit()
    await db.refresh(project)
    return project


async def get_projects(db: AsyncSession, current_user: User):
    if current_user.role == "admin":
        result = await db.execute(
            select(Project).where(Project.company_id == current_user.company_id)
        )
    elif current_user.role == "team_lead":
        result = await db.execute(
            select(Project).where(Project.team_id == current_user.team_id)
        )
    else:
        result = await db.execute(
            select(Project).join(ProjectMembers, ProjectMembers.project_id == Project.id)
            .where(ProjectMembers.user_id == current_user.id)
        )
    return result.scalars().all()


async def get_single_project(db: AsyncSession, project_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    if current_user.role == "member":
        result = await db.execute(
            select(ProjectMembers).where(
                ProjectMembers.project_id == project_id,
                ProjectMembers.user_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise ValueError("Access denied")

    return project


async def update_project(db: AsyncSession, data: ProjectRequest, project_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    if data.title and data.title != project.title:
        result = await db.execute(
            select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("A project with this title already exists")

    if data.title:
        project.title = data.title
        # keep channel name in sync
        ch_result = await db.execute(
            select(Channel).where(Channel.project_id == project_id)
        )
        channel = ch_result.scalar_one_or_none()
        if channel:
            channel.name = data.title

    if data.description:
        project.description = data.description
    if data.status:
        project.status = data.status
    if data.deadline:
        project.deadline = data.deadline

    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    tasks_result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = tasks_result.scalars().all()

    for task in tasks:
        await db.execute(delete(TaskAssignees).where(TaskAssignees.task_id == task.id))
        await db.execute(delete(Comment).where(Comment.task_id == task.id))
        await db.execute(delete(Attachment).where(Attachment.task_id == task.id))

    await db.execute(delete(Task).where(Task.project_id == project_id))
    await db.execute(delete(ProjectMembers).where(ProjectMembers.project_id == project_id))

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}


async def add_project_member(db: AsyncSession, project_id: int, user_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found in this company")

    result = await db.execute(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == user_id
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("User is already in this project")

    member = ProjectMembers(project_id=project_id, user_id=user_id)
    db.add(member)
    await db.commit()
    return {"message": "Member added to project successfully"}


async def remove_project_member(db: AsyncSession, project_id: int, user_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    result = await db.execute(
        select(ProjectMembers).where(
            ProjectMembers.project_id == project_id,
            ProjectMembers.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise ValueError("User is not in this project")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed from project successfully"}


async def get_project_members(db: AsyncSession, project_id: int, current_user: User):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    result = await db.execute(
        select(User).join(ProjectMembers, ProjectMembers.user_id == User.id)
        .where(ProjectMembers.project_id == project_id)
    )
    return result.scalars().all()


















# from app.schemas.project import ProjectRequest
# from app.models.project import Project
# from app.models.user import User
# from app.core.dependencies import get_db_session,require_admin,require_admin_or_lead
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from app.models.team import Team
# from app.models.project_member import ProjectMembers
# from app.models.task import Task
# from app.schemas.project import ProjectRequest, ProjectUpdate
# from sqlalchemy import delete
# from app.models.task_assign import TaskAssignees
# from app.models.comment import Comment
# from app.models.attachment import Attachment
# from app.models.project_member import ProjectMembers







# async def create_project(db: AsyncSession, data: ProjectRequest, current_user: User):
#     result = await db.execute(
#         select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
#     )
#     if result.scalar_one_or_none():
#         raise ValueError("A project with this title already exists")

#     # auto assign team lead's team
#     team_id = data.team_id
#     if current_user.role == "team_lead":
#         if not current_user.team_id:
#             raise ValueError("You are not assigned to a team yet")
#         team_id = current_user.team_id

#     project = Project(
#         title=data.title,
#         description=data.description,
#         company_id=current_user.company_id,
#         team_id=team_id,
#         created_by=current_user.id
#     )
#     db.add(project)
#     await db.commit()
#     await db.refresh(project)
#     return project



# # GET /projects — Get all projects
# # - require_admin_or_lead or member
# # - admin sees all company projects
# # - team lead sees only their team projects
# # - member sees only projects they are assigned to
# # - return list
# async def get_projects(db: AsyncSession, current_user: User):
#     # deciding what to return → role first, then fetch different data based on role.
#     if current_user.role == "admin":
#         # admin sees all company projects
#         result = await db.execute(
#             select(Project).where(Project.company_id == current_user.company_id)
#         )
#     elif current_user.role == "team_lead":
#         # team lead sees only their team projects
#         result = await db.execute(
#             select(Project).where(Project.team_id == current_user.team_id)
#         )
#     else:
#         # member sees only projects they are assigned to
#         result = await db.execute(
#             select(Project).join(ProjectMembers, ProjectMembers.project_id == Project.id)
#             .where(ProjectMembers.user_id == current_user.id)
#         )
#     return result.scalars().all()






# async def get_single_project(db: AsyncSession, project_id: int, current_user: User):
#     #  validating something → fetch first, then check if it exists or not.
#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()

#     if not project:
#         raise ValueError("Project not found")

#     # team lead can only see their own team projects
#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     # member can only see projects they are assigned to
#     if current_user.role == "member":
#         result = await db.execute(
#             select(ProjectMembers).where(
#                 ProjectMembers.project_id == project_id,
#                 ProjectMembers.user_id == current_user.id
#             )
#         )
#         if not result.scalar_one_or_none():
#             raise ValueError("Access denied")

#     return project





# async def update_project(db: AsyncSession, data: ProjectRequest, project_id: int, current_user: User):

#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()
#     if not project:
#         raise ValueError("Project not found")

#     # team lead can only update their own team project
#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     # check duplicate title only if title is being changed
#     if data.title and data.title != project.title:
#         result = await db.execute(
#             select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
#         )
#         if result.scalar_one_or_none():
#             raise ValueError("A project with this title already exists")

#     # update only fields that are provided
#     if data.title:
#         project.title = data.title
#     if data.description:
#         project.description = data.description
#     if data.status:
#         project.status = data.status
#     if data.deadline:
#         project.deadline = data.deadline

#     await db.commit()
#     await db.refresh(project)
#     return project








# async def delete_project(db: AsyncSession, project_id: int, current_user: User):
#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()
#     if not project:
#         raise ValueError("Project not found")

#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     # get all project tasks
#     tasks_result = await db.execute(select(Task).where(Task.project_id == project_id))
#     tasks = tasks_result.scalars().all()

#     # delete task related records
#     for task in tasks:
#         await db.execute(delete(TaskAssignees).where(TaskAssignees.task_id == task.id))
#         await db.execute(delete(Comment).where(Comment.task_id == task.id))
#         await db.execute(delete(Attachment).where(Attachment.task_id == task.id))

#     # delete tasks
#     await db.execute(delete(Task).where(Task.project_id == project_id))

#     # delete project members
#     await db.execute(delete(ProjectMembers).where(ProjectMembers.project_id == project_id))

#     await db.delete(project)
#     await db.commit()
#     return {"message": "Project deleted successfully"}



# async def add_project_member(db: AsyncSession, project_id: int, user_id: int, current_user: User):
#     # check project exists in company
#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()
#     if not project:
#         raise ValueError("Project not found")

#     # team lead can only add members to their own team project
#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     # check user exists in company
#     result = await db.execute(
#         select(User).where(User.id == user_id, User.company_id == current_user.company_id)
#     )
#     user = result.scalar_one_or_none()
#     if not user:
#         raise ValueError("User not found in this company")

#     # check user not already in project
#     result = await db.execute(
#         select(ProjectMembers).where(
#             ProjectMembers.project_id == project_id,
#             ProjectMembers.user_id == user_id
#         )
#     )
#     if result.scalar_one_or_none():
#         raise ValueError("User is already in this project")

#     member = ProjectMembers(project_id=project_id, user_id=user_id)
#     db.add(member)
#     await db.commit()
#     return {"message": "Member added to project successfully"}


# async def remove_project_member(db: AsyncSession, project_id: int, user_id: int, current_user: User):
#     # check project exists in company
#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()
#     if not project:
#         raise ValueError("Project not found")

#     # team lead can only remove members from their own team project
#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     # check user is actually in project
#     result = await db.execute(
#         select(ProjectMembers).where(
#             ProjectMembers.project_id == project_id,
#             ProjectMembers.user_id == user_id
#         )
#     )
#     member = result.scalar_one_or_none()
#     if not member:
#         raise ValueError("User is not in this project")

#     await db.delete(member)
#     await db.commit()
#     return {"message": "Member removed from project successfully"}


# async def get_project_members(db: AsyncSession, project_id: int, current_user: User):
#     # check project exists in company
#     result = await db.execute(
#         select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
#     )
#     project = result.scalar_one_or_none()
#     if not project:
#         raise ValueError("Project not found")

#     # team lead can only see members of their own team project
#     if current_user.role == "team_lead" and project.team_id != current_user.team_id:
#         raise ValueError("Access denied")

#     result = await db.execute(
#         select(User).join(ProjectMembers, ProjectMembers.user_id == User.id)
#         .where(ProjectMembers.project_id == project_id)
#     )
#     return result.scalars().all()



# # Validating something → fetch first
# # Deciding what to return → role first


# # 1. Validate — does it exist? is it duplicate? (fetch first)
# # 2. Check permissions — who can access what? (role check)
# # 3. Perform action — create, fetch, update, delete
# # 4. Return result