"""
Tests for DiffStats functionality in PatchConverter
"""

import pytest

from src.minipipe.patch_converter import DiffStats, PatchConverter, UnifiedPatch


class TestDiffStats:
    """Tests for DiffStats dataclass."""

    def test_diff_stats_defaults(self):
        """Test DiffStats with default values."""
        stats = DiffStats()

        assert stats.files_added == 0
        assert stats.files_modified == 0
        assert stats.files_deleted == 0
        assert stats.lines_added == 0
        assert stats.lines_deleted == 0

    def test_diff_stats_to_dict(self):
        """Test DiffStats to_dict conversion."""
        stats = DiffStats(
            files_added=2,
            files_modified=3,
            files_deleted=1,
            lines_added=50,
            lines_deleted=20,
        )

        result = stats.to_dict()

        assert result == {
            "files_added": 2,
            "files_modified": 3,
            "files_deleted": 1,
            "lines_added": 50,
            "lines_deleted": 20,
        }

    def test_diff_stats_str(self):
        """Test DiffStats string representation."""
        stats = DiffStats(
            files_added=1, files_modified=2, files_deleted=1, lines_added=30, lines_deleted=10
        )

        result = str(stats)

        assert "4 files" in result  # 1 + 2 + 1
        assert "+1" in result  # files added
        assert "~2" in result  # files modified
        assert "-1" in result  # files deleted
        assert "+30" in result  # lines added
        assert "-10" in result  # lines deleted


class TestComputeDiffStats:
    """Tests for compute_diff_stats method."""

    def test_compute_diff_stats_empty(self):
        """Test computing stats from empty patch."""
        converter = PatchConverter()

        stats = converter.compute_diff_stats("")

        assert stats.files_added == 0
        assert stats.files_modified == 0
        assert stats.files_deleted == 0
        assert stats.lines_added == 0
        assert stats.lines_deleted == 0

    def test_compute_diff_stats_new_file(self):
        """Test computing stats for a new file."""
        patch = """
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,5 @@
+def hello():
+    print("Hello, World!")
+
+if __name__ == "__main__":
+    hello()
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.files_added == 1
        assert stats.files_modified == 0
        assert stats.files_deleted == 0
        assert stats.lines_added == 5
        assert stats.lines_deleted == 0

    def test_compute_diff_stats_deleted_file(self):
        """Test computing stats for a deleted file."""
        patch = """
--- a/old_file.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def old_function():
-    pass
-
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.files_added == 0
        assert stats.files_modified == 0
        assert stats.files_deleted == 1
        assert stats.lines_added == 0
        assert stats.lines_deleted == 3

    def test_compute_diff_stats_modified_file(self):
        """Test computing stats for a modified file."""
        patch = """
--- a/existing_file.py
+++ b/existing_file.py
@@ -1,5 +1,6 @@
 def existing_function():
-    old_line = 1
+    new_line = 2
+    another_new_line = 3
     print("Hello")
     return True
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.files_added == 0
        assert stats.files_modified == 1
        assert stats.files_deleted == 0
        assert stats.lines_added == 2
        assert stats.lines_deleted == 1

    def test_compute_diff_stats_multiple_files(self):
        """Test computing stats for multiple files."""
        patch = """
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
+def new():
+    pass
+
--- a/modified.py
+++ b/modified.py
@@ -1,2 +1,3 @@
 existing_line
-removed_line
+added_line
+another_added_line
--- a/deleted.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def deleted():
-    pass
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.files_added == 1
        assert stats.files_modified == 1
        assert stats.files_deleted == 1
        assert stats.lines_added == 5  # 3 + 2
        assert stats.lines_deleted == 3  # 1 + 2

    def test_compute_diff_stats_ignores_file_headers(self):
        """Test that file headers (---/+++) are not counted as line changes."""
        patch = """
--- a/file.py
+++ b/file.py
@@ -1,1 +1,1 @@
-old
+new
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        # Should count only the -old and +new lines, not --- and +++
        assert stats.lines_added == 1
        assert stats.lines_deleted == 1


class TestUnifiedPatchWithDiffStats:
    """Tests for UnifiedPatch with diff_stats field."""

    def test_unified_patch_has_diff_stats(self):
        """Test that UnifiedPatch includes diff_stats."""
        converter = PatchConverter()

        patch = converter.convert_tool_patch(
            tool_id="test-tool",
            output="""
--- /dev/null
+++ b/new.py
@@ -0,0 +1,2 @@
+line1
+line2
""",
            workstream_id="test-ws",
        )

        assert hasattr(patch, "diff_stats")
        assert isinstance(patch.diff_stats, DiffStats)
        assert patch.diff_stats.files_added == 1
        assert patch.diff_stats.lines_added == 2

    def test_convert_aider_patch_computes_stats(self):
        """Test that convert_aider_patch computes diff stats."""
        converter = PatchConverter()

        tool_result = {
            "output": """
diff --git a/test.py b/test.py
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 existing
-removed
+added
+another_added
""",
            "workstream_id": "test-ws",
        }

        patch = converter.convert_aider_patch(tool_result)

        assert patch.diff_stats.files_modified == 1
        assert patch.diff_stats.lines_added == 2
        assert patch.diff_stats.lines_deleted == 1

    def test_convert_tool_patch_computes_stats(self):
        """Test that convert_tool_patch computes diff stats."""
        converter = PatchConverter()

        output = """
--- a/modified.py
+++ b/modified.py
@@ -1,1 +1,2 @@
 existing
+added
"""

        patch = converter.convert_tool_patch(
            tool_id="custom-tool", output=output, workstream_id="test-ws"
        )

        assert patch.diff_stats.files_modified == 1
        assert patch.diff_stats.lines_added == 1
        assert patch.diff_stats.lines_deleted == 0


class TestDiffStatsEdgeCases:
    """Tests for edge cases in diff stats computation."""

    def test_diff_stats_no_changes(self):
        """Test patch with no actual changes."""
        patch = """
--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
 line1
 line2
 line3
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.files_modified == 1
        assert stats.lines_added == 0
        assert stats.lines_deleted == 0

    def test_diff_stats_malformed_patch(self):
        """Test handling of malformed patch."""
        patch = "not a valid patch format"
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        # Should return empty stats without crashing
        assert stats.files_added == 0
        assert stats.files_modified == 0
        assert stats.files_deleted == 0

    def test_diff_stats_context_only(self):
        """Test patch with only context lines."""
        patch = """
--- a/file.py
+++ b/file.py
@@ -1,3 +1,3 @@
 context1
 context2
 context3
"""
        converter = PatchConverter()

        stats = converter.compute_diff_stats(patch)

        assert stats.lines_added == 0
        assert stats.lines_deleted == 0
