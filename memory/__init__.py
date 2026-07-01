"""Memory Foundation for AI Factory Brain.

This package provides a comprehensive memory system for the AI Factory Brain,
including session-based memory, project-scoped memories, and brain-global context.

Core Components:
    - memory_models: Data models for memory items, sessions, and projects
    - memory_store: Storage protocol and in-memory implementation
    - memory_manager: High-level unified memory operations
    - session_manager: Session lifecycle and context management

Usage:
    from memory import MemoryManager, SessionManager, MemoryType

    # Initialize managers
    memory_mgr = MemoryManager()
    session_mgr = SessionManager()

    # Create a session
    session = session_mgr.create_session()
    session_mgr.set_current_session(session.session_id)

    # Add memories
    memory_mgr.add_conversation_turn("Hello", speaker="user")
    memory_mgr.add_conversation_turn("Hi there!", speaker="assistant")

    # Query memories
    turns = memory_mgr.get_conversation_history()
    print(f"Found {len(turns)} conversation turns")

    # Use context manager for nested sessions
    with session_mgr.session_context() as new_session:
        # new_session is now active
        pass
    # Previous session is restored

Schema Version: 1.0
"""

from .memory_models import (
    MemoryType,
    MemoryItem,
    ConversationTurn,
    DecisionRecord,
    SessionMemory,
    ProjectMemory,
    BrainMemory,
)
from .memory_store import (
    MemoryStoreProtocol,
    ProjectMemoryCollection,
    InMemoryStore,
)
from .memory_manager import MemoryManager
from .session_manager import SessionManager

__all__ = [
    # Enums
    "MemoryType",
    # Models
    "MemoryItem",
    "ConversationTurn",
    "DecisionRecord",
    "SessionMemory",
    "ProjectMemory",
    "BrainMemory",
    # Storage
    "MemoryStoreProtocol",
    "ProjectMemoryCollection",
    "InMemoryStore",
    # Managers
    "MemoryManager",
    "SessionManager",
]

__version__ = "1.0"
__schema_version__ = "1.0"
