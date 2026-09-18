"""Conversation and message use cases."""
from __future__ import annotations
from src.authorization.policy import require_message_access
from src.chat.repository import ConversationRepository
from src.errors.exceptions import NotFoundError
from src.events import events
from src.events.bus import EventBus
from src.types.models import Actor, CommunicationEvent, Conversation, Message
from src.utils.ids import new_id
from src.validation.validators import message_body, required_string
class ChatService:
    def __init__(self, repository: ConversationRepository, event_bus: EventBus) -> None:
        self.repository = repository
        self.event_bus = event_bus
    def create_conversation(self, actor: Actor, data: dict[str, object]) -> Conversation:
        customer_id = required_string(data, "customer_id")
        professional_id = required_string(data, "professional_id")
        if actor.type not in {"admin", "system"} and actor.id not in {
            customer_id,
            professional_id,
        }:
            from src.errors.exceptions import AuthorizationError
            raise AuthorizationError("actor must be a conversation participant")
        conversation = Conversation(
            id=new_id("conv"),
            customer_id=customer_id,
            professional_id=professional_id,
        )
        self.repository.save(conversation)
        self.event_bus.publish(
            CommunicationEvent(events.CONVERSATION_CREATED, conversation.id, actor.id, {})
        )
        return conversation
    def get_conversation(self, actor: Actor, conversation_id: str) -> Conversation:
        conversation = self.repository.get(conversation_id)
        if conversation is None:
            raise NotFoundError("conversation not found")
        from src.authorization.policy import require_conversation_access
        require_conversation_access(actor, conversation)
        return conversation
    def add_message(
        self, actor: Actor, conversation_id: str, data: dict[str, object]
    ) -> Message:
        conversation = self.get_conversation(actor, conversation_id)
        require_message_access(actor, conversation)
        message = Message(
            id=new_id("msg"),
            conversation_id=conversation.id,
            sender_id=actor.id,
            sender_type=actor.type,
            body=message_body(data),
        )
        conversation.messages.append(message)
        self.repository.save(conversation)
        self.event_bus.publish(
            CommunicationEvent(
                events.MESSAGE_CREATED,
                conversation.id,
                actor.id,
                {"message_id": message.id},
            )
        )
        return message

