"""PluginProtocol: Interface for runtime plugins.

Single responsibility: Define plugin interface.
All plugins must implement this protocol to be registered.
"""

from __future__ import annotations

from typing import List, Protocol, Tuple, runtime_checkable


@runtime_checkable
class PluginProtocol(Protocol):
    """Protocol for runtime plugins.

    All plugins must implement this protocol to be registered
    with PluginRegistry and used by runtime.

    Responsibilities:
    - Provide plugin identification
    - Return metadata descriptor
    - Declare extension point
    - List capabilities
    - Validate structure
    - Report enable/disable status

    Design:
    - Minimal interface (intentionally small)
    - No execution interface
    - No AI provider assumptions
    - Extensible via metadata
    - Protocol-based (duck typing)

    Notes:
    - Separate from ExecutorProtocol (Phase 6A)
    - Phase 7+ will bridge executors and plugins
    - Plugins can be enabled/disabled without unregistering

    [TODO - Phase 7+: Plugin execution interfaces]
    [TODO - Phase 7+: Dynamic plugin loading]
    [TODO - Phase 7+: Dependency resolution]
    """

    def get_plugin_id(self) -> str:
        """Get unique plugin identifier.

        Returns:
            Plugin ID (e.g., "openai.gpt4", "custom.provider")
            Must be unique within registry
        """
        ...

    def get_metadata(self) -> "PluginMetadata":  # noqa: F821
        """Get plugin metadata descriptor.

        Returns:
            PluginMetadata instance with full plugin information

        Notes:
        - Metadata is immutable after registration
        - Contains plugin identity, version, capabilities
        - Used for discovery and introspection
        """
        ...

    def get_extension_point(self) -> str:
        """Get ExtensionPoint this plugin implements.

        Returns:
            Extension point identifier (from ExtensionPoint enum)

        Notes:
        - Must match one of: "executor", "ai_provider", "memory",
          "knowledge", "custom", or custom string
        - Used for capability-based discovery
        """
        ...

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities provided.

        Returns:
            List of capability identifiers (e.g., ["openai", "gpt4"])

        Notes:
        - Capabilities determine what this plugin can do
        - Used by registry for find_by_capability()
        - Plugin-specific naming allowed
        """
        ...

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate plugin structure.

        Returns:
            (is_valid: bool, errors: List[str])

        Notes:
        - Called by registry after registration
        - Should validate internal state only
        - Errors list empty if valid
        - Example errors: "missing_config", "invalid_metadata"
        """
        ...

    def is_enabled(self) -> bool:
        """Check if plugin is enabled.

        Returns:
            True if plugin is enabled, False if disabled

        Notes:
        - Disabled plugins remain registered but not used
        - Registry can enable/disable without unregistering
        - Used to conditionally select plugins during discovery
        """
        ...
