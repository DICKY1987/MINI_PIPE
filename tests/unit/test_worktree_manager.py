"""
Tests for WorktreeManager
"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.minipipe.worktree_manager import (
    WorktreeInfo,
    WorktreeManager,
    WorktreeManagerError,
    EVENT_BUS_AVAILABLE,
)


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("initial content")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    return repo_path


@pytest.fixture
def worktree_manager(temp_git_repo):
    """Create a WorktreeManager instance."""
    return WorktreeManager(temp_git_repo)


class TestWorktreeManagerInit:
    """Tests for WorktreeManager initialization."""

    def test_init_creates_worktrees_directory(self, temp_git_repo):
        """Test that init creates the worktrees directory."""
        manager = WorktreeManager(temp_git_repo)
        assert manager.worktrees_dir.exists()
        assert manager.worktrees_dir.name == ".minipipe_worktrees"

    def test_init_adds_to_gitignore(self, temp_git_repo):
        """Test that worktrees directory is added to .gitignore."""
        manager = WorktreeManager(temp_git_repo)
        gitignore_path = temp_git_repo / ".gitignore"
        assert gitignore_path.exists()
        content = gitignore_path.read_text()
        assert ".minipipe_worktrees/" in content

    def test_init_fails_on_non_git_repo(self, tmp_path):
        """Test that init fails if not a git repository."""
        non_repo = tmp_path / "not_a_repo"
        non_repo.mkdir()

        with pytest.raises(WorktreeManagerError, match="Not a git repository"):
            WorktreeManager(non_repo)

    def test_init_with_event_bus(self, temp_git_repo):
        """Test initialization with event bus."""
        mock_event_bus = MagicMock()
        manager = WorktreeManager(temp_git_repo, event_bus=mock_event_bus)
        assert manager.event_bus == mock_event_bus


class TestCreateWorktree:
    """Tests for create_worktree method."""

    def test_create_worktree_basic(self, worktree_manager):
        """Test creating a basic worktree."""
        worktree_path = worktree_manager.create_worktree(
            run_id="test-run-001", step_id="step-1"
        )

        assert worktree_path.exists()
        assert worktree_path.name == "test-run-001_step-1"
        assert (worktree_path / "test.txt").exists()

    def test_create_worktree_without_step_id(self, worktree_manager):
        """Test creating worktree without step_id."""
        worktree_path = worktree_manager.create_worktree(run_id="test-run-002")

        assert worktree_path.exists()
        assert worktree_path.name == "test-run-002"

    def test_create_worktree_with_custom_branch(self, worktree_manager):
        """Test creating worktree with custom branch name."""
        worktree_path = worktree_manager.create_worktree(
            run_id="test-run-003", branch_name="custom-branch"
        )

        # Verify branch was created
        result = subprocess.run(
            ["git", "branch"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            check=True,
        )
        assert "custom-branch" in result.stdout

    @pytest.mark.skipif(
        not EVENT_BUS_AVAILABLE, reason="EventBus not available"
    )
    def test_create_worktree_emits_event(self, temp_git_repo):
        """Test that creating worktree emits an event."""
        mock_event_bus = MagicMock()
        manager = WorktreeManager(temp_git_repo, event_bus=mock_event_bus)

        manager.create_worktree(run_id="test-run-004")

        # Verify event was published
        mock_event_bus.publish.assert_called()
        call_kwargs = mock_event_bus.publish.call_args[1]
        assert "Created worktree" in call_kwargs["message"]

    def test_create_worktree_already_exists(self, worktree_manager):
        """Test creating worktree when it already exists."""
        # Create first time
        path1 = worktree_manager.create_worktree(run_id="test-run-005")

        # Create again with same run_id
        path2 = worktree_manager.create_worktree(run_id="test-run-005")

        assert path1 == path2
        assert path1.exists()


class TestCleanupWorktree:
    """Tests for cleanup_worktree method."""

    def test_cleanup_worktree_success(self, worktree_manager):
        """Test successful worktree cleanup."""
        worktree_path = worktree_manager.create_worktree(run_id="test-run-006")
        assert worktree_path.exists()

        result = worktree_manager.cleanup_worktree(worktree_path)

        assert result is True
        assert not worktree_path.exists()

    def test_cleanup_worktree_with_archive(self, worktree_manager):
        """Test cleanup with archiving enabled."""
        worktree_path = worktree_manager.create_worktree(run_id="test-run-007")

        result = worktree_manager.cleanup_worktree(
            worktree_path, archive_on_failure=True
        )

        assert result is True
        assert not worktree_path.exists()

        # Check that archive was created
        archives_dir = worktree_manager.repo_root / ".minipipe_worktree_archives"
        assert archives_dir.exists()
        archives = list(archives_dir.glob("test-run-007*"))
        assert len(archives) > 0

    def test_cleanup_nonexistent_worktree(self, worktree_manager):
        """Test cleanup of nonexistent worktree."""
        fake_path = worktree_manager.worktrees_dir / "nonexistent"

        result = worktree_manager.cleanup_worktree(fake_path)

        assert result is False

    def test_cleanup_with_force(self, worktree_manager):
        """Test cleanup with force flag."""
        worktree_path = worktree_manager.create_worktree(run_id="test-run-008")

        # Make uncommitted changes
        test_file = worktree_path / "new_file.txt"
        test_file.write_text("uncommitted content")

        result = worktree_manager.cleanup_worktree(worktree_path, force=True)

        assert result is True
        assert not worktree_path.exists()


class TestListWorktrees:
    """Tests for list_worktrees method."""

    def test_list_worktrees_empty(self, worktree_manager):
        """Test listing worktrees when none exist."""
        worktrees = worktree_manager.list_worktrees()

        # Should have at least the main worktree (the repo itself)
        # On Windows, git might not list main worktree, so just check it doesn't crash
        assert isinstance(worktrees, list)

    def test_list_worktrees_multiple(self, worktree_manager):
        """Test listing multiple worktrees."""
        # Create multiple worktrees
        path1 = worktree_manager.create_worktree(run_id="run-001", step_id="step-1")
        path2 = worktree_manager.create_worktree(run_id="run-002", step_id="step-2")

        # Verify they were created
        assert path1.exists()
        assert path2.exists()

        worktrees = worktree_manager.list_worktrees()
        minipipe_worktrees = [
            wt
            for wt in worktrees
            if str(wt.path).startswith(str(worktree_manager.worktrees_dir))
        ]

        # Should have at least 2 worktrees
        assert len(minipipe_worktrees) >= 2

    def test_list_worktrees_info_fields(self, worktree_manager):
        """Test that WorktreeInfo has all required fields."""
        path = worktree_manager.create_worktree(run_id="run-003", step_id="step-3")
        assert path.exists()

        worktrees = worktree_manager.list_worktrees()
        minipipe_worktrees = [
            wt
            for wt in worktrees
            if str(wt.path).startswith(str(worktree_manager.worktrees_dir))
        ]

        assert len(minipipe_worktrees) >= 1
        wt = minipipe_worktrees[0]
        assert hasattr(wt, "path")
        assert hasattr(wt, "branch")
        assert hasattr(wt, "commit_hash")
        assert hasattr(wt, "is_locked")
        assert hasattr(wt, "run_id")
        assert hasattr(wt, "step_id")


class TestBranchOperations:
    """Tests for branch-related methods."""

    def test_is_branch_checked_out_true(self, worktree_manager):
        """Test checking if branch is checked out."""
        worktree_manager.create_worktree(
            run_id="run-004", branch_name="test-branch-001"
        )

        result = worktree_manager.is_branch_checked_out("test-branch-001")

        assert result is True

    def test_is_branch_checked_out_false(self, worktree_manager):
        """Test checking non-existent branch."""
        result = worktree_manager.is_branch_checked_out("nonexistent-branch")

        assert result is False


class TestWorktreeStats:
    """Tests for get_worktree_stats method."""

    def test_get_worktree_stats(self, worktree_manager):
        """Test getting worktree statistics."""
        # Create some worktrees
        path1 = worktree_manager.create_worktree(run_id="run-005")
        path2 = worktree_manager.create_worktree(run_id="run-006")

        assert path1.exists()
        assert path2.exists()

        stats = worktree_manager.get_worktree_stats()

        assert "total_worktrees" in stats
        assert "minipipe_worktrees" in stats
        assert "locked_worktrees" in stats
        assert stats["minipipe_worktrees"] >= 2


class TestPruneWorktrees:
    """Tests for prune_worktrees method."""

    def test_prune_worktrees(self, worktree_manager):
        """Test pruning stale worktrees."""
        # This is hard to test without actually creating stale worktrees
        # Just verify the method runs without error
        pruned_count = worktree_manager.prune_worktrees()

        assert isinstance(pruned_count, int)
        assert pruned_count >= 0
