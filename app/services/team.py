from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.team import Team
from app.models.user import User
from app.models.team_members import TeamMembers
from app.schemas.team import TeamCreate, TeamUpdate


# CREATE TEAM — admin only
async def create_team(db: AsyncSession, data: TeamCreate, current_user: User):
    # check team name doesn't already exist in this company
    result = await db.execute(
        select(Team).where(Team.name == data.name, Team.company_id == current_user.company_id)
    )
    if result.scalar_one_or_none():
        raise ValueError("Team name already exists in this company")

    # check team lead exists and belongs to same company
    result = await db.execute(
        select(User).where(User.id == data.team_lead_id, User.company_id == current_user.company_id)
    )
    team_lead = result.scalar_one_or_none()
    if not team_lead:
        raise ValueError("Team lead not found in this company")

    # check user actually has team lead role
    if team_lead.role != "team_lead":
        raise ValueError("User is not a team lead")

    team = Team(
        name=data.name,
        company_id=current_user.company_id,
        team_lead_id=data.team_lead_id
    )
    db.add(team)
    await db.commit()
    await db.refresh(team)
    return team


# GET ALL TEAMS — admin sees all, team lead sees only their team
async def get_teams(db: AsyncSession, current_user: User):
    if current_user.role == "admin":
        # admin gets all teams in their company
        result = await db.execute(
            select(Team).where(Team.company_id == current_user.company_id)
        )
    else:
        # team lead only gets their own team
        result = await db.execute(
            select(Team).where(Team.team_lead_id == current_user.id)
        )
    return result.scalars().all()


# GET SINGLE TEAM
async def get_team(db: AsyncSession, team_id: int, current_user: User):
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    # team lead can only see their own team
    if current_user.role == "team_lead" and team.team_lead_id != current_user.id:
        raise ValueError("Access denied")

    return team


# UPDATE TEAM — admin only
async def update_team(db: AsyncSession, team_id: int, data: TeamUpdate, current_user: User):
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    # update name if provided
    if data.name:
        # check new name doesn't already exist in company
        result = await db.execute(
            select(Team).where(Team.name == data.name, Team.company_id == current_user.company_id)
        )
        if result.scalar_one_or_none():
            raise ValueError("Team name already exists in this company")
        team.name = data.name

    # update team lead if provided
    if data.team_lead_id:
        # check new team lead exists in company
        result = await db.execute(
            select(User).where(User.id == data.team_lead_id, User.company_id == current_user.company_id)
        )
        new_lead = result.scalar_one_or_none()
        if not new_lead:
            raise ValueError("New team lead not found in this company")
        if new_lead.role != "team_lead":
            raise ValueError("User is not a team lead")
        team.team_lead_id = data.team_lead_id

    await db.commit()
    await db.refresh(team)
    return team


# DELETE TEAM — admin only
async def delete_team(db: AsyncSession, team_id: int, current_user: User):
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    await db.delete(team)
    await db.commit()
    return {"message": "Team deleted successfully"}


# ADD MEMBER TO TEAM — admin only
async def add_team_member(db: AsyncSession, team_id: int, user_id: int, current_user: User):
    # check team exists in company
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    # team lead can only add to their own team
    if current_user.role == "team_lead" and team.team_lead_id != current_user.id:
        raise ValueError("Access denied")

    # check user exists in company
    result = await db.execute(
        select(User).where(User.id == user_id, User.company_id == current_user.company_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found in this company")

    # admin should not be added to a team
    if user.role == "admin":
        raise ValueError("Admin cannot be added to a team")

    # check user is not already in team
    result = await db.execute(
        select(TeamMembers).where(TeamMembers.team_id == team_id, TeamMembers.user_id == user_id)
    )
    if result.scalar_one_or_none():
        raise ValueError("User is already in this team")

    member = TeamMembers(team_id=team_id, user_id=user_id)
    db.add(member)
    await db.commit()
    return {"message": "Member added to team successfully"}

# REMOVE MEMBER FROM TEAM — admin only
async def remove_team_member(db: AsyncSession, team_id: int, user_id: int, current_user: User):
    # check team exists in company
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    # team lead can only remove from their own team
    if current_user.role == "team_lead" and team.team_lead_id != current_user.id:
        raise ValueError("Access denied")

    # check user is actually in team
    result = await db.execute(
        select(TeamMembers).where(TeamMembers.team_id == team_id, TeamMembers.user_id == user_id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise ValueError("User is not in this team")

    # team lead cannot be removed this way
    if team.team_lead_id == user_id:
        raise ValueError("Cannot remove team lead, update team instead")

    await db.delete(member)
    await db.commit()
    return {"message": "Member removed from team successfully"}



# GET TEAM MEMBERS — admin or team lead
async def get_team_members(db: AsyncSession, team_id: int, current_user: User):
    # check team exists in company
    result = await db.execute(
        select(Team).where(Team.id == team_id, Team.company_id == current_user.company_id)
    )
    team = result.scalar_one_or_none()
    if not team:
        raise ValueError("Team not found")

    # team lead can only see their own team members
    if current_user.role == "team_lead" and team.team_lead_id != current_user.id:
        raise ValueError("Access denied")

    # get all members in team
    result = await db.execute(
        select(User).join(TeamMembers, TeamMembers.user_id == User.id).where(TeamMembers.team_id == team_id)
    )
    return result.scalars().all()