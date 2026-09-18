import base64
import hashlib
import hmac
import unittest
from src.providers.twilio.webhooks import normalize_status, verify_signature
class TwilioProviderTests(unittest.TestCase):
    def test_verifies_twilio_signature(self) -> None:
        token = "local-test-token"
        url = "https://example.test/v1/providers/twilio/webhooks"
        form = {"CallSid": "call_123", "CallStatus": "completed"}
        value = url + "CallSidcall_123CallStatuscompleted"
        signature = base64.b64encode(
            hmac.new(token.encode(), value.encode(), hashlib.sha1).digest()
        ).decode()
        self.assertTrue(
            verify_signature(auth_token=token, url=url, form_data=form, signature=signature)
        )
    def test_normalizes_provider_status(self) -> None:
        self.assertEqual(normalize_status("in-progress"), "in_progress")
        self.assertEqual(normalize_status("no-answer"), "failed")
if __name__ == "__main__":
    unittest.main()

