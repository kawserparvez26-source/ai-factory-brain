"""ExecutorProtocol: Interface for task execution.

Single responsibility: Define executor interface.
Executors implement this protocol to be registered and used.
"""

from __future__ import annotations

from typing import Any, Dict, List, Protocol, runtime_checkable

from execution import ExecutionTask, ExecutionResult


@runtime_checkable
class ExecutorProtocol(Protocol):
    """Protocol for ExecutionTask executors.
    
    All executors must implement this protocol to be registered
    with ExecutorRegistry and used by RuntimeDispatcher.
    
    Responsibilities:
    - Accept ExecutionTask (from Phase 5)
    - Execute it synchronously
    - Return ExecutionResult (to Phase 5)
    - No side effects beyond task execution
    - No Phase 3/4 dependencies
    
    Design:
    - Task is read-only (no modification)
    - Context is minimal (no session, no events)
    - Result is fully populated (status, output, error, trace)
    - Errors raised as ExecutionError subclasses
    
    [TODO - Phase 7+: AI provider implementations]
    [TODO - Phase 7+: Knowledge/Memory integrations]
    """
    
    def get_executor_id(self) -> str:
        """Get unique executor identifier.
        
        Returns:
            Executor ID (e.g., "openai.gpt4", "query.sql")
            Must be unique within registry
        """
        ...
    
    def get_supported_task_types(self) -> List[str]:
        """Get task types this executor handles.
        
        Task type is determined by ExecutionTask.metadata or
        a custom field in ExecutionTask passed by higher layers.
        
        Returns:
            List of task type identifiers
            (e.g., ["query", "filter"] or ["openai", "gemini"])
        
        Note:
        - Executor defines its own task type classification
        - Registry uses this to route tasks
        - No dependency on Phase 4 StepType enum
        - Executor-specific interpretation
        """
        ...
    
    def execute(self, task: ExecutionTask, context: ExecutionContext) -> ExecutionResult:  # noqa: F821
        """Execute an ExecutionTask synchronously.
        
        Single responsibility: Execute task, return result.
        
        Args:
            task: ExecutionTask from Phase 5 (read-only)
            context: Minimal execution context
        
        Returns:
            ExecutionResult with:
            - result_id: unique result identifier
            - task_id: matching task.task_id
            - status: from ResultStatus enum
            - output: Dict[str, Any] (executor-specific)
            - error: error message if failed
            - execution_trace: list of trace messages
        
        Raises:
            ExecutionError: Base class for all executor errors
            - ExecutorFailedError: Executor logic error
            - InvalidTaskError: Task structure invalid
            - InvalidResultError: Executor produced invalid result
        
        Notes:
        - Must be synchronous (blocking)
        - No async/await, no threading, no multiprocessing
        - No networking, no external API calls
        - No state modifications outside return value
        - Task should not be modified
        - Result should be fully populated
        - Must handle all error cases gracefully
        
        [TODO - Phase 7+: Async wrapper for blocking I/O]
        [TODO - Phase 7+: Timeout enforcement at dispatcher level]
        """
        ...
