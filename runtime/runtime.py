"""ExecutionRuntime: Thin facade for Phase 6A.

Single responsibility: Provide high-level execution API.
"""

from __future__ import annotations

from typing import List, Optional

from execution import ExecutionTask, ExecutionResult

from .executor import ExecutorProtocol
from .registry import ExecutorRegistry
from .dispatcher import RuntimeDispatcher
from .errors import ExecutionError


class ExecutionRuntime:
    """Minimal execution runtime.
    
    Thin facade over ExecutorRegistry and RuntimeDispatcher.
    Provides high-level execution API.
    
    Responsibilities:
    - Accept executor registrations
    - Execute tasks via dispatcher
    - No lifecycle management in Phase 6A
    - No state beyond registry
    
    Design:
    - Facade pattern (delegates to dispatcher and registry)
    - Stateless (all state in registry)
    - Single instance per application
    - Can be initialized without parameters
    
    [TODO - Phase 6B: Add lifecycle management]
    [TODO - Phase 6B: Add event bus integration]
    """
    
    def __init__(self) -> None:
        """Initialize runtime.
        
        Creates empty ExecutorRegistry and RuntimeDispatcher.
        No additional initialization in Phase 6A.
        """
        self.executor_registry = ExecutorRegistry()
        self.dispatcher = RuntimeDispatcher(self.executor_registry)
    
    def register_executor(self, executor_id: str,
                         executor: ExecutorProtocol,
                         task_types: List[str],
                         name: str = "",
                         version: str = "1.0") -> None:
        """Register custom executor.
        
        Args:
            executor_id: Unique executor ID
            executor: ExecutorProtocol implementation
            task_types: Supported task types
            name: Human-readable name (optional)
            version: Executor version (optional)
        
        Raises:
            ValueError: If executor_id already registered
        
        Notes:
        - Called before any task execution
        - Example:
            runtime.register_executor(
                "my.executor",
                MyExecutor(),
                ["my_task_type"],
                name="My Custom Executor",
                version="1.0"
            )
        """
        self.executor_registry.register(
            executor_id, executor, task_types, name, version
        )
    
    def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute a task synchronously.
        
        Args:
            task: ExecutionTask from Phase 5
        
        Returns:
            ExecutionResult from Phase 5
        
        Raises:
            InvalidTaskError: Task validation failed
            ExecutorNotFoundError: No executor for task
            ExecutionFailedError: Executor error
            InvalidResultError: Result validation failed
        
        Notes:
        - Synchronous (blocking) execution
        - Caller is responsible for task/result persistence
        - Example:
            try:
                result = runtime.execute_task(task)
                execution_manager.create_result(result)
            except ExecutionError as e:
                # Handle error
        
        [TODO - Phase 6B: Auto-persist via ExecutionManager]
        """
        return self.dispatcher.execute_task(task)
    
    def get_executor_registry(self) -> ExecutorRegistry:
        """Get executor registry for direct access.
        
        Returns:
            ExecutorRegistry instance
        
        Notes:
        - Use for introspection/monitoring only
        - Don't modify directly (use register_executor)
        """
        return self.executor_registry
