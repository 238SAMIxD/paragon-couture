import os
import urllib.parse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI

app = FastAPI(title="Paragon Couture API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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

class CoutureLLMResponse(BaseModel):
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_prompt: str

class CoutureResponse(BaseModel):
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_url: str

# Retrieve API key or set a placeholder for local development
api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
client = AsyncOpenAI(api_key=api_key)

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="ok", 
        message="200 OK!"
    )

@app.post("/api/generate", response_model=CoutureResponse)
async def generate_couture(request: CoutureRequest):
    system_prompt = (
        "You are an elite, eccentric luxury fashion designer creating haute couture strictly "
        "for the monkeys of the Bloons TD 6 universe. Mix high-end editorial fashion terms "
        "with BTD6 lore (e.g., MOABs, Paragons, Camo bloons). Be creative and extremely serious "
        "about monkey fashion."
    )
    
    user_prompt = (
        f"Design a high-end fashion collection based on this trend: '{request.trend_description}'.\n"
        f"Target demographic: {request.monkey_tower_class}.\n"
        f"Requirements - Camo Detection: {request.camo_detection}, Lead Popping: {request.lead_popping}."
        "Provide a highly detailed image prompt suitable for an image generation model to showcase the key outfit."
    )

    completion = await client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=CoutureLLMResponse
    )

    llm_response = completion.choices[0].message.parsed
    
    image_url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(llm_response.image_prompt)

    return CoutureResponse(
        collection_title=llm_response.collection_title,
        species_fit=llm_response.species_fit,
        keywords=llm_response.keywords,
        image_url=image_url
    )

