"""ExecutionError: Exception hierarchy for Phase 6A.

Single responsibility: Define error types.

All Phase 6A errors inherit from ExecutionError.
Used for error propagation from dispatcher to caller.
"""

from __future__ import annotations

from typing import Optional


class ExecutionError(Exception):
    """Base execution error.
    
    All Phase 6A errors inherit from this.
    
    Attributes:
        message: Error message
        task_id: Associated task ID (optional)
        cause: Root cause exception (optional)
    """
    
    def __init__(self, message: str, task_id: Optional[str] = None,
                 cause: Optional[Exception] = None) -> None:
        """Initialize error.
        
        Args:
            message: Error description
            task_id: Task that caused error (optional)
            cause: Root cause exception (optional)
        """
        super().__init__(message)
        self.message = message
        self.task_id = task_id
        self.cause = cause
    
    def __str__(self) -> str:
        """String representation."""
        if self.task_id:
            return f"{self.__class__.__name__}: {self.message} (task_id: {self.task_id})"
        return f"{self.__class__.__name__}: {self.message}"


class InvalidTaskError(ExecutionError):
    """Task validation failed.
    
    Raised when:
    - task_id is empty
    - task structure is invalid
    - task type not specified
    """


class ExecutorNotFoundError(ExecutionError):
    """No executor registered for task type.
    
    Raised when:
    - task_type not in registry
    - executor unregistered before execution
    """


class ExecutionFailedError(ExecutionError):
    """Executor raised ExecutionError.
    
    Wraps executor's error for caller.
    
    Attributes:
        executor_id: ID of executor that failed
        executor_error: Original error from executor
    """
    
    def __init__(self, message: str, task_id: Optional[str] = None,
                 executor_id: Optional[str] = None,
                 executor_error: Optional[Exception] = None) -> None:
        """Initialize error.
        
        Args:
            message: Error message
            task_id: Associated task ID
            executor_id: ID of executor that failed
            executor_error: Original error from executor
        """
        super().__init__(message, task_id, executor_error)
        self.executor_id = executor_id
        self.executor_error = executor_error
    
    def __str__(self) -> str:
        """String representation."""
        if self.executor_id:
            return f"{self.__class__.__name__}: {self.message} (executor: {self.executor_id}, task_id: {self.task_id})"
        return super().__str__()


class InvalidResultError(ExecutionError):
    """Executor returned invalid result.
    
    Raised when:
    - result is None
    - result_id is empty
    - result.task_id != task.task_id
    - result.status is invalid
    """
