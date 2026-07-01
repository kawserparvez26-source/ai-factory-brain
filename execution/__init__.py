"""Execution Foundation - Phase 5

Pure state management for execution task lifecycle and transitions.
No execution, no AI, no async, no external dependencies.

Public API:
  - ExecutionManager: Task lifecycle orchestration
  - ExecutionStoreProtocol: Storage backend interface
  - ExecutionTask, ExecutionResult: Core data models
  - ExecutionStatus, ResultStatus: Status enums
  - ExecutionEvent: State transition events
  - validate_transition, is_valid_transition: State validation
"""

from .execution_models import (
    ExecutionStatus,
    ResultStatus,
    CancellationReason,
    RetryPolicy,
    TimeoutPolicy,
    CancellationPolicy,
    ExecutionMetadata,
    ExecutionTask,
    ExecutionResult,
)

from .execution_protocol import ExecutionStoreProtocol

from .execution_state import (
    ExecutionEvent,
    is_valid_transition,
    validate_transition,
)

from .execution_manager import ExecutionManager

__all__ = [
    # Data models
    "ExecutionStatus",
    "ResultStatus",
    "CancellationReason",
    "RetryPolicy",
    "TimeoutPolicy",
    "CancellationPolicy",
    "ExecutionMetadata",
    "ExecutionTask",
    "ExecutionResult",
    # Protocols
    "ExecutionStoreProtocol",
    # State machine
    "ExecutionEvent",
    "is_valid_transition",
    "validate_transition",
    # Manager
    "ExecutionManager",
]
