from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings



# craeet your engine here connection to DB, session factory   but we are using async  the async for psocopg
# Using PostgreSQL → need a PostgreSQL driver
# Using async      → need an async driver
# asyncpg          → async PostgreSQL driver
# Your code
#     ↓
# SQLAlchemy (ORM — handles queries, models)
#     ↓
# asyncpg (driver — actually sends data to PostgreSQL)
#     ↓
# PostgreSQL (database)



engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
)


# a temporayworkspace to CRUD
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()