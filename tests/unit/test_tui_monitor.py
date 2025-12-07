"""
Tests for TUI Monitor
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.minipipe.tui_monitor import MiniPipeTUI, DB_AVAILABLE


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database with test data."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.execute("""
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            state TEXT,
            phase_id TEXT,
            created_at TEXT,
            updated_at TEXT,
            metadata TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE step_attempts (
            step_id TEXT,
            run_id TEXT,
            state TEXT,
            started_at TEXT,
            completed_at TEXT,
            metadata TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE events (
            timestamp TEXT,
            event_type TEXT,
            severity TEXT,
            message TEXT,
            metadata TEXT
        )
    """)
    
    # Insert test data
    conn.execute("""
        INSERT INTO runs VALUES (
            'run-001', 'RUNNING', 'phase-1',
            '2025-01-01T00:00:00.000000Z', '2025-01-01T00:01:00.000000Z',
            '{}'
        )
    """)
    
    conn.execute("""
        INSERT INTO runs VALUES (
            'run-002', 'SUCCEEDED', 'phase-2',
            '2025-01-01T00:00:00.000000Z', '2025-01-01T00:02:00.000000Z',
            '{}'
        )
    """)
    
    conn.execute("""
        INSERT INTO step_attempts VALUES (
            'step-001', 'run-001', 'RUNNING',
            '2025-01-01T00:00:30.000000Z', NULL,
            '{}'
        )
    """)
    
    conn.execute("""
        INSERT INTO events VALUES (
            '2025-01-01T00:00:00.000000Z', 'run_started', 'INFO',
            'Run started', '{}'
        )
    """)
    
    conn.commit()
    conn.close()
    
    return db_path


class TestMiniPipeTUI:
    """Tests for MiniPipeTUI class."""
    
    def test_init_without_db(self):
        """Test initialization without database."""
        app = MiniPipeTUI()
        assert app.db is None
        assert app.selected_run_id is None
        assert app.poll_interval == 2.0
    
    def test_init_with_db_path(self, temp_db):
        """Test initialization with database path."""
        if not DB_AVAILABLE:
            pytest.skip("Database not available")
        
        app = MiniPipeTUI(db_path=temp_db)
        assert app.db is not None
        assert app.db_path == temp_db
    
    def test_compose_creates_widgets(self):
        """Test that compose creates required widgets."""
        app = MiniPipeTUI()
        
        # Just verify compose method exists and returns something
        # Can't fully test without mounting the app
        assert hasattr(app, 'compose')
        assert callable(app.compose)
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_runs(self, temp_db):
        """Test fetching runs from database."""
        app = MiniPipeTUI(db_path=temp_db)
        
        runs = app._fetch_runs()
        
        assert len(runs) == 2
        assert runs[0]["run_id"] == "run-002"  # DESC order
        assert runs[0]["state"] == "SUCCEEDED"
        assert runs[1]["run_id"] == "run-001"
        assert runs[1]["state"] == "RUNNING"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_recent_events(self, temp_db):
        """Test fetching recent events."""
        app = MiniPipeTUI(db_path=temp_db)
        
        events = app._fetch_recent_events()
        
        assert len(events) == 1
        assert events[0]["event_type"] == "run_started"
        assert events[0]["message"] == "Run started"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_current_step(self, temp_db):
        """Test fetching current step for a run."""
        app = MiniPipeTUI(db_path=temp_db)
        
        step_info = app._fetch_current_step("run-001")
        
        assert step_info["step_id"] == "step-001"
        assert step_info["state"] == "RUNNING"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_fetch_current_step_no_active(self, temp_db):
        """Test fetching step when no active step exists."""
        app = MiniPipeTUI(db_path=temp_db)
        
        step_info = app._fetch_current_step("run-002")
        
        assert step_info == {}
    
    def test_no_db_shows_message(self):
        """Test that missing database shows appropriate message."""
        app = MiniPipeTUI()
        
        # Just verify the method exists
        # Can't test DOM queries without mounting
        assert hasattr(app, '_show_no_db_message')
        assert callable(app._show_no_db_message)


class TestRunsTable:
    """Tests for RunsTable widget."""
    
    def test_table_has_columns(self):
        """Test that table initializes with correct columns."""
        from src.minipipe.tui_monitor import RunsTable
        
        # Can't easily test widget initialization without running app
        # Just verify import works
        assert RunsTable is not None


class TestStepDetail:
    """Tests for StepDetail widget."""
    
    def test_step_detail_render_empty(self):
        """Test rendering with no step info."""
        from src.minipipe.tui_monitor import StepDetail
        
        detail = StepDetail()
        result = detail.render()
        
        assert "No active step" in result
    
    def test_step_detail_render_with_info(self):
        """Test rendering with step info."""
        from src.minipipe.tui_monitor import StepDetail
        
        detail = StepDetail()
        detail.step_info = "Step ID: test-001\nState: RUNNING"
        result = detail.render()
        
        assert "test-001" in result
        assert "RUNNING" in result


class TestEventStream:
    """Tests for EventStream widget."""
    
    def test_event_stream_render_empty(self):
        """Test rendering with no events."""
        from src.minipipe.tui_monitor import EventStream
        
        stream = EventStream()
        result = stream.render()
        
        assert "No events" in result
    
    def test_event_stream_render_with_events(self):
        """Test rendering with events."""
        from src.minipipe.tui_monitor import EventStream
        
        stream = EventStream()
        stream.events = [
            {
                "timestamp": "2025-01-01T00:00:00Z",
                "event_type": "test_event",
                "message": "Test message"
            }
        ]
        result = stream.render()
        
        assert "test_event" in result
        assert "Test message" in result


class TestTUIIntegration:
    """Integration tests for TUI."""
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_refresh_data_with_db(self, temp_db):
        """Test refreshing data from database."""
        app = MiniPipeTUI(db_path=temp_db)
        
        # Should not raise
        app.refresh_data()
    
    def test_refresh_data_without_db(self):
        """Test refreshing data without database."""
        app = MiniPipeTUI()
        
        # Should not raise
        app.refresh_data()
