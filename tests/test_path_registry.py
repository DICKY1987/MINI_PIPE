"""
Unit Tests for Path Registry

Tests for contracts/path_registry.py
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.acms.path_registry import PathRegistry, resolve_path, get_path_registry


class TestPathRegistry:
    """Tests for PathRegistry class"""

    def test_resolve_simple_path(self, tmp_path):
        """Test resolving a simple path key."""
        # Create a test path index
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"test": {"file": "test.txt"}}

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        result = registry.resolve_path("test.file")

        assert result == tmp_path / "test.txt"

    def test_resolve_nested_path(self, tmp_path):
        """Test resolving a deeply nested path key."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {
            "acms": {"docs": {"specs": {"controller": "docs/specs/controller.md"}}}
        }

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        result = registry.resolve_path("acms.docs.specs.controller")

        assert result == tmp_path / "docs" / "specs" / "controller.md"

    def test_resolve_with_template_vars(self, tmp_path):
        """Test resolving paths with template variables."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"runs": {"dir": ".runs/{run_id}/output"}}

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        result = registry.resolve_path("runs.dir", run_id="run-001")

        assert result == tmp_path / ".runs" / "run-001" / "output"

    def test_missing_key_raises_error(self, tmp_path):
        """Test that missing key raises KeyError."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"test": {"file": "test.txt"}}

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))

        with pytest.raises(KeyError, match="Path key not found"):
            registry.resolve_path("nonexistent.key")

    def test_resolve_str(self, tmp_path):
        """Test resolve_str returns string."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"test": {"file": "test.txt"}}

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        result = registry.resolve_str("test.file")

        assert isinstance(result, str)
        assert result == str(tmp_path / "test.txt")

    def test_ensure_dir_creates_directory(self, tmp_path):
        """Test ensure_dir creates directory if it doesn't exist."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"test": {"dir": "output/logs"}}

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        result = registry.ensure_dir("test.dir")

        assert result.exists()
        assert result.is_dir()
        assert result == tmp_path / "output" / "logs"

    def test_list_keys(self, tmp_path):
        """Test list_keys returns all path keys."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {
            "acms": {"docs": "docs/acms.md", "config": "config/acms.yaml"},
            "mini_pipe": {"docs": "docs/mini_pipe.md"},
        }

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        keys = registry.list_keys()

        assert "acms.docs" in keys
        assert "acms.config" in keys
        assert "mini_pipe.docs" in keys

    def test_list_keys_with_prefix(self, tmp_path):
        """Test list_keys with prefix filter."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {
            "acms": {"docs": "docs/acms.md", "config": "config/acms.yaml"},
            "mini_pipe": {"docs": "docs/mini_pipe.md"},
        }

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))
        keys = registry.list_keys("acms")

        assert "acms.docs" in keys
        assert "acms.config" in keys
        assert "mini_pipe.docs" not in keys

    def test_non_string_value_raises_error(self, tmp_path):
        """Test that non-string path value raises error."""
        index_file = tmp_path / "config" / "path_index.yaml"
        index_file.parent.mkdir(parents=True)

        index_data = {"test": {"invalid": {"nested": "dict"}}}  # Not a string

        with open(index_file, "w") as f:
            yaml.dump(index_data, f)

        registry = PathRegistry(str(index_file))

        with pytest.raises(ValueError, match="does not resolve to a string"):
            registry.resolve_path("test.invalid")


class TestGlobalHelpers:
    """Tests for global helper functions"""

    def test_get_path_registry_singleton(self):
        """Test that get_path_registry returns singleton."""
        registry1 = get_path_registry()
        registry2 = get_path_registry()

        assert registry1 is registry2

    def test_resolve_path_global(self):
        """Test global resolve_path function."""
        # This test assumes config/path_index.yaml exists
        try:
            result = resolve_path("acms.docs.controller_spec")
            assert isinstance(result, Path)
        except (FileNotFoundError, KeyError):
            pytest.skip("Path index not configured")


class TestPathIndexIntegration:
    """Integration tests with actual path_index.yaml"""

    def test_acms_paths_exist(self):
        """Test that ACMS paths are defined."""
        try:
            registry = get_path_registry()
            keys = registry.list_keys("acms")

            # Should have at least docs, schemas, modules, runtime
            assert any("acms.docs" in k for k in keys)
            assert any("acms.schemas" in k for k in keys)
        except FileNotFoundError:
            pytest.skip("Path index not configured")

    def test_mini_pipe_paths_exist(self):
        """Test that MINI_PIPE paths are defined."""
        try:
            registry = get_path_registry()
            keys = registry.list_keys("mini_pipe")

            # Should have at least docs, modules, runtime
            assert any("mini_pipe.docs" in k for k in keys)
            assert any("mini_pipe.modules" in k for k in keys)
        except FileNotFoundError:
            pytest.skip("Path index not configured")

    def test_runtime_path_templates(self):
        """Test that runtime paths support template substitution."""
        try:
            result = resolve_path("workstreams.runtime.plans_dir", run_id="test-001")

            # Should contain the run_id
            assert "test-001" in str(result)
        except (FileNotFoundError, KeyError):
            pytest.skip("Path index not configured")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
