"""Event definitions for Phase 6B.

Defines event structure, types, and status.
No execution logic, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, Optional
from uuid import uuid4


class EventType(Enum):
    """Categories of runtime events."""

    # Task lifecycle
    TASK_REGISTERED = "task_registered"
    TASK_QUEUED = "task_queued"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"

    # Executor lifecycle
    EXECUTOR_SELECTED = "executor_selected"
    EXECUTOR_STARTED = "executor_started"
    EXECUTOR_COMPLETED = "executor_completed"
    EXECUTOR_FAILED = "executor_failed"

    # Result lifecycle
    RESULT_VALIDATED = "result_validated"
    RESULT_INVALID = "result_invalid"

    # Session lifecycle
    SESSION_CREATED = "session_created"
    SESSION_CLOSED = "session_closed"

    # Error handling (flows)
    RETRY_ATTEMPT = "retry_attempt"
    TIMEOUT_EXCEEDED = "timeout_exceeded"
    CANCELLATION_REQUESTED = "cancellation_requested"


class EventStatus(Enum):
    """Status of an event (for event tracking)."""

    CREATED = "created"
    PUBLISHED = "published"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass(frozen=True)
class EventDefinition:
    """Immutable event structure.

    Represents a single event in the runtime.
    No modification after creation.

    Attributes:
        event_id: Unique event identifier
        event_type: Category (EventType)
        source: Where event originated (e.g., "dispatcher", "executor")
        task_id: Associated task ID (optional)
        session_id: Associated session ID (optional)
        timestamp: UTC creation time
        status: Event status
        payload: Event-specific data
        metadata: Additional context
        schema_version: Data model version
    """

    schema_version: ClassVar[str] = "1.0"

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = field()
    source: str = field()
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: EventStatus = field(default=EventStatus.CREATED)
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"Event(type={self.event_type.value}, "
            f"source={self.source}, "
            f"task_id={self.task_id}, "
            f"timestamp={self.timestamp.isoformat()})"
        )
