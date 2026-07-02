"""Phase 6B: Runtime Lifecycle Management.

Lifecycle states and transitions for execution runtime.
Structure/interface only.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class RuntimeState(Enum):
    """Lifecycle states of the execution runtime."""

    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class LifecycleManager:
    """Manages runtime lifecycle state transitions.

    Tracks and validates runtime state changes.
    No complex logic, pure state machine.

    Design:
    - Simple state transitions
    - No async or concurrent operations
    - No business logic
    - Thread-safe via state tracking
    """

    def __init__(self, initial_state: RuntimeState = RuntimeState.CREATED) -> None:
        """Initialize lifecycle manager.

        Args:
            initial_state: Starting state (default CREATED)
        """
        self._state = initial_state

    @property
    def state(self) -> RuntimeState:
        """Get current runtime state.

        Returns:
            Current RuntimeState
        """
        return self._state

    def is_created(self) -> bool:
        """Check if state is CREATED.

        Returns:
            True if state is CREATED
        """
        return self._state == RuntimeState.CREATED

    def is_initialized(self) -> bool:
        """Check if state is INITIALIZED.

        Returns:
            True if state is INITIALIZED
        """
        return self._state == RuntimeState.INITIALIZED

    def is_running(self) -> bool:
        """Check if state is RUNNING.

        Returns:
            True if state is RUNNING
        """
        return self._state == RuntimeState.RUNNING

    def is_paused(self) -> bool:
        """Check if state is PAUSED.

        Returns:
            True if state is PAUSED
        """
        return self._state == RuntimeState.PAUSED

    def is_shutdown(self) -> bool:
        """Check if state is SHUTDOWN.

        Returns:
            True if state is SHUTDOWN
        """
        return self._state == RuntimeState.SHUTDOWN

    def is_error(self) -> bool:
        """Check if state is ERROR.

        Returns:
            True if state is ERROR
        """
        return self._state == RuntimeState.ERROR

    def transition(self, new_state: RuntimeState) -> bool:
        """Attempt transition to new state.

        Args:
            new_state: Target RuntimeState

        Returns:
            True if transition allowed, False otherwise

        Notes:
        - CREATED -> INITIALIZED or ERROR
        - INITIALIZED -> RUNNING or SHUTDOWN or ERROR
        - RUNNING -> PAUSED, SHUTDOWN, or ERROR
        - PAUSED -> RUNNING, SHUTDOWN, or ERROR
        - SHUTDOWN is terminal (cannot transition out)
        - ERROR can transition to SHUTDOWN
        """
        # Terminal states
        if self._state == RuntimeState.SHUTDOWN:
            return False

        # CREATED transitions
        if self._state == RuntimeState.CREATED:
            if new_state in (RuntimeState.INITIALIZED, RuntimeState.ERROR):
                self._state = new_state
                return True

        # INITIALIZED transitions
        elif self._state == RuntimeState.INITIALIZED:
            if new_state in (RuntimeState.RUNNING, RuntimeState.SHUTDOWN, RuntimeState.ERROR):
                self._state = new_state
                return True

        # RUNNING transitions
        elif self._state == RuntimeState.RUNNING:
            if new_state in (RuntimeState.PAUSED, RuntimeState.SHUTDOWN, RuntimeState.ERROR):
                self._state = new_state
                return True

        # PAUSED transitions
        elif self._state == RuntimeState.PAUSED:
            if new_state in (RuntimeState.RUNNING, RuntimeState.SHUTDOWN, RuntimeState.ERROR):
                self._state = new_state
                return True

        # ERROR transitions
        elif self._state == RuntimeState.ERROR:
            if new_state == RuntimeState.SHUTDOWN:
                self._state = new_state
                return True

        return False

    def initialize(self) -> bool:
        """Transition to INITIALIZED state.

        Returns:
            True if initialized, False if not allowed
        """
        if self._state == RuntimeState.CREATED:
            self._state = RuntimeState.INITIALIZED
            return True
        return False

    def start(self) -> bool:
        """Transition to RUNNING state.

        Returns:
            True if started, False if not allowed
        """
        if self._state == RuntimeState.INITIALIZED:
            self._state = RuntimeState.RUNNING
            return True
        return False

    def pause(self) -> bool:
        """Transition to PAUSED state.

        Returns:
            True if paused, False if not allowed
        """
        if self._state == RuntimeState.RUNNING:
            self._state = RuntimeState.PAUSED
            return True
        return False

    def resume(self) -> bool:
        """Transition to RUNNING state from PAUSED.

        Returns:
            True if resumed, False if not allowed
        """
        if self._state == RuntimeState.PAUSED:
            self._state = RuntimeState.RUNNING
            return True
        return False

    def shutdown(self) -> bool:
        """Transition to SHUTDOWN state.

        Returns:
            True if shutdown, False if already shutdown
        """
        if self._state != RuntimeState.SHUTDOWN:
            self._state = RuntimeState.SHUTDOWN
            return True
        return False

    def mark_error(self) -> bool:
        """Transition to ERROR state.

        Returns:
            True if marked as error, False if already shutdown
        """
        if self._state != RuntimeState.SHUTDOWN:
            self._state = RuntimeState.ERROR
            return True
        return False
