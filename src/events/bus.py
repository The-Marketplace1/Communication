"""In-process event publisher; integration consumers can subscribe at the boundary."""
from __future__ import annotations
from collections.abc import Callable
from threading import Lock
from src.types.models import CommunicationEvent
EventHandler = Callable[[CommunicationEvent], None]
class EventBus:
    def __init__(self) -> None:
        self._events: list[CommunicationEvent] = []
        self._handlers: list[EventHandler] = []
        self._lock = Lock()
    def subscribe(self, handler: EventHandler) -> None:
        with self._lock:
            self._handlers.append(handler)
    def publish(self, event: CommunicationEvent) -> None:
        with self._lock:
            self._events.append(event)
            handlers = tuple(self._handlers)
        for handler in handlers:
            handler(event)
    def recent(self) -> list[CommunicationEvent]:
        with self._lock:
            return list(self._events)

