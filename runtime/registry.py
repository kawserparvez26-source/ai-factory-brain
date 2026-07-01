"""ExecutorRegistry: Executor discovery and lookup.

Single responsibility: Map task types to executor instances.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .executor import ExecutorProtocol


@dataclass
class ExecutorRegistration:
    """Metadata for a registered executor.
    
    Attributes:
        executor_id: Unique identifier
        name: Human-readable name
        version: Executor version
        task_types: Set of supported task types
        executor: ExecutorProtocol instance
        registered_at: Timestamp when registered
    """
    
    executor_id: str
    name: str
    version: str
    task_types: List[str]
    executor: ExecutorProtocol
    registered_at: datetime


class ExecutorRegistry:
    """Registry for executor discovery and routing.
    
    Responsibilities:
    - Store executor registrations
    - Look up executor by task type
    - Provide registration/unregistration
    - No persistence, all in-memory
    - Single instance per runtime
    
    Design:
    - Simple dict-based storage
    - Thread-safe via GIL (no explicit locking, Phase 6A is sync)
    - No complex querying, only by task type
    - One executor per task type (first-come-first-served)
    """
    
    def __init__(self) -> None:
        """Initialize empty registry.
        
        Registry starts empty. Executors registered via register().
        """
        self._executors: Dict[str, ExecutorProtocol] = {}
        self._registrations: Dict[str, ExecutorRegistration] = {}
        self._task_type_index: Dict[str, str] = {}  # task_type → executor_id
    
    def register(self, executor_id: str, executor: ExecutorProtocol,
                 task_types: List[str], name: str = "",
                 version: str = "1.0") -> None:
        """Register an executor for task types.
        
        Args:
            executor_id: Unique executor identifier
            executor: ExecutorProtocol implementation
            task_types: List of supported task types
            name: Human-readable name (optional)
            version: Executor version (optional, default "1.0")
        
        Raises:
            ValueError: If executor_id already registered
            ValueError: If executor_id empty or task_types empty
        
        Notes:
        - If task type already registered, replaces previous executor
        - executor must implement ExecutorProtocol
        - executor_id must be unique globally
        - task_types determines routing in get_executor()
        """
        if not executor_id:
            raise ValueError("executor_id cannot be empty")
        if not task_types:
            raise ValueError("task_types cannot be empty")
        if executor_id in self._executors:
            raise ValueError(f"Executor '{executor_id}' already registered")
        
        # Store executor
        self._executors[executor_id] = executor
        
        # Create registration
        registration = ExecutorRegistration(
            executor_id=executor_id,
            name=name or executor_id,
            version=version,
            task_types=task_types,
            executor=executor,
            registered_at=datetime.utcnow()
        )
        self._registrations[executor_id] = registration
        
        # Index by task types
        for task_type in task_types:
            self._task_type_index[task_type] = executor_id
    
    def get_executor(self, task_type: str) -> Optional[ExecutorProtocol]:
        """Get executor for task type.
        
        Args:
            task_type: Task type identifier
        
        Returns:
            ExecutorProtocol instance or None if not found
        
        Notes:
        - Returns first registered executor for task_type
        - Returns None if task_type not registered
        - No error raised (caller checks for None)
        """
        executor_id = self._task_type_index.get(task_type)
        if executor_id is None:
            return None
        return self._executors.get(executor_id)
    
    def get_executor_id(self, task_type: str) -> Optional[str]:
        """Get executor ID for task type.
        
        Args:
            task_type: Task type identifier
        
        Returns:
            executor_id or None if not found
        """
        return self._task_type_index.get(task_type)
    
    def has_executor(self, task_type: str) -> bool:
        """Check if executor registered for task type.
        
        Args:
            task_type: Task type identifier
        
        Returns:
            True if registered, False otherwise
        """
        return task_type in self._task_type_index
    
    def unregister(self, executor_id: str) -> bool:
        """Unregister an executor by ID.
        
        Args:
            executor_id: Executor to remove
        
        Returns:
            True if removed, False if not found
        """
        if executor_id not in self._executors:
            return False
        
        # Remove executor
        del self._executors[executor_id]
        
        # Get task types before removing registration
        if executor_id in self._registrations:
            registration = self._registrations[executor_id]
            del self._registrations[executor_id]
            
            # Remove from task type index
            for task_type in registration.task_types:
                if self._task_type_index.get(task_type) == executor_id:
                    del self._task_type_index[task_type]
        
        return True
    
    def get_registration(self, executor_id: str) -> Optional[ExecutorRegistration]:
        """Get registration metadata.
        
        Args:
            executor_id: Executor identifier
        
        Returns:
            ExecutorRegistration or None
        """
        return self._registrations.get(executor_id)
    
    def get_all_executors(self) -> Dict[str, ExecutorProtocol]:
        """Get all registered executors.
        
        Returns:
            Dict mapping executor_id to ExecutorProtocol
        """
        return dict(self._executors)
    
    def list_registered_task_types(self) -> List[str]:
        """List all registered task types.
        
        Returns:
            List of task type identifiers
        """
        return list(self._task_type_index.keys())
    
    def statistics(self) -> Dict[str, Any]:
        """Get registry statistics.
        
        Returns:
            Dict with:
            - executor_count: number of registered executors
            - task_type_count: number of supported task types
            - executors: dict of registration metadata
        """
        return {
            "executor_count": len(self._executors),
            "task_type_count": len(self._task_type_index),
            "executors": {
                executor_id: {
                    "name": reg.name,
                    "version": reg.version,
                    "task_types": reg.task_types,
                    "registered_at": reg.registered_at.isoformat(),
                }
                for executor_id, reg in self._registrations.items()
            },
        }
