"""Execution Protocols for Execution Foundation (Phase 5)

Contains only Protocol definitions describing storage backends used by
ExecutionManager. No implementations, no logic, standard-library only.
"""

from __future__ import annotations

from typing import Optional, List, Protocol

from .execution_models import ExecutionTask, ExecutionResult


class ExecutionStoreProtocol(Protocol):
    """Protocol for execution storage backends.

    Implementations must be simple structural stores; the protocol defines
    the methods ExecutionManager expects. No behavior is specified here.
    """

    def create_task(self, task: ExecutionTask) -> ExecutionTask: ...

    def update_task(self, task: ExecutionTask) -> ExecutionTask: ...

    def get_task(self, task_id: str) -> Optional[ExecutionTask]: ...

    def list_tasks(self, limit: Optional[int] = None, offset: int = 0) -> List[ExecutionTask]: ...

    def delete_task(self, task_id: str) -> bool: ...

    def create_result(self, result: ExecutionResult) -> ExecutionResult: ...

    def get_result(self, result_id: str) -> Optional[ExecutionResult]: ...

    def list_results_for_task(self, task_id: str) -> List[ExecutionResult]: ...

    def delete_result(self, result_id: str) -> bool: ...
