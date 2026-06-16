"""
ComfyUI image generation service.

Submits the Qwen.json API-format workflow to a ComfyUI instance,
polls the history endpoint until the prompt finishes, then downloads
the first output image and returns it as a base64 data URI.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import random
from pathlib import Path
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

_WORKFLOW_PATH = Path(__file__).parent / "Qwen.json"


_POSITIVE_PROMPT_NODE = "6"
_KSAMPLER_NODE = "3"


def _load_workflow() -> dict[str, Any]:
    """Load and return a fresh copy of the workflow template."""
    with _WORKFLOW_PATH.open() as f:
        return json.load(f)


def _build_prompt(positive_text: str, seed: int | None = None) -> dict[str, Any]:
    """
    Clone the workflow and inject a custom positive prompt + fresh seed.

    Args:
        positive_text: The image generation prompt.
        seed: Optional seed for reproducibility. Randomised if *None*.

    Returns:
        The modified workflow dict ready to POST to /prompt.
    """
    workflow = _load_workflow()

    workflow[_POSITIVE_PROMPT_NODE]["inputs"]["text"] = positive_text

    workflow[_KSAMPLER_NODE]["inputs"]["seed"] = (
        seed if seed is not None else random.randint(0, 2**32 - 1)
    )

    return workflow


class ComfyUIService:
    """
    Async client for ComfyUI's HTTP API.

    Usage::

        service = ComfyUIService()
        data_uri = await service.generate_image("a cyberpunk monkey in haute couture")
    """

    def __init__(
        self,
        base_url: str | None = None,
        poll_interval: float = 2.0,
        timeout: float = 300.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv("COMFYUI_BASE_URL", "http://localhost:8188")
        ).rstrip("/")
        self.poll_interval = poll_interval
        self.timeout = timeout

    async def generate_image(
        self,
        prompt: str,
        seed: int | None = None,
    ) -> str:
        """
        Generate an image via ComfyUI and return it as a *data URI*.

        Args:
            prompt: Positive text prompt for the Qwen diffusion workflow.
            seed:   Optional RNG seed (randomised when omitted).

        Returns:
            A ``data:image/png;base64,...`` string ready to embed in HTML
            or store in the database.

        Raises:
            httpx.HTTPError: On network-level failures.
            RuntimeError:    When the workflow errors or produces no images.
            TimeoutError:    When ComfyUI takes longer than *self.timeout* seconds.
        """
        workflow = _build_prompt(prompt, seed)

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            prompt_id = await self._queue_prompt(client, workflow)
            logger.info("comfyui_prompt_queued", prompt_id=prompt_id)

            output = await self._poll_until_done(client, prompt_id)
            logger.info("comfyui_prompt_done", prompt_id=prompt_id)

            image_bytes = await self._fetch_image(client, output)

        data_uri = _bytes_to_data_uri(image_bytes)
        return data_uri

    async def _queue_prompt(
        self, client: httpx.AsyncClient, workflow: dict[str, Any]
    ) -> str:
        """POST the workflow to /prompt and return the assigned prompt_id."""
        payload = {"prompt": workflow}
        response = await client.post("/prompt", json=payload)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            raise RuntimeError(f"ComfyUI rejected the prompt: {data['error']}")

        prompt_id: str = data["prompt_id"]
        return prompt_id

    async def _poll_until_done(
        self, client: httpx.AsyncClient, prompt_id: str
    ) -> dict[str, Any]:
        """
        Poll /history/{prompt_id} until the job finishes.

        Returns the ``outputs`` dict for the finished prompt.
        Raises ``TimeoutError`` if the job exceeds *self.timeout* seconds.
        Raises ``RuntimeError`` if ComfyUI reports an execution error.
        """
        elapsed = 0.0
        while elapsed < self.timeout:
            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

            response = await client.get(f"/history/{prompt_id}")
            response.raise_for_status()
            history = response.json()

            if prompt_id not in history:
                continue

            entry = history[prompt_id]

            status = entry.get("status", {})
            if status.get("status_str") == "error":
                messages = status.get("messages", [])
                raise RuntimeError(
                    f"ComfyUI execution error for prompt {prompt_id}: {messages}"
                )

            outputs: dict[str, Any] = entry.get("outputs", {})
            if not outputs:
                raise RuntimeError(
                    f"ComfyUI returned no outputs for prompt {prompt_id}"
                )

            return outputs

        raise TimeoutError(
            f"ComfyUI did not finish prompt {prompt_id} within {self.timeout}s"
        )

    async def _fetch_image(
        self, client: httpx.AsyncClient, outputs: dict[str, Any]
    ) -> bytes:
        """Download the first image from the workflow outputs and return raw bytes."""
        for _node_id, node_output in outputs.items():
            images: list[dict[str, str]] = node_output.get("images", [])
            if images:
                img_info = images[0]
                filename = img_info["filename"]
                subfolder = img_info.get("subfolder", "")
                file_type = img_info.get("type", "output")

                params: dict[str, str] = {
                    "filename": filename,
                    "type": file_type,
                }
                if subfolder:
                    params["subfolder"] = subfolder

                response = await client.get("/view", params=params)
                response.raise_for_status()
                logger.info(
                    "comfyui_image_downloaded",
                    filename=filename,
                    bytes=len(response.content),
                )
                return response.content

        raise RuntimeError("No images found in ComfyUI outputs")

    async def health_check(self) -> bool:
        """Return True if ComfyUI is reachable and responsive."""
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=5.0
            ) as client:
                response = await client.get("/system_stats")
                return response.status_code == 200
        except Exception as exc:
            logger.warning("comfyui_unreachable", error=str(exc))
            return False


def _bytes_to_data_uri(image_bytes: bytes, mime: str = "image/png") -> str:
    """Encode raw image bytes as a RFC 2397 data URI."""
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"
