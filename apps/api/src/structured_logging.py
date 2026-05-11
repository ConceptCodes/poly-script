"""Structured logging configuration using structlog."""

import logging

import structlog

from poly_core.logging_context import (
    job_id_var,
    request_id_var,
    team_id_var,
)


def setup_logging() -> None:
    """Configure structlog for JSON output with correlation IDs."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure standard logging to work with structlog
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def get_logger(name: str):
    """Get a structlog logger with the given name."""
    return structlog.get_logger(name)


class StructuredLogger:
    """Helper class for structured logging with correlation IDs."""

    @staticmethod
    def log_request(logger_name: str = "api") -> structlog.BoundLogger:
        """Get a logger bound with request context."""
        log = structlog.get_logger(logger_name)
        return log.bind(
            request_id=request_id_var.get(),
            team_id=team_id_var.get(),
        )

    @staticmethod
    def log_job(logger_name: str = "worker") -> structlog.BoundLogger:
        """Get a logger bound with job context."""
        log = structlog.get_logger(logger_name)
        return log.bind(
            job_id=job_id_var.get(),
            team_id=team_id_var.get(),
        )
