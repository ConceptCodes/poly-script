#!/usr/bin/env python3
"""
Error Documentation Generator Script

Generates OpenAPI and Markdown documentation for API error codes.
Extracts error codes from poly_core.constants.I18nKeys and creates
comprehensive documentation for Swagger UI and developer reference.

Usage:
    uv run python apps/api/scripts/generate_error_docs.py --format openapi
    uv run python apps/api/scripts/generate_error_docs.py --format markdown
    uv run python apps/api/scripts/generate_error_docs.py --format markdown --output error_docs.md
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add packages/core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "core"))

from poly_core.constants import I18N_KEY_HTTP_STATUS, I18nKeys


def get_error_category(i18n_key: I18nKeys) -> str:
    """Extract category from I18nKey value."""
    value = i18n_key.value
    if value.startswith("errors."):
        return value.split(".")[1]
    return "other"


def get_error_description(i18n_key: I18nKeys) -> str:
    """Generate human-readable description from I18nKey name."""
    name = i18n_key.name

    # Map common error names to descriptions
    descriptions = {
        "ERR_AUTH_INVALID_CREDENTIALS": "Invalid email or password provided",
        "ERR_AUTH_USER_NOT_FOUND": "User account does not exist",
        "ERR_AUTH_EMAIL_ALREADY_EXISTS": "Email address is already registered",
        "ERR_AUTH_EMAIL_NOT_VERIFIED": "Email verification required before login",
        "ERR_AUTH_ACCOUNT_SUSPENDED": "Account has been suspended by admin",
        "ERR_JOBS_NOT_FOUND": "Transcription job not found",
        "ERR_JOBS_LIMIT_REACHED": "Monthly upload limit reached for plan",
        "ERR_JOBS_UNSUPPORTED_LANGUAGE": "Language not supported by current plan",
        "ERR_TRANSCRIPTS_NOT_FOUND": "Transcript not found",
        "ERR_TEAMS_NOT_FOUND": "Team not found",
        "ERR_TEAMS_MEMBER_LIMIT_REACHED": "Team member limit reached for plan",
        "ERR_BILLING_PAYMENT_REQUIRED": "Payment required to complete action",
        "ERR_BILLING_PAYMENT_FAILED": "Payment processing failed",
        "ERR_VALIDATION_INVALID_INPUT": "Request validation failed",
        "ERR_RATE_LIMIT_EXCEEDED": "Rate limit exceeded",
        "ERR_GENERIC_INTERNAL_ERROR": "An internal server error occurred",
    }

    return descriptions.get(name, name.replace("_", " ").title())


def generate_openapi_docs() -> dict[str, Any]:
    """Generate OpenAPI-compatible error documentation."""

    # Build error schemas
    error_codes = []

    for i18n_key in I18nKeys:
        if i18n_key.name.startswith("ERR_"):
            status_code = I18N_KEY_HTTP_STATUS.get(i18n_key, 500)
            category = get_error_category(i18n_key)

            error_codes.append(
                {
                    "code": i18n_key.value,
                    "i18n_key": i18n_key.name,
                    "category": category,
                    "http_status": status_code,
                    "description": get_error_description(i18n_key),
                }
            )

    # Group by category
    by_category = {}
    for error in error_codes:
        cat = error["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(error)

    # Build OpenAPI schema
    openapi_doc = {
        "openapi": "3.0.0",
        "info": {
            "title": "PolyScript API Error Documentation",
            "version": "1.0.0",
            "description": "Standardized error codes and responses for the PolyScript API",
        },
        "components": {
            "schemas": {
                "ErrorDetail": {
                    "type": "object",
                    "required": ["code", "message"],
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Machine-readable error code",
                            "example": "errors.auth.invalid_credentials",
                        },
                        "message": {
                            "type": "string",
                            "description": "Human-readable error message",
                            "example": "Invalid email or password",
                        },
                        "details": {
                            "type": "object",
                            "description": "Additional error context",
                            "nullable": True,
                        },
                        "request_id": {
                            "type": "string",
                            "description": "Request ID for tracing",
                            "example": "req_550e8400-e29b-41d4-a716-446655440000",
                            "nullable": True,
                        },
                        "documentation_url": {
                            "type": "string",
                            "description": "Link to error documentation",
                            "example": "https://api.polyscript.io/docs/errors/auth",
                            "nullable": True,
                        },
                    },
                },
                "ErrorResponse": {
                    "type": "object",
                    "required": ["error"],
                    "properties": {
                        "error": {
                            "$ref": "#/components/schemas/ErrorDetail",
                        },
                    },
                    "example": {
                        "error": {
                            "code": "errors.auth.invalid_credentials",
                            "message": "Invalid email or password",
                            "details": None,
                            "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                            "documentation_url": "https://api.polyscript.io/docs/errors/auth",
                        }
                    },
                },
            },
            "examples": {},
        },
        "x-error-codes": {
            "total": len(error_codes),
            "categories": by_category,
        },
    }

    # Add examples for each HTTP status
    status_examples = {}
    for error in error_codes:
        status = error["http_status"]
        if status not in status_examples:
            status_examples[status] = error

    for status, error in status_examples.items():
        openapi_doc["components"]["examples"][f"Error{status}"] = {
            "summary": f"HTTP {status} Error Example",
            "value": {
                "error": {
                    "code": error["code"],
                    "message": error["description"],
                    "details": None,
                    "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                    "documentation_url": f"https://api.polyscript.io/docs/errors/{error['category']}",
                }
            },
        }

    return openapi_doc


def generate_markdown_docs() -> str:
    """Generate Markdown error documentation."""

    lines = [
        "# PolyScript API Error Documentation",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overview",
        "",
        "All API errors follow a standardized response format:",
        "",
        "```json",
        '{\n  "error": {\n    "code": "errors.category.specific_error",\n    "message": "Human-readable error message",\n    "details": {...},\n    "request_id": "uuid",\n    "documentation_url": "https://api.polyscript.io/docs/errors/category"\n  }\n}',
        "```",
        "",
        "## Error Response Format",
        "",
        "| Field | Type | Description |",
        "|-------|------|-------------|",
        "| `code` | string | Machine-readable error code in dot notation |",
        "| `message` | string | Human-readable error message (localized) |",
        "| `details` | object | Optional additional context (field errors, etc.) |",
        "| `request_id` | string | Unique request ID for tracing |",
        "| `documentation_url` | string | Link to error documentation |",
        "",
        "## HTTP Status Codes",
        "",
        "| Status | Description |",
        "|--------|-------------|",
        "| 400 | Bad Request - Validation or malformed request |",
        "| 401 | Unauthorized - Authentication required or failed |",
        "| 402 | Payment Required - Payment needed for action |",
        "| 403 | Forbidden - Authenticated but lacks permission |",
        "| 404 | Not Found - Resource does not exist |",
        "| 409 | Conflict - Resource conflict or state mismatch |",
        "| 410 | Gone - Resource permanently unavailable |",
        "| 413 | Payload Too Large - File exceeds size limit |",
        "| 422 | Unprocessable Entity - Validation failed |",
        "| 429 | Too Many Requests - Rate limit exceeded |",
        "| 500 | Internal Server Error - Unexpected error |",
        "| 502 | Bad Gateway - External service error |",
        "| 503 | Service Unavailable - Temporary outage |",
        "| 504 | Gateway Timeout - Operation timeout |",
        "",
        "## Error Codes by Category",
        "",
    ]

    # Group errors by category
    errors_by_category: dict[str, list] = {}

    for i18n_key in I18nKeys:
        if i18n_key.name.startswith("ERR_"):
            category = get_error_category(i18n_key)
            if category not in errors_by_category:
                errors_by_category[category] = []

            errors_by_category[category].append(
                {
                    "code": i18n_key.value,
                    "i18n_key": i18n_key.name,
                    "status": I18N_KEY_HTTP_STATUS.get(i18n_key, 500),
                    "description": get_error_description(i18n_key),
                }
            )

    # Sort categories
    category_order = [
        "auth",
        "jobs",
        "transcripts",
        "teams",
        "billing",
        "validation",
        "rate_limit",
        "generic",
    ]

    for category in category_order:
        if category in errors_by_category:
            lines.append(f"### {category.title()}")
            lines.append("")
            lines.append("| Error Code | I18nKey | HTTP Status | Description |")
            lines.append("|------------|---------|-------------|-------------|")

            # Sort by status code
            sorted_errors = sorted(errors_by_category[category], key=lambda x: x["status"])

            for error in sorted_errors:
                lines.append(
                    f"| `{error['code']}` | `{error['i18n_key']}` | {error['status']} | {error['description']} |"
                )

            lines.append("")

    # Add examples section
    lines.extend(
        [
            "## Error Examples",
            "",
            "### Authentication Error (401)",
            "",
            "```json",
            '{\n  "error": {\n    "code": "errors.auth.invalid_credentials",\n    "message": "Invalid email or password",\n    "details": null,\n    "request_id": "req_550e8400-e29b-41d4-a716-446655440000",\n    "documentation_url": "https://api.polyscript.io/docs/errors/auth"\n  }\n}',
            "```",
            "",
            "### Validation Error (422)",
            "",
            "```json",
            '{\n  "error": {\n    "code": "errors.validation.invalid_input",\n    "message": "Request validation failed",\n    "details": {\n      "field": "email",\n      "error": "Invalid email format"\n    },\n    "request_id": "req_550e8400-e29b-41d4-a716-446655440000",\n    "documentation_url": "https://api.polyscript.io/docs/errors/validation"\n  }\n}',
            "```",
            "",
            "### Rate Limit Error (429)",
            "",
            "```json",
            '{\n  "error": {\n    "code": "errors.rate_limit.exceeded",\n    "message": "Rate limit exceeded. Please try again later.",\n    "details": {\n      "limit": 60,\n      "window": "1 minute",\n      "retry_after": 30\n    },\n    "request_id": "req_550e8400-e29b-41d4-a716-446655440000",\n    "documentation_url": "https://api.polyscript.io/docs/errors/rate-limit"\n  }\n}',
            "```",
            "",
            "## Localization",
            "",
            "Error messages are automatically localized based on the `Accept-Language` header.",
            "Supported languages: English (en), German (de), Spanish (es), French (fr), Japanese (jp).",
            "",
            "Example:",
            "",
            "```bash",
            'curl -H "Accept-Language: de" https://api.polyscript.io/v1/jobs/invalid-id',
            "```",
            "",
            "## Implementation Notes",
            "",
            "- All errors include a `request_id` for debugging and support",
            "- The `documentation_url` provides links to detailed error documentation",
            "- Validation errors include field-level details in the `details` object",
            "- Rate limit errors include `Retry-After` header with seconds to wait",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate error documentation for PolyScript API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --format openapi
  %(prog)s --format markdown --output error_docs.md
  %(prog)s --format openapi --output error_docs.json
        """,
    )

    parser.add_argument(
        "--format",
        choices=["openapi", "markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    # Generate documentation
    if args.format == "openapi":
        output = json.dumps(generate_openapi_docs(), indent=2)
    else:
        output = generate_markdown_docs()

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Error documentation written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
