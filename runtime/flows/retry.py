"""Retry flow for Phase 6B.

Defines retry policy structure for task retries.
No execution logic, structure only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, Optional


class RetryStrategy(Enum):
    """Retry strategies."""

    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_WITH_JITTER = "exponential_with_jitter"


class BackoffStrategy(Enum):
    """Backoff calculation strategies."""

    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass(frozen=True)
class RetryFlow:
    """Immutable retry policy structure.

    Represents retry configuration for tasks.
    No modification after creation.

    Attributes:
        max_attempts: Maximum number of retry attempts
        initial_delay_ms: Initial delay in milliseconds
        max_delay_ms: Maximum delay in milliseconds
        strategy: Retry strategy (IMMEDIATE, LINEAR, EXPONENTIAL, etc.)
        backoff_strategy: Backoff calculation (FIXED, LINEAR, EXPONENTIAL)
        retry_on: Exception types to retry on (optional)
        metadata: Additional context
        schema_version: Data model version

    Notes:
    - Structure only (no retry execution)
    - No business logic
    - Used to configure retry behavior
    """

    schema_version: ClassVar[str] = "1.0"

    max_attempts: int = field(default=3)
    initial_delay_ms: int = field(default=1000)
    max_delay_ms: int = field(default=60000)
    strategy: RetryStrategy = field(default=RetryStrategy.EXPONENTIAL)
    backoff_strategy: BackoffStrategy = field(default=BackoffStrategy.EXPONENTIAL)
    retry_on: tuple = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return (
            f"RetryFlow(max_attempts={self.max_attempts}, "
            f"strategy={self.strategy.value}, "
            f"initial_delay_ms={self.initial_delay_ms})"
        )
