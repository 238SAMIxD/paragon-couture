import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logger import bind_request_id, get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        bind_request_id(request_id)

        logger.info(
            "incoming_request",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
        )

        start_time = time.time()

        response: Response = await call_next(request)

        process_time = (time.time() - start_time) * 1000

        logger.info(
            "outgoing_response",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
            request_id=request_id,
        )

        return response
