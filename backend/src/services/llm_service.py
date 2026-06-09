"""
LLM text-generation service.

Wraps the OpenAI-compatible client (Ollama / any OpenAI-format backend)
and exposes a single coroutine that turns a couture request into structured
JSON metadata: collection_title, species_fit, and keywords.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CoutureMetadata:
    collection_title: str
    species_fit: str
    keywords: list[str]
    image_prompt: str


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are an elite luxury fashion designer for the monkeys of the Bloons TD 6 universe. "
    "You must respond in valid JSON matching exactly this schema: "
    "{ 'collection_title': '...', 'species_fit': '...', 'keywords': ['...', '...', '...'], 'image_prompt': '...' }. "
    "Do not include any other keys, explanation, or surrounding text. "
    "For the 'image_prompt', write a highly detailed, descriptive, and cinematic prompt for an AI image generator that perfectly embodies the user's requested trend. "
    "Describe the monkey's luxurious outfit, materials, textures, dynamic lighting, and background. "
    "Use terms like 'high-fashion editorial photography', 'shallow depth of field', 'sharp focus', 'ultra-detailed', and 'cinematic lighting'. "
    "Adapt the theme entirely based on the user's trend description—do not force any specific aesthetic (like cyberpunk or cyborgs) unless the user asks for it."
)

_REQUIRED_KEYS = ("collection_title", "species_fit", "keywords", "image_prompt")


class LLMService:
    """
    Async client for an OpenAI-compatible text-generation backend.

    Usage::

        service = LLMService()
        meta = await service.generate_couture_metadata(
            trend_description="neon brutalism",
            monkey_tower_class="Dart Monkey",
            camo_detection=True,
            lead_popping=False,
        )
        print(meta.collection_title)
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.model = model or os.getenv(
            "OLLAMA_MODEL", "huggingface.co/speakleash/Bielik-11B-v3.0-Instruct-GGUF:Q8_0"
        )
        self._client = AsyncOpenAI(
            base_url=base_url or os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
            api_key=api_key or os.getenv("OPENAI_API_KEY", "ollama"),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_couture_metadata(
        self,
        trend_description: str,
        monkey_tower_class: str,
        camo_detection: bool,
        lead_popping: bool,
    ) -> CoutureMetadata:
        """
        Call the LLM and return parsed couture collection metadata.

        Args:
            trend_description:  Free-text trend description from the user.
            monkey_tower_class: Target BTD6 tower class (e.g. "Dart Monkey").
            camo_detection:     Whether the tower detects camo bloons.
            lead_popping:       Whether the tower pops lead bloons.

        Returns:
            A :class:`CoutureMetadata` dataclass with the parsed fields.

        Raises:
            RuntimeError: On network errors, missing keys, or invalid JSON.
        """
        user_prompt = (
            f"Trend: {trend_description}. "
            f"Target tower class: {monkey_tower_class}. "
            f"Camo detection: {camo_detection}. Lead popping: {lead_popping}."
        )

        raw = await self._call_llm(user_prompt)
        return self._parse(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _call_llm(self, user_prompt: str) -> str:
        """Send the prompt to the LLM and return the raw content string."""
        try:
            completion = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            logger.error("llm_request_failed", error=str(exc))
            raise RuntimeError("Upstream LLM service unavailable") from exc

        try:
            choice = completion.choices[0]
        except Exception as exc:
            logger.error("llm_no_choices", error=str(exc))
            raise RuntimeError("Upstream LLM service unavailable") from exc

        message = choice.message
        content: str = ""

        if hasattr(message, "content"):
            content = str(message.content) if message.content is not None else ""
        elif isinstance(message, dict):
            content = str(message.get("content", "") or "")

        # Handle content that arrives as a list of parts (some providers)
        if isinstance(content, list):
            content = "".join(
                str(part.get("text", "")) if isinstance(part, dict) else str(part)
                for part in content
            )

        if not content:
            logger.error("llm_no_content")
            raise RuntimeError("Upstream LLM service returned empty content")

        return content

    def _parse(self, content: str) -> CoutureMetadata:
        """Parse the raw JSON string into a :class:`CoutureMetadata`."""
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("llm_invalid_json", error=str(exc), content=content)
            raise RuntimeError("LLM returned invalid JSON") from exc

        if not isinstance(parsed, dict) or not all(
            k in parsed for k in _REQUIRED_KEYS
        ):
            logger.error("llm_missing_keys", parsed=parsed)
            raise RuntimeError(f"LLM JSON missing required keys: {_REQUIRED_KEYS}")

        return CoutureMetadata(
            collection_title=parsed["collection_title"],
            species_fit=parsed["species_fit"],
            keywords=parsed["keywords"],
            image_prompt=parsed["image_prompt"],
        )
