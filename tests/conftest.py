import os
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:Testing123!@db:5432/projectmanagement_test"

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from unittest.mock import AsyncMock, patch
from app.main import app
from app.core.database import Base
from app.models import *


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:Testing123!@db:5432/projectmanagement_test",
        poolclass=NullPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = replica"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("SET session_replication_role = DEFAULT"))
    await engine.dispose()


@pytest.fixture(autouse=True)
def mock_external():
    with patch("app.utils.email.send_otp_email", new_callable=AsyncMock), \
         patch("app.utils.email.send_admin_invite_email", new_callable=AsyncMock), \
         patch("app.utils.email.send_invite_email", new_callable=AsyncMock), \
         patch("app.utils.otp.verify_otp", new_callable=AsyncMock, return_value=True):
        yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c