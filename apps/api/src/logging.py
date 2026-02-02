import logging

from poly_core.logging_context import ContextFilter


def setup_logging() -> None:
    log_format = (
        "%(asctime)s %(levelname)s "
        "request_id=%(request_id)s team_id=%(team_id)s job_id=%(job_id)s "
        "%(name)s: %(message)s"
    )
    logging.basicConfig(level=logging.INFO, format=log_format)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(ContextFilter())
