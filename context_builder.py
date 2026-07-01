from __future__ import annotations

"""Context builder for assembling reasoning context.

Builds ReasoningContext by consuming Knowledge and Memory Foundations
through protocol-based interfaces (read-only).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional, Protocol, runtime_checkable
from uuid import uuid4

from .reasoning_models import ReasoningModel, ReasoningConstraint


@runtime_checkable
class KnowledgeProviderProtocol(Protocol):
    """Protocol for knowledge base access (read-only).

    Implementations provide read-only access to knowledge items.
    """

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a knowledge item by ID."""
        ...

    def validate_refs(self, refs: List[str]) -> tuple[bool, List[str]]:
        """Validate that references exist in knowledge base.

        Returns:
            (is_valid, missing_refs)
        """
        ...


@runtime_checkable
class MemoryProviderProtocol(Protocol):
    """Protocol for memory access (read-only).

    Implementations provide read-only access to memory items.
    """

    def get_memory_item(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory item by ID."""
        ...

    def get_session_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session memory context."""
        ...

    def validate_memory_refs(self, refs: List[str]) -> tuple[bool, List[str]]:
        """Validate that memory references exist.

        Returns:
            (is_valid, missing_refs)
        """
        ...


@dataclass
class ReasoningContext:
    """Context for reasoning operations.

    Assembled from Knowledge and Memory Foundations (read-only).
    Contains references to external items, not copies.

    Attributes:
        context_id: Unique identifier.
        session_id: Optional link to memory session.
        model: Reasoning model to use.
        knowledge_refs: References to knowledge base items.
        memory_items: References to memory items.
        constraints: Reasoning constraints.
        metadata: Additional metadata.
        schema_version: Schema version for compatibility.
    """

    schema_version: ClassVar[str] = "1.0"

    context_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: Optional[str] = None
    model: Optional[ReasoningModel] = None
    knowledge_refs: List[str] = field(default_factory=list)
    memory_items: List[str] = field(default_factory=list)
    constraints: List[ReasoningConstraint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ContextBuilder:
    """Builder for assembling reasoning context.

    Uses protocol-based providers to access Knowledge and Memory Foundations
    without modification. Reads only, never writes.
    """

    def __init__(
        self,
        knowledge_provider: Optional[KnowledgeProviderProtocol] = None,
        memory_provider: Optional[MemoryProviderProtocol] = None,
    ) -> None:
        """Initialize context builder with optional providers.

        Args:
            knowledge_provider: Optional knowledge provider (read-only).
            memory_provider: Optional memory provider (read-only).
        """
        self.knowledge_provider = knowledge_provider
        self.memory_provider = memory_provider

    def build_context(
        self,
        model: ReasoningModel,
        knowledge_refs: Optional[List[str]] = None,
        memory_items: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        constraints: Optional[List[ReasoningConstraint]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReasoningContext:
        """Build a reasoning context.

        Assembles context from references to Knowledge and Memory Foundations.
        No modifications made to either foundation.

        Args:
            model: Reasoning model for this context.
            knowledge_refs: References to knowledge items.
            memory_items: References to memory items.
            session_id: Optional session identifier.
            constraints: Optional reasoning constraints.
            metadata: Optional metadata.

        Returns:
            Assembled ReasoningContext.
        """
        return ReasoningContext(
            session_id=session_id,
            model=model,
            knowledge_refs=knowledge_refs or [],
            memory_items=memory_items or [],
            constraints=constraints or [],
            metadata=metadata or {},
        )

    def validate_context(self, context: ReasoningContext) -> tuple[bool, List[str]]:
        """Validate a reasoning context.

        Checks that all references are valid (if providers available).
        Does not modify context.

        Args:
            context: Context to validate.

        Returns:
            (is_valid, list_of_errors)
        """
        errors: List[str] = []

        if not context.model:
            errors.append("Context must have a model")

        if self.knowledge_provider and context.knowledge_refs:
            valid, missing = self.knowledge_provider.validate_refs(
                context.knowledge_refs
            )
            if not valid:
                errors.append(f"Missing knowledge refs: {missing}")

        if self.memory_provider and context.memory_items:
            valid, missing = self.memory_provider.validate_memory_refs(
                context.memory_items
            )
            if not valid:
                errors.append(f"Missing memory refs: {missing}")

        return (len(errors) == 0, errors)

    def extend_context(
        self,
        context: ReasoningContext,
        knowledge_refs: Optional[List[str]] = None,
        memory_items: Optional[List[str]] = None,
        constraints: Optional[List[ReasoningConstraint]] = None,
    ) -> ReasoningContext:
        """Extend a context with additional references.

        Returns new context, does not modify original.

        Args:
            context: Context to extend.
            knowledge_refs: Additional knowledge references.
            memory_items: Additional memory items.
            constraints: Additional constraints.

        Returns:
            Extended ReasoningContext (new instance).
        """
        return ReasoningContext(
            context_id=context.context_id,
            session_id=context.session_id,
            model=context.model,
            knowledge_refs=context.knowledge_refs + (knowledge_refs or []),
            memory_items=context.memory_items + (memory_items or []),
            constraints=context.constraints + (constraints or []),
            metadata=context.metadata.copy(),
            created_at=context.created_at,
        )

    def clone_context(self, context: ReasoningContext) -> ReasoningContext:
        """Create an independent copy of a context.

        Args:
            context: Context to clone.

        Returns:
            Independent copy with new context_id.
        """
        return ReasoningContext(
            model=context.model,
            session_id=context.session_id,
            knowledge_refs=context.knowledge_refs.copy(),
            memory_items=context.memory_items.copy(),
            constraints=context.constraints.copy(),
            metadata=context.metadata.copy(),
        )

    def to_dict(self, context: ReasoningContext) -> Dict[str, Any]:
        """Convert context to dictionary.

        Args:
            context: Context to serialize.

        Returns:
            Dictionary representation.
        """
        return {
            "context_id": context.context_id,
            "session_id": context.session_id,
            "model_id": context.model.model_id if context.model else None,
            "knowledge_refs": context.knowledge_refs,
            "memory_items": context.memory_items,
            "constraint_count": len(context.constraints),
            "metadata": context.metadata,
            "created_at": context.created_at.isoformat(),
        }
