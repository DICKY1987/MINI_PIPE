"""
Tests for Daemon Orchestrator
"""

import json
import sqlite3
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.minipipe.daemon_orchestrator import (
    DaemonConfig,
    DaemonOrchestrator,
    load_config,
    DB_AVAILABLE,
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database with test data."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    
    # Create runs table
    conn.execute("""
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            project_id TEXT,
            phase_id TEXT,
            state TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        )
    """)
    
    # Insert pending runs
    conn.execute("""
        INSERT INTO runs VALUES (
            'run-001', 'project-1', 'phase-1', 'PENDING',
            '2025-01-01T00:00:00.000000Z', '2025-01-01T00:00:00.000000Z',
            '{}'
        )
    """)
    
    conn.execute("""
        INSERT INTO runs VALUES (
            'run-002', 'project-1', 'phase-2', 'PENDING',
            '2025-01-01T00:01:00.000000Z', '2025-01-01T00:01:00.000000Z',
            '{}'
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path


@pytest.fixture
def daemon_config(tmp_path):
    """Create a daemon config for testing."""
    return DaemonConfig(
        max_concurrent_runs=2,
        poll_interval_seconds=0.1,  # Fast for testing
        auto_cleanup_completed=False,  # Don't cleanup in tests
        log_dir=tmp_path / "logs",
    )


class TestDaemonConfig:
    """Tests for DaemonConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DaemonConfig()
        
        assert config.max_concurrent_runs == 4
        assert config.poll_interval_seconds == 5.0
        assert config.auto_cleanup_completed is True
        assert config.log_dir is None
    
    def test_custom_config(self, tmp_path):
        """Test custom configuration values."""
        log_dir = tmp_path / "logs"
        config = DaemonConfig(
            max_concurrent_runs=10,
            poll_interval_seconds=1.0,
            auto_cleanup_completed=False,
            log_dir=log_dir,
        )
        
        assert config.max_concurrent_runs == 10
        assert config.poll_interval_seconds == 1.0
        assert config.auto_cleanup_completed is False
        assert config.log_dir == log_dir


class TestDaemonOrchestrator:
    """Tests for DaemonOrchestrator class."""
    
    def test_init_creates_log_dir(self, daemon_config):
        """Test that initialization creates log directory."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        assert daemon.config.log_dir.exists()
    
    def test_init_sets_signal_handlers(self, daemon_config):
        """Test that signal handlers are set."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Verify daemon was created
        assert daemon is not None
        assert daemon.should_stop is False
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_pending_runs(self, temp_db, daemon_config):
        """Test fetching pending runs from database."""
        from core.state.db import Database
        
        db = Database(temp_db)
        db.connect()
        
        daemon = DaemonOrchestrator(config=daemon_config, db=db)
        pending = daemon._fetch_pending_runs(limit=10)
        
        assert len(pending) == 2
        assert pending[0]["run_id"] == "run-001"  # ASC order
        assert pending[1]["run_id"] == "run-002"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_pending_runs_with_limit(self, temp_db, daemon_config):
        """Test fetching with limit."""
        from core.state.db import Database
        
        db = Database(temp_db)
        db.connect()
        
        daemon = DaemonOrchestrator(config=daemon_config, db=db)
        pending = daemon._fetch_pending_runs(limit=1)
        
        assert len(pending) == 1
        assert pending[0]["run_id"] == "run-001"
    
    def test_start_run_creates_process(self, daemon_config):
        """Test that start_run creates a subprocess."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Mock subprocess.Popen
        with patch("subprocess.Popen") as mock_popen:
            mock_proc = MagicMock()
            mock_proc.pid = 12345
            mock_popen.return_value = mock_proc
            
            daemon.start_run("test-run-001")
            
            # Verify subprocess was started
            mock_popen.assert_called_once()
            assert "test-run-001" in daemon.running_processes
    
    def test_check_running_processes_cleans_completed(self, daemon_config):
        """Test that completed processes are cleaned up."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add a mock completed process
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 0  # Completed with exit code 0
        daemon.running_processes["test-run"] = mock_proc
        
        daemon.check_running_processes()
        
        # Verify process was removed
        assert "test-run" not in daemon.running_processes
    
    def test_check_running_processes_keeps_running(self, daemon_config):
        """Test that running processes are kept."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add a mock running process
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # Still running
        daemon.running_processes["test-run"] = mock_proc
        
        daemon.check_running_processes()
        
        # Verify process was not removed
        assert "test-run" in daemon.running_processes
    
    def test_stop_run_graceful(self, daemon_config):
        """Test graceful run stop."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add a mock process
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.return_value = None  # Simulate successful wait
        daemon.running_processes["test-run"] = mock_proc
        
        result = daemon.stop_run("test-run", timeout=1.0)
        
        assert result is True
        assert "test-run" not in daemon.running_processes
        mock_proc.terminate.assert_called_once()
    
    def test_stop_run_force_kill(self, daemon_config):
        """Test force kill when graceful stop fails."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add a mock process that doesn't stop gracefully
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_proc.wait.side_effect = [
            Exception("Timeout"),  # First wait times out
            None  # Second wait (after kill) succeeds
        ]
        daemon.running_processes["test-run"] = mock_proc
        
        with patch("subprocess.TimeoutExpired", Exception):
            result = daemon.stop_run("test-run", timeout=0.1)
        
        assert result is True
        mock_proc.kill.assert_called_once()
    
    def test_get_status(self, daemon_config):
        """Test getting daemon status."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add some mock processes
        daemon.running_processes["run-001"] = MagicMock()
        daemon.running_processes["run-002"] = MagicMock()
        
        status = daemon.get_status()
        
        assert status["running_count"] == 2
        assert status["max_concurrent"] == 2
        assert status["capacity_available"] == 0
        assert "run-001" in status["running_runs"]
        assert "run-002" in status["running_runs"]
    
    def test_cleanup_stops_all_processes(self, daemon_config):
        """Test that cleanup stops all running processes."""
        daemon = DaemonOrchestrator(config=daemon_config)
        
        # Add mock processes
        mock_proc1 = MagicMock()
        mock_proc1.wait.return_value = None
        mock_proc2 = MagicMock()
        mock_proc2.wait.return_value = None
        
        daemon.running_processes["run-001"] = mock_proc1
        daemon.running_processes["run-002"] = mock_proc2
        
        daemon.cleanup()
        
        # Verify all processes were stopped
        assert len(daemon.running_processes) == 0
        mock_proc1.terminate.assert_called()
        mock_proc2.terminate.assert_called()


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_load_config_from_file(self, tmp_path):
        """Test loading configuration from file."""
        config_path = tmp_path / "daemon_config.json"
        config_data = {
            "max_concurrent_runs": 10,
            "poll_interval_seconds": 2.5,
            "auto_cleanup_completed_runs": False,
            "log_dir": str(tmp_path / "logs"),
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        config = load_config(config_path)
        
        assert config.max_concurrent_runs == 10
        assert config.poll_interval_seconds == 2.5
        assert config.auto_cleanup_completed is False
        assert config.log_dir == tmp_path / "logs"
    
    def test_load_config_missing_file(self, tmp_path):
        """Test loading config with missing file."""
        config_path = tmp_path / "nonexistent.json"
        
        config = load_config(config_path)
        
        # Should return default config
        assert config.max_concurrent_runs == 4
        assert config.poll_interval_seconds == 5.0
    
    def test_load_config_invalid_json(self, tmp_path):
        """Test loading config with invalid JSON."""
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{ invalid json }")
        
        config = load_config(config_path)
        
        # Should return default config
        assert config.max_concurrent_runs == 4


class TestDaemonIntegration:
    """Integration tests for daemon."""
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_poll_and_start_runs_respects_limit(self, temp_db, daemon_config):
        """Test that daemon respects concurrency limit."""
        from core.state.db import Database
        
        db = Database(temp_db)
        db.connect()
        
        daemon = DaemonOrchestrator(config=daemon_config, db=db)
        
        # Mock start_run to track calls
        start_calls = []
        def mock_start_run(run_id):
            start_calls.append(run_id)
            daemon.running_processes[run_id] = MagicMock()
        
        daemon.start_run = mock_start_run
        
        # Poll should start up to max_concurrent_runs
        daemon.poll_and_start_runs()
        
        # Should start 2 runs (limit is 2)
        assert len(start_calls) == 2
        assert "run-001" in start_calls
        assert "run-002" in start_calls
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_poll_and_start_runs_at_capacity(self, temp_db, daemon_config):
        """Test that daemon doesn't start runs when at capacity."""
        from core.state.db import Database
        
        db = Database(temp_db)
        db.connect()
        
        daemon = DaemonOrchestrator(config=daemon_config, db=db)
        
        # Fill capacity
        daemon.running_processes["existing-001"] = MagicMock()
        daemon.running_processes["existing-002"] = MagicMock()
        
        # Mock start_run
        start_calls = []
        daemon.start_run = lambda run_id: start_calls.append(run_id)
        
        daemon.poll_and_start_runs()
        
        # Should not start any new runs
        assert len(start_calls) == 0
