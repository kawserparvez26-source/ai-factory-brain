"""Phase 6B: Event System.

Event bus for decoupling dispatcher from event listeners.

Public API:
- EventBus: Central event distribution
- EventDefinition: Event structure
- EventType: Event category enumeration
- EventStatus: Event state enumeration
- EventListener: Protocol for event handlers

Design:
- No async, no threading, synchronous only
- Simple dict-based registry
- No persistence, in-memory only
- No external dependencies

[TODO - Phase 6C: Event persistence]
[TODO - Phase 6C: Event filtering]
[TODO - Phase 7+: Event history/audit]
"""

from .definitions import (
    EventDefinition,
    EventType,
    EventStatus,
)
from .listeners import (
    EventListener,
    ListenerRegistry,
)
from .bus import EventBus

__all__ = [
    "EventBus",
    "EventDefinition",
    "EventType",
    "EventStatus",
    "EventListener",
    "ListenerRegistry",
]

__version__ = "1.0.0"
__schema_version__ = "1.0"
