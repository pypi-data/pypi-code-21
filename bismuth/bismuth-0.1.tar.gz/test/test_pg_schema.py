# coding=utf-8
import os
from os.path import dirname, join

import asyncpg
import pytest
import uvloop

from bismuth_server.db_setup import create_schema


@pytest.fixture(scope='session')
def event_loop():
    """Event loop for pytest.mark.asyncio"""
    return uvloop.new_event_loop()


@pytest.fixture(scope='session')
def schema_test_script():
    with open(join(dirname(__file__), 'postgres', 'test_schema.sql'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='session')
def sql_error_script():
    with open(join(dirname(__file__), 'postgres', 'test_errs.sql'), 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture(scope='session')
async def pg_db():
    pool = await asyncpg.create_pool(os.environ['TEST_DB_URL'])
    async with pool.acquire() as conn:
        # set up database schema
        await create_schema(conn)
    # provide connection as fixture
    yield pool
    await pool.close()


@pytest.mark.asyncio
async def test_db_alive(pg_db):
    async with pg_db.acquire() as conn:
        assert await conn.fetchval('SELECT 1') == 1


@pytest.mark.asyncio
async def test_schema(pg_db, schema_test_script):
    async with pg_db.acquire() as conn:
        await conn.execute(schema_test_script)


@pytest.mark.asyncio
async def test_schema_setup_is_idempotent(pg_db):
    async with pg_db.acquire() as conn:
        await create_schema(conn)


@pytest.mark.asyncio
async def test_pg_error(pg_db, sql_error_script):
    async with pg_db.acquire() as conn:
        with pytest.raises(asyncpg.exceptions.AssertError):
            await conn.execute(sql_error_script)
