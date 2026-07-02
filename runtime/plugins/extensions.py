"""ExtensionPoint: Well-known extension points for plugins.

Single responsibility: Define and describe extension points.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Optional


class ExtensionPoint(Enum):
    """Well-known extension points in the runtime.

    Extension points define contract boundaries where plugins can plug in.
    Each extension point has a specific interface and responsibility.

    Enum Values:
        EXECUTOR: Low-level task executors (Phase 7+)
        AI_PROVIDER: AI model adapters (OpenAI, Gemini, etc.)
        MEMORY_ADAPTER: Memory system bridges
        KNOWLEDGE_ADAPTER: Knowledge system bridges
        CUSTOM: User-defined custom extensions

    Design:
    - Extensible via CUSTOM type
    - Maps to Phase 7+ implementation targets
    - No mandatory support in Phase 6C-1
    - Used for capability-based plugin discovery

    Notes:
    - Plugins implement one ExtensionPoint
    - Multiple plugins can implement same ExtensionPoint
    - ExtensionPoint.CUSTOM allows user-defined extensions
    """

    EXECUTOR = "executor"
    AI_PROVIDER = "ai_provider"
    MEMORY_ADAPTER = "memory"
    KNOWLEDGE_ADAPTER = "knowledge"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ExtensionPointDef:
    """Definition of an extension point.

    Immutable descriptor for an extension point in the system.

    Attributes:
        name: Extension point name (e.g., "executor")
        description: Human-readable description
        version: ExtensionPoint version (for evolution)
        schema_version: Data model version

    Design:
    - Frozen to prevent accidental mutation
    - Used for introspection and documentation
    - Version allows evolution of extension point contracts
    """

    schema_version: ClassVar[str] = "1.0"

    name: str
    description: str
    version: str = "1.0"

    def __hash__(self) -> int:
        """Hash based on name."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Equality based on name."""
        if not isinstance(other, ExtensionPointDef):
            return NotImplemented
        return self.name == other.name


# Standard extension point definitions
EXECUTOR_EXTENSION = ExtensionPointDef(
    name=ExtensionPoint.EXECUTOR.value,
    description="Low-level task executors implementing ExecutorProtocol",
    version="1.0",
)

AI_PROVIDER_EXTENSION = ExtensionPointDef(
    name=ExtensionPoint.AI_PROVIDER.value,
    description="AI model adapters (OpenAI, Gemini, Anthropic, etc.)",
    version="1.0",
)

MEMORY_ADAPTER_EXTENSION = ExtensionPointDef(
    name=ExtensionPoint.MEMORY_ADAPTER.value,
    description="Memory system bridges and adapters",
    version="1.0",
)

KNOWLEDGE_ADAPTER_EXTENSION = ExtensionPointDef(
    name=ExtensionPoint.KNOWLEDGE_ADAPTER.value,
    description="Knowledge system bridges and adapters",
    version="1.0",
)

CUSTOM_EXTENSION = ExtensionPointDef(
    name=ExtensionPoint.CUSTOM.value,
    description="User-defined custom extension points",
    version="1.0",
)
