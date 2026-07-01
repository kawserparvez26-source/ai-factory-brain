"""ExecutionContext: Minimal execution context.

Single responsibility: Provide executor with task and metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Optional
from uuid import uuid4

from execution import ExecutionTask


@dataclass(frozen=True)
class ExecutionContext:
    """Minimal context for task execution.
    
    Contains only information needed by executor to execute task.
    No session state, no event bus, no queue reference.
    
    Attributes:
        context_id: Unique context identifier (for tracing)
        execution_task: The ExecutionTask being executed (read-only)
        executor_id: ID of executor handling this task
        started_at: Timestamp execution started
        schema_version: Data model version
    
    Design:
    - Minimal fields only
    - No Phase 3/4 dependencies
    - Immutable (frozen=True) to prevent accidental mutations
    - Used only during single task execution
    - Discarded after execute_task() returns
    
    Notes:
    - NOT a session (that's Phase 6B)
    - NOT a context for entire chain (that's Phase 6B/6C)
    - NOT meant to persist across task executions
    - Only used within execute_task() call
    """
    
    context_id: str = field(default_factory=lambda: str(uuid4()))
    execution_task: ExecutionTask = field()
    executor_id: str = field()
    started_at: datetime = field(default_factory=datetime.utcnow)
    schema_version: ClassVar[str] = "1.0"
    
    @property
    def task_id(self) -> str:
        """Get task ID from embedded task."""
        return self.execution_task.task_id
    
    @property
    def elapsed_ms(self) -> int:
        """Get elapsed milliseconds since context created.
        
        Returns:
            Milliseconds elapsed
        
        Notes:
        - For monitoring/debugging only
        - Used by Phase 7+ timeout logic
        """
        elapsed = datetime.utcnow() - self.started_at
        return int(elapsed.total_seconds() * 1000)
