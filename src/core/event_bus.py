"""Event bus for inter-bot communication."""

import asyncio
import logging
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict


@dataclass
class Event:
    """Represents an event in the system."""
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """
    Central event bus for communication between bots.

    Implements publish-subscribe pattern for loosely coupled
    bot communication.
    """

    def __init__(self):
        """Initialize the event bus."""
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000
        self.logger = logging.getLogger("pipe.eventbus")

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Async function to call when event is published
        """
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"New subscriber for event type: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"Subscriber removed from event type: {event_type}")

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish
        """
        self.logger.info(f"Publishing event: {event.event_type} from {event.source}")

        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)

        # Notify subscribers
        subscribers = self.subscribers.get(event.event_type, [])
        if subscribers:
            tasks = [callback(event) for callback in subscribers]
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            self.logger.debug(f"No subscribers for event type: {event.event_type}")

    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Get event history.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of events
        """
        if event_type:
            filtered = [e for e in self.event_history if e.event_type == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history.clear()
        self.logger.info("Event history cleared")
