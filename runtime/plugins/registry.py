"""PluginRegistry: Plugin discovery and lifecycle management.

Single responsibility: Register, discover, and manage plugins.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .metadata import PluginMetadata, PluginStatus
from .protocol import PluginProtocol


@dataclass
class PluginRegistration:
    """Metadata for a registered plugin.

    Tracks plugin state within the registry.

    Attributes:
        metadata: PluginMetadata descriptor
        plugin: PluginProtocol instance
        is_enabled: Current enabled/disabled state
        registered_at: Timestamp when registered
    """

    metadata: PluginMetadata
    plugin: PluginProtocol
    is_enabled: bool
    registered_at: datetime


class PluginRegistry:
    """Central registry for plugin discovery and lifecycle.

    Responsibilities:
    - Register and unregister plugins
    - Discover plugins by extension point or capability
    - Enable/disable plugins without unregistering
    - Provide plugin metadata and statistics
    - No persistence (in-memory only)
    - No validation (validation in plugins themselves)

    Design:
    - Simple dict-based storage (no complex querying)
    - Thread-safe via GIL (synchronous, no async)
    - Indexes by: plugin_id, extension_point, capability
    - Single instance per runtime
    - No dependency resolution (Phase 7+ feature)

    Notes:
    - In-memory only (no persistence)
    - No complex validation (plugins self-validate)
    - Enables/disables without unregistering
    - All operations synchronous
    """

    def __init__(self) -> None:
        """Initialize empty registry.

        Creates internal data structures for plugin storage and indexing.
        """
        self._plugins: Dict[str, PluginProtocol] = {}
        self._registrations: Dict[str, PluginRegistration] = {}
        self._by_extension: Dict[str, List[str]] = {}  # extension → [plugin_ids]
        self._by_capability: Dict[str, List[str]] = {}  # capability → [plugin_ids]

    def register(
        self, metadata: PluginMetadata, plugin: PluginProtocol
    ) -> None:
        """Register a plugin.

        Args:
            metadata: PluginMetadata instance
            plugin: PluginProtocol implementation

        Raises:
            ValueError: If plugin_id already registered
            ValueError: If plugin_id empty

        Notes:
        - plugin_id must be unique globally
        - plugin must implement PluginProtocol
        - metadata.enabled determines initial state
        - No validation performed on metadata
        """
        if not metadata.plugin_id:
            raise ValueError("plugin_id cannot be empty")
        if metadata.plugin_id in self._plugins:
            raise ValueError(f"Plugin '{metadata.plugin_id}' already registered")

        # Store plugin
        self._plugins[metadata.plugin_id] = plugin

        # Create registration
        registration = PluginRegistration(
            metadata=metadata,
            plugin=plugin,
            is_enabled=metadata.enabled,
            registered_at=datetime.utcnow(),
        )
        self._registrations[metadata.plugin_id] = registration

        # Index by extension point
        ext_point = metadata.extension_point
        if ext_point not in self._by_extension:
            self._by_extension[ext_point] = []
        self._by_extension[ext_point].append(metadata.plugin_id)

        # Index by capabilities
        for capability in metadata.supports:
            if capability not in self._by_capability:
                self._by_capability[capability] = []
            self._by_capability[capability].append(metadata.plugin_id)

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_id: Plugin to unregister

        Returns:
            True if unregistered, False if not found

        Notes:
        - Removes plugin from all indexes
        - Cannot unregister non-existent plugin
        """
        if plugin_id not in self._plugins:
            return False

        # Get registration before removing
        registration = self._registrations[plugin_id]
        metadata = registration.metadata

        # Remove from plugins
        del self._plugins[plugin_id]
        del self._registrations[plugin_id]

        # Remove from extension index
        ext_point = metadata.extension_point
        if ext_point in self._by_extension:
            self._by_extension[ext_point] = [
                p for p in self._by_extension[ext_point] if p != plugin_id
            ]
            if not self._by_extension[ext_point]:
                del self._by_extension[ext_point]

        # Remove from capability index
        for capability in metadata.supports:
            if capability in self._by_capability:
                self._by_capability[capability] = [
                    p for p in self._by_capability[capability] if p != plugin_id
                ]
                if not self._by_capability[capability]:
                    del self._by_capability[capability]

        return True

    def get(self, plugin_id: str) -> Optional[PluginProtocol]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginProtocol instance or None if not found

        Notes:
        - Returns plugin regardless of enabled/disabled state
        - Use is_enabled() to check if plugin is active
        """
        return self._plugins.get(plugin_id)

    def get_metadata(self, plugin_id: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginMetadata or None if not found
        """
        registration = self._registrations.get(plugin_id)
        return registration.metadata if registration else None

    def find_by_extension(self, extension_point: str) -> List[PluginProtocol]:
        """Find all plugins for an extension point.

        Args:
            extension_point: Extension point identifier

        Returns:
            List of enabled PluginProtocol instances

        Notes:
        - Returns only enabled plugins
        - Order not guaranteed
        - Returns empty list if no plugins found
        """
        plugin_ids = self._by_extension.get(extension_point, [])
        return [
            self._plugins[p]
            for p in plugin_ids
            if p in self._registrations and self._registrations[p].is_enabled
        ]

    def find_by_capability(
        self, capability: str, extension_point: Optional[str] = None
    ) -> List[PluginProtocol]:
        """Find plugins by capability, optionally filtered by extension point.

        Args:
            capability: Capability identifier
            extension_point: Optional extension point filter

        Returns:
            List of enabled PluginProtocol instances

        Notes:
        - Returns only enabled plugins
        - If extension_point specified, filters results
        - Returns empty list if no plugins found
        """
        plugin_ids = self._by_capability.get(capability, [])

        result = [
            self._plugins[p]
            for p in plugin_ids
            if p in self._registrations and self._registrations[p].is_enabled
        ]

        if extension_point:
            result = [
                p
                for p in result
                if self._registrations[self._plugins[p].get_plugin_id()].metadata.extension_point
                == extension_point
            ]

        return result

    def enable(self, plugin_id: str) -> bool:
        """Enable a plugin.

        Args:
            plugin_id: Plugin to enable

        Returns:
            True if enabled, False if not found

        Notes:
        - Plugin must be registered
        - Can be called multiple times (idempotent)
        """
        if plugin_id not in self._registrations:
            return False

        self._registrations[plugin_id].is_enabled = True
        return True

    def disable(self, plugin_id: str) -> bool:
        """Disable a plugin.

        Args:
            plugin_id: Plugin to disable

        Returns:
            True if disabled, False if not found

        Notes:
        - Plugin must be registered
        - Can be called multiple times (idempotent)
        - Disabled plugins remain registered but not discovered
        """
        if plugin_id not in self._registrations:
            return False

        self._registrations[plugin_id].is_enabled = False
        return True

    def is_enabled(self, plugin_id: str) -> bool:
        """Check if plugin is enabled.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if enabled, False if disabled or not found
        """
        registration = self._registrations.get(plugin_id)
        return registration.is_enabled if registration else False

    def list_all(self) -> List[PluginMetadata]:
        """List all registered plugins.

        Returns:
            List of PluginMetadata for all registered plugins

        Notes:
        - Includes both enabled and disabled plugins
        - Order not guaranteed
        """
        return [registration.metadata for registration in self._registrations.values()]

    def list_enabled(self) -> List[PluginMetadata]:
        """List all enabled plugins.

        Returns:
            List of PluginMetadata for enabled plugins only
        """
        return [
            registration.metadata
            for registration in self._registrations.values()
            if registration.is_enabled
        ]

    def get_registration(self, plugin_id: str) -> Optional[PluginRegistration]:
        """Get registration details for a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginRegistration or None if not found

        Notes:
        - For introspection/monitoring only
        - Do not modify returned object
        """
        return self._registrations.get(plugin_id)

    def statistics(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dict with registry information

        Notes:
        - Useful for monitoring and debugging
        - Statistics computed on-demand
        """
        enabled_count = sum(
            1 for reg in self._registrations.values() if reg.is_enabled
        )

        return {
            "total_plugins": len(self._plugins),
            "enabled_plugins": enabled_count,
            "disabled_plugins": len(self._plugins) - enabled_count,
            "extension_points": list(self._by_extension.keys()),
            "capabilities": list(self._by_capability.keys()),
            "plugins": {
                plugin_id: {
                    "name": registration.metadata.name,
                    "version": registration.metadata.version,
                    "extension_point": registration.metadata.extension_point,
                    "supports": registration.metadata.supports,
                    "enabled": registration.is_enabled,
                    "registered_at": registration.registered_at.isoformat(),
                }
                for plugin_id, registration in self._registrations.items()
            },
        }
