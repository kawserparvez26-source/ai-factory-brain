"""Event bus for Phase 6B.

Central event publication and subscription.
No async, no persistence, synchronous only.
"""

from __future__ import annotations

from typing import List, Optional

from .definitions import EventDefinition, EventType
from .listeners import EventListener, ListenerRegistry


class EventBus:
    """Central event distribution point.

    Responsibilities:
    - Maintain listener registry
    - Publish events synchronously
    - Call all registered listeners
    - No persistence or filtering

    Design:
    - Stateless (registry is only state)
    - Synchronous execution
    - No error handling in event propagation
    - Listeners are responsible for handling exceptions

    Notes:
    - This is NOT a message queue (no persistence)
    - This is NOT async (no coroutines)
    - This is NOT persistent (in-memory only)
    """

    def __init__(self) -> None:
        """Initialize event bus with empty registry."""
        self.registry = ListenerRegistry()

    def subscribe(self, event_type: EventType, listener: EventListener) -> str:
        """Subscribe to events of a type.

        Args:
            event_type: EventType to subscribe to
            listener: Callable to invoke when event published

        Returns:
            Subscription ID (for later unsubscribe)

        Example:
            def my_handler(event):
                print(f"Task: {event.task_id}")

            bus = EventBus()
            sub_id = bus.subscribe(EventType.TASK_COMPLETED, my_handler)
            # Later: bus.unsubscribe(sub_id)
        """
        return self.registry.subscribe(event_type, listener)

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from an event.

        Args:
            subscription_id: ID returned by subscribe()

        Returns:
            True if unsubscribed, False if not found
        """
        return self.registry.unsubscribe(subscription_id)

    def publish(self, event: EventDefinition) -> None:
        """Publish an event to all listeners.

        Calls all registered listeners synchronously.
        Listener exceptions do NOT stop other listeners.

        Args:
            event: EventDefinition to publish

        Notes:
        - Synchronous (blocking until all listeners return)
        - Listeners are called in subscription order
        - If a listener raises, it is NOT caught (caller responsible)
        """
        listeners = self.registry.get_listeners(event.event_type)
        for listener in listeners:
            listener(event)

    def publish_safe(self, event: EventDefinition) -> List[Exception]:
        """Publish an event, catching listener exceptions.

        Calls all registered listeners, collecting exceptions.
        Listener errors do NOT prevent other listeners from running.

        Args:
            event: EventDefinition to publish

        Returns:
            List of exceptions raised by listeners (may be empty)

        Notes:
        - Synchronous (blocking until all listeners return)
        - Useful for testing or non-critical listeners
        - Exceptions are returned, not raised
        """
        listeners = self.registry.get_listeners(event.event_type)
        errors = []
        for listener in listeners:
            try:
                listener(event)
            except Exception as e:
                errors.append(e)
        return errors

    def has_listeners(self, event_type: EventType) -> bool:
        """Check if there are listeners for an event type.

        Args:
            event_type: EventType to check

        Returns:
            True if listeners exist
        """
        return self.registry.has_listeners(event_type)

    def clear(self) -> None:
        """Clear all listeners.

        Useful for testing and cleanup.
        """
        self.registry.clear()
