"""Domain types for the Communication service."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
ActorType = Literal["customer", "professional", "admin", "system", "provider"]
ConversationStatus = Literal["active", "closed"]
CallStatus = Literal["initiated", "ringing", "in_progress", "completed", "failed"]
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
@dataclass(frozen=True)
class Actor:
    id: str
    type: ActorType
@dataclass
class Message:
    id: str
    conversation_id: str
    sender_id: str
    sender_type: ActorType
    body: str
    created_at: str = field(default_factory=utc_now)
    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_id": self.sender_id,
            "sender_type": self.sender_type,
            "body": self.body,
            "created_at": self.created_at,
        }
@dataclass
class Conversation:
    id: str
    customer_id: str
    professional_id: str
    status: ConversationStatus = "active"
    messages: list[Message] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    closed_at: str | None = None
    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "professional_id": self.professional_id,
            "status": self.status,
            "messages": [message.public() for message in self.messages],
            "created_at": self.created_at,
            "closed_at": self.closed_at,
        }
@dataclass
class MaskedCall:
    id: str
    conversation_id: str
    caller_id: str
    recipient_id: str
    caller_number: str
    recipient_number: str
    provider_call_id: str | None = None
    status: CallStatus = "initiated"
    created_at: str = field(default_factory=utc_now)
    ended_at: str | None = None
    def public(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "caller_id": self.caller_id,
            "recipient_id": self.recipient_id,
            "status": self.status,
            "provider_call_id": self.provider_call_id,
            "created_at": self.created_at,
            "ended_at": self.ended_at,
        }
@dataclass(frozen=True)
class CommunicationEvent:
    name: str
    aggregate_id: str
    actor_id: str
    payload: dict[str, Any]
    occurred_at: str = field(default_factory=utc_now)
    def public(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "aggregate_id": self.aggregate_id,
            "actor_id": self.actor_id,
            "payload": self.payload,
            "occurred_at": self.occurred_at,
        }
""
