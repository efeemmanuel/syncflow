import pytest
from httpx import AsyncClient
from tests.helpers import get_admin_token 


# test adding attachment without token — should fail
async def test_add_attachment_unauthorized(client: AsyncClient):
    response = await client.post("/tasks/1/attachments", json={
        "file_url": "http://example.com/file.pdf",
        "file_type": "pdf"
    })
    assert response.status_code == 401


# test adding attachment to nonexistent task — should fail
async def test_add_attachment_invalid_task(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.post("/tasks/99999/attachments",
        json={"file_url": "http://example.com/file.pdf", "file_type": "pdf"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "not found" in response.json()["detail"]


# test getting attachments without token — should fail
async def test_get_attachments_unauthorized(client: AsyncClient):
    response = await client.get("/tasks/1/attachments")
    assert response.status_code == 401


# test deleting nonexistent attachment — should fail
async def test_delete_attachment_not_found(client: AsyncClient):
    token = await get_admin_token(client)
    response = await client.delete("/tasks/1/attachments/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400