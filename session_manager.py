from __future__ import annotations

"""Session management for the Memory Foundation.

Handles session lifecycle, context switching, and session-level metadata.
Provides a context manager for automatic session cleanup and convenient
session-scoped operations.
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, Optional

from .memory_models import SessionMemory, MemoryItem, MemoryType
from .memory_store import MemoryStoreProtocol, InMemoryStore


class SessionManager:
    """Manager for session lifecycle and context switching.

    Provides session creation, retrieval, context management, and cleanup.
    Supports both explicit session management and context manager usage.
    """

    def __init__(self, store: Optional[MemoryStoreProtocol] = None) -> None:
        """Initialize the SessionManager with an optional storage backend.

        Args:
            store: Storage backend implementing MemoryStoreProtocol.
                   If None, uses InMemoryStore (default for development).
        """
        self.store: MemoryStoreProtocol = store or InMemoryStore()
        self._current_session_id: Optional[str] = None
        self._session_stack: list[str] = []

    # Session Lifecycle
    def create_session(self, session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> SessionMemory:
        """Create a new session.

        Args:
            session_id: Optional session identifier. If None, generates a UUID.
            metadata: Optional session-level metadata.

        Returns:
            A new SessionMemory object.
        """
        session = self.store.create_session(session_id or self._generate_session_id())
        if metadata:
            session.metadata.update(metadata)
        return session

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Retrieve a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            SessionMemory if found, otherwise None.
        """
        return self.store.get_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: The session identifier.

        Returns:
            True if deleted, False if not found.
        """
        deleted = self.store.delete_session(session_id)
        if self._current_session_id == session_id:
            self._current_session_id = None
        return deleted

    def list_sessions(self, limit: Optional[int] = None, offset: int = 0) -> list[SessionMemory]:
        """List all sessions.

        Args:
            limit: Maximum sessions to return.
            offset: Number of sessions to skip.

        Returns:
            List of SessionMemory objects.
        """
        return self.store.list_sessions(limit=limit, offset=offset)

    # Session Context Management
    def set_current_session(self, session_id: str) -> bool:
        """Set the current active session.

        Args:
            session_id: The session to activate.

        Returns:
            True if session exists and was set, False otherwise.
        """
        session = self.get_session(session_id)
        if session is not None:
            self._current_session_id = session_id
            return True
        return False

    def get_current_session(self) -> Optional[SessionMemory]:
        """Get the currently active session.

        Returns:
            The active SessionMemory, or None if no session is active.
        """
        if self._current_session_id is None:
            return None
        return self.get_session(self._current_session_id)

    def get_current_session_id(self) -> Optional[str]:
        """Get the ID of the currently active session.

        Returns:
            The session ID, or None if no session is active.
        """
        return self._current_session_id

    def clear_current_session(self) -> None:
        """Clear the currently active session."""
        self._current_session_id = None

    # Session Stack (for nested contexts)
    def push_session(self, session_id: str) -> bool:
        """Push a session onto the stack and make it current.

        Args:
            session_id: The session to push.

        Returns:
            True if session exists and was pushed, False otherwise.
        """
        session = self.get_session(session_id)
        if session is not None:
            if self._current_session_id:
                self._session_stack.append(self._current_session_id)
            self._current_session_id = session_id
            return True
        return False

    def pop_session(self) -> Optional[str]:
        """Pop a session from the stack, restoring the previous session.

        Returns:
            The session ID that was popped, or None if stack is empty.
        """
        if not self._session_stack:
            popped = self._current_session_id
            self._current_session_id = None
            return popped

        popped = self._current_session_id
        self._current_session_id = self._session_stack.pop()
        return popped

    def session_stack_depth(self) -> int:
        """Get the depth of the session stack.

        Returns:
            Number of sessions in the stack (not including current).
        """
        return len(self._session_stack)

    # Context Manager
    @contextmanager
    def session_context(self, session_id: Optional[str] = None) -> Generator[SessionMemory, None, None]:
        """Context manager for session-scoped operations.

        Creates a new session if session_id is None, pushes it onto the stack,
        yields it, then pops it when exiting the context.

        Args:
            session_id: Optional session ID. If None, creates a new session.

        Yields:
            The active SessionMemory within the context.

        Example:
            with session_manager.session_context() as session:
                # session is active here
                pass
            # session is restored to previous after exiting
        """
        if session_id is None:
            session = self.create_session()
            session_id = session.session_id
        else:
            session = self.get_session(session_id)
            if session is None:
                raise ValueError(f"Session {session_id} not found")

        self.push_session(session_id)
        try:
            yield session
        finally:
            self.pop_session()

    # Session Metadata Management
    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> bool:
        """Update session-level metadata.

        Args:
            session_id: The session identifier.
            metadata: Metadata dict to merge into session.metadata.

        Returns:
            True if updated, False if session not found.
        """
        session = self.get_session(session_id)
        if session is not None:
            session.metadata.update(metadata)
            return True
        return False

    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session-level metadata.

        Args:
            session_id: The session identifier.

        Returns:
            The metadata dict, or None if session not found.
        """
        session = self.get_session(session_id)
        return session.metadata if session else None

    # Session Query
    def find_sessions_by_metadata(
        self,
        metadata_filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[SessionMemory]:
        """Find sessions matching metadata criteria.

        Args:
            metadata_filters: Key/value pairs that must match in session.metadata.
            limit: Maximum sessions to return.
            offset: Number of sessions to skip.

        Returns:
            List of matching SessionMemory objects.
        """
        all_sessions = self.list_sessions(limit=None)
        matching = []

        for session in all_sessions:
            match = True
            for key, value in metadata_filters.items():
                if session.metadata.get(key) != value:
                    match = False
                    break
            if match:
                matching.append(session)

        # Apply pagination
        if offset:
            matching = matching[offset:]
        if limit is not None:
            matching = matching[:limit]

        return matching

    def find_sessions_created_after(
        self,
        timestamp: datetime,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> list[SessionMemory]:
        """Find sessions created after a given timestamp.

        Args:
            timestamp: The reference timestamp.
            limit: Maximum sessions to return.
            offset: Number of sessions to skip.

        Returns:
            List of matching SessionMemory objects.
        """
        all_sessions = self.list_sessions(limit=None)
        matching = [s for s in all_sessions if s.created_at >= timestamp]

        # Apply pagination
        if offset:
            matching = matching[offset:]
        if limit is not None:
            matching = matching[:limit]

        return matching

    # Session Statistics
    def session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of session contents and statistics.

        Args:
            session_id: The session identifier.

        Returns:
            A dict with session summary, or None if session not found.
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        stats = session.statistics()
        stats["metadata"] = session.metadata
        return stats

    def all_sessions_summary(self) -> Dict[str, Any]:
        """Get aggregate summary of all sessions.

        Returns:
            A dict with aggregate statistics.
        """
        store_stats = self.store.statistics()
        sessions = self.list_sessions(limit=None)

        return {
            "total_sessions": len(sessions),
            "store_statistics": store_stats,
            "oldest_session": min((s.created_at for s in sessions), default=None),
            "newest_session": max((s.created_at for s in sessions), default=None),
        }

    # Utility
    def _generate_session_id(self) -> str:
        """Generate a unique session ID.

        Returns:
            A new session ID.
        """
        from uuid import uuid4

        return str(uuid4())
