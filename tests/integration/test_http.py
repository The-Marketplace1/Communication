import io
import json
import unittest
from typing import Any
from src.app.main import build_application
def request(
    application: Any,
    method: str,
    path: str,
    body: dict[str, object] | None = None,
    *,
    actor_id: str | None = None,
    actor_type: str | None = None,
) -> tuple[str, dict[str, object]]:
    payload = json.dumps(body or {}).encode()
    environment = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(payload)),
        "CONTENT_TYPE": "application/json",
        "wsgi.input": io.BytesIO(payload),
    }
    if actor_id:
        environment["HTTP_X_ACTOR_ID"] = actor_id
    if actor_type:
        environment["HTTP_X_ACTOR_TYPE"] = actor_type
    response: dict[str, object] = {}
    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        response["status"] = status
        response["headers"] = headers
    raw = b"".join(application(environment, start_response))
    return str(response["status"]), json.loads(raw)
class HttpIntegrationTests(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        status, payload = request(build_application(), "GET", "/health")
        self.assertTrue(status.startswith("200"))
        self.assertEqual(payload["status"], "ok")
    def test_conversation_and_message_flow(self) -> None:
        application = build_application()
        status, conversation = request(
            application,
            "POST",
            "/v1/conversations",
            {"customer_id": "customer-1", "professional_id": "professional-1"},
            actor_id="customer-1",
            actor_type="customer",
        )
        self.assertTrue(status.startswith("201"))
        conversation_id = str(conversation["id"])
        status, message = request(
            application,
            "POST",
            f"/v1/conversations/{conversation_id}/messages",
            {"body": "I need help with my booking."},
            actor_id="customer-1",
            actor_type="customer",
        )
        self.assertTrue(status.startswith("201"))
        self.assertEqual(message["sender_id"], "customer-1")
    def test_missing_actor_is_rejected(self) -> None:
        status, payload = request(
            build_application(), "POST", "/v1/conversations", {"customer_id": "c", "professional_id": "p"}
        )
        self.assertTrue(status.startswith("401"))
        self.assertEqual(payload["error"]["code"], "authentication_required")
if __name__ == "__main__":
    unittest.main()

