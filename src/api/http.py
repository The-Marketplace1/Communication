"""Minimal WSGI HTTP adapter, keeping the service dependency-free."""
from __future__ import annotations
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs
from src.errors.exceptions import CommunicationError
def json_response(start_response: Callable[..., Any], status: int, payload: object) -> list[bytes]:
    body = json.dumps(payload).encode("utf-8")
    start_response(
        f"{status} {'OK' if status < 400 else 'ERROR'}",
        [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]
def read_json(environ: dict[str, Any]) -> dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        if length > 1_000_000:
            raise ValueError("request too large")
        raw = environ["wsgi.input"].read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON object required")
        return data
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        from src.errors.exceptions import ValidationError
        raise ValidationError("request body must be a JSON object") from exc
def read_form(environ: dict[str, Any]) -> dict[str, str]:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    raw = environ["wsgi.input"].read(length).decode("utf-8")
    return {key: values[-1] for key, values in parse_qs(raw).items() if values}
def application_error(
    start_response: Callable[..., Any], error: CommunicationError
) -> list[bytes]:
    return json_response(
        start_response,
        error.status,
        {"error": {"code": error.code, "message": error.message}},
    )
