"""Communication service entry point."""
from __future__ import annotations
import os
from wsgiref.simple_server import make_server
from src.api.routes import Router
from src.calls.service import CallService
from src.chat.repository import ConversationRepository
from src.chat.service import ChatService
from src.events.bus import EventBus
from src.providers.twilio.client import (
    HttpTwilioClient,
    LocalTwilioClient,
    TwilioClient,
    TwilioConfiguration,
)

from src.app.config import settings
def build_application() -> Router:
    event_bus = EventBus()
    conversations = ConversationRepository()
    chat = ChatService(conversations, event_bus)
    twilio: TwilioClient
    if TwilioConfiguration.configured():
        twilio = HttpTwilioClient(
            account_sid=os.environ["TWILIO_ACCOUNT_SID"],
            auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            twilio_number=os.environ["TWILIO_NUMBER"],
            public_base_url=settings.public_base_url,
            
            
        )
    else:
        twilio = LocalTwilioClient()
    calls = CallService(conversations, event_bus, twilio())
    return Router(chat, calls, event_bus)
def main() -> None:
    application = build_application()
    with make_server(settings.host, settings.port, application) as server:
        print(f"communication service listening on {settings.host}:{settings.port}", flush=True)
        server.serve_forever()
if __name__ == "__main__":
    main()

