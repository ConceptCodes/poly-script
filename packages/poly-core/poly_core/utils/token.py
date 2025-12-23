import secrets
import base64


def generate_token() -> str:
    token = secrets.token_urlsafe(32)
    return base64.urlsafe_b64encode(token.encode()).decode().rstrip("=")


def generate_short_token() -> str:
    return secrets.token_urlsafe(16)
