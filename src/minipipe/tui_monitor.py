"""
TUI Monitor - Read-only Terminal UI for Run Observability

Provides a real-time, keyboard-driven interface for monitoring MINI_PIPE runs.
"""

# DOC_ID: DOC-CORE-ENGINE-TUI-MONITOR-201

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Footer, Header, Static
from textual.reactive import reactive

# Optional database integration
try:
    from core.state.db import Database, get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    Database = None
    get_db = None


class RunsTable(DataTable):
    """Table widget showing active and recent runs."""
    
    def on_mount(self) -> None:
        """Initialize table columns."""
        self.add_columns("Run ID", "State", "Phase", "Progress", "Duration")
        self.cursor_type = "row"


class StepDetail(Static):
    """Widget showing current step details."""
    
    step_info = reactive("")
    
    def render(self) -> str:
        """Render step information."""
        if not self.step_info:
            return "No active step selected"
        return self.step_info


class EventStream(Static):
    """Widget showing recent events."""
    
    events = reactive([])
    
    def render(self) -> str:
        """Render event stream."""
        if not self.events:
            return "No events"
        
        lines = []
        for event in self.events[-10:]:  # Show last 10 events
            timestamp = event.get("timestamp", "")
            event_type = event.get("event_type", "")
            message = event.get("message", "")
            lines.append(f"{timestamp}  {event_type:20s}  {message}")
        
        return "\n".join(lines)


