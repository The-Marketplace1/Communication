"""Provider webhook verification and normalized status handling."""
from __future__ import annotations
import base64
import hashlib
import hmac
from src.errors.exceptions import AuthenticationError, ValidationError
def verify_signature(
    *, auth_token: str, url: str, form_data: dict[str, str], signature: str
) -> bool:
    """Verify Twilio's HMAC-SHA1 signature without retaining provider secrets."""
    payload = url + "".join(
        f"{key}{form_data[key]}" for key in sorted(form_data)
    )
    digest = hmac.new(auth_token.encode(), payload.encode(), hashlib.sha1).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature)
def require_valid_webhook(
    *, auth_token: str, url: str, form_data: dict[str, str], signature: str
) -> None:
    if not signature or not verify_signature(
        auth_token=auth_token,
        url=url,
        form_data=form_data,
        signature=signature,
    ):
        raise AuthenticationError("invalid provider signature")
def normalize_status(value: str) -> str:
    status = value.lower().strip()
    allowed = {"initiated", "ringing", "in-progress", "completed", "failed", "busy", "no-answer"}
    if status not in allowed:
        raise ValidationError("unsupported provider status")
    return "in_progress" if status == "in-progress" else (
        "failed" if status in {"busy", "no-answer"} else status
    )

