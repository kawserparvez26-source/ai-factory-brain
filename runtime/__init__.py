"""Phase 6A: Minimal Execution Runtime.

Core execution layer for AI Factory Brain.

Responsibilities:
- Execute ExecutionTask objects using registered executors
- Manage executor registry and discovery
- Minimal state management (registry only)
- Pure execution orchestration (no infrastructure)

Design:
- Depends only on Phase 5 (execution module)
- No Phase 3/4 dependencies
- Synchronous execution only
- Protocol-based executor extensibility

Public API:
- ExecutionRuntime: Main entry point
- ExecutorProtocol: Executor interface
- ExecutionError: Base error class
- InvalidTaskError: Task validation error
- ExecutorNotFoundError: Executor not found
- ExecutionFailedError: Executor execution error
- InvalidResultError: Result validation error

Usage Example:
    from runtime import ExecutionRuntime, ExecutorProtocol, ExecutionError
    from execution import ExecutionTask, ExecutionResult, ResultStatus
    
    # Create runtime
    runtime = ExecutionRuntime()
    
    # Register executor
    class MyExecutor:
        def get_executor_id(self) -> str:
            return "my.executor"
        
        def get_supported_task_types(self) -> List[str]:
            return ["my_task"]
        
        def execute(self, task, context):
            return ExecutionResult(
                result_id=str(uuid4()),
                task_id=task.task_id,
                status=ResultStatus.SUCCESS.value,
                output={}
            )
    
    runtime.register_executor(
        "my.executor",
        MyExecutor(),
        ["my_task"]
    )
    
    # Execute task
    task = ExecutionTask(
        task_id="task_1",
        chain_id="chain_1",
        metadata={"executor_type": "my_task"}
    )
    
    try:
        result = runtime.execute_task(task)
        print(f"Success: {result.status}")
    except ExecutionError as e:
        print(f"Error: {e.message}")

[TODO - Phase 6B: Add event bus, sessions, lifecycle]
[TODO - Phase 6C: Add plugins, dependency resolution]
[TODO - Phase 7+: Add AI adapters]
"""

from .executor import ExecutorProtocol
from .registry import ExecutorRegistry
from .dispatcher import RuntimeDispatcher
from .context import ExecutionContext
from .runtime import ExecutionRuntime
from .errors import (
    ExecutionError,
    InvalidTaskError,
    ExecutorNotFoundError,
    ExecutionFailedError,
    InvalidResultError,
)

__all__ = [
    # Main API
    "ExecutionRuntime",
    
    # Protocols
    "ExecutorProtocol",
    
    # Errors
    "ExecutionError",
    "InvalidTaskError",
    "ExecutorNotFoundError",
    "ExecutionFailedError",
    "InvalidResultError",
]

__version__ = "1.0.0"
__schema_version__ = "1.0"
