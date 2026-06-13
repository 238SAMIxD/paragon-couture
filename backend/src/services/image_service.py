"""
Image Generation Service.

Defines the base Protocol for image generation services and provides
implementations for DALL-E, Banana/Replicate (Placeholder), and
local ComfyUI. Also provides a factory to get the right service based
on the environment.
"""

from __future__ import annotations

import os
from typing import Protocol

import structlog
from openai import AsyncOpenAI

logger = structlog.get_logger(__name__)


class ImageService(Protocol):
    """Protocol defining the interface for image generation services."""

    async def generate_image(self, prompt: str, seed: int | None = None) -> str:
        """
        Generate an image and return it as a data URI.

        Args:
            prompt: The text prompt describing the image.
            seed: Optional RNG seed.

        Returns:
            A string in the format "data:image/png;base64,...".
        """
        ...

    async def health_check(self) -> bool:
        """Return True if the service is reachable and responsive."""
        ...


class DalleService:
    """
    Async client for OpenAI's DALL-E 3 image generation.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set to use DalleService")
        self._client = AsyncOpenAI(api_key=self.api_key)

    async def generate_image(self, prompt: str, seed: int | None = None) -> str:
        try:
            response = await self._client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="b64_json",
            )
        except Exception as exc:
            logger.error("dalle_request_failed", error=str(exc))
            raise RuntimeError("DALL-E image generation failed") from exc

        data = response.data[0]
        b64_data = data.b64_json

        if not b64_data:
            logger.error("dalle_no_image_data")
            raise RuntimeError("DALL-E returned no image data")

        return f"data:image/png;base64,{b64_data}"

    async def health_check(self) -> bool:
        return True


class BananaService:
    """
    Placeholder client for Banana.dev / Replicate / Fal.ai or other serverless GPUs.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("BANANA_API_KEY")
        if not self.api_key:
            logger.warning("BANANA_API_KEY not set, BananaService will fail")

    async def generate_image(self, prompt: str, seed: int | None = None) -> str:
        logger.info("banana_generate_called", prompt=prompt)
        raise NotImplementedError("Banana API integration is not fully implemented yet.")

    async def health_check(self) -> bool:
        return True


def get_image_service() -> ImageService:
    """Factory to return the configured ImageService."""
    provider = os.getenv("IMAGE_PROVIDER", "comfyui").lower()

    if provider == "dalle":
        return DalleService()
    elif provider == "banana":
        return BananaService()
    elif provider == "comfyui":
        from src.services.comfyui_service import ComfyUIService
        return ComfyUIService()
    else:
        logger.warning(f"Unknown IMAGE_PROVIDER '{provider}', falling back to comfyui")
        from src.services.comfyui_service import ComfyUIService
        return ComfyUIService()
