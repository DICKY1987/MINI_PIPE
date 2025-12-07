"""
Patch Converter - Convert Tool Outputs to Unified Diff Format
Standardizes patches from different tools (aider, custom tools)
"""

# DOC_ID: DOC-CORE-ENGINE-PATCH-CONVERTER-152

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict


@dataclass
class DiffStats:
    """Statistics about a patch/diff."""

    files_added: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    lines_added: int = 0
    lines_deleted: int = 0

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for JSON serialization."""
        return {
            "files_added": self.files_added,
            "files_modified": self.files_modified,
            "files_deleted": self.files_deleted,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
        }

    def __str__(self) -> str:
        """Human-readable summary."""
        file_count = self.files_added + self.files_modified + self.files_deleted
        return (
            f"[{file_count} files: "
            f"+{self.files_added} ~{self.files_modified} -{self.files_deleted}] "
            f"[+{self.lines_added} -{self.lines_deleted} lines]"
        )


@dataclass
class UnifiedPatch:
    """Unified patch format."""

    patch_id: str
    workstream_id: str
    content: str
    status: str
    created_at: str
    metadata: Dict[str, Any]
    diff_stats: DiffStats = field(default_factory=DiffStats)


class PatchConverter:
    """Convert tool-specific patches to unified diff format."""

    def __init__(self):
        self.patch_count = 0

    def convert_aider_patch(self, tool_result: Dict) -> UnifiedPatch:
        """Convert aider output to unified patch."""
        self.patch_count += 1
        patch_id = f"patch-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{self.patch_count:04d}"

        # Extract git diff from aider output
        content = tool_result.get("output", "")
        git_diff = self.extract_git_diff(content)

        # Compute diff stats
        diff_stats = self.compute_diff_stats(git_diff)

        return UnifiedPatch(
            patch_id=patch_id,
            workstream_id=tool_result.get("workstream_id", "unknown"),
            content=git_diff,
            status="created",
            created_at=datetime.now(UTC).isoformat(),
            metadata={"tool": "aider", "original_output_length": len(content)},
            diff_stats=diff_stats,
        )

    def convert_tool_patch(
        self, tool_id: str, output: str, workstream_id: str = "unknown"
    ) -> UnifiedPatch:
        """Convert generic tool output to unified patch."""
        self.patch_count += 1
        patch_id = f"patch-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}-{self.patch_count:04d}"

        git_diff = self.extract_git_diff(output)
        content = git_diff if git_diff else output

        # Compute diff stats
        diff_stats = self.compute_diff_stats(content)

        return UnifiedPatch(
            patch_id=patch_id,
            workstream_id=workstream_id,
            content=content,
            status="created",
            created_at=datetime.now(UTC).isoformat(),
            metadata={"tool": tool_id, "has_git_diff": bool(git_diff)},
            diff_stats=diff_stats,
        )

    def extract_git_diff(self, output: str) -> str:
        """Extract git diff from tool output."""
        # Look for git diff markers
        diff_pattern = r"diff --git.*?(?=diff --git|\Z)"
        matches = re.findall(diff_pattern, output, re.DOTALL)

        if matches:
            return "\n".join(matches)

        # Fallback: look for unified diff format
        unified_pattern = r"---.*?\n\+\+\+.*?(?=---|\Z)"
        matches = re.findall(unified_pattern, output, re.DOTALL)

        if matches:
            return "\n".join(matches)

        return ""

    def validate_unified_diff(self, diff: str) -> bool:
        """Validate that string is a valid unified diff."""
        if not diff:
            return False

        # Check for diff markers
        has_header = "---" in diff and "+++" in diff
        has_hunks = "@@" in diff

        return has_header or has_hunks

    def compute_diff_stats(self, patch_content: str) -> DiffStats:
        """
        Compute statistics from a unified diff patch.

        Parses the patch to count files and lines added/modified/deleted.

        Args:
            patch_content: Unified diff patch content

        Returns:
            DiffStats object with computed statistics
        """
        stats = DiffStats()

        if not patch_content:
            return stats

        current_file_old = None
        current_file_new = None

        for line in patch_content.splitlines():
            # Track file changes
            if line.startswith("--- "):
                current_file_old = line[4:].strip()
            elif line.startswith("+++ "):
                current_file_new = line[4:].strip()

                # Determine file status
                if current_file_old and current_file_new:
                    if current_file_old == "/dev/null":
                        stats.files_added += 1
                    elif current_file_new == "/dev/null":
                        stats.files_deleted += 1
                    else:
                        stats.files_modified += 1

            # Count line changes (skip file headers and hunk headers)
            elif line.startswith("+") and not line.startswith("+++"):
                stats.lines_added += 1
            elif line.startswith("-") and not line.startswith("---"):
                stats.lines_deleted += 1

        return stats
