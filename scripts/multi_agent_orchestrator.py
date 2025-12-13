#!/usr/bin/env python3
"""
Multi-Agent Orchestrator for Workstream Execution
Automates parallel execution of workstreams across multiple AI agents
"""

import asyncio
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx

from worktree_manager import WorktreeManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('orchestrator')


# ============================================================================
# Workstream Dependency Graph
# ============================================================================

class WorkstreamGraph:
    """Build and analyze workstream dependency graph"""
    
    def __init__(self, workstreams_dir: Path):
        self.workstreams_dir = workstreams_dir
        self.graph = nx.DiGraph()
        self._load_workstreams()
    
    def _load_workstreams(self):
        """Load all workstream JSON files and build graph"""
        for ws_file in sorted(self.workstreams_dir.glob("ws-*.json")):
            try:
                with open(ws_file) as f:
                    ws = json.load(f)
                
                ws_id = ws["id"]
                depends_on = ws.get("depends_on", [])
                
                # Add node with all metadata
                self.graph.add_node(ws_id, **ws)
                
                # Add edges (dependency → workstream)
                for dep in depends_on:
                    self.graph.add_edge(dep, ws_id)
                    
                logger.debug(f"Loaded {ws_id}: {len(depends_on)} dependencies")
            except Exception as e:
                logger.error(f"Failed to load {ws_file}: {e}")
    
    def get_ready_workstreams(self, completed: Set[str]) -> List[str]:
        """Get workstreams ready to execute (all dependencies met)"""
        ready = []
        for ws_id in self.graph.nodes():
            if ws_id in completed:
                continue
            
            # Check if all dependencies are completed
            deps = list(self.graph.predecessors(ws_id))
            if all(dep in completed for dep in deps):
                ready.append(ws_id)
        
        return ready
    
    def get_independent_workstreams(self) -> List[str]:
        """Get workstreams with no dependencies"""
        return [
            ws_id for ws_id in self.graph.nodes()
            if self.graph.in_degree(ws_id) == 0
        ]
    
    def get_workstream_data(self, ws_id: str) -> Dict:
        """Get workstream metadata"""
        return dict(self.graph.nodes[ws_id])
    
    def topological_sort(self) -> List[str]:
        """Get topologically sorted workstream order"""
        return list(nx.topological_sort(self.graph))


# ============================================================================
# Agent Pool
# ============================================================================

class AgentType(Enum):
    AIDER = "aider"
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"


@dataclass
class Agent:
    id: str
    type: AgentType
    status: str  # "idle", "busy", "failed"
    current_workstream: Optional[str] = None
    assigned_track: Optional[str] = None


