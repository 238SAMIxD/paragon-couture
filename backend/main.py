import os
import json
import uuid
import urllib.parse
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import Base, engine, get_db
from src.models.database_models import CoutureCollection
from src.core.telemetry import setup_telemetry
from src.api.middleware import LoggingMiddleware
from src.services.comfyui_service import ComfyUIService
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
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    status: str
    message: str


class CoutureRequest(BaseModel):
    trend_description: str
    monkey_tower_class: str
    camo_detection: bool
    lead_popping: bool


class ImageGenerateRequest(BaseModel):
    prompt: str
    seed: int | None = None


class ImageGenerateResponse(BaseModel):
    image_data_uri: str


class CoutureResponse(BaseModel):
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_url: str


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


client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
)

comfyui = ComfyUIService()


@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", message="200 OK!")


@app.get("/health/comfyui", response_model=HealthCheck)
async def comfyui_health_check():
    """Probe whether the ComfyUI instance is reachable."""
    ok = await comfyui.health_check()
    if ok:
        return HealthCheck(status="ok", message="ComfyUI is reachable")
    raise HTTPException(status_code=503, detail="ComfyUI is not reachable")


@app.post("/api/generate", response_model=CoutureResponse)
async def generate_couture(request: CoutureRequest, session: AsyncSession = Depends(get_db)):
    system_prompt = (
        "You are an elite luxury fashion designer for the monkeys of the Bloons TD 6 universe. "
        "You must respond in valid JSON matching exactly this schema: { 'collection_title': '...', 'species_fit': '...', 'keywords': ['...', '...', '...'] }. "
        "Do not include any other keys, explanation, or surrounding text."
    )

    user_prompt = (
        f"Trend: {request.trend_description}. "
        f"Target tower class: {request.monkey_tower_class}. "
        f"Camo detection: {request.camo_detection}. Lead popping: {request.lead_popping}."
    )

    try:
        completion = await client.chat.completions.create(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    except Exception as e:
        structlog.get_logger().error("llm_request_failed", error=str(e))
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    try:
        choice = completion.choices[0]
    except Exception as e:
        structlog.get_logger().error("llm_no_choices", error=str(e))
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    message = choice.message
    content_str = ""

    if hasattr(message, 'content'):
        content_str = str(message.content) if message.content is not None else ""
    elif isinstance(message, dict):
        content_str = str(message.get('content', '')) if message.get('content') is not None else ""
        
    if isinstance(content_str, list):
        content_str = "".join(
            str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content_str
        )

    if not content_str:
        structlog.get_logger().error("llm_no_content")
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    try:
        parsed = json.loads(content_str)
    except Exception as e:
        structlog.get_logger().error("llm_invalid_json", error=str(e), content=content_str)
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    if not isinstance(parsed, dict) or not all(k in parsed for k in ("collection_title", "species_fit", "keywords")):
        structlog.get_logger().error("llm_missing_keys", parsed=parsed)
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    # Build an image prompt from the LLM-generated keywords + collection title
    image_prompt = (
        f"{parsed['collection_title']} – {parsed['species_fit']} – "
        + ", ".join(parsed["keywords"])
        + f". Trend: {request.trend_description}. "
        "High-fashion editorial photography, luxury couture, ultra-detailed."
    )

    try:
        image_url = await comfyui.generate_image(image_prompt)
        structlog.get_logger().info("comfyui_image_generated", prompt_preview=image_prompt[:80])
    except Exception as exc:
        structlog.get_logger().error("comfyui_generation_failed", error=str(exc))
        # Fall back to a static placeholder so the rest of the flow keeps working
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
        image_url = f"{frontend_url}/{urllib.parse.quote('Dart Monkey.png')}"

    db_collection = CoutureCollection(
        trend_description=request.trend_description,
        monkey_tower_class=request.monkey_tower_class,
        collection_title=parsed["collection_title"],
        species_fit=parsed["species_fit"],
        keywords=parsed["keywords"],
        image_url=image_url,
    )
    session.add(db_collection)
    await session.commit()
    await session.refresh(db_collection)

    response_obj = {
        "collection_title": parsed["collection_title"],
        "species_fit": parsed["species_fit"],
        "keywords": parsed["keywords"],
        "image_url": image_url,
    }

    try:
        return CoutureResponse.model_validate(response_obj)
    except Exception as e:
        structlog.get_logger().error("response_validation_failed", error=str(e))
        raise HTTPException(status_code=502, detail="Upstream service unavailable")


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
    Generate an image directly from a prompt via ComfyUI.

    Returns a base64-encoded data URI (``data:image/png;base64,...``).
    This endpoint bypasses the LLM step and can be called independently
    to test or preview image generation.
    """
    try:
        data_uri = await comfyui.generate_image(request.prompt, seed=request.seed)
    except TimeoutError as exc:
        structlog.get_logger().error("comfyui_timeout", error=str(exc))
        raise HTTPException(status_code=504, detail="ComfyUI timed out")
    except Exception as exc:
        structlog.get_logger().error("comfyui_error", error=str(exc))
        raise HTTPException(status_code=502, detail="Image generation failed")

    return ImageGenerateResponse(image_data_uri=data_uri)
