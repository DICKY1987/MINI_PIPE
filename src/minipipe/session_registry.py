"""
Session Registry - Long-lived AI Agent Session Management

Tracks AI agent sessions as first-class entities with persistence across runs.
Enables resuming long-running AI tasks after restarts.
"""

# DOC_ID: DOC-CORE-ENGINE-SESSION-REGISTRY-203

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional database integration
try:
    from core.state.db import Database, get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    Database = None
    get_db = None


class SessionRegistryError(Exception):
    """Base exception for session registry errors."""
    pass


class SessionRegistry:
    """
    Registry for managing long-lived AI agent sessions.
    
    Sessions are first-class entities that can span multiple runs and persist
    across application restarts. Each session tracks an AI agent working on a
    specific project/workstream.
    """
    
    # Valid session states
    VALID_STATES = frozenset([
        "created",      # Session created but not yet active
        "active",       # Session currently running
        "paused",       # Session paused (e.g., waiting for review)
        "completed",    # Session completed successfully
        "failed",       # Session failed
    ])
    
    # Valid state transitions
    STATE_TRANSITIONS = {
        "created": ["active", "failed"],
        "active": ["paused", "completed", "failed"],
        "paused": ["active", "completed", "failed"],
        "completed": [],  # Terminal state
        "failed": [],     # Terminal state
    }
    
    def __init__(self, db: Optional[Database] = None):
        """
        Initialize session registry.
        
        Args:
            db: Database instance (optional)
        """
        self.db = db
        
        if self.db and DB_AVAILABLE:
            self._ensure_table_exists()
    
    def _ensure_table_exists(self) -> None:
        """Ensure sessions table exists in database."""
        if not self.db:
            return
        
        self.db.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                workstream_id TEXT,
                agent_type TEXT NOT NULL,
                title TEXT,
                workspace_path TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                state TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Create indexes for common queries
        self.db.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_project_id 
            ON sessions(project_id)
        """)
        
        self.db.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_state 
            ON sessions(state)
        """)
        
        self.db.conn.commit()
    
    def create_session(
        self,
        project_id: str,
        agent_type: str,
        title: str,
        workspace_path: Optional[str] = None,
        workstream_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new session.
        
        Args:
            project_id: Project identifier
            agent_type: Type of AI agent (e.g., 'aider', 'claude', 'codex')
            title: Human-readable session title
            workspace_path: Optional workspace path
            workstream_id: Optional workstream identifier
            metadata: Optional metadata dictionary
        
        Returns:
            session_id: Created session identifier
        
        Raises:
            SessionRegistryError: If creation fails
        """
        if not self.db or not DB_AVAILABLE:
            raise SessionRegistryError("Database not available")
        
        # Generate session ID
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        session_id = f"session-{timestamp}-{project_id[:8]}"
        
        now = datetime.now(UTC).isoformat() + "Z"
        
        try:
            self.db.conn.execute(
                """
                INSERT INTO sessions (
                    session_id, project_id, workstream_id, agent_type,
                    title, workspace_path, created_at, updated_at, state, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    project_id,
                    workstream_id,
                    agent_type,
                    title,
                    workspace_path,
                    now,
                    now,
                    "created",
                    json.dumps(metadata or {}),
                ),
            )
            self.db.conn.commit()
            
            return session_id
        
        except Exception as e:
            raise SessionRegistryError(f"Failed to create session: {e}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session data dictionary
        
        Raises:
            SessionRegistryError: If session not found
        """
        if not self.db or not DB_AVAILABLE:
            raise SessionRegistryError("Database not available")
        
        cursor = self.db.conn.execute(
            """
            SELECT session_id, project_id, workstream_id, agent_type,
                   title, workspace_path, created_at, updated_at, state, metadata
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        )
        
        row = cursor.fetchone()
        if not row:
            raise SessionRegistryError(f"Session not found: {session_id}")
        
        return self._row_to_dict(row)
    
    def list_sessions(
        self,
        project_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        List sessions with optional filters.
        
        Args:
            project_id: Optional filter by project
            state: Optional filter by state
            limit: Maximum number of results
        
        Returns:
            List of session dictionaries
        """
        if not self.db or not DB_AVAILABLE:
            return []
        
        # Build query dynamically based on filters
        query = """
            SELECT session_id, project_id, workstream_id, agent_type,
                   title, workspace_path, created_at, updated_at, state, metadata
            FROM sessions
            WHERE 1=1
        """
        params = []
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if state:
            query += " AND state = ?"
            params.append(state)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.db.conn.execute(query, params)
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def update_session_state(
        self,
        session_id: str,
        new_state: str,
        metadata_updates: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            new_state: New state
            metadata_updates: Optional metadata updates to merge
        
        Returns:
            True if update succeeded
        
        Raises:
            SessionRegistryError: If state transition is invalid
        """
        if new_state not in self.VALID_STATES:
            raise SessionRegistryError(f"Invalid state: {new_state}")
        
        # Get current session
        session = self.get_session(session_id)
        current_state = session["state"]
        
        # Validate state transition
        valid_transitions = self.STATE_TRANSITIONS.get(current_state, [])
        if new_state not in valid_transitions:
            raise SessionRegistryError(
                f"Invalid state transition: {current_state} -> {new_state}"
            )
        
        # Update metadata if provided
        metadata = json.loads(session["metadata"]) if session["metadata"] else {}
        if metadata_updates:
            metadata.update(metadata_updates)
        
        now = datetime.now(UTC).isoformat() + "Z"
        
        try:
            self.db.conn.execute(
                """
                UPDATE sessions
                SET state = ?, updated_at = ?, metadata = ?
                WHERE session_id = ?
                """,
                (new_state, now, json.dumps(metadata), session_id),
            )
            self.db.conn.commit()
            return True
        
        except Exception as e:
            raise SessionRegistryError(f"Failed to update session: {e}")
    
    def pause_session(self, session_id: str) -> bool:
        """
        Pause a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if paused successfully
        """
        return self.update_session_state(
            session_id,
            "paused",
            {"paused_at": datetime.now(UTC).isoformat() + "Z"},
        )
    
    def resume_session(self, session_id: str) -> bool:
        """
        Resume a paused session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if resumed successfully
        """
        return self.update_session_state(
            session_id,
            "active",
            {"resumed_at": datetime.now(UTC).isoformat() + "Z"},
        )
    
    def complete_session(self, session_id: str, success: bool = True) -> bool:
        """
        Mark session as complete.
        
        Args:
            session_id: Session identifier
            success: Whether session completed successfully
        
        Returns:
            True if marked complete
        """
        new_state = "completed" if success else "failed"
        return self.update_session_state(
            session_id,
            new_state,
            {
                "completed_at": datetime.now(UTC).isoformat() + "Z",
                "success": success,
            },
        )
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deleted successfully
        """
        if not self.db or not DB_AVAILABLE:
            raise SessionRegistryError("Database not available")
        
        try:
            self.db.conn.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            self.db.conn.commit()
            return True
        
        except Exception as e:
            raise SessionRegistryError(f"Failed to delete session: {e}")
    
    def get_active_sessions(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all active sessions.
        
        Args:
            project_id: Optional filter by project
        
        Returns:
            List of active session dictionaries
        """
        return self.list_sessions(project_id=project_id, state="active")
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            "session_id": row[0],
            "project_id": row[1],
            "workstream_id": row[2],
            "agent_type": row[3],
            "title": row[4],
            "workspace_path": row[5],
            "created_at": row[6],
            "updated_at": row[7],
            "state": row[8],
            "metadata": row[9],
        }


__all__ = ["SessionRegistry", "SessionRegistryError"]
