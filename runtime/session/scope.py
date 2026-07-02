"""Session scope enumeration and management for Phase 6B.

Defines session lifecycle states.
No execution logic, pure state tracking.
"""

from __future__ import annotations

from enum import Enum


class SessionScope(Enum):
    """Lifecycle state of a runtime session.

    Tracks whether a session is active, paused, or closed.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ScopeManager:
    """Manages session scope transitions.

    Tracks and validates session state changes.
    No complex logic, pure state machine.

    Design:
    - Simple state transitions
    - No async or concurrent operations
    - No business logic
    """

    def __init__(self, initial_scope: SessionScope = SessionScope.ACTIVE) -> None:
        """Initialize scope manager.

        Args:
            initial_scope: Starting scope (default ACTIVE)
        """
        self._scope = initial_scope

    @property
    def scope(self) -> SessionScope:
        """Get current scope.

        Returns:
            Current SessionScope
        """
        return self._scope

    def is_active(self) -> bool:
        """Check if scope is ACTIVE.

        Returns:
            True if scope is ACTIVE
        """
        return self._scope == SessionScope.ACTIVE

    def is_paused(self) -> bool:
        """Check if scope is PAUSED.

        Returns:
            True if scope is PAUSED
        """
        return self._scope == SessionScope.PAUSED

    def is_closed(self) -> bool:
        """Check if scope is CLOSED.

        Returns:
            True if scope is CLOSED
        """
        return self._scope == SessionScope.CLOSED

    def transition(self, new_scope: SessionScope) -> bool:
        """Attempt transition to new scope.

        Args:
            new_scope: Target SessionScope

        Returns:
            True if transition allowed, False otherwise

        Notes:
        - ACTIVE can transition to PAUSED or CLOSED
        - PAUSED can transition to ACTIVE or CLOSED
        - CLOSED is terminal (cannot transition out)
        """
        # Terminal state
        if self._scope == SessionScope.CLOSED:
            return False

        # Valid transitions
        if self._scope == SessionScope.ACTIVE:
            if new_scope in (SessionScope.PAUSED, SessionScope.CLOSED):
                self._scope = new_scope
                return True
        elif self._scope == SessionScope.PAUSED:
            if new_scope in (SessionScope.ACTIVE, SessionScope.CLOSED):
                self._scope = new_scope
                return True

        return False

    def pause(self) -> bool:
        """Transition to PAUSED state.

        Returns:
            True if paused, False if not allowed
        """
        if self._scope == SessionScope.ACTIVE:
            self._scope = SessionScope.PAUSED
            return True
        return False

    def resume(self) -> bool:
        """Transition to ACTIVE state from PAUSED.

        Returns:
            True if resumed, False if not allowed
        """
        if self._scope == SessionScope.PAUSED:
            self._scope = SessionScope.ACTIVE
            return True
        return False

    def close(self) -> bool:
        """Transition to CLOSED state.

        Returns:
            True if closed, False if already closed
        """
        if self._scope != SessionScope.CLOSED:
            self._scope = SessionScope.CLOSED
            return True
        return False
