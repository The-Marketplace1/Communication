"""HTTP routes and request-to-domain translation."""
from __future__ import annotations
import os
from typing import Any
from urllib.parse import urlparse
from src.api.http import application_error, json_response, read_form, read_json

from src.chat.service import ChatService
from src.errors.exceptions import (
    AuthenticationError,
    CommunicationError,
    InternalError,
    NotFoundError,
)
from src.events import events
from src.events.bus import EventBus
from src.providers.twilio.webhooks import normalize_status, require_valid_webhook
from src.types.models import Actor, CommunicationEvent
from src.validation.validators import actor_type, required_string
class Router:
    def __init__(self, chat: ChatService, calls: Any, event_bus: EventBus) -> None:
        self.chat = chat
        self.calls = calls
        self.event_bus = event_bus
    def __call__(self, environ: dict[str, Any], start_response: Any) -> list[bytes]:
        try:
            method = environ.get("REQUEST_METHOD", "GET").upper()
            path = urlparse(environ.get("PATH_INFO", "/")).path.rstrip("/") or "/"
            if method == "GET" and path == "/health":
                return json_response(start_response, 200, {"status": "ok", "service": "communication"})
            if method == "POST" and path == "/v1/conversations":
                actor = self.actor(environ)
                return json_response(
                    start_response, 201, self.chat.create_conversation(actor, read_json(environ)).public()
                )
            if method == "GET" and path.startswith("/v1/conversations/"):
                actor = self.actor(environ)
                conversation_id = path.split("/")[-1]
                return json_response(
                    start_response, 200, self.chat.get_conversation(actor, conversation_id).public()
                )
            if method == "POST" and path.endswith("/messages") and path.startswith("/v1/conversations/"):
                actor = self.actor(environ)
                conversation_id = path.split("/")[3]
                return json_response(
                    start_response,
                    201,
                    self.chat.add_message(actor, conversation_id, read_json(environ)).public(),
                )
            if method == "POST" and path == "/v1/calls/masked":
                actor = self.actor(environ)
                return json_response(
                    start_response, 201, self.calls.create_masked_call(actor, read_json(environ)).public()
                )
            if method == "POST" and path == "/v1/providers/twilio/webhooks":
                return self.webhook(environ, start_response)
            return application_error(start_response, NotFoundError("route not found"))
        except CommunicationError as error:
            return 
application_error(start_response, error)
        except Exception:
            return application_error(
                return 
application_error(start_response, InternalError("internal communication error"))
                

    @staticmethod
    def actor(environ: dict[str, Any]) -> Actor:
        actor_id = environ.get("HTTP_X_ACTOR_ID", "").strip()
        actor_kind = environ.get("HTTP_X_ACTOR_TYPE", "").strip()
        if not actor_id or not actor_kind:
            raise AuthenticationError("X-Actor-Id and X-Actor-Type are required")
        return Actor(actor_id, actor_type(actor_kind))  # type: ignore[arg-type]
    def webhook(self, environ: dict[str, Any], start_response: Any) -> list[bytes]:
        form = read_form(environ)
        token = os.getenv("TWILIO_AUTH_TOKEN", "")
        if not token:
            raise AuthenticationError("provider webhook integration is not configured")
        url = os.getenv("PUBLIC_BASE_URL", "") + environ.get("PATH_INFO", "")
        require_valid_webhook(
            auth_token=token,
            url=url,
            form_data=form,
            signature=environ.get("HTTP_X_TWILIO_SIGNATURE", ""),
        )
        call_id = required_string(form, "CallSid")
        self.calls.apply_provider_update(
            call_id,
            normalize_status(required_string(form, "CallStatus")),
        )
        self.event_bus.publish(
	    CommunicationEvent(
                events.PROVIDER_WEBHOOK_RECEIVED, call_id, "provider", {"status": form["CallStatus"]}
            )
        )
        return json_response(start_response, 200, {"received": True})
