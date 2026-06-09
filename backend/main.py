import os
import uuid
import urllib.parse
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import Base, engine, get_db
from src.models.database_models import CoutureCollection
from src.core.telemetry import setup_telemetry
from src.api.middleware import LoggingMiddleware
from src.services.image_service import get_image_service
from src.services.llm_service import LLMService
import structlog

load_dotenv()

from src.core.logger import configure_structlog
configure_structlog()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Paragon Couture API", version="1.0.0", lifespan=lifespan)

setup_telemetry(app)

app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOW_ORIGINS",
            "http://localhost:5174,http://localhost:5173,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    status: str
    message: str


class CoutureRequest(BaseModel):
    trend_description: str = Field(min_length=1, max_length=500)
    monkey_tower_class: Literal["primary", "military", "magic", "support", "hero"]
    camo_detection: bool
    lead_popping: bool


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    seed: int | None = None


class ImageGenerateResponse(BaseModel):
    image_data_uri: str


class CoutureResponse(BaseModel):
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_url: str
    fallback_used: bool = False


class CoutureCollectionResponse(BaseModel):
    id: uuid.UUID
    trend_description: str
    monkey_tower_class: str
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


llm = LLMService()
image_service = get_image_service()


@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", message="200 OK!")


@app.get("/health/image", response_model=HealthCheck)
async def image_health_check():
    """Probe whether the image generation service is reachable."""
    ok = await image_service.health_check()
    if ok:
        return HealthCheck(status="ok", message="Image service is reachable")
    raise HTTPException(status_code=503, detail="Image service is not reachable")


@app.post("/api/generate", response_model=CoutureResponse)
async def generate_couture(request: CoutureRequest, session: AsyncSession = Depends(get_db)):
    # 1. Generate collection metadata via LLM
    try:
        meta = await llm.generate_couture_metadata(
            trend_description=request.trend_description,
            monkey_tower_class=request.monkey_tower_class,
            camo_detection=request.camo_detection,
            lead_popping=request.lead_popping,
        )
    except RuntimeError as exc:
        structlog.get_logger().error("llm_failed", error=str(exc))
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    # 2. Generate image via ImageService (graceful fallback to placeholder)
    try:
        image_url = await image_service.generate_image(meta.image_prompt)
        fallback_used = False
        structlog.get_logger().info("image_generated", prompt_preview=meta.image_prompt[:80])
    except Exception as exc:
        structlog.get_logger().error("image_generation_failed", error=str(exc))
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
        image_url = f"{frontend_url}/{urllib.parse.quote('Dart Monkey.png')}"
        fallback_used = True

    # 3. Persist to database
    db_collection = CoutureCollection(
        trend_description=request.trend_description,
        monkey_tower_class=request.monkey_tower_class,
        collection_title=meta.collection_title,
        species_fit=meta.species_fit,
        keywords=meta.keywords,
        image_url=image_url,
        fallback_used=fallback_used,
    )
    session.add(db_collection)
    await session.commit()
    await session.refresh(db_collection)

    return CoutureResponse(
        collection_title=meta.collection_title,
        species_fit=meta.species_fit,
        keywords=meta.keywords,
        image_url=image_url,
        fallback_used=fallback_used,
    )


@app.get("/api/collections", response_model=list[CoutureCollectionResponse])
async def get_collections(session: AsyncSession = Depends(get_db)):
    from sqlalchemy import desc, select
    result = await session.execute(
        select(CoutureCollection).order_by(desc(CoutureCollection.created_at)).limit(10)
    )
    collections = result.scalars().all()
    return collections


@app.post("/api/image-generate", response_model=ImageGenerateResponse)
async def image_generate(request: ImageGenerateRequest):
    """
    Generate an image directly from a prompt via the active ImageService.

    Returns a base64-encoded data URI (``data:image/png;base64,...``).
    This endpoint bypasses the LLM step and can be called independently
    to test or preview image generation.
    """
    try:
        data_uri = await image_service.generate_image(request.prompt, seed=request.seed)
    except TimeoutError as exc:
        structlog.get_logger().error("image_timeout", error=str(exc))
        raise HTTPException(status_code=504, detail="Image service timed out")
    except Exception as exc:
        structlog.get_logger().error("image_error", error=str(exc))
        raise HTTPException(status_code=502, detail="Image generation failed")

    return ImageGenerateResponse(image_data_uri=data_uri)
