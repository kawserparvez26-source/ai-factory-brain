"""Execution Manager for Phase 5 - Execution Foundation

Orchestrates execution task lifecycle and state transitions.
Uses pluggable storage backends via ExecutionStoreProtocol.
Pure state management; no execution, no AI, no async, no external deps.

[TODO - Phase 6+: Actual execution dispatch to executors]
[TODO - Phase 6+: Policy enforcement (retry, timeout, cancellation)]
[TODO - Phase 6+: DAG-based dependency scheduling]
"""

from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from .execution_models import ExecutionTask, ExecutionResult, ExecutionStatus
from .execution_protocol import ExecutionStoreProtocol
from .execution_state import (
    ExecutionEvent,
    validate_transition,
    is_valid_transition,
)


class ExecutionManager:
    """Manages execution task lifecycle and state transitions.

    Provides a clean interface for creating, updating, and querying tasks
    via a pluggable storage backend. Enforces state transition rules from
    the state machine. No execution logic; that's Phase 6+.

    Attributes:
        store: Backend storage implementation (ExecutionStoreProtocol)
    """

    def __init__(self, store: ExecutionStoreProtocol) -> None:
        """Initialize ExecutionManager with a storage backend.

        Args:
            store: An object implementing ExecutionStoreProtocol.
                   The manager will use it to persist and retrieve tasks.
        """
        self.store = store

    def create_task(self, task: ExecutionTask) -> ExecutionTask:
        """Create a new execution task.

        Args:
            task: The ExecutionTask to create.

        Returns:
            The created task (from store).

        Raises:
            ValueError: If the task is invalid.
        """
        # Phase 5: Structural validation only
        if not task.task_id:
            raise ValueError("Task must have a task_id")
        if not task.chain_id:
            raise ValueError("Task must have a chain_id")

        # Status must start as CREATED
        if task.status != ExecutionStatus.CREATED.value:
            raise ValueError(f"New task status must be {ExecutionStatus.CREATED.value}")

        return self.store.create_task(task)

    def update_task(self, task: ExecutionTask) -> ExecutionTask:
        """Update an existing task.

        Args:
            task: The ExecutionTask with updated values.

        Returns:
            The updated task (from store).

        Raises:
            ValueError: If the task doesn't exist or update is invalid.
        """
        if not task.task_id:
            raise ValueError("Task must have a task_id")

        # Get current task to validate transition
        current = self.store.get_task(task.task_id)
        if current is None:
            raise ValueError(f"Task {task.task_id} not found")

        # Validate status transition if status changed
        if task.status != current.status:
            validate_transition(current.status, task.status)

        # Increment version on update
        task.version += 1

        return self.store.update_task(task)

    def get_task(self, task_id: str) -> Optional[ExecutionTask]:
        """Retrieve a task by ID.

        Args:
            task_id: The task ID.

        Returns:
            The ExecutionTask, or None if not found.
        """
        return self.store.get_task(task_id)

    def list_tasks(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ExecutionTask]:
        """List tasks with pagination.

        Args:
            limit: Maximum number of tasks to return.
            offset: Number of tasks to skip.

        Returns:
            List of ExecutionTask objects.
        """
        return self.store.list_tasks(limit=limit, offset=offset)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID.

        Returns:
            True if deleted, False if not found.
        """
        return self.store.delete_task(task_id)

    def transition_task(self, task_id: str, to_status: str) -> ExecutionEvent:
        """Transition a task to a new status.

        Validates the state transition, updates the task, and returns an
        ExecutionEvent for audit/event tracking.

        Args:
            task_id: The task to transition.
            to_status: The target status (string value).

        Returns:
            An ExecutionEvent describing the transition.

        Raises:
            ValueError: If the transition is invalid or task not found.
        """
        task = self.store.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        from_status = task.status

        # Validate transition
        validate_transition(from_status, to_status)

        # Update task status and timestamps
        task.status = to_status

        if to_status == ExecutionStatus.RUNNING.value and task.started_at is None:
            task.started_at = datetime.utcnow()

        if to_status in (
            ExecutionStatus.COMPLETED.value,
            ExecutionStatus.FAILED.value,
            ExecutionStatus.TIMEOUT.value,
            ExecutionStatus.CANCELLED.value,
        ):
            task.completed_at = datetime.utcnow()

        # Persist the updated task
        self.store.update_task(task)

        # Create and return event
        event = ExecutionEvent(
            task_id=task_id,
            from_status=from_status,
            to_status=to_status,
            timestamp=datetime.utcnow(),
        )

        return event

    def create_result(self, result: ExecutionResult) -> ExecutionResult:
        """Create an execution result.

        Args:
            result: The ExecutionResult to create.

        Returns:
            The created result (from store).

        Raises:
            ValueError: If the result is invalid.
        """
        if not result.result_id:
            raise ValueError("Result must have a result_id")
        if not result.task_id:
            raise ValueError("Result must have a task_id")

        # Verify task exists
        task = self.store.get_task(result.task_id)
        if task is None:
            raise ValueError(f"Task {result.task_id} not found")

        return self.store.create_result(result)

    def get_result(self, result_id: str) -> Optional[ExecutionResult]:
        """Retrieve a result by ID.

        Args:
            result_id: The result ID.

        Returns:
            The ExecutionResult, or None if not found.
        """
        return self.store.get_result(result_id)

    def list_results_for_task(self, task_id: str) -> List[ExecutionResult]:
        """List all results for a given task.

        Args:
            task_id: The task ID.

        Returns:
            List of ExecutionResult objects.
        """
        return self.store.list_results_for_task(task_id)

    def delete_result(self, result_id: str) -> bool:
        """Delete a result by ID.

        Args:
            result_id: The result ID.

        Returns:
            True if deleted, False if not found.
        """
        return self.store.delete_result(result_id)

    def is_task_complete(self, task_id: str) -> bool:
        """Check if a task is in a terminal state.

        Args:
            task_id: The task ID.

        Returns:
            True if task is COMPLETED, FAILED, TIMEOUT, CANCELLED, or ARCHIVED.

        Raises:
            ValueError: If task not found.
        """
        task = self.store.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        terminal_states = {
            ExecutionStatus.COMPLETED.value,
            ExecutionStatus.FAILED.value,
            ExecutionStatus.TIMEOUT.value,
            ExecutionStatus.CANCELLED.value,
            ExecutionStatus.ARCHIVED.value,
        }
        return task.status in terminal_states

    def can_transition(self, task_id: str, to_status: str) -> bool:
        """Check if a task can transition to a status without raising.

        Args:
            task_id: The task ID.
            to_status: The target status.

        Returns:
            True if transition is valid, False otherwise.
        """
        task = self.store.get_task(task_id)
        if task is None:
            return False

        return is_valid_transition(task.status, to_status)
