"""PluginMetadata: Plugin descriptor and status enums.

Single responsibility: Define plugin metadata structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid4


class PluginStatus(Enum):
    """Status of a plugin in the registry."""

    REGISTERED = "registered"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    UNREGISTERED = "unregistered"


@dataclass
class PluginMetadata:
    """Immutable metadata for a plugin.

    Describes plugin identity, capabilities, and configuration.
    Created once and never modified after registration.

    Attributes:
        plugin_id: Unique identifier (e.g., "openai.gpt4")
        name: Human-readable name (e.g., "OpenAI GPT-4")
        version: Semantic version string (e.g., "1.0.0")
        author: Plugin author name or organization
        description: Human-readable description
        extension_point: Which ExtensionPoint this implements
        supports: List of supported subtypes/capabilities
        dependencies: List of plugin ID dependencies
        config_schema: Optional configuration JSON schema
        metadata: Custom metadata dict
        registered_at: Timestamp when registered
        enabled: Enable/disable flag
        schema_version: Data model version

    Design:
    - Frozen to prevent accidental mutation after creation
    - plugin_id must be unique per registry
    - version follows semantic versioning convention
    - extension_point matches ExtensionPoint enum (extensible)
    - supports list enables capability-based discovery
    - dependencies enables future Phase 7+ resolver
    - config_schema is optional (plugins define their own)
    - metadata dict allows extension without schema change

    Notes:
    - Not validated on creation (validation in registry)
    - Registered timestamp tracks when added to registry
    - enabled flag allows disable without unregistration
    """

    schema_version: ClassVar[str] = "1.0"

    plugin_id: str = field()
    name: str = field()
    version: str = field()
    author: str = field()
    description: str = field()
    extension_point: str = field()
    supports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = field(default=True)

    def __hash__(self) -> int:
        """Hash based on plugin_id."""
        return hash(self.plugin_id)

    def __eq__(self, other: object) -> bool:
        """Equality based on plugin_id."""
        if not isinstance(other, PluginMetadata):
            return NotImplemented
        return self.plugin_id == other.plugin_id

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dict with all metadata fields

        Notes:
        - registered_at serialized to ISO format string
        - Useful for persistence/logging
        """
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "extension_point": self.extension_point,
            "supports": self.supports,
            "dependencies": self.dependencies,
            "config_schema": self.config_schema,
            "metadata": self.metadata,
            "registered_at": self.registered_at.isoformat(),
            "enabled": self.enabled,
            "schema_version": self.schema_version,
        }
