"""
Daemon Orchestrator - Background Multi-Run Management

Manages multiple concurrent runs, auto-starts pending runs, and enforces
concurrency limits.
"""

# DOC_ID: DOC-CORE-ENGINE-DAEMON-ORCHESTRATOR-202

from __future__ import annotations

import json
import logging
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

# Optional database integration
try:
    from core.state.db import Database, get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    Database = None
    get_db = None


@dataclass
class DaemonConfig:
    """Configuration for daemon orchestrator."""
    
    max_concurrent_runs: int = 4
    poll_interval_seconds: float = 5.0
    auto_cleanup_completed: bool = True
    log_dir: Optional[Path] = None
    minipipe_command: str = "python -m src.minipipe.orchestrator"


class DaemonOrchestrator:
    """
    Background daemon for managing multiple concurrent runs.
    
    Responsibilities:
    - Poll for pending runs
    - Start runs up to concurrency limit
    - Monitor running processes
    - Cleanup completed runs
    """
    
    def __init__(
        self,
        config: Optional[DaemonConfig] = None,
        db: Optional[Database] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize daemon orchestrator.
        
        Args:
            config: Daemon configuration
            db: Database instance
            logger: Logger instance
        """
        self.config = config or DaemonConfig()
        self.db = db
        self.logger = logger or self._setup_logger()
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.should_stop = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Ensure log directory exists
        if self.config.log_dir:
            self.config.log_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup default logger."""
        logger = logging.getLogger("daemon_orchestrator")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.should_stop = True
    
    def start(self) -> None:
        """
        Start daemon main loop.
        
        Runs until interrupted by signal or error.
        """
        self.logger.info("Daemon orchestrator starting...")
        self.logger.info(f"Config: max_concurrent={self.config.max_concurrent_runs}, "
                        f"poll_interval={self.config.poll_interval_seconds}s")
        
        if not DB_AVAILABLE or not self.db:
            self.logger.warning("Database not available - daemon will not function")
            return
        
        try:
            while not self.should_stop:
                try:
                    # Poll and start pending runs
                    self.poll_and_start_runs()
                    
                    # Check running processes
                    self.check_running_processes()
                    
                    # Sleep until next poll
                    time.sleep(self.config.poll_interval_seconds)
                
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}", exc_info=True)
                    time.sleep(self.config.poll_interval_seconds)
        
        finally:
            self.cleanup()
    
    def poll_and_start_runs(self) -> None:
        """Find pending runs and start them if capacity available."""
        if not self.db:
            return
        
        # Check if we have capacity
        current_count = len(self.running_processes)
        if current_count >= self.config.max_concurrent_runs:
            self.logger.debug(f"At capacity: {current_count}/{self.config.max_concurrent_runs}")
            return
        
        # Fetch pending runs
        pending_runs = self._fetch_pending_runs(
            limit=self.config.max_concurrent_runs - current_count
        )
        
        if not pending_runs:
            self.logger.debug("No pending runs found")
            return
        
        # Start runs
        for run in pending_runs:
            if len(self.running_processes) >= self.config.max_concurrent_runs:
                break
            
            run_id = run["run_id"]
            self.logger.info(f"Starting run: {run_id}")
            
            try:
                self.start_run(run_id)
            except Exception as e:
                self.logger.error(f"Failed to start run {run_id}: {e}", exc_info=True)
    
    def _fetch_pending_runs(self, limit: int = 10) -> List[Dict]:
        """Fetch pending runs from database."""
        if not self.db:
            return []
        
        try:
            cursor = self.db.conn.execute(
                """
                SELECT run_id, project_id, phase_id, created_at, metadata
                FROM runs
                WHERE state = 'PENDING'
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (limit,)
            )
            
            runs = []
            for row in cursor.fetchall():
                run_id, project_id, phase_id, created_at, metadata = row
                runs.append({
                    "run_id": run_id,
                    "project_id": project_id,
                    "phase_id": phase_id,
                    "created_at": created_at,
                    "metadata": metadata,
                })
            
            return runs
        
        except Exception as e:
            self.logger.error(f"Error fetching pending runs: {e}")
            return []
    
    def start_run(self, run_id: str) -> None:
        """
        Spawn subprocess to execute a run.
        
        Args:
            run_id: Run identifier to start
        """
        # Build command
        cmd = self.config.minipipe_command.split() + ["--run-id", run_id]
        
        # Setup log files if log directory is configured
        stdout_file = None
        stderr_file = None
        
        if self.config.log_dir:
            stdout_path = self.config.log_dir / f"{run_id}.stdout.log"
            stderr_path = self.config.log_dir / f"{run_id}.stderr.log"
            
            stdout_file = open(stdout_path, "w")
            stderr_file = open(stderr_path, "w")
            
            self.logger.info(f"Logs: {stdout_path}, {stderr_path}")
        
        # Spawn subprocess
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=stdout_file or subprocess.DEVNULL,
                stderr=stderr_file or subprocess.DEVNULL,
                start_new_session=True,  # Detach from parent
            )
            
            self.running_processes[run_id] = proc
            self.logger.info(f"Started run {run_id} (PID: {proc.pid})")
        
        except Exception as e:
            if stdout_file:
                stdout_file.close()
            if stderr_file:
                stderr_file.close()
            raise
    
    def check_running_processes(self) -> None:
        """Poll running processes and cleanup completed ones."""
        for run_id in list(self.running_processes.keys()):
            proc = self.running_processes[run_id]
            
            # Check if process has finished
            exit_code = proc.poll()
            
            if exit_code is not None:
                # Process finished
                self.logger.info(f"Run {run_id} completed (exit_code={exit_code})")
                
                # Remove from tracking
                del self.running_processes[run_id]
                
                # Cleanup if configured
                if self.config.auto_cleanup_completed:
                    self._cleanup_run(run_id, exit_code)
    
    def _cleanup_run(self, run_id: str, exit_code: int) -> None:
        """
        Cleanup completed run.
        
        Args:
            run_id: Run identifier
            exit_code: Process exit code
        """
        # Update run state in database
        if self.db and exit_code == 0:
            try:
                self.db.conn.execute(
                    """
                    UPDATE runs
                    SET state = 'SUCCEEDED', updated_at = ?
                    WHERE run_id = ?
                    """,
                    (datetime.now(UTC).isoformat() + "Z", run_id)
                )
                self.db.conn.commit()
                self.logger.info(f"Marked run {run_id} as SUCCEEDED")
            except Exception as e:
                self.logger.error(f"Failed to update run {run_id}: {e}")
    
    def stop_run(self, run_id: str, timeout: float = 30.0) -> bool:
        """
        Stop a running run gracefully.
        
        Args:
            run_id: Run identifier to stop
            timeout: Timeout in seconds for graceful shutdown
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if run_id not in self.running_processes:
            self.logger.warning(f"Run {run_id} not found in running processes")
            return False
        
        proc = self.running_processes[run_id]
        
        # Send SIGTERM for graceful shutdown
        self.logger.info(f"Stopping run {run_id} (PID: {proc.pid})...")
        proc.terminate()
        
        try:
            # Wait for graceful shutdown
            proc.wait(timeout=timeout)
            self.logger.info(f"Run {run_id} stopped gracefully")
            del self.running_processes[run_id]
            return True
        
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown failed
            self.logger.warning(f"Run {run_id} did not stop gracefully, force killing...")
            proc.kill()
            proc.wait()
            del self.running_processes[run_id]
            return True
    
    def cleanup(self) -> None:
        """Cleanup all running processes before shutdown."""
        self.logger.info("Cleaning up running processes...")
        
        for run_id in list(self.running_processes.keys()):
            self.stop_run(run_id, timeout=10.0)
        
        self.logger.info("Daemon orchestrator stopped")
    
    def get_status(self) -> Dict:
        """
        Get daemon status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "running_count": len(self.running_processes),
            "max_concurrent": self.config.max_concurrent_runs,
            "capacity_available": self.config.max_concurrent_runs - len(self.running_processes),
            "running_runs": list(self.running_processes.keys()),
        }


def load_config(config_path: Optional[Path] = None) -> DaemonConfig:
    """
    Load daemon configuration from file.
    
    Args:
        config_path: Path to config file (JSON)
    
    Returns:
        DaemonConfig instance
    """
    if not config_path or not config_path.exists():
        return DaemonConfig()
    
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
        
        return DaemonConfig(
            max_concurrent_runs=data.get("max_concurrent_runs", 4),
            poll_interval_seconds=data.get("poll_interval_seconds", 5.0),
            auto_cleanup_completed=data.get("auto_cleanup_completed_runs", True),
            log_dir=Path(data["log_dir"]) if "log_dir" in data else None,
            minipipe_command=data.get("minipipe_command", "python -m src.minipipe.orchestrator"),
        )
    
    except Exception as e:
        logging.error(f"Failed to load config from {config_path}: {e}")
        return DaemonConfig()


def run_daemon(
    config_path: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> None:
    """
    Run the daemon orchestrator.
    
    Args:
        config_path: Path to config file
        db_path: Path to SQLite database
    """
    config = load_config(config_path)
    
    db = None
    if DB_AVAILABLE and db_path:
        db = Database(db_path)
        db.connect()
    
    daemon = DaemonOrchestrator(config=config, db=db)
    daemon.start()


__all__ = ["DaemonOrchestrator", "DaemonConfig", "run_daemon", "load_config"]
