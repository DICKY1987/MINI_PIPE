"""
Path Registry - Indirection layer for important paths.

Provides resolve_path() for all ACMS/MINI_PIPE modules.
No hardcoded important paths allowed - use path keys instead.

Reference: UET_PATH_ABSTRACTION_LAYER.md
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class PathRegistry:
    """
    Path indirection layer.
    Maps logical path keys to physical paths.
    """

    def __init__(self, index_file: str = "config/path_index.yaml"):
        self.index_file = Path(index_file)
        self._index: Dict[str, Any] = {}
        self._repo_root: Optional[Path] = None
        self._load_index()

    def _load_index(self):
        """Load path index from YAML."""
        if not self.index_file.exists():
            raise FileNotFoundError(
                f"Path index not found: {self.index_file}\n"
                f"Create it using the template from UET_PATH_ABSTRACTION_LAYER.md"
            )

        with open(self.index_file, "r", encoding="utf-8") as f:
            self._index = yaml.safe_load(f)

        # Determine repo root (parent of config dir)
        self._repo_root = self.index_file.parent.parent

    def resolve_path(self, key: str, **kwargs) -> Path:
        """
        Resolve a path key to an absolute path.

        Args:
            key: Dot-separated path key (e.g., "acms.docs.controller_spec")
            **kwargs: Template variables for runtime paths (e.g., run_id)

        Returns:
            Absolute Path object

        Raises:
            KeyError: If path key not found in index

        Examples:
            >>> registry.resolve_path("acms.docs.controller_spec")
            Path("C:/Users/richg/ALL_AI/MINI_PIPE/docs/specs/ACMS_CONTROLLER_SPEC.md")

            >>> registry.resolve_path("workstreams.runtime.plans_dir", run_id="run-001")
            Path("C:/Users/richg/ALL_AI/MINI_PIPE/.acms_runs/run-001/workstreams")
        """
        # Navigate nested dict using dot notation
        parts = key.split(".")
        value = self._index

        try:
            for part in parts:
                value = value[part]
        except (KeyError, TypeError) as e:
            raise KeyError(
                f"Path key not found: '{key}'\n"
                f"Available top-level keys: {', '.join(self._index.keys())}"
            ) from e

        if not isinstance(value, str):
            raise ValueError(
                f"Path key '{key}' does not resolve to a string path.\n"
                f"Got: {type(value).__name__}"
            )

        # Apply template substitutions
        path_template = value
        if kwargs:
            path_template = path_template.format(**kwargs)

        # Make absolute relative to repo root
        resolved = self._repo_root / path_template
        return resolved

    def resolve_str(self, key: str, **kwargs) -> str:
        """Resolve path key to string (for compatibility)."""
        return str(self.resolve_path(key, **kwargs))

    def ensure_dir(self, key: str, **kwargs) -> Path:
        """Resolve path key and ensure directory exists."""
        path = self.resolve_path(key, **kwargs)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def list_keys(self, prefix: str = "") -> list[str]:
        """
        List all available path keys.

        Args:
            prefix: Optional prefix filter (e.g., "acms" to see only ACMS paths)

        Returns:
            List of dot-separated path keys
        """
        keys = []

        def traverse(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{path}.{k}" if path else k
                    if isinstance(v, str):
                        keys.append(new_path)
                    else:
                        traverse(v, new_path)

        traverse(self._index)

        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]

        return sorted(keys)


# Singleton instance for global access
_registry: Optional[PathRegistry] = None


def get_path_registry() -> PathRegistry:
    """Get or create the global PathRegistry instance."""
    global _registry
    if _registry is None:
        _registry = PathRegistry()
    return _registry


def resolve_path(key: str, **kwargs) -> Path:
    """
    Global convenience function to resolve paths.

    Usage:
        from contracts.path_registry import resolve_path

        spec_path = resolve_path("acms.docs.controller_spec")
        ws_dir = resolve_path("workstreams.runtime.plans_dir", run_id="run-001")
    """
    return get_path_registry().resolve_path(key, **kwargs)


def resolve_str(key: str, **kwargs) -> str:
    """Resolve path key to string."""
    return str(resolve_path(key, **kwargs))


def ensure_dir(key: str, **kwargs) -> Path:
    """Resolve path key and ensure directory exists."""
    return get_path_registry().ensure_dir(key, **kwargs)


# CLI interface for path resolution
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python path_registry.py <path_key> [key=value ...]")
        print("\nExamples:")
        print("  python path_registry.py acms.docs.controller_spec")
        print("  python path_registry.py workstreams.runtime.plans_dir run_id=run-001")
        print("\nAvailable keys:")
        registry = get_path_registry()
        for key in registry.list_keys():
            print(f"  {key}")
        sys.exit(1)

    key = sys.argv[1]
    kwargs = {}

    # Parse key=value arguments
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v

    try:
        result = resolve_path(key, **kwargs)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
