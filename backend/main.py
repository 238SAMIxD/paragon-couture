from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Paragon Couture API", version="1.0.0")

class HealthCheck(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="ok", 
        message="200 OK!"
    )
