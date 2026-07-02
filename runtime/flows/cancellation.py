"""Cancellation flow for Phase 6B.

Defines cancellation policy structure for task cancellations.
No execution logic, structure only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, Optional
from datetime import datetime
from uuid import uuid4


class CancellationReason(Enum):
    """Reasons for task cancellation."""

    USER_REQUESTED = "user_requested"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEPENDENCY_FAILED = "dependency_failed"
    SESSION_CLOSED = "session_closed"
    UNKNOWN = "unknown"


class CancellationAction(Enum):
    """Actions to take on cancellation."""

    IMMEDIATE = "immediate"
    GRACEFUL = "graceful"
    CLEANUP = "cleanup"


@dataclass(frozen=True)
class CancellationFlow:
    """Immutable cancellation policy structure.

    Represents cancellation configuration for tasks.
    No modification after creation.

    Attributes:
        cancellation_id: Unique cancellation identifier
        task_id: Associated task ID
        reason: Reason for cancellation
        action: Action to take (IMMEDIATE, GRACEFUL, CLEANUP)
        cancelled_at: Timestamp of cancellation
        metadata: Additional context
        schema_version: Data model version

    Notes:
    - Structure only (no cancellation execution)
    - No business logic
    - Used to track cancellation intent
    - Actual cancellation execution at dispatcher level (Phase 7+)
    """

    schema_version: ClassVar[str] = "1.0"

    cancellation_id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = field()
    reason: CancellationReason = field(default=CancellationReason.UNKNOWN)
    action: CancellationAction = field(default=CancellationAction.GRACEFUL)
    cancelled_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"CancellationFlow(task_id={self.task_id}, "
            f"reason={self.reason.value}, "
            f"action={self.action.value})"
        )
