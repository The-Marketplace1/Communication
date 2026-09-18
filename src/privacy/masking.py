"""Privacy controls for phone numbers and communication payloads."""
from __future__ import annotations
def mask_phone_number(number: str) -> str:
    """Expose only the final two digits to application callers."""
    if len(number) < 4:
        return "***"
    return f"+{'*' * max(0, len(number) - 3)}{number[-2:]}"
def redact_provider_payload(payload: object) -> object:
    """Remove common secrets before a provider payload enters an event."""
    if not isinstance(payload, dict):
        return payload
    secret_keys = {"token", "authorization", "signature", "account_sid", "auth_token"}
    return {
        key: "[REDACTED]" if key.lower() in secret_keys else value
        for key, value in payload.items()
    }
