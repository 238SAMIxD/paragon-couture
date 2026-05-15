import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
import urllib.parse
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import Base, engine, get_db
from src.models.database_models import CoutureCollection

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Paragon Couture API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class HealthCheck(BaseModel):
    status: str
    message: str


class CoutureRequest(BaseModel):
    trend_description: str
    monkey_tower_class: str
    camo_detection: bool
    lead_popping: bool


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

    class Config:
        orm_mode = True


# Configure AsyncOpenAI to use local Ollama instance for development
# Ollama exposes an OpenAI-compatible API by default on http://localhost:11434
client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
)


@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="ok", message="200 OK!")


@app.post("/api/generate", response_model=CoutureResponse)
async def generate_couture(request: CoutureRequest, session: AsyncSession = Depends(get_db)):
    # System prompt: force strict JSON object with exact schema
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

    # Ask the local Ollama model to return a JSON object only
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
        raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")

    # Extract the first choice
    try:
        choice = completion.choices[0]
    except Exception:
        raise HTTPException(status_code=502, detail="LLM returned no choices")

    parsed = None

    # Many OpenAI-compatible clients put a parsed attribute when using structured outputs
    if hasattr(choice.message, "parsed"):
        parsed = choice.message.parsed
    else:
        # Fallback: try to extract textual content and parse as JSON
        content_str = None
        msg = choice.message
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, list):
                content_str = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part) for part in content
                )
            else:
                content_str = content
        else:
            content_attr = getattr(msg, "content", None)
            if isinstance(content_attr, list):
                content_str = "".join(getattr(p, "text", str(p)) for p in content_attr)
            else:
                content_str = content_attr

        if not content_str or not isinstance(content_str, str):
            raise HTTPException(status_code=502, detail="LLM returned no parsable content")

        try:
            parsed = json.loads(content_str)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"LLM returned invalid JSON: {e}\nContent: {content_str}")

    # Validate parsed structure contains required keys
    if not isinstance(parsed, dict) or not all(k in parsed for k in ("collection_title", "species_fit", "keywords")):
        raise HTTPException(status_code=502, detail=f"LLM JSON missing required keys: {parsed}")

    # Use the Dart Monkey image from the frontend public directory
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
    # URL encode the filename with space
    encoded_filename = urllib.parse.quote("Dart Monkey.png")
    placeholder_image = f"{frontend_url}/{encoded_filename}"

    # Create database record
    db_collection = CoutureCollection(
        trend_description=request.trend_description,
        monkey_tower_class=request.monkey_tower_class,
        collection_title=parsed["collection_title"],
        species_fit=parsed["species_fit"],
        keywords=parsed["keywords"],
        image_url=placeholder_image,
    )
    session.add(db_collection)
    await session.commit()
    await session.refresh(db_collection)

    response_obj = {
        "collection_title": parsed["collection_title"],
        "species_fit": parsed["species_fit"],
        "keywords": parsed["keywords"],
        "image_url": placeholder_image,
    }

    # Validate against Pydantic model before returning
    try:
        return CoutureResponse.parse_obj(response_obj)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Response validation failed: {e}")


@app.get("/api/collections", response_model=list[CoutureCollectionResponse])
async def get_collections(session: AsyncSession = Depends(get_db)):
    # Fetch the 10 most recently generated collections
    from sqlalchemy import desc, select
    result = await session.execute(
        select(CoutureCollection).order_by(desc(CoutureCollection.created_at)).limit(10)
    )
    collections = result.scalars().all()
    return collections

