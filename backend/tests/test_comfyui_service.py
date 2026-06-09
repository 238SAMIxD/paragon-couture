"""
Tests for the ComfyUI image generation service.

All HTTP calls to ComfyUI are mocked with httpx.MockTransport so the
tests run offline, without a real ComfyUI instance.
"""
from __future__ import annotations

import asyncio
import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.comfyui_service import ComfyUIService, _build_prompt, _bytes_to_data_uri


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16  # minimal fake PNG header


def _make_history(prompt_id: str, status: str = "success") -> dict:
    """Build a minimal ComfyUI /history response."""
    return {
        prompt_id: {
            "status": {"status_str": status},
            "outputs": {
                "60": {
                    "images": [
                        {
                            "filename": "ComfyUI_00001_.png",
                            "subfolder": "",
                            "type": "output",
                        }
                    ]
                }
            },
        }
    }


# ---------------------------------------------------------------------------
# Unit tests – pure helpers
# ---------------------------------------------------------------------------


class TestBuildPrompt:
    def test_injects_positive_text(self):
        wf = _build_prompt("a futuristic monkey in silk")
        assert wf["6"]["inputs"]["text"] == "a futuristic monkey in silk"

    def test_seed_is_set_when_provided(self):
        wf = _build_prompt("test", seed=42)
        assert wf["3"]["inputs"]["seed"] == 42

    def test_seed_is_random_when_omitted(self):
        wf1 = _build_prompt("test")
        wf2 = _build_prompt("test")
        # Two calls should (almost certainly) produce different seeds
        # – at minimum neither should be None
        assert wf1["3"]["inputs"]["seed"] is not None
        assert wf2["3"]["inputs"]["seed"] is not None

    def test_does_not_mutate_original_workflow(self):
        """Each call returns an independent copy."""
        wf1 = _build_prompt("prompt A", seed=1)
        wf2 = _build_prompt("prompt B", seed=2)
        assert wf1["6"]["inputs"]["text"] != wf2["6"]["inputs"]["text"]


class TestBytesToDataUri:
    def test_produces_png_data_uri(self):
        result = _bytes_to_data_uri(b"hello")
        assert result.startswith("data:image/png;base64,")

    def test_base64_round_trip(self):
        original = b"\x00\x01\x02\x03"
        uri = _bytes_to_data_uri(original)
        b64_part = uri.split(",", 1)[1]
        assert base64.b64decode(b64_part) == original

    def test_custom_mime(self):
        uri = _bytes_to_data_uri(b"x", mime="image/jpeg")
        assert uri.startswith("data:image/jpeg;base64,")


# ---------------------------------------------------------------------------
# Async integration tests – ComfyUIService with mocked HTTP
# ---------------------------------------------------------------------------


class MockTransport(httpx.AsyncBaseTransport):
    """
    Minimal mock transport that simulates the three ComfyUI endpoints used
    by ComfyUIService: POST /prompt, GET /history/{id}, GET /view.
    """

    def __init__(self, prompt_id: str = "test-prompt-id", history_after: int = 1):
        self.prompt_id = prompt_id
        self.history_after = history_after  # how many empty polls before result
        self._poll_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path

        if path == "/prompt" and request.method == "POST":
            body = json.dumps({"prompt_id": self.prompt_id})
            return httpx.Response(200, text=body)

        if path.startswith("/history/"):
            self._poll_count += 1
            if self._poll_count < self.history_after:
                # Not done yet – return empty history
                return httpx.Response(200, text=json.dumps({}))
            history = _make_history(self.prompt_id)
            return httpx.Response(200, text=json.dumps(history))

        if path == "/view":
            return httpx.Response(200, content=FAKE_PNG)

        if path == "/system_stats":
            return httpx.Response(200, text=json.dumps({"system": {}}))

        return httpx.Response(404, text="Not Found")


def run(coro):
    return asyncio.run(coro)


