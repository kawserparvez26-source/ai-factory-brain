from __future__ import annotations

"""Storage protocol and in-memory implementation.

Defines MemoryStoreProtocol as the store abstraction (protocol). InMemoryStore
implements this protocol and is intended as the default runtime store for the
Memory Foundation during development/testing.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Dict, List, Optional, Any, runtime_checkable

from .memory_models import (
    MemoryItem,
    SessionMemory,
    MemoryType,
)


@runtime_checkable
class MemoryStoreProtocol(Protocol):
    """Protocol (interface) for memory stores.

    Implementations must provide methods for session/project lifecycle,
    retrieval by id, filtering with pagination, and statistics.
    """

    def create_session(self, session_id: str) -> SessionMemory:
        ...

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        ...

    def delete_session(self, session_id: str) -> bool:
        ...

    def list_sessions(self, limit: Optional[int] = None, offset: int = 0) -> List[SessionMemory]:
        ...

    def get_or_create_project(self, project_id: str) -> Any:
        ...

    def add_project_memory(self, project_id: str, item: MemoryItem) -> None:
        ...

    def get_project_memories(self, project_id: str, limit: Optional[int] = None, offset: int = 0) -> List[MemoryItem]:
        ...

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        ...

    def filter_memories(
        self,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryItem]:
        ...

    def statistics(self) -> Dict[str, Any]:
        ...


@dataclass
class ProjectMemoryCollection:
    """Container for memories associated with a project."""

    project_id: str
    memories: List[MemoryItem] = field(default_factory=list)

    def add(self, item: MemoryItem) -> None:
        """Add a MemoryItem to the project collection."""
        self.memories.append(item)

    def get_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory by id from this project collection."""
        for m in self.memories:
            if m.id == memory_id:
                return m
        return None

    def list(self, limit: Optional[int] = None, offset: int = 0) -> List[MemoryItem]:
        """Return memories with optional pagination."""
        items = self.memories[offset:]
        return items if limit is None else items[:limit]


class InMemoryStore:
    """In-memory implementation of MemoryStoreProtocol.

    This implementation is intentionally simple and single-process. It is
    suitable for testing and early development. It supports pagination
    (limit, offset) on all listing/filtering methods.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionMemory] = {}
        self._projects: Dict[str, ProjectMemoryCollection] = {}

    # Session operations
    def create_session(self, session_id: str) -> SessionMemory:
        """Create or return an existing SessionMemory."""
        if session_id in self._sessions:
            return self._sessions[session_id]
        session = SessionMemory(session_id=session_id)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Retrieve a session by id."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session; return True if removed."""
        return self._sessions.pop(session_id, None) is not None

    def list_sessions(self, limit: Optional[int] = None, offset: int = 0) -> List[SessionMemory]:
        """List sessions with optional pagination."""
        items = list(self._sessions.values())[offset:]
        return items if limit is None else items[:limit]

    # Project operations
    def get_or_create_project(self, project_id: str) -> ProjectMemoryCollection:
        """Get or create a project collection."""
        if project_id not in self._projects:
            self._projects[project_id] = ProjectMemoryCollection(project_id=project_id)
        return self._projects[project_id]

    def add_project_memory(self, project_id: str, item: MemoryItem) -> None:
        """Add a memory item to a project collection."""
        coll = self.get_or_create_project(project_id)
        coll.add(item)

    def get_project_memories(self, project_id: str, limit: Optional[int] = None, offset: int = 0) -> List[MemoryItem]:
        """Return a project's memories with pagination."""
        coll = self._projects.get(project_id)
        return coll.list(limit=limit, offset=offset) if coll else []

    # Lookup operations
    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Search for a memory item by id across sessions and projects."""
        for session in self._sessions.values():
            item = session.get_memory_by_id(memory_id)
            if item:
                return item
        for project in self._projects.values():
            item = project.get_by_id(memory_id)
            if item:
                return item
        return None

    def filter_memories(
        self,
        session_id: Optional[str] = None,
        project_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Filter memories across sessions and projects with pagination."""
        results: List[MemoryItem] = []

        if session_id:
            session = self._sessions.get(session_id)
            if not session:
                return []
            sources = (
                list(session.conversation_history)
                + list(session.decision_history)
                + list(session.general_memories)
            )
        elif project_id:
            coll = self._projects.get(project_id)
            sources = list(coll.memories) if coll else []
        else:
            items: List[MemoryItem] = []
            for session in self._sessions.values():
                items.extend(session.conversation_history)
                items.extend(session.decision_history)
                items.extend(session.general_memories)
            for coll in self._projects.values():
                items.extend(coll.memories)
            sources = items

        for item in sources:
            if memory_type and item.memory_type != memory_type:
                continue
            if tags and not all(tag in item.tags for tag in tags):
                continue
            if metadata_filters:
                ok = True
                for k, v in metadata_filters.items():
                    if item.metadata.get(k) != v:
                        ok = False
                        break
                if not ok:
                    continue
            if since and item.created_at < since:
                continue
            if until and item.created_at > until:
                continue
            results.append(item)

        if offset:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]

        return results

    def statistics(self) -> Dict[str, Any]:
        """Return stats for sessions, projects and total memory items."""
        session_count = len(self._sessions)
        project_count = len(self._projects)
        memory_count = 0
        for s in self._sessions.values():
            memory_count += len(s.conversation_history)
            memory_count += len(s.decision_history)
            memory_count += len(s.general_memories)
        for p in self._projects.values():
            memory_count += len(p.memories)

        return {
            "session_count": session_count,
            "project_count": project_count,
            "total_memory_items": memory_count,
        }
