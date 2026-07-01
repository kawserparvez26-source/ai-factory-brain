from __future__ import annotations

"""High-level memory manager for the Memory Foundation.

Provides a unified interface for managing memory across sessions, projects, and
brain-scoped contexts. Handles memory lifecycle, query execution, and integration
with the storage backend.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .memory_models import (
    MemoryItem,
    MemoryType,
    SessionMemory,
    ConversationTurn,
    DecisionRecord,
    ProjectMemory,
    BrainMemory,
)
from .memory_store import MemoryStoreProtocol, InMemoryStore


class MemoryManager:
    """High-level memory manager for the Memory Foundation.

    Provides unified operations for creating, querying, and managing memories
    across sessions, projects, and brain scopes. Uses a pluggable storage backend.
    """

    def __init__(self, store: Optional[MemoryStoreProtocol] = None) -> None:
        """Initialize the MemoryManager with an optional storage backend.

        Args:
            store: Storage backend implementing MemoryStoreProtocol.
                   If None, uses InMemoryStore (default for development).
        """
        self.store: MemoryStoreProtocol = store or InMemoryStore()
        self._active_session_id: Optional[str] = None

    # Session Management
    def create_session(self, session_id: Optional[str] = None) -> SessionMemory:
        """Create a new session or retrieve existing one.

        Args:
            session_id: Optional session identifier. If None, generates a UUID.

        Returns:
            A SessionMemory object.
        """
        if session_id is None:
            session_id = str(uuid4())
        return self.store.create_session(session_id)

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Retrieve a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            SessionMemory if found, otherwise None.
        """
        return self.store.get_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its memories.

        Args:
            session_id: The session identifier.

        Returns:
            True if session was deleted, False if not found.
        """
        return self.store.delete_session(session_id)

    def list_sessions(self, limit: Optional[int] = None, offset: int = 0) -> List[SessionMemory]:
        """List all sessions with optional pagination.

        Args:
            limit: Maximum number of sessions to return.
            offset: Number of sessions to skip.

        Returns:
            List of SessionMemory objects.
        """
        return self.store.list_sessions(limit=limit, offset=offset)

    def set_active_session(self, session_id: str) -> bool:
        """Set the active session for convenience operations.

        Args:
            session_id: The session to activate.

        Returns:
            True if session exists and was set, False otherwise.
        """
        if self.get_session(session_id) is not None:
            self._active_session_id = session_id
            return True
        return False

    def get_active_session(self) -> Optional[SessionMemory]:
        """Get the currently active session.

        Returns:
            The active SessionMemory, or None if no session is active.
        """
        if self._active_session_id is None:
            return None
        return self.get_session(self._active_session_id)

    # Conversation Management
    def add_conversation_turn(
        self,
        content: str,
        speaker: str = "user",
        channel: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ConversationTurn]:
        """Add a conversation turn to a session.

        Args:
            content: The turn content.
            speaker: Who produced the turn (e.g., 'user', 'assistant').
            channel: Optional channel or context name.
            session_id: Target session. Uses active session if not provided.
            tags: Optional tags for this turn.
            metadata: Optional metadata dict.

        Returns:
            The ConversationTurn object if successful, None if session not found.
        """
        target_session_id = session_id or self._active_session_id
        if target_session_id is None:
            return None

        session = self.get_session(target_session_id)
        if session is None:
            return None

        turn = ConversationTurn(
            content=content,
            speaker=speaker,
            channel=channel,
            tags=tags or [],
            metadata=metadata or {},
        )
        session.add_conversation_turn(turn)
        return turn

    def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[ConversationTurn]:
        """Retrieve conversation history from a session.

        Args:
            session_id: Target session. Uses active session if not provided.
            limit: Maximum turns to return.
            offset: Number of turns to skip.

        Returns:
            List of ConversationTurn objects.
        """
        target_session_id = session_id or self._active_session_id
        if target_session_id is None:
            return []

        session = self.get_session(target_session_id)
        return session.get_conversation_history(limit=limit, offset=offset) if session else []

    # Decision Management
    def add_decision(
        self,
        decision_summary: str,
        rationale: Optional[str] = None,
        outcome: Optional[str] = None,
        session_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[DecisionRecord]:
        """Add a decision record to a session.

        Args:
            decision_summary: Short summary of the decision.
            rationale: Optional detailed rationale.
            outcome: Optional outcome or result pointer.
            session_id: Target session. Uses active session if not provided.
            tags: Optional tags for this decision.
            metadata: Optional metadata dict.

        Returns:
            The DecisionRecord object if successful, None if session not found.
        """
        target_session_id = session_id or self._active_session_id
        if target_session_id is None:
            return None

        session = self.get_session(target_session_id)
        if session is None:
            return None

        decision = DecisionRecord(
            content=decision_summary,
            decision_summary=decision_summary,
            rationale=rationale,
            outcome=outcome,
            tags=tags or [],
            metadata=metadata or {},
        )
        session.add_decision(decision)
        return decision

    def get_decision_history(
        self,
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[DecisionRecord]:
        """Retrieve decision history from a session.

        Args:
            session_id: Target session. Uses active session if not provided.
            limit: Maximum decisions to return.
            offset: Number of decisions to skip.

        Returns:
            List of DecisionRecord objects.
        """
        target_session_id = session_id or self._active_session_id
        if target_session_id is None:
            return []

        session = self.get_session(target_session_id)
        return session.get_decision_history(limit=limit, offset=offset) if session else []

    # Project Memory Management
    def add_project_memory(
        self,
        project_id: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProjectMemory:
        """Add a memory to a project.

        Args:
            project_id: The project identifier.
            content: Memory content.
            tags: Optional tags for categorization.
            metadata: Optional metadata dict.

        Returns:
            The ProjectMemory object.
        """
        memory = ProjectMemory(
            content=content,
            project_id=project_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.store.add_project_memory(project_id, memory)
        return memory

    def get_project_memories(
        self,
        project_id: str,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Retrieve memories from a project.

        Args:
            project_id: The project identifier.
            limit: Maximum memories to return.
            offset: Number of memories to skip.

        Returns:
            List of MemoryItem objects.
        """
        return self.store.get_project_memories(project_id, limit=limit, offset=offset)

    # Brain Memory Management
    def add_brain_memory(
        self,
        content: str,
        brain_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BrainMemory:
        """Add a global brain-scoped memory.

        Args:
            content: Memory content.
            brain_id: Optional brain/workspace identifier.
            tags: Optional tags for categorization.
            metadata: Optional metadata dict.

        Returns:
            The BrainMemory object (stored in projects with special ID).
        """
        brain_key = f"brain_{brain_id}" if brain_id else "brain_global"
        memory = BrainMemory(
            content=content,
            brain_id=brain_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        self.store.add_project_memory(brain_key, memory)
        return memory

    # Query Operations
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory by its ID from any scope.

        Args:
            memory_id: The memory item ID.

        Returns:
            The MemoryItem if found, otherwise None.
        """
        return self.store.get_memory_by_id(memory_id)

    def filter_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Filter memories across the system with flexible criteria.

        Args:
            memory_type: Filter by memory type (CONVERSATION, DECISION, etc).
            tags: Filter by tags (AND semantics - item must have all tags).
            metadata_filters: Filter by metadata key/value pairs.
            since: Include only memories created at or after this time.
            until: Include only memories created before or at this time.
            session_id: Limit to a specific session.
            project_id: Limit to a specific project.
            limit: Maximum memories to return.
            offset: Number of memories to skip.

        Returns:
            List of matching MemoryItem objects.
        """
        return self.store.filter_memories(
            session_id=session_id,
            project_id=project_id,
            memory_type=memory_type,
            tags=tags,
            metadata_filters=metadata_filters,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )

    # Statistics and Introspection
    def statistics(self) -> Dict[str, Any]:
        """Get aggregate statistics about all memories.

        Returns:
            Dict with session count, project count, and total memory items.
        """
        return self.store.statistics()

    def session_statistics(self, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific session.

        Args:
            session_id: Target session. Uses active session if not provided.

        Returns:
            Dict with session statistics, or None if session not found.
        """
        target_session_id = session_id or self._active_session_id
        if target_session_id is None:
            return None

        session = self.get_session(target_session_id)
        return session.statistics() if session else None