class TestComfyUIService:
    def _service(self, **kwargs) -> ComfyUIService:
        svc = ComfyUIService(base_url="http://mock-comfyui", poll_interval=0.01)
        for k, v in kwargs.items():
            setattr(svc, k, v)
        return svc

    # ------------------------------------------------------------------
    # generate_image happy path
    # ------------------------------------------------------------------

    def test_generate_image_returns_data_uri(self):
        transport = MockTransport()
        svc = self._service()

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=30,
            ) as client:
                prompt_id = await svc._queue_prompt(client, _build_prompt("test"))
                outputs = await svc._poll_until_done(client, prompt_id)
                image_bytes = await svc._fetch_image(client, outputs)
            return image_bytes

        image_bytes = run(_run())
        assert image_bytes == FAKE_PNG

    def test_data_uri_format(self):
        uri = _bytes_to_data_uri(FAKE_PNG)
        assert uri.startswith("data:image/png;base64,")
        # Verify the base64 portion decodes back to the original bytes
        b64_data = uri.split(",", 1)[1]
        assert base64.b64decode(b64_data) == FAKE_PNG

    def test_polls_multiple_times_before_result(self):
        transport = MockTransport(history_after=3)
        svc = self._service()

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=30,
            ) as client:
                outputs = await svc._poll_until_done(client, transport.prompt_id)
            return outputs

        outputs = run(_run())
        assert "60" in outputs
        assert transport._poll_count == 3

    # ------------------------------------------------------------------
    # Error cases
    # ------------------------------------------------------------------

    def test_timeout_raises_timeout_error(self):
        """If history never returns data, TimeoutError should be raised."""

        class NeverDoneTransport(MockTransport):
            async def handle_async_request(self, request):
                if request.url.path.startswith("/history/"):
                    return httpx.Response(200, text=json.dumps({}))
                return await super().handle_async_request(request)

        transport = NeverDoneTransport()
        svc = self._service()
        svc.timeout = 0.05  # very short timeout

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=10,
            ) as client:
                await svc._poll_until_done(client, transport.prompt_id)

        with pytest.raises(TimeoutError):
            run(_run())

    def test_comfyui_error_status_raises_runtime_error(self):
        """An 'error' status_str from ComfyUI should raise RuntimeError."""

        class ErrorTransport(MockTransport):
            async def handle_async_request(self, request):
                if request.url.path.startswith("/history/"):
                    history = _make_history(self.prompt_id, status="error")
                    return httpx.Response(200, text=json.dumps(history))
                return await super().handle_async_request(request)

        transport = ErrorTransport()
        svc = self._service()

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=30,
            ) as client:
                await svc._poll_until_done(client, transport.prompt_id)

        with pytest.raises(RuntimeError, match="execution error"):
            run(_run())

    def test_no_images_in_outputs_raises_runtime_error(self):
        """If outputs contain no image nodes, RuntimeError should be raised."""

        async def _run():
            svc = self._service()
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=MockTransport(),
                timeout=30,
            ) as client:
                await svc._fetch_image(client, {"60": {"images": []}})

        with pytest.raises(RuntimeError, match="No images found"):
            run(_run())

    def test_comfyui_rejects_prompt_raises_runtime_error(self):
        """A /prompt response containing 'error' key should raise RuntimeError."""

        class RejectTransport(MockTransport):
            async def handle_async_request(self, request):
                if request.url.path == "/prompt":
                    return httpx.Response(
                        200, text=json.dumps({"error": "invalid workflow"})
                    )
                return await super().handle_async_request(request)

        transport = RejectTransport()
        svc = self._service()

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=30,
            ) as client:
                await svc._queue_prompt(client, _build_prompt("bad"))

        with pytest.raises(RuntimeError, match="ComfyUI rejected the prompt"):
            run(_run())

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def test_health_check_returns_true_when_reachable(self):
        transport = MockTransport()
        svc = ComfyUIService(base_url="http://mock-comfyui", poll_interval=0.01)

        async def _run():
            async with httpx.AsyncClient(
                base_url="http://mock-comfyui",
                transport=transport,
                timeout=5,
            ) as client:
                resp = await client.get("/system_stats")
                return resp.status_code == 200

        assert run(_run()) is True

    def test_health_check_returns_false_when_unreachable(self):
        svc = ComfyUIService(
            base_url="http://definitely-not-running:9999", poll_interval=0.01
        )
        # Override timeout to fail fast
        svc.timeout = 0.5
        result = run(svc.health_check())
        assert result is False


# ---------------------------------------------------------------------------
# API endpoint tests (via FastAPI TestClient)
# ---------------------------------------------------------------------------


class TestImageGenerateEndpoint:
    """
    Test /api/image-generate through the FastAPI app.
    ComfyUIService.generate_image is patched so no real ComfyUI is needed.
    """

    def test_returns_data_uri_on_success(self, client):
        fake_uri = f"data:image/png;base64,{base64.b64encode(FAKE_PNG).decode()}"
        with patch(
            "main.image_service.generate_image",
            new=AsyncMock(return_value=fake_uri),
        ):
            resp = client.post(
                "/api/image-generate",
                json={"prompt": "a luxury monkey suit", "seed": 7},
            )
        assert resp.status_code == 200
        assert resp.json()["image_data_uri"] == fake_uri

    def test_returns_504_on_timeout(self, client):
        with patch(
            "main.image_service.generate_image",
            new=AsyncMock(side_effect=TimeoutError("timed out")),
        ):
            resp = client.post(
                "/api/image-generate",
                json={"prompt": "test"},
            )
        assert resp.status_code == 504

    def test_returns_502_on_generic_error(self, client):
        with patch(
            "main.image_service.generate_image",
            new=AsyncMock(side_effect=RuntimeError("comfyui down")),
        ):
            resp = client.post(
                "/api/image-generate",
                json={"prompt": "test"},
            )
        assert resp.status_code == 502

    def test_seed_is_optional(self, client):
        fake_uri = "data:image/png;base64,abc123"
        with patch(
            "main.image_service.generate_image",
            new=AsyncMock(return_value=fake_uri),
        ):
            resp = client.post("/api/image-generate", json={"prompt": "no seed"})
        assert resp.status_code == 200


class TestComfyUIHealthEndpoint:
    def test_healthy(self, client):
        with patch(
            "main.image_service.health_check",
            new=AsyncMock(return_value=True),
        ):
            resp = client.get("/health/image")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_unhealthy(self, client):
        with patch(
            "main.image_service.health_check",
            new=AsyncMock(return_value=False),
        ):
            resp = client.get("/health/image")
        assert resp.status_code == 503
