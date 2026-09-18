import unittest
from src.calls.service import AbuseGuard, CallService
from src.chat.repository import ConversationRepository
from src.chat.service import ChatService
from src.events.bus import EventBus
from src.providers.twilio.client import LocalTwilioClient
from src.types.models import Actor
class MaskedCallE2ETests(unittest.TestCase):
    def test_participant_can_start_a_masked_call(self) -> None:
        event_bus = EventBus()
        repository = ConversationRepository()
        chat = ChatService(repository, event_bus)
        calls = CallService(
            repository, event_bus, LocalTwilioClient(), AbuseGuard(max_calls_per_actor=1)
        )
        conversation = chat.create_conversation(
            Actor("customer-1", "customer"),
            {"customer_id": "customer-1", "professional_id": "professional-1"},
        )
        call = calls.create_masked_call(
            Actor("customer-1", "customer"),
            {
                "conversation_id": conversation.id,
                "recipient_id": "professional-1",
                "caller_number": "+2348012345678",
                "recipient_number": "+2348098765432",
            },
        )
        self.assertEqual(call.status, "ringing")
        self.assertIsNotNone(call.provider_call_id)
        self.assertNotIn("+2348012345678", call.public().__repr__())
        self.assertTrue(any(event.name == "communication.call.created" for event in event_bus.recent()))
if __name__ == "__main__":
    unittest.main()

