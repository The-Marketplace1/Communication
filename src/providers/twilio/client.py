"""Twilio boundary. No SDK is required; production wiring can implement this port."""
from __future__ import annotations
import base64
import http.client
import html
import json
import os
import secrets
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlencode
from src.errors.exceptions import ProviderError
from typing import Protocol

class TwilioClient(Protocol):
    def start_masked_call(
        self, *, caller_number: str, recipient_number: str, callback_reference: str
    ) -> str:
        ...

class LocalTwilioClient:
    """Deterministic local provider substitute that never contacts Twilio."""
    def start_masked_call(
        self, *, caller_number: str, recipient_number: str, callback_reference: str
    ) -> str:
        del caller_number, recipient_number
        return f"local_{callback_reference}_{secrets.token_hex(4)}"

class HttpTwilioClient:
    """Twilio REST adapter for masked outbound calls."""

    def __init__(
        self,
        *,
        account_sid: str,
        auth_token: str,
        twilio_number: str,
        public_base_url: str,
        timeout_seconds: int = 10,
    ) -> None:
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.twilio_number = twilio_number
        self.public_base_url = public_base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def start_masked_call(
        self, *, caller_number: str, recipient_number: str, callback_reference: str
    ) -> str:
        # Twilio calls the caller first, then connects the recipient through the
        # provider-owned number, so neither participant learns the other number.
        twiml = (
            "<Response><Dial callerId=\""
            + html.escape(self.twilio_number, quote=True)
            + "\"><Number>"
            + html.escape(recipient_number, quote=True)
            + "</Number></Dial></Response>"
        )
        payload = urlencode(
            {
                "To": caller_number,
                "From": self.twilio_number,
                "Twiml": twiml,
                "StatusCallback": f"{self.public_base_url}/v1/providers/twilio/webhooks",
                "StatusCallbackEvent": "initiated ringing answered completed",
            }
        ).encode()
        path = (
            f"/2010-04-01/Accounts/{quote(self.account_sid, safe='')}/Calls.json"
        )
        credentials = base64.b64encode(
            f"{self.account_sid}:{self.auth_token}".encode()
        ).decode()
        connection = http.client.HTTPSConnection(
            "api.twilio.com", timeout=self.timeout_seconds
        )
        try:
            connection.request(
                "POST",
                path,
                body=payload,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
            response = connection.getresponse()
            content_type = response.getheader("Content-Type", "")
            raw_body = response.read()
        except OSError as exc:
            raise ProviderError("Twilio request failed") from exc
        finally:
            connection.close()
        if response.status >= 400:
            raise ProviderError("Twilio rejected the masked call")
        
        provider_call_id = None
        decoded_body = raw_body.decode("utf-8")

        try:
            # Parse as XML if Twilio bypasses the Accept header or defaults to an XML response payload
            if "xml" in content_type or decoded_body.strip().startswith("<?xml"):
                root = ET.fromstring(decoded_body)
                # Look up the Call SID element inside the Twilio XML structure
                sid_element = root.find(".//Sid") or root.find(".//sid")
                if sid_element is not None:
                    provider_call_id = sid_element.text
            else:
                # Fallback standard JSON parsing parsing logic
                result = json.loads(decoded_body)
                provider_call_id = result.get("sid")
        except (KeyError, TypeError, ValueError, ET.ParseError) as exc:
            raise ProviderError("Twilio returned an invalid call response payload structure") from exc

        if not isinstance(provider_call_id, str) or not provider_call_id:
            raise ProviderError("Twilio returned an invalid call identifier")
            
        del callback_reference
        return provider_call_id

class TwilioConfiguration:
    @staticmethod
    def configured() -> bool:
        return all(
            os.getenv(name)
            for name in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_NUMBER")
        )
