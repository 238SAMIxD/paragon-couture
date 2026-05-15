import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base
from main import app, get_db
from httpx import AsyncClient

# Test database URL (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests
engine_test = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


# Create tables before tests run
@pytest.fixture(scope="session")
async def create_test_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop tables after tests
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Override the get_db dependency to use the test database
@pytest.fixture
def override_get_db(create_test_database):
    async def _override_get_db():
        async with TestingSessionLocal() as session:
            yield session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# Async client fixture
@pytest.fixture
async def async_client(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client