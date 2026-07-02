"""Queue protocol for Phase 6B.

Defines queue interface for task queuing.
No execution logic, structure only.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Protocol

from execution import ExecutionTask, ExecutionResult


class QueueType(Enum):
    """Categories of task queues."""

    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"


class QueueStatus(Enum):
    """Status of a queue."""

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class TaskQueue(Protocol):
    """Protocol for task queue implementations.

    All queues must implement this protocol to be registered
    and used by the runtime.

    Responsibilities:
    - Accept ExecutionTask instances
    - Store tasks in queue
    - Retrieve tasks in queue order
    - Track queue status
    - No persistence or complex ordering

    Design:
    - Synchronous only (no async)
    - In-memory (no persistence)
    - Simple FIFO/LIFO/priority ordering
    - Protocol-based extensibility

    Notes:
    - This is NOT a message queue (no persistence)
    - This is NOT async (no coroutines)
    - This is NOT persistent (in-memory only)
    """

    def enqueue(self, task: ExecutionTask) -> str:
        """Enqueue a task.

        Args:
            task: ExecutionTask to queue

        Returns:
            Queue entry ID (for tracking)

        Notes:
        - Task is read-only (not modified)
        - Entry ID is unique per queue
        """
        ...

    def dequeue(self) -> Optional[ExecutionTask]:
        """Dequeue next task.

        Returns:
            ExecutionTask or None if queue empty

        Notes:
        - Order determined by queue type (FIFO/LIFO/priority)
        - Removes task from queue
        """
        ...

    def peek(self) -> Optional[ExecutionTask]:
        """Peek at next task without dequeueing.

        Returns:
            ExecutionTask or None if queue empty

        Notes:
        - Does not remove task
        - Useful for monitoring/debugging
        """
        ...

    def size(self) -> int:
        """Get current queue size.

        Returns:
            Number of tasks in queue
        """
        ...

    def is_empty(self) -> bool:
        """Check if queue is empty.

        Returns:
            True if queue empty
        """
        ...

    def clear(self) -> None:
        """Clear all tasks from queue.

        Notes:
        - Used for testing and cleanup
        """
        ...
