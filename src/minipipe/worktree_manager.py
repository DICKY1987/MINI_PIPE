"""
Worktree Manager - Git worktree isolation for parallel task execution

Provides isolated git worktrees per run/step to prevent file conflicts during
concurrent execution. Supports cleanup, archiving, and branch validation.
"""

# DOC_ID: DOC-CORE-ENGINE-WORKTREE-MANAGER-200

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

# Optional event bus integration
try:
    from core.events.event_bus import EventBus, EventSeverity, EventType
    EVENT_BUS_AVAILABLE = True
except ImportError:
    EVENT_BUS_AVAILABLE = False
    EventBus = None
    EventSeverity = None
    EventType = None


@dataclass
class WorktreeInfo:
    """Information about a git worktree."""

    path: Path
    branch: str
    commit_hash: str
    is_locked: bool
    run_id: str
    step_id: Optional[str] = None


class WorktreeManagerError(Exception):
    """Base exception for worktree manager errors."""

    pass


class WorktreeManager:
    """Manages git worktrees for isolated task execution."""

    def __init__(
        self,
        repo_root: Path,
        event_bus: Optional[EventBus] = None,
        worktrees_subdir: str = ".minipipe_worktrees",
    ):
        """
        Initialize WorktreeManager.

        Args:
            repo_root: Path to the git repository root
            event_bus: Optional event bus for emitting events
            worktrees_subdir: Subdirectory name for worktrees (default: .minipipe_worktrees)
        """
        self.repo_root = Path(repo_root).resolve()
        self.worktrees_dir = self.repo_root / worktrees_subdir
        self.event_bus = event_bus

        # Validate that repo_root is a git repository
        if not (self.repo_root / ".git").exists():
            raise WorktreeManagerError(
                f"Not a git repository: {self.repo_root}"
            )

        # Create worktrees directory if it doesn't exist
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

        # Add to .gitignore if not already present
        self._ensure_gitignore()

    def _ensure_gitignore(self) -> None:
        """Ensure worktrees directory is in .gitignore."""
        gitignore_path = self.repo_root / ".gitignore"
        ignore_pattern = f"{self.worktrees_dir.name}/"

        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            if ignore_pattern not in content:
                with gitignore_path.open("a", encoding="utf-8") as f:
                    f.write(f"\n# MINI_PIPE worktrees\n{ignore_pattern}\n")
        else:
            gitignore_path.write_text(
                f"# MINI_PIPE worktrees\n{ignore_pattern}\n", encoding="utf-8"
            )

    def _run_git_command(
        self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a git command and return the result."""
        full_cmd = ["git"] + cmd
        result = subprocess.run(
            full_cmd,
            cwd=cwd or self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )

        if check and result.returncode != 0:
            raise WorktreeManagerError(
                f"Git command failed: {' '.join(full_cmd)}\n"
                f"Error: {result.stderr}"
            )

        return result

    def create_worktree(
        self,
        run_id: str,
        step_id: Optional[str] = None,
        branch_name: Optional[str] = None,
        base_ref: str = "HEAD",
    ) -> Path:
        """
        Create a new git worktree for isolated execution.

        Args:
            run_id: Unique run identifier
            step_id: Optional step identifier (for step-level isolation)
            branch_name: Optional custom branch name (default: auto-generated)
            base_ref: Git ref to branch from (default: HEAD)

        Returns:
            Path to the created worktree

        Raises:
            WorktreeManagerError: If worktree creation fails
        """
        # Generate worktree path and branch name
        worktree_name = f"{run_id}" + (f"_{step_id}" if step_id else "")
        worktree_path = self.worktrees_dir / worktree_name

        if not branch_name:
            timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
            branch_name = f"minipipe/{run_id}/{timestamp}"

        # Check if worktree already exists
        if worktree_path.exists():
            if EVENT_BUS_AVAILABLE:
                self._emit_event(
                    EventType.WARNING,
                    f"Worktree already exists: {worktree_path}",
                    {"run_id": run_id, "step_id": step_id},
                )
            return worktree_path

        # Check if branch already exists
        if self._branch_exists(branch_name):
            # Use existing branch
            self._run_git_command(
                ["worktree", "add", str(worktree_path), branch_name]
            )
        else:
            # Create new branch
            self._run_git_command(
                ["worktree", "add", "-b", branch_name, str(worktree_path), base_ref]
            )

        if EVENT_BUS_AVAILABLE:
            self._emit_event(
                EventType.INFO,
                f"Created worktree: {worktree_path.name} on branch {branch_name}",
                {
                    "run_id": run_id,
                    "step_id": step_id,
                    "worktree_path": str(worktree_path),
                    "branch": branch_name,
                },
            )

        return worktree_path

    def cleanup_worktree(
        self,
        worktree_path: Path,
        archive_on_failure: bool = False,
        force: bool = False,
    ) -> bool:
        """
        Remove a worktree and optionally archive it.

        Args:
            worktree_path: Path to the worktree
            archive_on_failure: If True, archive the worktree instead of deleting
            force: Force removal even if worktree has uncommitted changes

        Returns:
            True if cleanup succeeded, False otherwise
        """
        worktree_path = Path(worktree_path).resolve()

        if not worktree_path.exists():
            if EVENT_BUS_AVAILABLE:
                self._emit_event(
                    EventType.WARNING,
                    f"Worktree does not exist: {worktree_path}",
                    {"worktree_path": str(worktree_path)},
                )
            return False

        try:
            if archive_on_failure:
                archive_path = self._archive_worktree(worktree_path)
                if EVENT_BUS_AVAILABLE:
                    self._emit_event(
                        EventType.INFO,
                        f"Archived worktree to: {archive_path}",
                        {"worktree_path": str(worktree_path), "archive_path": archive_path},
                    )

            # Remove worktree
            cmd = ["worktree", "remove", str(worktree_path)]
            if force:
                cmd.append("--force")

            self._run_git_command(cmd)

            if EVENT_BUS_AVAILABLE:
                self._emit_event(
                    EventType.INFO,
                    f"Removed worktree: {worktree_path.name}",
                    {"worktree_path": str(worktree_path)},
                )

            return True

        except WorktreeManagerError as e:
            if EVENT_BUS_AVAILABLE:
                self._emit_event(
                    EventType.ERROR,
                    f"Failed to cleanup worktree: {e}",
                    {"worktree_path": str(worktree_path), "error": str(e)},
                )
            return False

    def _archive_worktree(self, worktree_path: Path) -> str:
        """Archive a worktree for debugging."""
        archives_dir = self.repo_root / ".minipipe_worktree_archives"
        archives_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        archive_name = f"{worktree_path.name}_{timestamp}"
        archive_path = archives_dir / archive_name

        shutil.copytree(worktree_path, archive_path)
        return str(archive_path)

    def list_worktrees(self) -> List[WorktreeInfo]:
        """
        List all active worktrees.

        Returns:
            List of WorktreeInfo objects
        """
        result = self._run_git_command(["worktree", "list", "--porcelain"])
        return self._parse_worktree_list(result.stdout)

    def _parse_worktree_list(self, output: str) -> List[WorktreeInfo]:
        """Parse git worktree list --porcelain output."""
        worktrees = []
        current_worktree = {}

        for line in output.strip().split("\n"):
            if not line:
                if current_worktree:
                    # Try to extract run_id and step_id from path
                    path = Path(current_worktree.get("worktree", ""))
                    parts = path.name.split("_")
                    run_id = parts[0] if parts else "unknown"
                    step_id = parts[1] if len(parts) > 1 else None

                    worktrees.append(
                        WorktreeInfo(
                            path=path,
                            branch=current_worktree.get("branch", ""),
                            commit_hash=current_worktree.get("HEAD", ""),
                            is_locked=current_worktree.get("locked", False),
                            run_id=run_id,
                            step_id=step_id,
                        )
                    )
                    current_worktree = {}
                continue

            if line.startswith("worktree "):
                current_worktree["worktree"] = line.split(" ", 1)[1]
            elif line.startswith("HEAD "):
                current_worktree["HEAD"] = line.split(" ", 1)[1]
            elif line.startswith("branch "):
                current_worktree["branch"] = line.split(" ", 1)[1]
            elif line.startswith("locked"):
                current_worktree["locked"] = True

        # Handle last worktree if output doesn't end with blank line
        if current_worktree:
            path = Path(current_worktree.get("worktree", ""))
            parts = path.name.split("_")
            run_id = parts[0] if parts else "unknown"
            step_id = parts[1] if len(parts) > 1 else None

            worktrees.append(
                WorktreeInfo(
                    path=path,
                    branch=current_worktree.get("branch", ""),
                    commit_hash=current_worktree.get("HEAD", ""),
                    is_locked=current_worktree.get("locked", False),
                    run_id=run_id,
                    step_id=step_id,
                )
            )

        return worktrees

    def is_branch_checked_out(self, branch_name: str) -> bool:
        """
        Check if a branch is currently checked out in any worktree.

        Args:
            branch_name: Name of the branch to check (with or without refs/heads/ prefix)

        Returns:
            True if branch is checked out, False otherwise
        """
        worktrees = self.list_worktrees()
        # Normalize branch names for comparison (strip refs/heads/ prefix)
        normalized_target = branch_name.replace("refs/heads/", "")
        return any(
            wt.branch.replace("refs/heads/", "") == normalized_target
            for wt in worktrees
        )

    def _branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists."""
        result = self._run_git_command(
            ["show-ref", "--verify", f"refs/heads/{branch_name}"],
            check=False,
        )
        return result.returncode == 0

    def prune_worktrees(self) -> int:
        """
        Prune stale worktree administrative files.

        Returns:
            Number of worktrees pruned
        """
        result = self._run_git_command(["worktree", "prune", "--verbose"])
        # Count pruned worktrees from output
        pruned_count = result.stdout.count("Removing worktrees/")

        if pruned_count > 0 and EVENT_BUS_AVAILABLE:
            self._emit_event(
                EventType.INFO,
                f"Pruned {pruned_count} stale worktree(s)",
                {"count": pruned_count},
            )

        return pruned_count

    def get_worktree_stats(self) -> Dict[str, int]:
        """Get statistics about active worktrees."""
        worktrees = self.list_worktrees()
        minipipe_worktrees = [
            wt for wt in worktrees if str(wt.path).startswith(str(self.worktrees_dir))
        ]

        return {
            "total_worktrees": len(worktrees),
            "minipipe_worktrees": len(minipipe_worktrees),
            "locked_worktrees": sum(1 for wt in minipipe_worktrees if wt.is_locked),
        }

    def _emit_event(
        self, event_type, message: str, metadata: Dict = None
    ) -> None:
        """Emit an event to the event bus if available."""
        if self.event_bus and EVENT_BUS_AVAILABLE:
            severity = (
                EventSeverity.ERROR
                if event_type == EventType.ERROR
                else (
                    EventSeverity.WARNING
                    if event_type == EventType.WARNING
                    else EventSeverity.INFO
                )
            )
            self.event_bus.publish(
                event_type=event_type,
                severity=severity,
                message=message,
                component="WorktreeManager",
                metadata=metadata or {},
            )


__all__ = ["WorktreeManager", "WorktreeInfo", "WorktreeManagerError"]
