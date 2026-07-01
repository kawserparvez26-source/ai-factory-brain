"""Execution state machine and event definitions for Phase 5.

Contains only the state transitions mapping, ExecutionEvent dataclass and
validation helpers. No execution logic, no stores, standard-library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Dict, Set, Any
from uuid import uuid4

from .execution_models import ExecutionStatus


# Allowed transitions map (string values) — Phase 5 structural rules only
_ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    ExecutionStatus.CREATED.value: {ExecutionStatus.QUEUED.value, ExecutionStatus.CANCELLED.value},
    ExecutionStatus.QUEUED.value: {ExecutionStatus.RUNNING.value, ExecutionStatus.CANCELLED.value},
    ExecutionStatus.RUNNING.value: {
        ExecutionStatus.COMPLETED.value,
        ExecutionStatus.FAILED.value,
        ExecutionStatus.TIMEOUT.value,
        ExecutionStatus.PAUSED.value,
        ExecutionStatus.CANCELLED.value,
    },
    ExecutionStatus.PAUSED.value: {ExecutionStatus.RUNNING.value, ExecutionStatus.CANCELLED.value},
    ExecutionStatus.COMPLETED.value: {ExecutionStatus.ARCHIVED.value},
    ExecutionStatus.FAILED.value: {ExecutionStatus.ARCHIVED.value},
    ExecutionStatus.TIMEOUT.value: {ExecutionStatus.ARCHIVED.value},
    ExecutionStatus.CANCELLED.value: {ExecutionStatus.ARCHIVED.value},
    ExecutionStatus.ARCHIVED.value: set(),
}


@dataclass
class ExecutionEvent:
    """Represents a state transition event for an execution task.

    Attributes:
        event_id: Unique identifier for the event
        task_id: Associated task identifier
        from_status: Original status value (string)
        to_status: New status value (string)
        timestamp: UTC timestamp when event created
        metadata: Optional metadata for the event
    """

    schema_version: ClassVar[str] = "1.0"

    event_id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = field(default_factory=str)
    from_status: str = field(default_factory=str)
    to_status: str = field(default_factory=str)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


def is_valid_transition(from_status: str, to_status: str) -> bool:
    """Return True if transition from -> to is allowed by the state map."""
    allowed = _ALLOWED_TRANSITIONS.get(from_status)
    if allowed is None:
        return False
    return to_status in allowed


def validate_transition(from_status: str, to_status: str) -> None:
    """Validate transition and raise ValueError if invalid.

    This is a pure, deterministic validation used by ExecutionManager.
    """
    if not is_valid_transition(from_status, to_status):
        raise ValueError(f"Invalid state transition: {from_status} -> {to_status}")
