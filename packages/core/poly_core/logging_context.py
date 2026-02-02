import contextvars
import logging
from typing import Optional

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
team_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("team_id", default="-")
job_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("job_id", default="-")


def set_request_context(request_id: str, team_id: Optional[str] = None) -> None:
    request_id_var.set(request_id)
    if team_id is not None:
        team_id_var.set(team_id)


def clear_request_context() -> None:
    request_id_var.set("-")
    team_id_var.set("-")


def set_job_context(job_id: str, team_id: Optional[str] = None) -> None:
    job_id_var.set(job_id)
    if team_id is not None:
        team_id_var.set(team_id)


def clear_job_context() -> None:
    job_id_var.set("-")


def get_request_id() -> str:
    return request_id_var.get()


def get_team_id() -> str:
    return team_id_var.get()


def get_job_id() -> str:
    return job_id_var.get()


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_var.get()
        if not hasattr(record, "team_id"):
            record.team_id = team_id_var.get()
        if not hasattr(record, "job_id"):
            record.job_id = job_id_var.get()
        return True
