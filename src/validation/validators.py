"""Input validation shared by the API and domain services."""
from __future__ import annotations
import re
from typing import Any
from src.errors.exceptions import ValidationError
PHONE_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
ACTOR_TYPES = {"customer", "professional", "admin", "system", "provider"}
def required_string(data: dict[str, Any], key: str, *, maximum: int = 255) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{key} is required")
    value = value.strip()
    if len(value) > maximum:
        raise ValidationError(f"{key} must be at most {maximum} characters")
    return value
def actor_type(value: str) -> str:
    if value not in ACTOR_TYPES:
        raise ValidationError("unsupported actor type")
    return value
def phone_number(value: str) -> str:
    if not isinstance(value, str) or not PHONE_PATTERN.fullmatch(value):
        raise ValidationError("phone numbers must use E.164 format")
    return value
def message_body(data: dict[str, Any]) -> str:
    value = required_string(data, "body", maximum=4000)
    if "\x00" in value:
        raise ValidationError("body contains an invalid character")
    return value

