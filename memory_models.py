from __future__ import annotations

"""Memory models for the Memory Foundation.

This module defines dataclasses used to represent memory items, conversation
turns, decisions, session, project, and brain-level memories. Models include
schema_version class variables for future compatibility.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, ClassVar
import uuid


class MemoryType(Enum):
    """Enumeration of supported memory item types."""

    GENERIC = "generic"
    CONVERSATION = "conversation"
    DECISION = "decision"
    PROJECT = "project"
    BRAIN = "brain"


@dataclass
class MemoryItem:
    """Represents a single memory item.

    Attributes:
        content: Free-form text content of the memory.
        memory_type: Category/type of the memory.
        metadata: Arbitrary key/value metadata attached to the memory.
        tags: List of tags for quick filtering and categorization.
        related_ids: References to other memory item ids.
        source: Optional origin identifier (e.g., "user", "system").
        id: Unique identifier for the memory item.
        created_at: UTC timestamp when the memory was created.

    Class Attributes:
        schema_version: Version string for the memory item schema.
    """

    schema_version: ClassVar[str] = "1.0"

    content: str
    memory_type: MemoryType = MemoryType.GENERIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    source: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-serializable representation of the memory item.

        Returns:
            A dict with primitive types suitable for storage or transport.
        """
        data = asdict(self)
        data["memory_type"] = self.memory_type.value
        data["created_at"] = self.created_at.isoformat()
        data["schema_version"] = self.schema_version
        return data


@dataclass
class ConversationTurn(MemoryItem):
    """Represents a single conversation turn.

    Attributes:
        speaker: Who produced the turn (e.g., 'user', 'assistant').
        channel: Optional channel or context name.
    """

    schema_version: ClassVar[str] = "1.0"

    speaker: str = "user"
    channel: Optional[str] = None

    def __post_init__(self) -> None:
        # Ensure conversation turns are typed correctly
        self.memory_type = MemoryType.CONVERSATION


@dataclass
class DecisionRecord(MemoryItem):
    """Represents a decision taken during a session.

    Attributes:
        decision_summary: Short summary of the decision.
        rationale: Optional detailed rationale or notes.
        outcome: Optional outcome or result pointer.
    """

    schema_version: ClassVar[str] = "1.0"

    decision_summary: str = ""
    rationale: Optional[str] = None
    outcome: Optional[str] = None

    def __post_init__(self) -> None:
        # Ensure decision records are typed correctly
        self.memory_type = MemoryType.DECISION


@dataclass
class SessionMemory:
    """Container for memory belonging to a single session.

    Holds conversation history, decision history, general memories, and
    session-level metadata.
    """

    schema_version: ClassVar[str] = "1.0"

    session_id: str
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = field(default_factory=lambda: datetime.utcnow())
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    decision_history: List[DecisionRecord] = field(default_factory=list)
    general_memories: List[MemoryItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_conversation_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the session.

        Args:
            turn: ConversationTurn to append.
        """
        self.conversation_history.append(turn)
        self.updated_at = datetime.utcnow()

    def add_decision(self, decision: DecisionRecord) -> None:
        """Add a decision record to the session.

        Args:
            decision: DecisionRecord to append.
        """
        self.decision_history.append(decision)
        self.updated_at = datetime.utcnow()

    def add_memory(self, memory: MemoryItem) -> None:
        """Add a general memory item to the session.

        Args:
            memory: MemoryItem to append.
        """
        self.general_memories.append(memory)
        self.updated_at = datetime.utcnow()

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a memory item by id from this session.

        Searches conversation turns, decisions, and general memories.

        Args:
            memory_id: The id to look up.

        Returns:
            The MemoryItem if found, otherwise None.
        """
        for collection in (self.conversation_history, self.decision_history, self.general_memories):
            for item in collection:
                if item.id == memory_id:
                    return item
        return None

    def filter_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[MemoryItem]:
        """Filter memories in this session by criteria with pagination.

        Args:
            memory_type: If provided, only return items of this type.
            tags: If provided, item must contain all tags (AND semantics).
            metadata_filters: If provided, item.metadata must contain matching key/value pairs.
            since: If provided, only items created at or after this time are returned.
            until: If provided, only items created before or at this time are returned.
            limit: Optional maximum number of items to return.
            offset: Optional number of items to skip before returning results.

        Returns:
            List of matching MemoryItem objects.
        """
        results: List[MemoryItem] = []

        all_items: List[MemoryItem] = []
        all_items.extend(self.conversation_history)
        all_items.extend(self.decision_history)
        all_items.extend(self.general_memories)

        for item in all_items:
            if memory_type and item.memory_type != memory_type:
                continue
            if tags:
                if not all(tag in item.tags for tag in tags):
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

        # Apply offset and limit
        if offset:
            results = results[offset:]
        if limit is not None:
            results = results[:limit]

        return results

    def get_conversation_history(self, limit: Optional[int] = None, offset: int = 0) -> List[ConversationTurn]:
        """Return conversation history with optional pagination.

        Args:
            limit: Optional maximum number of turns to return.
            offset: Number of turns to skip.

        Returns:
            List of ConversationTurn objects.
        """
        items = self.conversation_history[offset:]
        return items if limit is None else items[:limit]

    def get_decision_history(self, limit: Optional[int] = None, offset: int = 0) -> List[DecisionRecord]:
        """Return decision history with optional pagination.

        Args:
            limit: Optional maximum number of decisions to return.
            offset: Number of decisions to skip.

        Returns:
            List of DecisionRecord objects.
        """
        items = self.decision_history[offset:]
        return items if limit is None else items[:limit]

    def statistics(self) -> Dict[str, Any]:
        """Return simple statistics about the session memory.

        Returns:
            A dict containing counts for conversation turns, decisions, and general memories.
        """
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "conversation_count": len(self.conversation_history),
            "decision_count": len(self.decision_history),
            "general_memory_count": len(self.general_memories),
            "total_memories": len(self.conversation_history)
            + len(self.decision_history)
            + len(self.general_memories),
            "schema_version": self.schema_version,
        }


@dataclass
class ProjectMemory(MemoryItem):
    """Represents a memory item tied to a specific project.

    Attributes:
        project_id: Identifier for the project the memory belongs to.
    """

    schema_version: ClassVar[str] = "1.0"

    project_id: str = ""

    def __post_init__(self) -> None:
        self.memory_type = MemoryType.PROJECT


@dataclass
class BrainMemory(MemoryItem):
    """Represents a brain-scoped memory (global to the agent/brain).

    Attributes:
        brain_id: Optional identifier for the brain or workspace.
    """

    schema_version: ClassVar[str] = "1.0"

    brain_id: Optional[str] = None

    def __post_init__(self) -> None:
        self.memory_type = MemoryType.BRAIN
