import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from src.core.database import Base, get_db, engine, AsyncSessionLocal

# Override the get_db dependency to use a test session
async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Create the tables once for the test session
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    # For SQLite with aiosqlite, we need to use a different approach
    # Create tables using the engine's begin() method
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())

@pytest.fixture
def client():
    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db
    # Return the test client
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()