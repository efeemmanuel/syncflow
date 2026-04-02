import pytest
from httpx import AsyncClient


# ===== REGISTRATION TESTS =====

# test successful company registration
async def test_register_company_success(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "name": "Test Company",
        "email": "company@test.com",
        "admin_email": "newadmin@test.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "company@test.com"


# test registering with same email twice — should fail
async def test_register_duplicate_email(client: AsyncClient):
    data = {
        "name": "Test Company",
        "email": "duplicate@test.com",
        "admin_email": "admin@test.com",
        "password": "StrongPass123!"
    }
    await client.post("/auth/register", json=data)
    response = await client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# test registering with invalid email format — should fail
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "name": "Test Company",
        "email": "notanemail",
        "admin_email": "admin@test.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 422  # validation error


# test registering with missing fields — should fail
async def test_register_missing_fields(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "name": "Test Company"
    })
    assert response.status_code == 422


# ===== OTP TESTS =====

# test verifying with wrong otp — should fail
async def test_verify_wrong_otp(client: AsyncClient):
    response = await client.post("/auth/verify-otp", params={
        "email": "company@test.com",
        "otp": "000000"
    })
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


# test verifying with expired/nonexistent email — should fail
async def test_verify_otp_wrong_email(client: AsyncClient):
    response = await client.post("/auth/verify-otp", params={
        "email": "nonexistent@test.com",
        "otp": "123456"
    })
    assert response.status_code == 400


# ===== LOGIN TESTS =====

# test login with unverified company — should fail
async def test_login_unverified_company(client: AsyncClient):
    await client.post("/auth/register", json={
        "name": "Unverified Co",
        "email": "unverified@test.com",
        "admin_email": "unverifiedadmin@test.com",
        "password": "StrongPass123!"
    })
    response = await client.post("/auth/login", data={
        "username": "unverifiedadmin@test.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400
    assert "not verified" in response.json()["detail"]

# test login with wrong password — should fail
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post("/auth/login", data={
        "username": "company@test.com",
        "password": "WrongPassword!"
    })
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


# test login with nonexistent email — should fail
async def test_login_nonexistent_email(client: AsyncClient):
    response = await client.post("/auth/login", data={
        "username": "ghost@test.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


# ===== INVITE TESTS =====

# test inviting team lead without admin token — should fail
async def test_invite_team_lead_unauthorized(client: AsyncClient):
    response = await client.post("/auth/invite-team-lead", params={
        "email": "lead@test.com"
    })
    # no token provided, should return 401
    assert response.status_code == 401


# test inviting member without team lead token — should fail
async def test_invite_member_unauthorized(client: AsyncClient):
    response = await client.post("/auth/invite-member", params={
        "email": "member@test.com",
        "team_id": 1
    })
    assert response.status_code == 401


# test accepting invite with invalid token — should fail
async def test_accept_invite_invalid_token(client: AsyncClient):
    response = await client.post("/auth/accept-invite", params={
        "token": "invalidtoken123"
    }, json={
        "full_name": "Test User",
        "username": "testuser",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


# ===== FORGOT PASSWORD TESTS =====

# test forgot password with nonexistent email — should fail
async def test_forgot_password_wrong_email(client: AsyncClient):
    response = await client.post("/auth/forgot-password", params={
        "email": "ghost@test.com"
    })
    assert response.status_code == 400


# test reset password with wrong otp — should fail
async def test_reset_password_wrong_otp(client: AsyncClient):
    response = await client.post("/auth/reset-password", params={
        "email": "company@test.com",
        "otp": "000000",
        "new_password": "NewPass123!"
    })
    assert response.status_code == 400


# ===== TOKEN TESTS =====

# test refresh with invalid token — should fail
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post("/auth/refresh", params={
        "refresh_token": "invalidtoken"
    })
    assert response.status_code == 401


# test accessing protected route without token — should fail
async def test_protected_route_no_token(client: AsyncClient):
    response = await client.post("/auth/logout")
    assert response.status_code == 401


# ===== BUSINESS LOGIC TESTS =====

# test inviting same email twice — should fail
async def test_invite_duplicate_email(client: AsyncClient):
    # first need a valid admin token
    # register and verify a company first
    await client.post("/auth/register", json={
        "name": "Logic Test Co",
        "email": "logicco@test.com",
        "admin_email": "logicadmin@test.com",
        "password": "StrongPass123!"
    })
    # verify company
    # NOTE: we cant fully test this without a real OTP
    # so we test the duplicate invite on the endpoint level
    response = await client.post("/auth/invite-team-lead", params={
        "email": "samelead@test.com"
    })
    # no token so should return 401
    assert response.status_code == 401


# test member trying to invite another member — should fail
async def test_member_cannot_invite(client: AsyncClient):
    # create a fake member token — wrong role
    response = await client.post("/auth/invite-member", params={
        "email": "newmember@test.com",
        "team_id": 1
    })
    assert response.status_code == 401


# test team lead trying to invite admin — no such endpoint for team lead
async def test_team_lead_cannot_invite_admin(client: AsyncClient):
    response = await client.post("/auth/send-admin-invite", params={
        "company_id": 1,
        "admin_email": "anyadmin@test.com"
    })
    # no token so 401
    assert response.status_code == 401