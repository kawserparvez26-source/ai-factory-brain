"""Reasoning Foundation for AI Factory Brain.

Phase 4: Data structures and orchestration only.
No reasoning execution, AI provider integration, or external API calls.

Core Components:
    - reasoning_models: Base models and constraints
    - context_builder: Context assembly from KB/Memory
    - reasoning_chain: Chain and step structures
    - reasoning_manager: Chain lifecycle management

Usage:
    from reasoning import ReasoningManager, ContextBuilder, ReasoningModel

    # Build context (read-only from KB/Memory)
    builder = ContextBuilder(knowledge_provider=kb, memory_provider=memory)
    context = builder.build_context(model=my_model, knowledge_refs=[...])

    # Create chain
    manager = ReasoningManager(context_builder=builder)
    chain = manager.create_chain("My Chain", context=context, steps=[...])

    # Validate and prepare
    chain = manager.prepare_chain(chain)

    # [TODO - Phase 5+] ExecutionEngine handles actual reasoning

Schema Version: 1.0
"""

from .context_builder import ContextBuilder, ReasoningContext
from .reasoning_chain import (
    ChainStatus,
    ReasoningChain,
    ReasoningResult,
    ReasoningStep,
    StepStatus,
    StepType,
)
from .reasoning_manager import ReasoningManager
from .reasoning_models import ReasoningConstraint, ReasoningModel, ReasoningModelType

__all__ = [
    # Models
    "ReasoningModel",
    "ReasoningModelType",
    "ReasoningConstraint",
    # Context
    "ReasoningContext",
    "ContextBuilder",
    # Chain
    "ReasoningChain",
    "ReasoningStep",
    "ReasoningResult",
    "ChainStatus",
    "StepType",
    "StepStatus",
    # Manager
    "ReasoningManager",
]

__version__ = "1.0"
__schema_version__ = "1.0"
