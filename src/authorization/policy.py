"""Authorization rules owned by Communication, not authentication."""
from __future__ import annotations
from src.errors.exceptions import AuthorizationError
from src.types.models import Actor, Conversation

def can_view_conversation(actor: Actor, conversation: Conversation) -> bool:
    return (
        actor.type in {"admin", "system"}
        or actor.id in {conversation.customer_id, conversation.professional_id}
    )

def require_conversation_access(actor: Actor, conversation: Conversation) -> None:
    if not can_view_conversation(actor, conversation):
        raise AuthorizationError("actor is not a participant in this conversation")

def require_message_access(actor: Actor, conversation: Conversation) -> None:
    require_conversation_access(actor, conversation)
    if conversation.status != "active":
        raise AuthorizationError("conversation is closed")

def require_call_access(actor: Actor, conversation: Conversation) -> None:
    require_conversation_access(actor, conversation)
    if actor.type not in {"customer", "professional", "admin", "system"}:
        raise AuthorizationError("actor cannot initiate calls")
