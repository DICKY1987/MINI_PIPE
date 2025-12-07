"""
Tests for Session Registry
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.minipipe.session_registry import (
    SessionRegistry,
    SessionRegistryError,
    DB_AVAILABLE,
)


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.close()
    return db_path


@pytest.fixture
def session_registry(temp_db):
    """Create a SessionRegistry with test database."""
    if not DB_AVAILABLE:
        pytest.skip("Database not available")
    
    from core.state.db import Database
    db = Database(temp_db)
    db.connect()
    
    return SessionRegistry(db=db)


class TestSessionRegistry:
    """Tests for SessionRegistry class."""
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_init_creates_table(self, temp_db):
        """Test that initialization creates sessions table."""
        from core.state.db import Database
        db = Database(temp_db)
        db.connect()
        
        registry = SessionRegistry(db=db)
        
        # Verify table exists
        cursor = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        )
        assert cursor.fetchone() is not None
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_create_session(self, session_registry):
        """Test creating a new session."""
        session_id = session_registry.create_session(
            project_id="project-001",
            agent_type="aider",
            title="Refactor authentication module",
            workspace_path="/workspace/auth",
        )
        
        assert session_id.startswith("session-")
        assert "project-001" in session_id
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_get_session(self, session_registry):
        """Test getting a session."""
        session_id = session_registry.create_session(
            project_id="project-002",
            agent_type="claude",
            title="Test session",
        )
        
        session = session_registry.get_session(session_id)
        
        assert session["session_id"] == session_id
        assert session["project_id"] == "project-002"
        assert session["agent_type"] == "claude"
        assert session["title"] == "Test session"
        assert session["state"] == "created"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_get_session_not_found(self, session_registry):
        """Test getting non-existent session."""
        with pytest.raises(SessionRegistryError, match="Session not found"):
            session_registry.get_session("nonexistent-session")
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_list_sessions(self, session_registry):
        """Test listing sessions."""
        # Create multiple sessions
        session_registry.create_session(
            project_id="project-003",
            agent_type="aider",
            title="Session 1",
        )
        session_registry.create_session(
            project_id="project-003",
            agent_type="claude",
            title="Session 2",
        )
        
        sessions = session_registry.list_sessions(project_id="project-003")
        
        assert len(sessions) == 2
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_list_sessions_by_state(self, session_registry):
        """Test listing sessions filtered by state."""
        session_id = session_registry.create_session(
            project_id="project-004",
            agent_type="aider",
            title="Active session",
        )
        
        # Transition to active
        session_registry.update_session_state(session_id, "active")
        
        active_sessions = session_registry.list_sessions(state="active")
        
        assert len(active_sessions) >= 1
        assert all(s["state"] == "active" for s in active_sessions)
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_update_session_state(self, session_registry):
        """Test updating session state."""
        session_id = session_registry.create_session(
            project_id="project-005",
            agent_type="aider",
            title="Test",
        )
        
        # Transition created -> active
        result = session_registry.update_session_state(session_id, "active")
        
        assert result is True
        
        session = session_registry.get_session(session_id)
        assert session["state"] == "active"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_invalid_state_transition(self, session_registry):
        """Test that invalid state transitions are rejected."""
        session_id = session_registry.create_session(
            project_id="project-006",
            agent_type="aider",
            title="Test",
        )
        
        # Cannot go from created to completed
        with pytest.raises(SessionRegistryError, match="Invalid state transition"):
            session_registry.update_session_state(session_id, "completed")
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_invalid_state(self, session_registry):
        """Test that invalid states are rejected."""
        session_id = session_registry.create_session(
            project_id="project-007",
            agent_type="aider",
            title="Test",
        )
        
        with pytest.raises(SessionRegistryError, match="Invalid state"):
            session_registry.update_session_state(session_id, "invalid_state")
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_pause_session(self, session_registry):
        """Test pausing a session."""
        session_id = session_registry.create_session(
            project_id="project-008",
            agent_type="aider",
            title="Test",
        )
        
        # Activate then pause
        session_registry.update_session_state(session_id, "active")
        result = session_registry.pause_session(session_id)
        
        assert result is True
        session = session_registry.get_session(session_id)
        assert session["state"] == "paused"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_resume_session(self, session_registry):
        """Test resuming a paused session."""
        session_id = session_registry.create_session(
            project_id="project-009",
            agent_type="aider",
            title="Test",
        )
        
        # Activate, pause, then resume
        session_registry.update_session_state(session_id, "active")
        session_registry.pause_session(session_id)
        result = session_registry.resume_session(session_id)
        
        assert result is True
        session = session_registry.get_session(session_id)
        assert session["state"] == "active"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_complete_session_success(self, session_registry):
        """Test completing a session successfully."""
        session_id = session_registry.create_session(
            project_id="project-010",
            agent_type="aider",
            title="Test",
        )
        
        # Activate then complete
        session_registry.update_session_state(session_id, "active")
        result = session_registry.complete_session(session_id, success=True)
        
        assert result is True
        session = session_registry.get_session(session_id)
        assert session["state"] == "completed"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_complete_session_failure(self, session_registry):
        """Test marking session as failed."""
        session_id = session_registry.create_session(
            project_id="project-011",
            agent_type="aider",
            title="Test",
        )
        
        # Activate then fail
        session_registry.update_session_state(session_id, "active")
        result = session_registry.complete_session(session_id, success=False)
        
        assert result is True
        session = session_registry.get_session(session_id)
        assert session["state"] == "failed"
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_delete_session(self, session_registry):
        """Test deleting a session."""
        session_id = session_registry.create_session(
            project_id="project-012",
            agent_type="aider",
            title="Test",
        )
        
        result = session_registry.delete_session(session_id)
        
        assert result is True
        
        # Should raise error when getting deleted session
        with pytest.raises(SessionRegistryError):
            session_registry.get_session(session_id)
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_get_active_sessions(self, session_registry):
        """Test getting all active sessions."""
        # Create and activate sessions
        session_id1 = session_registry.create_session(
            project_id="project-013",
            agent_type="aider",
            title="Active 1",
        )
        session_id2 = session_registry.create_session(
            project_id="project-013",
            agent_type="claude",
            title="Active 2",
        )
        
        session_registry.update_session_state(session_id1, "active")
        session_registry.update_session_state(session_id2, "active")
        
        active = session_registry.get_active_sessions(project_id="project-013")
        
        assert len(active) >= 2
        assert all(s["state"] == "active" for s in active)
    
    @pytest.mark.skipif(not DB_AVAILABLE, reason="Database not available")
    def test_metadata_updates(self, session_registry):
        """Test metadata updates during state transitions."""
        session_id = session_registry.create_session(
            project_id="project-014",
            agent_type="aider",
            title="Test",
            metadata={"initial": "value"},
        )
        
        # Update with additional metadata
        session_registry.update_session_state(
            session_id,
            "active",
            metadata_updates={"extra": "data"},
        )
        
        session = session_registry.get_session(session_id)
        metadata = session["metadata"]
        
        assert "extra" in metadata
    
    def test_init_without_db(self):
        """Test initialization without database."""
        registry = SessionRegistry(db=None)
        
        assert registry.db is None
    
    def test_create_session_without_db(self):
        """Test that operations fail gracefully without database."""
        registry = SessionRegistry(db=None)
        
        with pytest.raises(SessionRegistryError, match="Database not available"):
            registry.create_session(
                project_id="test",
                agent_type="aider",
                title="test",
            )
