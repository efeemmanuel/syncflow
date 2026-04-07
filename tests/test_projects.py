import pytest
from httpx import AsyncClient
from tests.helpers import get_admin_token 

# ===== CREATE PROJECT TESTS =====

# test creating project without token — should fail
async def test_create_project_unauthorized(client: AsyncClient):
    response = await client.post("/projects/", json={
        "title": "Test Project",
        "description": "Test"
    })
    assert response.status_code == 401


# test creating project with missing fields — should fail
async def test_create_project_missing_fields(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/projects/",
        json={"description": "no title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


# test creating duplicate project title — should fail
async def test_create_project_duplicate_title(client: AsyncClient):
    token = await get_admin_token(client)
    data = {"title": "Duplicate Project"}
    await client.post("/projects/", json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    response = await client.post("/projects/", json=data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "exists" in response.json()["detail"]


# ===== GET PROJECTS TESTS =====

# test getting projects without token — should fail
async def test_get_projects_unauthorized(client: AsyncClient):
    response = await client.get("/projects/")
    assert response.status_code == 401


# test getting projects with valid token — should pass
async def test_get_projects_authorized(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/projects/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ===== GET SINGLE PROJECT TESTS =====

# test getting nonexistent project — should fail
async def test_get_project_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/projects/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== UPDATE PROJECT TESTS =====

# test updating project without token — should fail
async def test_update_project_unauthorized(client: AsyncClient):
    response = await client.put("/projects/1", json={"title": "New Title"})
    assert response.status_code == 401


# test updating nonexistent project — should fail
async def test_update_project_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.put("/projects/99999",
        json={"title": "New Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== DELETE PROJECT TESTS =====

# test deleting project without token — should fail
async def test_delete_project_unauthorized(client: AsyncClient):
    response = await client.delete("/projects/1")
    assert response.status_code == 401


# test deleting nonexistent project — should fail
async def test_delete_project_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.delete("/projects/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]