import pytest
from httpx import AsyncClient
from tests.helpers import get_admin_token 

# ===== CREATE TEAM TESTS =====

# test creating team without token — should fail
async def test_create_team_unauthorized(client: AsyncClient):
    response = await client.post("/teams/", json={
        "name": "Test Team",
        "team_lead_id": 1
    })
    assert response.status_code == 401


# test creating team with missing fields — should fail
async def test_create_team_missing_fields(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/teams/", 
        json={"name": "Test Team"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


# test creating team with nonexistent team lead — should fail
async def test_create_team_invalid_lead(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/teams/",
        json={"name": "Test Team", "team_lead_id": 99999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== GET TEAMS TESTS =====

# test getting teams without token — should fail
async def test_get_teams_unauthorized(client: AsyncClient):
    response = await client.get("/teams/")
    assert response.status_code == 401


# test getting teams with valid token — should pass
async def test_get_teams_authorized(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/teams/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ===== GET SINGLE TEAM TESTS =====

# test getting nonexistent team — should fail
async def test_get_team_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/teams/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== UPDATE TEAM TESTS =====

# test updating team without token — should fail
async def test_update_team_unauthorized(client: AsyncClient):
    response = await client.put("/teams/1", json={"name": "New Name"})
    assert response.status_code == 401


# ===== DELETE TEAM TESTS =====

# test deleting team without token — should fail
async def test_delete_team_unauthorized(client: AsyncClient):
    response = await client.delete("/teams/1")
    assert response.status_code == 401


# test deleting nonexistent team — should fail
async def test_delete_team_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.delete("/teams/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== TEAM MEMBERS TESTS =====

# test adding member without token — should fail
async def test_add_member_unauthorized(client: AsyncClient):
    response = await client.post("/teams/1/members", params={"user_id": 1})
    assert response.status_code == 401


# test adding nonexistent member — should fail
async def test_add_nonexistent_member(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/teams/1/members",
        params={"user_id": 99999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


# test removing member without token — should fail
async def test_remove_member_unauthorized(client: AsyncClient):
    response = await client.delete("/teams/1/members/1")
    assert response.status_code == 401