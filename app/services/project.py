
from app.schemas.project import ProjectRequest
from app.models.project import Project
from app.models.user import User
from app.core.dependencies import get_db_session,require_admin,require_admin_or_lead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.team import Team




# async def create_team(db: AsyncSession, data: TeamCreate, current_user: User):
#     # check team name doesn't already exist in this company
#     result = await db.execute(
#         select(Team).where(Team.name == data.name, Team.company_id == current_user.company_id)
#     )
#     if result.scalar_one_or_none():
#         raise ValueError("Team name already exists in this company")

#     # check team lead exists and belongs to same company
#     result = await db.execute(
#         select(User).where(User.id == data.team_lead_id, User.company_id == current_user.company_id)
#     )
#     team_lead = result.scalar_one_or_none()
#     if not team_lead:
#         raise ValueError("Team lead not found in this company")

#     # check user actually has team lead role
#     if team_lead.role != "team_lead":
#         raise ValueError("User is not a team lead")

#     team = Team(
#         name=data.name,
#         company_id=current_user.company_id,
#         team_lead_id=data.team_lead_id
#     )
#     db.add(team)
#     await db.commit()
#     await db.refresh(team)
#     return team








async def create_proect(db: AsyncSession, data: ProjectRequest, current_user: User):

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


