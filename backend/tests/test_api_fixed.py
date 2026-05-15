import pytest
from unittest.mock import patch
import json

# Test 1: Healthcheck
def test_healthcheck(client):
    """Test that the health endpoint returns 200 and expected JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "200 OK!"

# Test 2: Generate Couture (Mocked LLM)
def test_generate_couture(client):
    """Test the generate endpoint with mocked LLM response."""
    # Mock data that matches CoutureResponse schema
    mock_response_data = {
        "collection_title": "Dart Monkey Collection",
        "species_fit": "Dart Monkey",
        "keywords": ["dart", "monkey", "futuristic", "cyberpunk"]
    }
    
    # Mock the AsyncOpenAI client call
    with patch('main.client.chat.completions.create') as mock_create:
        # Configure the mock to return a response with parsed attribute
        mock_choice = type('MockChoice', (), {})()
        mock_choice.message = type('MockMessage', (), {})()
        mock_choice.message.parsed = mock_response_data
        mock_completion = type('MockCompletion', (), {})()
        mock_completion.choices = [mock_choice]
        mock_create.return_value = mock_completion
        
        # Make the request
        request_data = {
            "trend_description": "futuristic cyberpunk streetwear",
            "monkey_tower_class": "wizard",
            "camo_detection": True,
            "lead_popping": False
        }
        response = client.post("/api/generate", json=request_data)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["collection_title"] == mock_response_data["collection_title"]
        assert data["species_fit"] == mock_response_data["species_fit"]
        assert data["keywords"] == mock_response_data["keywords"]


# Test 3: Fetch Collections
def test_fetch_collections(client):
    """Test that the collections endpoint returns 200 and fetches items."""
    # For now, we'll just test that the endpoint returns 200
    # A more comprehensive test would require database setup
    response = client.get("/api/collections")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)