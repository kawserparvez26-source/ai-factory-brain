from __future__ import annotations

"""Reasoning chain models for orchestrating reasoning steps.

Defines chain structure and lifecycle, but does not execute reasoning.
Execution is responsibility of Phase 5+ ExecutionEngine.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid4

from .reasoning_models import ReasoningConstraint


class StepType(Enum):
    """Types of reasoning steps."""

    QUERY = "query"
    FILTER = "filter"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    REASON = "reason"  # [TODO - Phase 5+: AI execution]
    DECIDE = "decide"
    CUSTOM = "custom"


class StepStatus(Enum):
    """Status of a reasoning step."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ChainStatus(Enum):
    """Status of a reasoning chain."""

    CREATED = "created"
    VALIDATED = "validated"
    PREPARED = "prepared"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass
class ReasoningStep:
    """A single step in a reasoning chain.

    Attributes:
        step_id: Unique identifier.
        step_index: Position in chain.
        name: Step name.
        step_type: Type of reasoning step.
        inputs: Input data.
        input_refs: References to other steps or context.
        outputs: Output schema (structure only).
        constraints: Step-level constraints.
        status: Current status.
        error: Error message if failed.
        metadata: Additional metadata.
        schema_version: Schema version.
    """

    schema_version: ClassVar[str] = "1.0"

    step_id: str = field(default_factory=lambda: str(uuid4()))
    step_index: int = 0
    name: str = ""
    step_type: StepType = StepType.CUSTOM
    inputs: Dict[str, Any] = field(default_factory=dict)
    input_refs: List[str] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    constraints: List[ReasoningConstraint] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningResult:
    """Result from executing a reasoning step or chain.

    Attributes:
        result_id: Unique identifier.
        step_id: Source step (None for chain-level result).
        chain_id: Parent chain identifier.
        status: Success/failure status.
        output: Result output data.
        evidence: Supporting evidence references.
        confidence: Optional confidence score (0.0-1.0).
        metadata: Additional metadata.
        schema_version: Schema version.
    """

    schema_version: ClassVar[str] = "1.0"

    result_id: str = field(default_factory=lambda: str(uuid4()))
    step_id: Optional[str] = None
    chain_id: str = ""
    status: str = "success"  # success, failed, inconclusive
    output: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningChain:
    """A chain of reasoning steps.

    Orchestrates step execution (structure only, no actual execution in Phase 4).

    Attributes:
        chain_id: Unique identifier.
        version: Version number for tracking changes.
        name: Chain name.
        description: Chain description.
        context: Reasoning context.
        steps: List of steps in execution order.
        status: Current chain status.
        current_step: Index of current step.
        results: Intermediate and final results.
        constraints: Chain-level constraints.
        metadata: Additional metadata.
        schema_version: Schema version.
    """

    schema_version: ClassVar[str] = "1.0"

    chain_id: str = field(default_factory=lambda: str(uuid4()))
    version: int = 1
    name: str = ""
    description: Optional[str] = None
    context: Optional[Any] = None  # ReasoningContext
    steps: List[ReasoningStep] = field(default_factory=list)
    status: ChainStatus = ChainStatus.CREATED
    current_step: int = 0
    results: Dict[str, ReasoningResult] = field(default_factory=dict)
    constraints: List[ReasoningConstraint] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def validate(self) -> tuple[bool, List[str]]:
        """Validate chain structure.

        Checks:
        - All steps have unique IDs
        - Step indices are valid
        - Input references are resolvable

        Returns:
            (is_valid, list_of_errors)
        """
        errors: List[str] = []

        if not self.steps:
            errors.append("Chain must have at least one step")
            return (False, errors)

        step_ids = {step.step_id for step in self.steps}
        if len(step_ids) != len(self.steps):
            errors.append("Duplicate step IDs found")

        for i, step in enumerate(self.steps):
            if step.step_index != i:
                errors.append(f"Step {i} has incorrect index {step.step_index}")

        return (len(errors) == 0, errors)

    def prepare_for_execution(self) -> ReasoningChain:
        """Prepare chain for execution.

        Validates structure and marks ready for execution.
        Does not execute (Phase 5+ responsibility).

        Returns:
            Updated chain with PREPARED status.
        """
        is_valid, errors = self.validate()
        if not is_valid:
            self.status = ChainStatus.FAILED
            return self

        self.status = ChainStatus.PREPARED
        self.current_step = 0
        return self

    def is_executable(self) -> bool:
        """Check if chain is in executable state.

        Returns:
            True if chain can be executed (status is PREPARED).
        """
        return self.status == ChainStatus.PREPARED
