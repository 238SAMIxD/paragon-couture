import pytest
from unittest.mock import patch, AsyncMock
from src.services.llm_service import CoutureMetadata

def test_healthcheck(client):
    """Test that the health endpoint returns 200 and expected JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "200 OK!"

def test_generate_couture(client):
    """Test the generate endpoint with mocked LLM and ComfyUI responses."""
    fake_meta = CoutureMetadata(
        collection_title="Dart Monkey Collection",
        species_fit="Dart Monkey",
        keywords=["dart", "monkey", "futuristic", "cyberpunk"],
        image_prompt="A cinematic image of a dart monkey",
    )
    fake_image_uri = "data:image/png;base64,abc123"

    with (
        patch("main.llm.generate_couture_metadata", new=AsyncMock(return_value=fake_meta)),
        patch("main.image_service.generate_image", new=AsyncMock(return_value=fake_image_uri)),
    ):
        request_data = {
            "trend_description": "futuristic cyberpunk streetwear",
            "monkey_tower_class": "magic",
            "camo_detection": True,
            "lead_popping": False,
        }
        response = client.post("/api/generate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["collection_title"] == "Dart Monkey Collection"
    assert data["species_fit"] == "Dart Monkey"
    assert data["keywords"] == ["dart", "monkey", "futuristic", "cyberpunk"]
    assert data["image_url"] == fake_image_uri
    assert data["fallback_used"] is False

def test_generate_rejects_invalid_tower_class(client):
    """Test that the generate endpoint rejects unknown tower classes."""
    response = client.post(
        "/api/generate",
        json={
            "trend_description": "futuristic cyberpunk streetwear",
            "monkey_tower_class": "wizard",
            "camo_detection": True,
            "lead_popping": False,
        },
    )

    assert response.status_code == 422

def test_generate_rejects_empty_trend_description(client):
    """Test that the generate endpoint rejects empty trend descriptions."""
    response = client.post(
        "/api/generate",
        json={
            "trend_description": "",
            "monkey_tower_class": "magic",
            "camo_detection": True,
            "lead_popping": False,
        },
    )

    assert response.status_code == 422

def test_fetch_collections(client):
    """Test that the collections endpoint returns 200 and fetches items."""
    response = client.get("/api/collections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