class AgentPool:
    """Manage pool of AI agents"""
    
    def __init__(self, agent_configs: List[Dict]):
        self.agents = [
            Agent(
                id=cfg["id"],
                type=AgentType(cfg["type"]),
                status="idle",
                assigned_track=cfg.get("track")
            )
            for cfg in agent_configs
        ]
        logger.info(f"Initialized agent pool with {len(self.agents)} agents")
    
    def get_available_agent(self, track: Optional[str] = None) -> Optional[Agent]:
        """Get first available agent, optionally for specific track"""
        for agent in self.agents:
            if agent.status != "idle":
                continue
            if track and agent.assigned_track and agent.assigned_track != track:
                continue
            return agent
        return None
    
    def assign_workstream(self, agent: Agent, workstream_id: str, track: str):
        """Assign workstream to agent"""
        agent.status = "busy"
        agent.current_workstream = workstream_id
        agent.assigned_track = track
        logger.info(f"Assigned {workstream_id} to {agent.id}")
    
    def release_agent(self, agent: Agent):
        """Mark agent as available"""
        agent.status = "idle"
        agent.current_workstream = None
        logger.debug(f"Released {agent.id}")
    
    async def execute_workstream(
        self, 
        agent: Agent, 
        workstream_id: str,
        workstream_data: Dict
    ) -> Dict:
        """Execute workstream using specified agent (no worktree)"""
        
        tool = workstream_data.get("tool", "aider")
        
        if tool == "aider":
            cmd = self._build_aider_command(workstream_id, workstream_data)
        elif tool == "codex":
            cmd = self._build_codex_command(workstream_id, workstream_data)
        else:
            cmd = self._build_generic_command(workstream_id, workstream_data)
        
        logger.info(f"Executing {workstream_id} with {tool}")
        
        # Execute asynchronously
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=Path.cwd()
        )
        
        stdout, stderr = await proc.communicate()
        
        success = proc.returncode == 0
        
        return {
            "workstream_id": workstream_id,
            "agent_id": agent.id,
            "exit_code": proc.returncode,
            "stdout": stdout.decode()[:1000],  # Limit output
            "stderr": stderr.decode()[:1000],
            "success": success
        }
    
    async def execute_workstream_in_worktree(
        self,
        agent: Agent,
        workstream_id: str,
        workstream_data: Dict,
        worktree_path: Path
    ) -> Dict:
        """Execute workstream in isolated worktree"""
        
        tool = workstream_data.get("tool", "aider")
        
        if tool == "aider":
            cmd = self._build_aider_command_with_worktree(
                workstream_id, 
                workstream_data, 
                worktree_path
            )
        elif tool == "codex":
            cmd = self._build_codex_command_with_worktree(
                workstream_id, 
                workstream_data,
                worktree_path
            )
        else:
            cmd = self._build_generic_command_with_worktree(
                workstream_id, 
                workstream_data,
                worktree_path
            )
        
        logger.info(f"Executing {workstream_id} with {tool} in {worktree_path}")
        
        # Execute in worktree directory
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=worktree_path
        )
        
        stdout, stderr = await proc.communicate()
        
        return {
            "workstream_id": workstream_id,
            "agent_id": agent.id,
            "exit_code": proc.returncode,
            "stdout": stdout.decode()[:1000],
            "stderr": stderr.decode()[:1000],
            "success": proc.returncode == 0,
            "worktree": str(worktree_path)
        }
    
    def _build_aider_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build aider command for workstream"""
        files = " ".join(ws_data.get("files_scope", []))
        tasks = ws_data.get("tasks", [])
        task_text = "\\n".join(tasks)
        
        return f"""
        aider {files} \\
          --message "{task_text}" \\
          --yes \\
          --auto-commits \\
          --edit-format whole \\
          --model gpt-4-turbo-preview
        """
    
    def _build_codex_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build codex command for workstream"""
        return f"codex execute --workstream workstreams/{ws_id}.json"
    
    def _build_generic_command(self, ws_id: str, ws_data: Dict) -> str:
        """Build generic execution command"""
        return f"python scripts/execute_workstream.py {ws_id}"
    
    def _build_aider_command_with_worktree(
        self, 
        ws_id: str, 
        ws_data: Dict,
        worktree_path: Path
    ) -> str:
        """Build aider command to run in worktree"""
        files = " ".join(ws_data.get("files_scope", []))
        tasks = ws_data.get("tasks", [])
        task_text = "\\n".join(tasks)
        
        # Note: aider runs in worktree directory (cwd parameter)
        return f"""
        aider {files} \\
          --message "{task_text}" \\
          --yes \\
          --auto-commits \\
          --edit-format whole
        """
    
    def _build_codex_command_with_worktree(
        self, 
        ws_id: str, 
        ws_data: Dict,
        worktree_path: Path
    ) -> str:
        """Build codex command to run in worktree"""
        return f"codex execute --workstream workstreams/{ws_id}.json"
    
    def _build_generic_command_with_worktree(
        self, 
        ws_id: str, 
        ws_data: Dict,
        worktree_path: Path
    ) -> str:
        """Build generic command to run in worktree"""
        return f"python scripts/execute_workstream.py {ws_id}"


# ============================================================================
# State Manager
# ============================================================================

