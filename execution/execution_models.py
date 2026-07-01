"""Execution Foundation - Data Models

This module defines the core data structures for execution management.
It provides immutable policies, mutable execution tasks and results, and 
supporting enums. All dataclasses include schema_version for versioning.

No execution logic, no AI providers, no external dependencies.

[TODO - Phase 6+: Execution engine implementation]
[TODO - Phase 6+: AI provider adapters]
[TODO - Phase 6+: Event streaming]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid4


class ExecutionStatus(Enum):
    """Execution lifecycle status."""

    CREATED = "created"  # Task created, not queued
    QUEUED = "queued"  # Queued for execution
    RUNNING = "running"  # Actively executing
    PAUSED = "paused"  # Execution paused
    COMPLETED = "completed"  # Completed successfully
    FAILED = "failed"  # Failed with error
    TIMEOUT = "timeout"  # Timed out
    CANCELLED = "cancelled"  # User cancelled
    ARCHIVED = "archived"  # Archived after completion


class ResultStatus(Enum):
    """Result outcome status."""

    SUCCESS = "success"  # Execution succeeded
    FAILED = "failed"  # Execution failed
    TIMEOUT = "timeout"  # Execution timed out
    CANCELLED = "cancelled"  # Execution cancelled
    INCONCLUSIVE = "inconclusive"  # No definitive outcome
    PARTIAL = "partial"  # Partial completion


class CancellationReason(Enum):
    """Why execution was cancelled."""

    USER_INITIATED = "user_initiated"
    TIMEOUT = "timeout"
    DEPENDENCY_FAILED = "dependency_failed"
    RESOURCE_LIMIT = "resource_limit"
    ERROR = "error"
    OTHER = "other"


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for retry behavior.

    Immutable policy defining retry rules and constraints.

    Attributes:
        retry_id: Unique identifier for this policy
        max_retries: Maximum number of retry attempts
        initial_delay_ms: Initial delay in milliseconds before first retry
        backoff_multiplier: Exponential backoff factor (1.0 = no backoff)
        max_delay_ms: Maximum delay between retries
        retry_on_status: List of ExecutionStatus values to retry on
        retry_on_error_types: List of error type strings to retry on
        metadata: Custom metadata for retry configuration
        created_at: Timestamp when policy was created
        schema_version: Data model version

    [TODO - Phase 6+: Actual retry execution and backoff calculation]
    """

    schema_version: ClassVar[str] = "1.0"

    retry_id: str = field(default_factory=lambda: str(uuid4()))
    max_retries: int = 3
    initial_delay_ms: int = 1000
    backoff_multiplier: float = 2.0
    max_delay_ms: int = 60000
    retry_on_status: List[str] = field(default_factory=list)
    retry_on_error_types: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class TimeoutPolicy:
    """Configuration for timeout behavior.

    Immutable policy defining timeout rules and constraints.

    Attributes:
        timeout_id: Unique identifier for this policy
        timeout_ms: Timeout in milliseconds
        timeout_action: Action on timeout ('abort', 'retry', 'extend')
        enable_heartbeat: Whether to track heartbeat
        heartbeat_interval_ms: Heartbeat check interval in milliseconds
        metadata: Custom metadata for timeout configuration
        created_at: Timestamp when policy was created
        schema_version: Data model version

    [TODO - Phase 6+: Actual timeout enforcement and heartbeat monitoring]
    """

    schema_version: ClassVar[str] = "1.0"

    timeout_id: str = field(default_factory=lambda: str(uuid4()))
    timeout_ms: int = 300000  # 5 minutes default
    timeout_action: str = "abort"  # abort, retry, extend
    enable_heartbeat: bool = False
    heartbeat_interval_ms: int = 10000
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class CancellationPolicy:
    """Configuration for cancellation behavior.

    Immutable policy defining cancellation rules and constraints.

    Attributes:
        cancellation_id: Unique identifier for this policy
        allow_cancel: Whether cancellation is allowed
        allow_cancel_after_ms: Only allow cancel after delay in milliseconds
        graceful_cancel: Attempt graceful shutdown first
        force_cancel_delay_ms: Delay before force cancellation in milliseconds
        cancel_dependent_tasks: Cancel tasks that depend on this one
        metadata: Custom metadata for cancellation configuration
        created_at: Timestamp when policy was created
        schema_version: Data model version

    [TODO - Phase 6+: Actual cancellation handling and forced termination]
    """

    schema_version: ClassVar[str] = "1.0"

    cancellation_id: str = field(default_factory=lambda: str(uuid4()))
    allow_cancel: bool = True
    allow_cancel_after_ms: int = 1000
    graceful_cancel: bool = True
    force_cancel_delay_ms: int = 5000
    cancel_dependent_tasks: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ExecutionMetadata:
    """Metadata about an execution.

    Immutable metadata providing execution context and grouping.

    Attributes:
        execution_id: Unique identifier for this execution
        chain_id: Parent reasoning chain ID (string reference only)
        session_id: Associated session ID (string reference only)
        executor_name: Name of executor implementation (set by Phase 6+)
        priority: Execution priority from 0-100 (50 = normal)
        execution_group: Optional group ID for batch/swarm execution (Enhancement 3)
        tags: Categorization tags
        custom_metadata: User-provided custom metadata
        created_at: Timestamp when metadata was created
        schema_version: Data model version

    [TODO - Phase 6+: Execution engine lookup and deployment]
    [TODO - Phase 6+: Batch and group coordination]
    [TODO - Phase 6+: Priority-based scheduling]
    """

    schema_version: ClassVar[str] = "1.0"

    execution_id: str = field(default_factory=lambda: str(uuid4()))
    chain_id: str = ""
    session_id: Optional[str] = None
    executor_name: Optional[str] = None
    priority: int = 50  # 0-100
    execution_group: Optional[str] = None  # Enhancement 3: Batch/swarm grouping
    tags: List[str] = field(default_factory=list)
    custom_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionTask:
    """Represents an executable task.

    Mutable task with lifecycle tracking, hierarchy, and DAG support.
    Contains only structural information; actual execution is Phase 6+.

    Attributes:
        task_id: Unique identifier for this task
        chain_id: Reference to reasoning chain (string ID, no ReasoningChain object)
        parent_task_id: Optional ID of parent task for hierarchy
        child_task_ids: List of child task IDs for hierarchy
        dependency_task_ids: List of task IDs this task depends on (Enhancement 1)
        metadata: Execution metadata and context
        retry_policy: Optional retry configuration
        timeout_policy: Optional timeout configuration
        cancellation_policy: Optional cancellation configuration
        status: Current execution status (from ExecutionStatus)
        version: Version number, incremented on structural updates
        created_at: Timestamp when task was created
        started_at: Timestamp when execution started (set by Phase 6+)
        completed_at: Timestamp when execution completed (set by Phase 6+)
        error: Error message if task failed
        schema_version: Data model version

    Design Notes:
    - chain_id is a string reference only (no module import from Phase 4)
    - Dependency management enables DAG scheduling (Enhancement 1)
    - Hierarchy supports tree-based task organization
    - Status transitions validated by ExecutionManager
    - All timestamps use UTC

    [TODO - Phase 6+: Actual execution and status updates]
    [TODO - Phase 6+: DAG scheduling using dependency_task_ids]
    [TODO - Phase 6+: Timeout and retry enforcement]
    """

    schema_version: ClassVar[str] = "1.0"

    task_id: str = field(default_factory=lambda: str(uuid4()))
    chain_id: str = field(default_factory=str)
    parent_task_id: Optional[str] = None
    child_task_ids: List[str] = field(default_factory=list)
    dependency_task_ids: List[str] = field(default_factory=list)  # Enhancement 1
    metadata: ExecutionMetadata = field(default_factory=ExecutionMetadata)
    retry_policy: Optional[RetryPolicy] = None
    timeout_policy: Optional[TimeoutPolicy] = None
    cancellation_policy: Optional[CancellationPolicy] = None
    status: str = ExecutionStatus.CREATED.value
    version: int = 1  # Version tracking for structural updates
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result from executing a task.

    Mutable result containing execution outcome and output.
    Output data structure is determined by Phase 6+ executor.

    Attributes:
        result_id: Unique identifier for this result
        task_id: ID of the task that produced this result
        status: Result status (from ResultStatus enum)
        duration_ms: Execution duration in milliseconds
        output: Execution output from Phase 6+ executor
        error: Error message if execution failed
        error_type: Category of error (e.g., 'timeout', 'permission', etc.)
        retry_count: Number of retries that occurred
        execution_trace: List of trace messages from execution
        metadata: Additional result metadata
        created_at: Timestamp when result was created
        schema_version: Data model version

    Design Notes:
    - Output data structure is executor-specific (Phase 6+)
    - Retry count tracks actual retries that occurred
    - Execution trace provides audit trail
    - All timestamps use UTC

    [TODO - Phase 6+: Population of output data from executor]
    [TODO - Phase 6+: Error type categorization]
    [TODO - Phase 6+: Execution trace generation]
    """

    schema_version: ClassVar[str] = "1.0"

    result_id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = field(default_factory=str)
    status: str = ResultStatus.SUCCESS.value
    duration_ms: Optional[int] = None
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    execution_trace: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
