import pytest
from httpx import AsyncClient
from tests.helpers import get_admin_token 


# test adding comment without token — should fail
async def test_add_comment_unauthorized(client: AsyncClient):
    response = await client.post("/tasks/1/comments", json={"content": "test"})
    assert response.status_code == 401


# test adding comment to nonexistent task — should fail
async def test_add_comment_invalid_task(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/tasks/99999/comments",
        json={"content": "test comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# test getting comments without token — should fail
async def test_get_comments_unauthorized(client: AsyncClient):
    response = await client.get("/tasks/1/comments")
    assert response.status_code == 401


# test deleting nonexistent comment — should fail
async def test_delete_comment_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.delete("/tasks/1/comments/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400