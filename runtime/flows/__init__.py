"""Phase 6B: Error Handling Flows.

Flow definitions for retry, timeout, and cancellation.

Public API:
- RetryFlow: Retry policy protocol
- TimeoutFlow: Timeout policy protocol
- CancellationFlow: Cancellation policy protocol
- FlowType: Flow type enumeration
- RetryStrategy: Retry strategy enumeration
- BackoffStrategy: Backoff strategy enumeration
- CancellationReason: Cancellation reason enumeration

Design:
- No async, no threading, synchronous only
- Structure/interface only
- No execution logic
- No business logic

[TODO - Phase 6C: Flow persistence]
[TODO - Phase 6C: Flow composition]
[TODO - Phase 7+: Flow execution]
"""

from .retry import (
    RetryFlow,
    RetryStrategy,
    BackoffStrategy,
)
from .timeout import (
    TimeoutFlow,
)
from .cancellation import (
    CancellationFlow,
    CancellationReason,
)

__all__ = [
    "RetryFlow",
    "RetryStrategy",
    "BackoffStrategy",
    "TimeoutFlow",
    "CancellationFlow",
    "CancellationReason",
]

__version__ = "1.0.0"
__schema_version__ = "1.0"