class StateManager:
    """Manage workstream execution state in SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workstream_status (
                workstream_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                agent_id TEXT,
                track TEXT,
                started_at TEXT,
                completed_at TEXT,
                exit_code INTEGER,
                attempt INTEGER DEFAULT 1,
                error_message TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                workstream_id TEXT NOT NULL,
                agent_id TEXT,
                event_type TEXT NOT NULL,
                message TEXT
            )
        """)
        conn.commit()
        conn.close()
        logger.info(f"Initialized state database: {self.db_path}")
    
    def mark_started(self, ws_id: str, agent_id: str, track: str):
        """Mark workstream as started"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO workstream_status 
            (workstream_id, status, agent_id, track, started_at)
            VALUES (?, 'running', ?, ?, ?)
        """, (ws_id, agent_id, track, datetime.now().isoformat()))
        
        conn.execute("""
            INSERT INTO execution_log (timestamp, workstream_id, agent_id, event_type)
            VALUES (?, ?, ?, 'started')
        """, (datetime.now().isoformat(), ws_id, agent_id))
        
        conn.commit()
        conn.close()
    
    def mark_completed(self, ws_id: str, exit_code: int, error_msg: str = ""):
        """Mark workstream as completed or failed"""
        status = "completed" if exit_code == 0 else "failed"
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE workstream_status
            SET status = ?, completed_at = ?, exit_code = ?, error_message = ?
            WHERE workstream_id = ?
        """, (status, datetime.now().isoformat(), exit_code, error_msg, ws_id))
        
        conn.execute("""
            INSERT INTO execution_log (timestamp, workstream_id, event_type, message)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), ws_id, status, error_msg))
        
        conn.commit()
        conn.close()
    
    def get_completed_workstreams(self) -> Set[str]:
        """Get set of completed workstream IDs"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT workstream_id FROM workstream_status 
            WHERE status = 'completed'
        """)
        completed = {row[0] for row in cur.fetchall()}
        conn.close()
        return completed
    
    def get_running_workstreams(self) -> List[str]:
        """Get list of currently running workstream IDs"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute("""
            SELECT workstream_id FROM workstream_status 
            WHERE status = 'running'
        """)
        running = [row[0] for row in cur.fetchall()]
        conn.close()
        return running


# ============================================================================
# Main Orchestrator
# ============================================================================

class MultiAgentOrchestrator:
    """Main orchestrator for multi-agent workstream execution"""
    
    def __init__(
        self,
        workstreams_dir: Path,
        state_db: Path,
        agent_configs: List[Dict],
        track_assignments: Dict[str, List[str]],
        use_worktrees: bool = True
    ):
        self.graph = WorkstreamGraph(workstreams_dir)
        self.state = StateManager(state_db)
        self.agents = AgentPool(agent_configs)
        self.track_assignments = track_assignments
        self.use_worktrees = use_worktrees
        
        # Initialize worktree manager if enabled
        if self.use_worktrees:
            self.worktree_manager = WorktreeManager(
                base_repo=Path.cwd(),
                worktree_root=Path(".worktrees")
            )
            logger.info("Worktree isolation: ENABLED")
        else:
            self.worktree_manager = None
            logger.info("Worktree isolation: DISABLED")
        
        logger.info("=== Multi-Agent Orchestrator Initialized ===")
        logger.info(f"Total workstreams: {len(self.graph.graph.nodes())}")
        logger.info(f"Independent workstreams: {len(self.graph.get_independent_workstreams())}")
        logger.info(f"Agents: {len(self.agents.agents)}")
    
    async def execute_all(self):
        """Execute all workstreams with dependency management"""
        
        iteration = 0
        
        while True:
            iteration += 1
            completed = self.state.get_completed_workstreams()
            running = self.state.get_running_workstreams()
            total = len(self.graph.graph.nodes())
            
            logger.info(f"=== Iteration {iteration} === Completed: {len(completed)}/{total}, Running: {len(running)}")
            
            # Check if all done
            if len(completed) >= total:
                logger.info("🎉 All workstreams completed!")
                break
            
            # Get ready workstreams
            ready = self.graph.get_ready_workstreams(completed)
            # Remove already running
            ready = [ws for ws in ready if ws not in running]
            
            if not ready:
                logger.info("Waiting for running workstreams to complete...")
                await asyncio.sleep(10)
                continue
            
            logger.info(f"Ready to execute: {ready}")
            
            # Assign ready workstreams to available agents
            tasks = []
            for ws_id in ready:
                track = self._get_track_for_workstream(ws_id)
                agent = self.agents.get_available_agent(track)
                
                if not agent:
                    logger.debug(f"No available agent for {ws_id} (track: {track})")
                    continue
                
                # Assign and execute
                ws_data = self.graph.get_workstream_data(ws_id)
                self.agents.assign_workstream(agent, ws_id, track)
                self.state.mark_started(ws_id, agent.id, track)
                
                # Create async task
                task = self._execute_workstream_async(agent, ws_id, ws_data)
                tasks.append(task)
            
            if not tasks:
                logger.info("No agents available, waiting...")
                await asyncio.sleep(5)
                continue
            
            # Execute tasks in parallel
            logger.info(f"Executing {len(tasks)} workstreams in parallel")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Execution error: {result}")
                    continue
                
                ws_id = result["workstream_id"]
                agent_id = result["agent_id"]
                success = result["success"]
                
                # Update state
                error_msg = result["stderr"] if not success else ""
                self.state.mark_completed(ws_id, result["exit_code"], error_msg)
                
                # Release agent
                agent = next(a for a in self.agents.agents if a.id == agent_id)
                self.agents.release_agent(agent)
                
                if success:
                    logger.info(f"✅ {ws_id} completed by {agent_id}")
                else:
                    logger.error(f"❌ {ws_id} failed by {agent_id}: {error_msg[:200]}")
        
        # Generate final report
        self._generate_report()
    
    async def _execute_workstream_async(self, agent, ws_id, ws_data):
        """Execute workstream asynchronously with optional worktree isolation"""
        
        if self.use_worktrees and self.worktree_manager:
            # Execute in isolated worktree
            branch_name = f"ws/{ws_id}/{agent.id}"
            
            try:
                # Create worktree
                worktree_path = self.worktree_manager.create_agent_worktree(
                    agent_id=agent.id,
                    branch_name=branch_name,
                    workstream_id=ws_id
                )
                
                logger.info(f"🚀 Starting {ws_id} on {agent.id} in worktree {worktree_path}")
                
                # Execute in worktree
                result = await self.agents.execute_workstream_in_worktree(
                    agent=agent,
                    workstream_id=ws_id,
                    workstream_data=ws_data,
                    worktree_path=worktree_path
                )
                
                # Merge back to main on success
                if result["success"]:
                    logger.info(f"Merging {branch_name} to main...")
                    merge_success = self.worktree_manager.merge_worktree_changes(
                        branch_name=branch_name,
                        target_branch="main"
                    )
                    
                    if not merge_success:
                        logger.error(f"Merge failed for {branch_name}")
                        result["success"] = False
                        result["error_message"] = "Merge conflict"
                
                # Cleanup worktree
                self.worktree_manager.cleanup_agent_worktree(agent.id, ws_id)
                
                return result
                
            except Exception as e:
                logger.error(f"Worktree execution failed for {ws_id}: {e}")
                # Cleanup on error
                try:
                    self.worktree_manager.cleanup_agent_worktree(agent.id, ws_id)
                except:
                    pass
                
                return {
                    "workstream_id": ws_id,
                    "agent_id": agent.id,
                    "exit_code": 1,
                    "success": False,
                    "error_message": str(e)
                }
        else:
            # Execute without worktree isolation
            logger.info(f"🚀 Starting {ws_id} on {agent.id} (no worktree)")
            result = await self.agents.execute_workstream(agent, ws_id, ws_data)
            return result
    
    def _get_track_for_workstream(self, ws_id: str) -> str:
        """Determine which track this workstream belongs to"""
        for track, ws_list in self.track_assignments.items():
            if ws_id in ws_list:
                return track
        return "default"
    
    def _generate_report(self):
        """Generate execution report"""
        completed = self.state.get_completed_workstreams()
        total = len(self.graph.graph.nodes())
        
        report = f"""# Multi-Agent Execution Report

