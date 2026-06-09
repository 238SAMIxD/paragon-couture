"""
Tests for LLMService.

The OpenAI client is fully mocked so no real LLM is required.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.llm_service import LLMService, CoutureMetadata


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_completion(content: str):
    """Build a minimal mock completion object that resembles openai.ChatCompletion."""
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message)
    return SimpleNamespace(choices=[choice])


VALID_JSON = '{"collection_title": "Dart Noir", "species_fit": "Dart Monkey", "keywords": ["black", "latex", "minimal"], "image_prompt": "A cinematic monkey"}'

INVALID_JSON = "not json at all"

MISSING_KEYS_JSON = '{"collection_title": "X"}'
INVALID_SCHEMA_JSON = '{"collection_title": "Dart Noir", "species_fit": "Dart Monkey", "keywords": "black", "image_prompt": "A cinematic monkey"}'


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestLLMServiceParse:
    """Test the _parse helper directly."""

    def setup_method(self):
        self.svc = LLMService(base_url="http://mock", api_key="x", model="test")

    def test_valid_json_returns_metadata(self):
        meta = self.svc._parse(VALID_JSON)
        assert isinstance(meta, CoutureMetadata)
        assert meta.collection_title == "Dart Noir"
        assert meta.species_fit == "Dart Monkey"
        assert meta.keywords == ["black", "latex", "minimal"]
        assert meta.image_prompt == "A cinematic monkey"

    def test_invalid_json_raises_runtime_error(self):
        with pytest.raises(RuntimeError, match="invalid JSON"):
            self.svc._parse(INVALID_JSON)

    def test_missing_keys_raises_runtime_error(self):
        with pytest.raises(RuntimeError, match="missing required keys"):
            self.svc._parse(MISSING_KEYS_JSON)

    def test_invalid_schema_raises_runtime_error(self):
        with pytest.raises(RuntimeError, match="schema validation"):
            self.svc._parse(INVALID_SCHEMA_JSON)


class TestLLMServiceCallLLM:
    """Test the _call_llm helper with a mocked AsyncOpenAI client."""

    def setup_method(self):
        self.svc = LLMService(base_url="http://mock", api_key="x", model="test")

    def _patch_client(self, return_value=None, side_effect=None):
        mock_create = AsyncMock(return_value=return_value, side_effect=side_effect)
        self.svc._client.chat.completions.create = mock_create
        return mock_create

    def test_returns_content_string(self):
        self._patch_client(return_value=_make_completion(VALID_JSON))

        result = asyncio.run(self.svc._call_llm("test prompt"))
        assert result == VALID_JSON

    def test_network_error_raises_runtime_error(self):
        self._patch_client(side_effect=Exception("connection refused"))

        with pytest.raises(RuntimeError, match="unavailable"):
            asyncio.run(self.svc._call_llm("test prompt"))

    def test_empty_content_raises_runtime_error(self):
        self._patch_client(return_value=_make_completion(""))

        with pytest.raises(RuntimeError, match="empty content"):
            asyncio.run(self.svc._call_llm("test prompt"))

    def test_none_content_raises_runtime_error(self):
        self._patch_client(return_value=_make_completion(None))

        with pytest.raises(RuntimeError, match="empty content"):
            asyncio.run(self.svc._call_llm("test prompt"))


class TestLLMServiceGenerateCoutureMetadata:
    """Integration-level test of the public generate_couture_metadata method."""

    def setup_method(self):
        self.svc = LLMService(base_url="http://mock", api_key="x", model="test")

    def test_happy_path_returns_couture_metadata(self):
        self.svc._client.chat.completions.create = AsyncMock(
            return_value=_make_completion(VALID_JSON)
        )

        meta = asyncio.run(
            self.svc.generate_couture_metadata(
                trend_description="neon brutalism",
                monkey_tower_class="magic",
                camo_detection=True,
                lead_popping=False,
            )
        )
        assert isinstance(meta, CoutureMetadata)
        assert meta.collection_title == "Dart Noir"

    def test_llm_error_bubbles_as_runtime_error(self):
        self.svc._client.chat.completions.create = AsyncMock(
            side_effect=Exception("timeout")
        )

        with pytest.raises(RuntimeError):
            asyncio.run(
                self.svc.generate_couture_metadata(
                    trend_description="test",
                    monkey_tower_class="primary",
                    camo_detection=False,
                    lead_popping=True,
                )
            )


# ---------------------------------------------------------------------------
# API endpoint test — /api/generate delegates to LLMService
# ---------------------------------------------------------------------------

class TestGenerateEndpointUsesLLMService:
    """
    Verifies that POST /api/generate delegates to LLMService and
    ComfyUIService, and returns the correct shape.
    """

    def test_generate_returns_couture_response(self, client):
        from src.services.llm_service import CoutureMetadata

        fake_meta = CoutureMetadata(
            collection_title="Dart Noir",
            species_fit="Dart Monkey",
            keywords=["black", "latex", "minimal"],
            image_prompt="A cinematic monkey",
        )

        with (
            patch("main.llm.generate_couture_metadata", new=AsyncMock(return_value=fake_meta)),
            patch("main.comfyui.generate_image", new=AsyncMock(return_value="data:image/png;base64,abc")),
        ):
            resp = client.post(
                "/api/generate",
                json={
                    "trend_description": "neon brutalism",
                    "monkey_tower_class": "primary",
                    "camo_detection": True,
                    "lead_popping": False,
                },
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["collection_title"] == "Dart Noir"
        assert body["species_fit"] == "Dart Monkey"
        assert body["keywords"] == ["black", "latex", "minimal"]
        assert body["image_url"] == "data:image/png;base64,abc"
        assert body["fallback_used"] is False

    def test_generate_falls_back_to_placeholder_when_comfyui_fails(self, client):
        from src.services.llm_service import CoutureMetadata

        fake_meta = CoutureMetadata(
            collection_title="Dart Noir",
            species_fit="Dart Monkey",
            keywords=["black"],
            image_prompt="A cinematic monkey",
        )

        with (
            patch("main.llm.generate_couture_metadata", new=AsyncMock(return_value=fake_meta)),
            patch("main.comfyui.generate_image", new=AsyncMock(side_effect=RuntimeError("down"))),
        ):
            resp = client.post(
                "/api/generate",
                json={
                    "trend_description": "test",
                    "monkey_tower_class": "primary",
                    "camo_detection": False,
                    "lead_popping": False,
                },
            )

        assert resp.status_code == 200
        # Falls back to the placeholder image URL (percent-encoded)
        assert "Dart%20Monkey.png" in resp.json()["image_url"]
        assert resp.json()["fallback_used"] is True


    def test_generate_returns_502_when_llm_fails(self, client):
        with patch(
            "main.llm.generate_couture_metadata",
            new=AsyncMock(side_effect=RuntimeError("LLM down")),
        ):
            resp = client.post(
                "/api/generate",
                json={
                    "trend_description": "test",
                    "monkey_tower_class": "primary",
                    "camo_detection": False,
                    "lead_popping": False,
                },
            )
        assert resp.status_code == 502
