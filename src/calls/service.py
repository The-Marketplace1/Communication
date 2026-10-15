"""Masked-call orchestration and provider-independent call state."""
from __future__ import annotations
from src.authorization.policy import require_call_access
from src.chat.repository import ConversationRepository
from src.errors.exceptions import ConflictError, NotFoundError
from src.events import events
from src.events.bus import EventBus
from src.providers.twilio.client import TwilioClient
from src.privacy.masking import mask_phone_number
from src.types.models import Actor, CommunicationEvent, MaskedCall
from src.utils.ids import new_id
from src.validation.validators import phone_number, required_string

class AbuseGuard:
    def __init__(self, max_calls_per_actor: int = 10) -> None:
        self.max_calls_per_actor = max_calls_per_actor
        self._calls: dict[str, int] = {}

    def check_call(self, actor_id: str) -> None:
        count = self._calls.get(actor_id, 0)
        if count >= self.max_calls_per_actor:
            from src.errors.exceptions import AbuseError
            raise AbuseError("call rate limit exceeded")
        self._calls[actor_id] = count + 1

class CallService:
    def __init__(
        self,
        conversations: ConversationRepository,
        event_bus: EventBus,
        twilio: TwilioClient,
        abuse_guard: AbuseGuard | None = None,
    ) -> None:
        self.conversations = conversations
        self.event_bus = event_bus
        self.twilio = twilio
        self.abuse_guard = abuse_guard or AbuseGuard()
        self._calls: dict[str, MaskedCall] = {}

    def create_masked_call(self, actor: Actor, data: dict[str, object]) -> MaskedCall:
        conversation_id = required_string(data, "conversation_id")
        conversation = self.conversations.get(conversation_id)
        if conversation is None:
            raise NotFoundError("conversation not found")
        require_call_access(actor, conversation)
        recipient_id = required_string(data, "recipient_id")
        caller_number = phone_number(required_string(data, "caller_number"))
        recipient_number = phone_number(required_string(data, "recipient_number"))
        if recipient_id not in {conversation.customer_id, conversation.professional_id}:
            raise ConflictError("recipient is not a conversation participant")
        if actor.id == recipient_id:
            raise ConflictError("caller and recipient must be different")
        self.abuse_guard.check_call(actor.id)
        call = MaskedCall(
            id=new_id("call"),
            conversation_id=conversation_id,
            caller_id=actor.id,
            recipient_id=recipient_id,
            caller_number=caller_number,
            recipient_number=recipient_number,
        )
        provider_call_id = self.twilio.start_masked_call(
            caller_number=caller_number,
            recipient_number=recipient_number,
            callback_reference=call.id,
        )
        call.provider_call_id = provider_call_id
        call.status = "ringing"
        self._calls[call.id] = call
        self.event_bus.publish(
            CommunicationEvent(
                events.CALL_CREATED,
                call.id,
                actor.id,
                {
                    "conversation_id": call.conversation_id,
                    "caller": mask_phone_number(caller_number),
                    "recipient": mask_phone_number(recipient_number),
                },
            )
        )
        return call

    def apply_provider_update(self, call_id: str, status: str) -> MaskedCall:
        call = self._calls.get(call_id)
        if call is None:
            call = next(
                (candidate for candidate in self._calls.values()
                 if candidate.provider_call_id == call_id),
                None,
            )
        if call is None:
            raise NotFoundError("call not found")
        if status not in {"initiated", "ringing", "in_progress", "completed", "failed"}:
            raise ConflictError("unsupported provider call status")
        call.status = status  # type: ignore[assignment]
        if status in {"completed", "failed"}:
            from src.utils.clock import now_iso
            call.ended_at = now_iso()
        self.event_bus.publish(
            CommunicationEvent(events.CALL_UPDATED, call.id, "provider", {"status": status})
        )
        return call

    def get_call(self, call_id: str) -> MaskedCall:
        call = self._calls.get(call_id)
        if call is None:
            raise NotFoundError("call not found")
        return call
