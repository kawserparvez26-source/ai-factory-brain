"""Phase 6B: Task Queue.

Queue protocol and registry for task queuing.

Public API:
- TaskQueue: Protocol for queue implementations
- QueueRegistry: Registry for queue types
- QueueType: Queue type enumeration
- QueueStatus: Queue status enumeration

Design:
- No async, no threading, synchronous only
- Structure/interface only
- No execution logic
- No persistence

[TODO - Phase 6C: Queue persistence]
[TODO - Phase 6C: Queue filtering/prioritization]
[TODO - Phase 7+: Queue monitoring/metrics]
"""

from .protocol import (
    TaskQueue,
    QueueType,
    QueueStatus,
)

__all__ = [
    "TaskQueue",
    "QueueType",
    "QueueStatus",
]

__version__ = "1.0.0"
__schema_version__ = "1.0"
