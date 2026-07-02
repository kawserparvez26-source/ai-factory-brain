"""Phase 6B: Session Management.

Session scope and lifecycle for execution context.

Public API:
- SessionScope: Session lifecycle state enumeration
- ScopeManager: Session scope state machine

Design:
- No async, no threading, synchronous only
- Structure/interface only
- No execution logic
- No persistence

[TODO - Phase 6C: Session persistence]
[TODO - Phase 6C: Session context/state]
[TODO - Phase 7+: Session monitoring/metrics]
"""

from .scope import (
    SessionScope,
    ScopeManager,
)

__all__ = [
    "SessionScope",
    "ScopeManager",
]

__version__ = "1.0.0"
__schema_version__ = "1.0"
