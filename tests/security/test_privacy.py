import unittest
from src.privacy.masking import mask_phone_number, redact_provider_payload
class PrivacyTests(unittest.TestCase):
    def test_public_call_data_does_not_expose_phone_numbers(self) -> None:
        self.assertEqual(mask_phone_number("+15551234567"), "+*********67")
    def test_provider_secrets_are_redacted_from_events(self) -> None:
        payload = redact_provider_payload(
            {"CallSid": "CA1", "Auth_Token": "do-not-publish", "status": "completed"}
        )
        self.assertEqual(payload["Auth_Token"], "[REDACTED]")
        self.assertEqual(payload["CallSid"], "CA1")
if __name__ == "__main__":
    unittest.main()

