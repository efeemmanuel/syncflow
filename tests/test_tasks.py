import pytest
from httpx import AsyncClient
from tests.helpers import get_admin_token 


# ===== CREATE TASK TESTS =====

# test creating task without token — should fail
async def test_create_task_unauthorized(client: AsyncClient):
    response = await client.post("/tasks/", json={
        "title": "Test Task",
        "project_id": 1
    })
    assert response.status_code == 401


# test creating task with missing fields — should fail
async def test_create_task_missing_fields(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/tasks/",
        json={"title": "no project"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


# test creating task with nonexistent project — should fail
async def test_create_task_invalid_project(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/tasks/",
        json={"title": "Test Task", "project_id": 99999},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== GET TASKS TESTS =====

# test getting tasks without token — should fail
async def test_get_tasks_unauthorized(client: AsyncClient):
    response = await client.get("/tasks/")
    assert response.status_code == 401


# test getting tasks with valid token — should pass
async def test_get_tasks_authorized(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ===== GET SINGLE TASK TESTS =====

# test getting nonexistent task — should fail
async def test_get_task_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.get("/tasks/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# ===== UPDATE TASK TESTS =====

# test updating task without token — should fail
async def test_update_task_unauthorized(client: AsyncClient):
    response = await client.put("/tasks/1", json={"title": "New Title"})
    assert response.status_code == 401


# ===== DELETE TASK TESTS =====

# test deleting task without token — should fail
async def test_delete_task_unauthorized(client: AsyncClient):
    response = await client.delete("/tasks/1")
    assert response.status_code == 401


# ===== ASSIGN TASK TESTS =====

# test assigning task without token — should fail
async def test_assign_task_unauthorized(client: AsyncClient):
    response = await client.post("/tasks/1/assign/1")
    assert response.status_code == 401


# test assigning task to nonexistent user — should fail
async def test_assign_task_invalid_user(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/tasks/1/assign/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400