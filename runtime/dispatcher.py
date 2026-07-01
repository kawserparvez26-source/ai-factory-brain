"""RuntimeDispatcher: Task execution orchestration.

Single responsibility: Receive task, find executor, call it, return result.
"""

from __future__ import annotations

from typing import List, Optional

from execution import ExecutionTask, ExecutionResult, ResultStatus

from .executor import ExecutorProtocol
from .registry import ExecutorRegistry
from .context import ExecutionContext
from .errors import (
    ExecutionError,
    ExecutorNotFoundError,
    ExecutionFailedError,
    InvalidTaskError,
    InvalidResultError,
)


class RuntimeDispatcher:
    """Orchestrates task execution.
    
    Responsibilities:
    - Validate task structure
    - Find executor in registry
    - Create minimal execution context
    - Call executor.execute()
    - Validate executor result
    - Return ExecutionResult to caller
    - Propagate executor errors
    
    Design:
    - Pure orchestration (no state management)
    - Synchronous only (no async)
    - Minimal context creation
    - Clear error propagation
    - No side effects beyond return value
    - Stateless (can be instantiated once per runtime)
    
    [TODO - Phase 6B: Add event emission]
    [TODO - Phase 7+: Add retry/timeout coordination]
    """
    
    def __init__(self, executor_registry: ExecutorRegistry) -> None:
        """Initialize dispatcher.
        
        Args:
            executor_registry: ExecutorRegistry instance for executor lookup
        
        Notes:
        - Dispatcher is stateless
        - Can be reused across multiple task executions
        - Thread-safe (reads only from registry)
        """
        self.executor_registry = executor_registry
    
    def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute an ExecutionTask synchronously.
        
        Execution phases:
        
        Phase 1: Validation
        - Verify task has task_id
        - Verify task has valid structure
        - Verify executor is available
        
        Phase 2: Preparation
        - Create minimal ExecutionContext
        - Store task_id in context
        - Store executor_id in context
        
        Phase 3: Execution
        - Call executor.execute(task, context)
        - Capture ExecutionResult
        - Capture any ExecutionError
        
        Phase 4: Return
        - Validate result structure
        - Raise error if executor raised error
        - Return ExecutionResult if successful
        
        Args:
            task: ExecutionTask from Phase 5 (read-only)
        
        Returns:
            ExecutionResult with status, output, error
        
        Raises:
            InvalidTaskError: Task validation failed
            ExecutorNotFoundError: No executor registered for task
            ExecutionFailedError: Executor raised ExecutionError
            InvalidResultError: Executor returned invalid result
        
        Notes:
        - This method is synchronous (blocking)
        - Caller is responsible for task persistence
        - Caller is responsible for result persistence
        - No state changes beyond return value
        - Errors raised, not wrapped in result
        
        [TODO - Phase 6B: Call ExecutionManager to update status]
        [TODO - Phase 7+: Enforce timeout via signal/alarm]
        """
        # Phase 1: Validation
        is_valid, errors = self.validate_task(task)
        if not is_valid:
            raise InvalidTaskError(
                f"Task validation failed: {'; '.join(errors)}",
                task_id=task.task_id
            )
        
        # Determine task type
        task_type = self._get_task_type(task)
        if not task_type:
            raise InvalidTaskError(
                "Task type not specified in metadata",
                task_id=task.task_id
            )
        
        # Phase 1.5: Find executor
        executor = self.find_executor(task_type)
        if executor is None:
            raise ExecutorNotFoundError(
                f"No executor registered for task type '{task_type}'",
                task_id=task.task_id
            )
        
        executor_id = self.executor_registry.get_executor_id(task_type)
        
        # Phase 2: Preparation
        context = self._create_context(task, executor_id)
        
        # Phase 3: Execution
        try:
            result = executor.execute(task, context)
        except ExecutionError as e:
            raise ExecutionFailedError(
                f"Executor failed: {e.message}",
                task_id=task.task_id,
                executor_id=executor_id,
                executor_error=e
            )
        except Exception as e:
            raise ExecutionFailedError(
                f"Executor raised unexpected error: {str(e)}",
                task_id=task.task_id,
                executor_id=executor_id,
                executor_error=e
            )
        
        # Phase 4: Validation
        is_valid, errors = self._validate_result(result, task)
        if not is_valid:
            raise InvalidResultError(
                f"Result validation failed: {'; '.join(errors)}",
                task_id=task.task_id
            )
        
        return result
    
    def validate_task(self, task: ExecutionTask) -> tuple[bool, List[str]]:
        """Validate task structure.
        
        Checks:
        - task is not None
        - task.task_id is not empty
        - task has valid Phase 5 structure
        
        Returns:
            (is_valid: bool, errors: List[str])
        
        Notes:
        - Does not validate against Phase 4 (ReasoningChain)
        - Does not validate against Phase 3 (Memory)
        - Pure structural validation
        """
        errors: List[str] = []
        
        if task is None:
            errors.append("Task cannot be None")
            return (False, errors)
        
        if not task.task_id:
            errors.append("Task must have task_id")
        
        if not task.chain_id:
            errors.append("Task must have chain_id")
        
        if not hasattr(task, "status"):
            errors.append("Task must have status attribute")
        
        return (len(errors) == 0, errors)
    
    def find_executor(self, task_type: str) -> Optional[ExecutorProtocol]:
        """Find executor for task type.
        
        Task type determination:
        - Look in task.metadata['executor_type'] if present
        - Otherwise look in task.metadata['task_type'] if present
        - Otherwise raise InvalidTaskError (no task type specified)
        
        Args:
            task_type: Task type to find executor for
        
        Returns:
            ExecutorProtocol instance or None
        
        Notes:
        - Executor determines its own task type routing
        - No dependency on Phase 4 StepType enum
        - Caller provides task type via metadata
        """
        return self.executor_registry.get_executor(task_type)
    
    def _get_task_type(self, task: ExecutionTask) -> Optional[str]:
        """Extract task type from task metadata.
        
        Checks (in order):
        1. task.metadata['executor_type']
        2. task.metadata['task_type']
        3. None
        
        Args:
            task: ExecutionTask
        
        Returns:
            Task type string or None
        """
        if not hasattr(task, "metadata") or task.metadata is None:
            return None
        
        # Check for executor_type first
        executor_type = task.metadata.get("executor_type")
        if executor_type:
            return executor_type
        
        # Fall back to task_type
        return task.metadata.get("task_type")
    
    def _create_context(self, task: ExecutionTask,
                       executor_id: str) -> ExecutionContext:
        """Create minimal execution context.
        
        Args:
            task: ExecutionTask
            executor_id: ExecutorProtocol identifier
        
        Returns:
            ExecutionContext with minimal fields
        
        Notes:
        - Internal method (single underscore prefix)
        - No external dependencies
        - No sessions, no events, no queues
        """
        return ExecutionContext(
            execution_task=task,
            executor_id=executor_id
        )
    
    def _validate_result(self, result: ExecutionResult,
                        task: ExecutionTask) -> tuple[bool, List[str]]:
        """Validate executor result.
        
        Checks:
        - result is not None
        - result.result_id is not empty
        - result.task_id == task.task_id
        - result.status is valid ResultStatus
        
        Returns:
            (is_valid: bool, errors: List[str])
        
        Notes:
        - Does not validate output structure (executor-specific)
        - Pure structural validation
        """
        errors: List[str] = []
        
        if result is None:
            errors.append("Result cannot be None")
            return (False, errors)
        
        if not result.result_id:
            errors.append("Result must have result_id")
        
        if result.task_id != task.task_id:
            errors.append(f"Result task_id '{result.task_id}' does not match task task_id '{task.task_id}'")
        
        # Validate status is a valid ResultStatus value
        valid_statuses = ["success", "failed", "timeout", "cancelled", "inconclusive", "partial"]
        if result.status not in valid_statuses:
            errors.append(f"Result status '{result.status}' is not a valid ResultStatus")
        
        return (len(errors) == 0, errors)
