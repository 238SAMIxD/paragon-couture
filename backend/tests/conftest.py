import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app
from src.core.database import Base, get_db, engine, AsyncSessionLocal

async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="session", autouse=True)
def create_tables():
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    import asyncio
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(init())
    finally:
        loop.close()

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
