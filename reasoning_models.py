from __future__ import annotations

"""Reasoning models for the Reasoning Foundation.

Defines core data structures for reasoning models, constraints, and configuration.
No reasoning algorithms or AI execution in this module.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid4


class ReasoningModelType(Enum):
    """Types of reasoning models supported."""

    LINEAR_CHAIN = "linear_chain"
    TREE_SEARCH = "tree_search"
    GRAPH = "graph"
    CUSTOM = "custom"


@dataclass
class ReasoningModel:
    """Configuration for a reasoning model.

    Attributes:
        model_id: Unique identifier for the model.
        model_type: Type of reasoning model.
        name: Human-readable model name.
        description: Optional description of the model.
        parameters: Flexible configuration parameters.
        schema_version: Schema version for compatibility.
    """

    schema_version: ClassVar[str] = "1.0"

    model_id: str = field(default_factory=lambda: str(uuid4()))
    model_type: ReasoningModelType = ReasoningModelType.LINEAR_CHAIN
    name: str = "Reasoning Model"
    description: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningConstraint:
    """A constraint on reasoning steps or results.

    Attributes:
        constraint_id: Unique identifier.
        name: Constraint name.
        description: Description of what the constraint enforces.
        rule: Constraint rule (description or expression).
        severity: MUST (required), SHOULD (recommended), MAY (optional).
        metadata: Additional metadata.
    """

    schema_version: ClassVar[str] = "1.0"

    constraint_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    rule: str = ""
    severity: str = "MUST"  # MUST, SHOULD, MAY
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
