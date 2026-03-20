import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from app.core.config import settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


run_migrations_online()


















# **The full flow when you run `alembic upgrade head`:**
# ```
# alembic reads alembic.ini
#       ↓
# loads migrations/env.py
#       ↓
# run_migrations_online() is called
#       ↓
# asyncio.run() starts the event loop
#       ↓
# async_engine_from_config creates DB connection
#       ↓
# connects to PostgreSQL
#       ↓
# do_run_migrations runs
#       ↓
# Alembic compares Base.metadata (your models)
# against current database state
#       ↓
# generates and runs the SQL
#       ↓
# 19 tables created in PostgreSQL
#       ↓
# connection disposed cleanly