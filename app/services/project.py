
from app.schemas.project import ProjectRequest
from app.models.project import Project
from app.models.user import User
from app.core.dependencies import get_db_session,require_admin,require_admin_or_lead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.team import Team
from app.models.project_member import ProjectMembers
from app.models.task import Task







async def create_project(db: AsyncSession, data: ProjectRequest, current_user: User):

    result = await db.execute(
        select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
    )
    if result.scalar_one_or_none():
        raise ValueError("A project with this title exists")
    
    # if team lead, verify team_id belongs to their own team
    if current_user.role == "team_lead":
        if not data.team_id:
            raise ValueError("Team lead must provide a team_id")
        result = await db.execute(
            select(Team).where(Team.id == data.team_id, Team.team_lead_id == current_user.id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("You can only create projects for your own team")

    
    project = Project(
        title = data.title,
        description = data.description,
        company_id = current_user.company_id,
        team_id = data.team_id,
        created_by=current_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project




# GET /projects — Get all projects
# - require_admin_or_lead or member
# - admin sees all company projects
# - team lead sees only their team projects
# - member sees only projects they are assigned to
# - return list
async def get_projects(db: AsyncSession, current_user: User):
    # deciding what to return → role first, then fetch different data based on role.
    if current_user.role == "admin":
        # admin sees all company projects
        result = await db.execute(
            select(Project).where(Project.company_id == current_user.company_id)
        )
    elif current_user.role == "team_lead":
        # team lead sees only their team projects
        result = await db.execute(
            select(Project).where(Project.team_id == current_user.team_id)
        )
    else:
        # member sees only projects they are assigned to
        result = await db.execute(
            select(Project).join(ProjectMembers, ProjectMembers.project_id == Project.id)
            .where(ProjectMembers.user_id == current_user.id)
        )
    return result.scalars().all()






async def get_single_project(db: AsyncSession, project_id: int, current_user: User):
    #  validating something → fetch first, then check if it exists or not.
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise ValueError("Project not found")

    # team lead can only see their own team projects
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    # member can only see projects they are assigned to
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

    # team lead can only update their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    # check duplicate title only if title is being changed
    if data.title and data.title != project.title:
        result = await db.execute(
            select(Project).where(Project.title == data.title, Project.company_id == current_user.company_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("A project with this title already exists")

    # update only fields that are provided
    if data.title:
        project.title = data.title
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

    # team lead can only delete their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    # check project has no active tasks
    result = await db.execute(
        select(Task).where(Task.project_id == project_id, Task.status == "active")
    )
    if result.scalar_one_or_none():
        raise ValueError("Project has active tasks, cannot be deleted")

    await db.delete(project)
    await db.commit()
    return {"message": "Project deleted successfully"}





async def add_project_member(db: AsyncSession, project_id: int, user_id: int, current_user: User):
    # check project exists in company
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    # team lead can only add members to their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    # check user exists in company
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found in this company")

    # check user not already in project
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
    # check project exists in company
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    # team lead can only remove members from their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    # check user is actually in project
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
    # check project exists in company
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.company_id == current_user.company_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError("Project not found")

    # team lead can only see members of their own team project
    if current_user.role == "team_lead" and project.team_id != current_user.team_id:
        raise ValueError("Access denied")

    result = await db.execute(
        select(User).join(ProjectMembers, ProjectMembers.user_id == User.id)
        .where(ProjectMembers.project_id == project_id)
    )
    return result.scalars().all()



# Validating something → fetch first
# Deciding what to return → role first


# 1. Validate — does it exist? is it duplicate? (fetch first)
# 2. Check permissions — who can access what? (role check)
# 3. Perform action — create, fetch, update, delete
# 4. Return result