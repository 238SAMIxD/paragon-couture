import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://paragon:couture_secret@localhost:5432/paragon_db")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for declarative models
Base = declarative_base()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session