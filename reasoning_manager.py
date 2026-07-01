from __future__ import annotations

"""Manager for reasoning chains.

Orchestrates chain creation, validation, preparation, and lifecycle management.
No execution logic (Phase 5+ responsibility).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from .context_builder import ContextBuilder, ReasoningContext
from .reasoning_chain import ChainStatus, ReasoningChain, ReasoningResult, ReasoningStep
from .reasoning_models import ReasoningModel


class ReasoningManager:
    """Manager for reasoning chains and components.

    Handles chain lifecycle, step management, and result storage.
    Does not execute reasoning (Phase 5+ responsibility).
    """

    def __init__(self, context_builder: Optional[ContextBuilder] = None) -> None:
        """Initialize the reasoning manager.

        Args:
            context_builder: Optional context builder for building contexts.
        """
        self.context_builder = context_builder or ContextBuilder()
        self._chains: Dict[str, ReasoningChain] = {}
        self._results: Dict[str, ReasoningResult] = {}

    def create_chain(
        self,
        name: str,
        description: Optional[str] = None,
        context: Optional[ReasoningContext] = None,
        steps: Optional[List[ReasoningStep]] = None,
        constraints: Optional[List[Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ReasoningChain:
        """Create a new reasoning chain.

        Args:
            name: Chain name.
            description: Optional description.
            context: Optional reasoning context.
            steps: Optional list of steps.
            constraints: Optional constraints.
            metadata: Optional metadata.

        Returns:
            Created ReasoningChain.
        """
        chain = ReasoningChain(
            name=name,
            description=description,
            context=context,
            steps=steps or [],
            constraints=constraints or [],
            metadata=metadata or {},
        )
        self._chains[chain.chain_id] = chain
        return chain

    def validate_chain(self, chain: ReasoningChain) -> tuple[bool, List[str]]:
        """Validate chain structure.

        Args:
            chain: Chain to validate.

        Returns:
            (is_valid, list_of_errors)
        """
        return chain.validate()

    def prepare_chain(self, chain: ReasoningChain) -> ReasoningChain:
        """Prepare chain for execution.

        Args:
            chain: Chain to prepare.

        Returns:
            Prepared chain (status = PREPARED).
        """
        prepared = chain.prepare_for_execution()
        self._chains[chain.chain_id] = prepared
        return prepared

    def get_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        """Retrieve a chain by ID.

        Args:
            chain_id: Chain identifier.

        Returns:
            Chain if found, None otherwise.
        """
        return self._chains.get(chain_id)

    def list_chains(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[ReasoningChain]:
        """List all chains with pagination.

        Args:
            limit: Maximum chains to return.
            offset: Number of chains to skip.

        Returns:
            List of chains.
        """
        chains = list(self._chains.values())
        if offset:
            chains = chains[offset:]
        if limit is not None:
            chains = chains[:limit]
        return chains

    def delete_chain(self, chain_id: str) -> bool:
        """Delete a chain.

        Args:
            chain_id: Chain to delete.

        Returns:
            True if deleted, False if not found.
        """
        if chain_id in self._chains:
            del self._chains[chain_id]
            return True
        return False

    def add_step(self, chain_id: str, step: ReasoningStep) -> Optional[ReasoningChain]:
        """Add a step to a chain.

        Args:
            chain_id: Target chain.
            step: Step to add.

        Returns:
            Updated chain, or None if chain not found.
        """
        chain = self.get_chain(chain_id)
        if chain is None:
            return None

        step.step_index = len(chain.steps)
        chain.steps.append(step)
        return chain

    def remove_step(self, chain_id: str, step_id: str) -> Optional[ReasoningChain]:
        """Remove a step from a chain.

        Args:
            chain_id: Target chain.
            step_id: Step to remove.

        Returns:
            Updated chain, or None if chain not found.
        """
        chain = self.get_chain(chain_id)
        if chain is None:
            return None

        chain.steps = [s for s in chain.steps if s.step_id != step_id]
        for i, step in enumerate(chain.steps):
            step.step_index = i
        return chain

    def store_result(
        self, chain_id: str, result: ReasoningResult
    ) -> Optional[ReasoningResult]:
        """Store a reasoning result.

        Args:
            chain_id: Associated chain.
            result: Result to store.

        Returns:
            Stored result, or None if chain not found.
        """
        chain = self.get_chain(chain_id)
        if chain is None:
            return None

        result.chain_id = chain_id
        self._results[result.result_id] = result
        chain.results[result.result_id] = result
        return result

    def get_result(self, result_id: str) -> Optional[ReasoningResult]:
        """Retrieve a result by ID.

        Args:
            result_id: Result identifier.

        Returns:
            Result if found, None otherwise.
        """
        return self._results.get(result_id)

    def get_chain_results(self, chain_id: str) -> Dict[str, ReasoningResult]:
        """Get all results for a chain.

        Args:
            chain_id: Target chain.

        Returns:
            Dictionary of results.
        """
        chain = self.get_chain(chain_id)
        return chain.results if chain else {}

    def update_chain(
        self,
        chain_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ReasoningChain]:
        """Update chain metadata.

        Args:
            chain_id: Chain to update.
            name: New name (if provided).
            description: New description (if provided).
            metadata: Metadata to merge (if provided).

        Returns:
            Updated chain, or None if not found.
        """
        chain = self.get_chain(chain_id)
        if chain is None:
            return None

        if name is not None:
            chain.name = name
            chain.version += 1

        if description is not None:
            chain.description = description
            chain.version += 1

        if metadata is not None:
            chain.metadata.update(metadata)
            chain.version += 1

        return chain

    def statistics(self, chain_id: str) -> Dict[str, Any]:
        """Get statistics for a chain.

        Args:
            chain_id: Target chain.

        Returns:
            Dictionary of statistics.
        """
        chain = self.get_chain(chain_id)
        if chain is None:
            return {}

        return {
            "chain_id": chain_id,
            "name": chain.name,
            "status": chain.status.value,
            "version": chain.version,
            "step_count": len(chain.steps),
            "result_count": len(chain.results),
            "created_at": chain.created_at.isoformat(),
            "completed_at": chain.completed_at.isoformat()
            if chain.completed_at
            else None,
        }
