import uuid
from httpx import AsyncClient


async def get_admin_token(client: AsyncClient, email: str = None, admin_email: str = None, name: str = None) -> str:
    # generate unique emails if not provided
    unique = str(uuid.uuid4())[:8]
    email = email or f"company_{unique}@test.com"
    admin_email = admin_email or f"admin_{unique}@test.com"
    name = name or f"Company {unique}"

    await client.post("/auth/register", json={
        "name": name,
        "email": email,
        "admin_email": admin_email,
        "password": "StrongPass123!"
    })
    await client.post("/auth/verify-otp", params={
        "email": email,
        "otp": "123456"
    })
    response = await client.post("/auth/login", data={
        "username": admin_email,
        "password": "StrongPass123!"
    })
    return response.json().get("access_token")