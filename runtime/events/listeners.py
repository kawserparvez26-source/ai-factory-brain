"""Event listeners and registry for Phase 6B.

Defines listener protocol and in-memory registry.
No persistence, no complex behavior.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Protocol

from .definitions import EventDefinition, EventType


class EventListener(Protocol):
    """Protocol for event handlers.

    Any callable accepting an EventDefinition.
    Handlers must be synchronous and non-blocking.
    """

    def __call__(self, event: EventDefinition) -> None:
        """Handle an event.

        Args:
            event: The EventDefinition to process

        Notes:
        - Must be synchronous (no async)
        - Must not raise exceptions (handler is responsible for error handling)
        - Must complete quickly (no long-running operations)
        """
        ...


class ListenerRegistry:
    """Registry for event listeners.

    Maintains subscriptions by event type.
    Supports subscribe/unsubscribe.

    Design:
    - Simple dict-based storage
    - In-memory only
    - No persistence
    - No ordering guarantees
    """

    def __init__(self) -> None:
        """Initialize empty listener registry."""
        self._listeners: Dict[EventType, List[tuple[str, EventListener]]] = {}
        self._subscription_counter = 0

    def subscribe(
        self, event_type: EventType, listener: EventListener
    ) -> str:
        """Subscribe to events of a type.

        Args:
            event_type: EventType to subscribe to
            listener: Callable that handles the event

        Returns:
            Subscription ID (for later unsubscribe)

        Raises:
            ValueError: If listener is None
        """
        if listener is None:
            raise ValueError("Listener cannot be None")

        if event_type not in self._listeners:
            self._listeners[event_type] = []

        subscription_id = f"{event_type.value}_{self._subscription_counter}"
        self._subscription_counter += 1

        self._listeners[event_type].append((subscription_id, listener))
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from an event.

        Args:
            subscription_id: ID returned by subscribe()

        Returns:
            True if unsubscribed, False if not found
        """
        for event_type in self._listeners.values():
            for i, (sub_id, _) in enumerate(event_type):
                if sub_id == subscription_id:
                    event_type.pop(i)
                    return True
        return False

    def get_listeners(self, event_type: EventType) -> List[EventListener]:
        """Get all listeners for an event type.

        Args:
            event_type: EventType to query

        Returns:
            List of EventListener callables
        """
        if event_type not in self._listeners:
            return []
        return [listener for _, listener in self._listeners[event_type]]

    def has_listeners(self, event_type: EventType) -> bool:
        """Check if there are listeners for an event type.

        Args:
            event_type: EventType to check

        Returns:
            True if listeners exist, False otherwise
        """
        return event_type in self._listeners and len(self._listeners[event_type]) > 0

    def clear(self) -> None:
        """Clear all listeners."""
        self._listeners.clear()
