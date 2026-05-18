import structlog
import uuid
from typing import Any

def configure_structlog() -> None:
    """
    Configure structlog for JSON output with request_id injection.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a structlog logger with the given name.
    """
    return structlog.get_logger(name)

def bind_request_id(request_id: str) -> None:
    """
    Bind a request_id to the current contextvars.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)