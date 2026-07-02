"""Timeout flow for Phase 6B.

Defines timeout policy structure for task timeouts.
No execution logic, structure only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, Optional


class TimeoutAction(Enum):
    """Actions to take on timeout."""

    FAIL = "fail"
    RETRY = "retry"
    CANCEL = "cancel"


@dataclass(frozen=True)
class TimeoutFlow:
    """Immutable timeout policy structure.

    Represents timeout configuration for tasks.
    No modification after creation.

    Attributes:
        timeout_ms: Timeout duration in milliseconds
        action: Action to take on timeout (FAIL, RETRY, CANCEL)
        warn_at_ms: Warning threshold in milliseconds (optional)
        metadata: Additional context
        schema_version: Data model version

    Notes:
    - Structure only (no timeout enforcement)
    - No business logic
    - Used to configure timeout behavior
    - Actual timeout enforcement at dispatcher level (Phase 7+)
    """

    schema_version: ClassVar[str] = "1.0"

    timeout_ms: int = field()
    action: TimeoutAction = field(default=TimeoutAction.FAIL)
    warn_at_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"TimeoutFlow(timeout_ms={self.timeout_ms}, "
            f"action={self.action.value})"
        )