class MiniPipeTUI(App):
    """
    MINI_PIPE TUI Monitor Application.
    
    Read-only interface for monitoring runs, steps, and events.
    """
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #runs-container {
        height: 40%;
        border: solid $primary;
        margin: 1;
    }
    
    #step-container {
        height: 30%;
        border: solid $secondary;
        margin: 1;
    }
    
    #events-container {
        height: 30%;
        border: solid $accent;
        margin: 1;
    }
    
    .section-title {
        background: $primary;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    
    DataTable {
        height: 100%;
    }
    
    Static {
        padding: 1;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("up", "cursor_up", "Up"),
        ("down", "cursor_down", "Down"),
    ]
    
    def __init__(
        self,
        db_path: Optional[Path] = None,
        poll_interval: float = 2.0,
        **kwargs
    ):
        """
        Initialize TUI Monitor.
        
        Args:
            db_path: Optional path to SQLite database
            poll_interval: Refresh interval in seconds
            **kwargs: Additional arguments passed to App
        """
        super().__init__(**kwargs)
        self.db_path = db_path
        self.poll_interval = poll_interval
        self.db: Optional[Database] = None
        self.selected_run_id: Optional[str] = None
        
        if DB_AVAILABLE and db_path:
            self.db = Database(db_path)
            self.db.connect()
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()
        
        with Container(id="runs-container"):
            yield Static("Active Runs", classes="section-title")
            yield RunsTable(id="runs-table")
        
        with Container(id="step-container"):
            yield Static("Current Step", classes="section-title")
            yield StepDetail(id="step-detail")
        
        with Container(id="events-container"):
            yield Static("Event Stream", classes="section-title")
            yield EventStream(id="event-stream")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted."""
        if self.db:
            # Start periodic refresh
            self.set_interval(self.poll_interval, self.refresh_data)
            # Initial load
            self.refresh_data()
        else:
            self._show_no_db_message()
    
    def _show_no_db_message(self) -> None:
        """Show message when database is not available."""
        table = self.query_one("#runs-table", RunsTable)
        table.add_row("", "No database", "Use --db-path", "", "")
    
    def refresh_data(self) -> None:
        """Refresh data from database."""
        if not self.db:
            return
        
        try:
            # Fetch runs
            runs = self._fetch_runs()
            self._update_runs_table(runs)
            
            # Fetch events
            events = self._fetch_recent_events()
            self._update_event_stream(events)
            
            # Update step detail if a run is selected
            if self.selected_run_id:
                step_info = self._fetch_current_step(self.selected_run_id)
                self._update_step_detail(step_info)
        
        except Exception as e:
            # Log error but don't crash
            self.log.error(f"Error refreshing data: {e}")
    
    def _fetch_runs(self) -> List[Dict[str, Any]]:
        """Fetch recent runs from database."""
        if not self.db:
            return []
        
        try:
            # Query for recent runs
            cursor = self.db.conn.execute(
                """
                SELECT run_id, state, phase_id, created_at, updated_at, metadata
                FROM runs
                ORDER BY created_at DESC
                LIMIT 20
                """
            )
            
            runs = []
            for row in cursor.fetchall():
                run_id, state, phase_id, created_at, updated_at, metadata = row
                
                # Calculate duration
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                duration = int((updated - created).total_seconds())
                
                runs.append({
                    "run_id": run_id,
                    "state": state,
                    "phase_id": phase_id,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "duration": duration,
                    "metadata": metadata,
                })
            
            return runs
        
        except Exception as e:
            self.log.error(f"Error fetching runs: {e}")
            return []
    
    def _fetch_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent events from database."""
        if not self.db:
            return []
        
        try:
            cursor = self.db.conn.execute(
                """
                SELECT timestamp, event_type, severity, message, metadata
                FROM events
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            
            events = []
            for row in cursor.fetchall():
                timestamp, event_type, severity, message, metadata = row
                events.append({
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "severity": severity,
                    "message": message,
                    "metadata": metadata,
                })
            
            return list(reversed(events))  # Show oldest first
        
        except Exception as e:
            self.log.error(f"Error fetching events: {e}")
            return []
    
    def _fetch_current_step(self, run_id: str) -> Dict[str, Any]:
        """Fetch current step for a run."""
        if not self.db:
            return {}
        
        try:
            cursor = self.db.conn.execute(
                """
                SELECT step_id, state, started_at, completed_at, metadata
                FROM step_attempts
                WHERE run_id = ? AND state IN ('RUNNING', 'PENDING')
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (run_id,)
            )
            
            row = cursor.fetchone()
            if row:
                step_id, state, started_at, completed_at, metadata = row
                return {
                    "step_id": step_id,
                    "state": state,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "metadata": metadata,
                }
            
            return {}
        
        except Exception as e:
            self.log.error(f"Error fetching step: {e}")
            return {}
    
    def _update_runs_table(self, runs: List[Dict[str, Any]]) -> None:
        """Update runs table with fresh data."""
        table = self.query_one("#runs-table", RunsTable)
        table.clear()
        
        for run in runs:
            # Calculate progress (mock for now - would need step counts from DB)
            progress = "N/A"
            
            # Format duration
            duration = f"{run['duration']}s"
            
            # Add row
            table.add_row(
                run["run_id"][:12],  # Truncate for display
                run["state"],
                run["phase_id"],
                progress,
                duration
            )
    
    def _update_event_stream(self, events: List[Dict[str, Any]]) -> None:
        """Update event stream widget."""
        stream = self.query_one("#event-stream", EventStream)
        stream.events = events
    
    def _update_step_detail(self, step_info: Dict[str, Any]) -> None:
        """Update step detail widget."""
        detail = self.query_one("#step-detail", StepDetail)
        
        if not step_info:
            detail.step_info = "No active step"
            return
        
        # Format step information
        info_lines = [
            f"Step ID: {step_info.get('step_id', 'N/A')}",
            f"State: {step_info.get('state', 'N/A')}",
            f"Started: {step_info.get('started_at', 'N/A')}",
        ]
        
        # Add metadata if available
        metadata = step_info.get("metadata")
        if metadata:
            info_lines.append(f"Metadata: {metadata}")
        
        detail.step_info = "\n".join(info_lines)
    
    def action_refresh(self) -> None:
        """Manual refresh action."""
        self.refresh_data()
    
    def action_cursor_up(self) -> None:
        """Move cursor up in runs table."""
        table = self.query_one("#runs-table", RunsTable)
        table.action_cursor_up()
    
    def action_cursor_down(self) -> None:
        """Move cursor down in runs table."""
        table = self.query_one("#runs-table", RunsTable)
        table.action_cursor_down()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in runs table."""
        table = self.query_one("#runs-table", RunsTable)
        
        # Get the run_id from the selected row
        row_key = event.row_key
        row_data = table.get_row(row_key)
        
        if row_data:
            # First column is run_id (truncated)
            self.selected_run_id = str(row_data[0])
            self.refresh_data()


def run_tui_monitor(
    db_path: Optional[Path] = None,
    poll_interval: float = 2.0
) -> None:
    """
    Run the TUI monitor application.
    
    Args:
        db_path: Path to SQLite database
        poll_interval: Refresh interval in seconds
    """
    app = MiniPipeTUI(db_path=db_path, poll_interval=poll_interval)
    app.run()


__all__ = ["MiniPipeTUI", "run_tui_monitor"]