Generated: {datetime.now().isoformat()}

## Summary
- Total workstreams: {total}
- Completed: {len(completed)}
- Success rate: {len(completed) / total * 100:.1f}%

## Completed Workstreams
{chr(10).join(f"- ✅ {ws}" for ws in sorted(completed))}

## Execution Timeline
See .state/orchestration.db for detailed logs
"""
        
        report_path = Path("reports/multi_agent_execution_report.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        
        logger.info(f"\n{report}")
        logger.info(f"Report saved to {report_path}")


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    
    # Configuration
    agent_configs = [
        {"id": "agent-1", "type": "aider", "track": "pipeline_plus"},
        {"id": "agent-2", "type": "aider", "track": "core_refactor"},
        {"id": "agent-3", "type": "aider", "track": "error_engine"},
    ]
    
    track_assignments = {
        "pipeline_plus": [
            "ws-22", "ws-23", "ws-24", "ws-25", 
            "ws-26", "ws-27", "ws-28", "ws-29", "ws-30"
        ],
        "core_refactor": [
            "ws-03", "ws-04", "ws-05", "ws-06", 
            "ws-07", "ws-08", "ws-09", "ws-18", "ws-19", "ws-20"
        ],
        "error_engine": [
            "ws-12", "ws-13", "ws-14", "ws-15", 
            "ws-16", "ws-17"
        ]
    }
    
    orchestrator = MultiAgentOrchestrator(
        workstreams_dir=Path("workstreams"),
        state_db=Path(".state/orchestration.db"),
        agent_configs=agent_configs,
        track_assignments=track_assignments
    )
    
    await orchestrator.execute_all()


if __name__ == "__main__":
    asyncio.run(main())
