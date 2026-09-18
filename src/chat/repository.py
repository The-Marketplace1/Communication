"""Repository boundary for communication-owned persistence."""
from __future__ import annotations
from threading import RLock
from src.types.models import Conversation
class ConversationRepository:
    """Safe default store for local development; replace behind this boundary."""
    def __init__(self) -> None:
        self._conversations: dict[str, Conversation] = {}
        self._lock = RLock()
    def save(self, conversation: Conversation) -> Conversation:
        with self._lock:
            self._conversations[conversation.id] = conversation
        return conversation
    def get(self, conversation_id: str) -> Conversation | None:
        with self._lock:
            return self._conversations.get(conversation_id)
    def list_for_actor(self, actor_id: str) -> list[Conversation]:
        with self._lock:
            return [
                conversation
                for conversation in self._conversations.values()
                if actor_id in {conversation.customer_id, conversation.professional_id}
            ]
