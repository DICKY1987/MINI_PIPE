# Claude Squad → MINI_PIPE: Comprehensive Pattern Analysis & Integration Guide

**Generated**: 2025-12-07
**Purpose**: Deep comparative analysis to identify patterns worth adopting from Claude Squad into MINI_PIPE
**Status**: Complete Analysis

---

## Executive Summary

This document presents a comprehensive architectural analysis comparing **Claude Squad** (a terminal application for managing multiple AI coding agents) with **MINI_PIPE** (a Python-based orchestration engine for structured execution plans). The goal is to identify which patterns from Claude Squad should be adopted into MINI_PIPE while preserving MINI_PIPE's superior architectural foundations.

**Key Findings**:
- **6 patterns** from Claude Squad are recommended for adoption (with adaptation)
- **8 core strengths** of MINI_PIPE must be preserved as-is
- **4 high-risk areas** require careful mitigation during integration
- **Zero direct code copying** recommended (license incompatibility + language mismatch)

**Recommendation**: Adopt **conceptual patterns only**, implemented from scratch in Python within MINI_PIPE's deterministic, state-machine-based architecture.

---

## Table of Contents

1. [Claude Squad – Key Ideas, Concepts, Processes, Patterns](#1-claude-squad--key-ideas-concepts-processes-patterns)
2. [MINI_PIPE – Architecture and Existing Strengths](#2-mini_pipe--architecture-and-existing-strengths)
3. [Pattern Mapping: Claude Squad → MINI_PIPE](#3-pattern-mapping-claude-squad--minipipe)
4. [Patterns to Copy or Adapt into MINI_PIPE](#4-patterns-to-copy-or-adapt-into-minipipe)
5. [MINI_PIPE – Things Done Better (KEEP-AS-IS)](#5-mini_pipe--things-done-better-keep-as-is)
6. [Integration Plan, Risks, and Next Steps](#6-integration-plan-risks-and-next-steps)
7. [AGENT_SUMMARY (JSON)](#agent_summary-json)

---

# 1. Claude Squad – Key Ideas, Concepts, Processes, Patterns

## 1.1 Architectural Overview

Claude Squad is a **terminal-based multi-agent orchestration system** written in Go that enables parallel execution of AI coding tasks (Claude Code, Aider, Codex, Gemini) in isolated environments. Its core value proposition is:

> "Run multiple AI coding agents simultaneously, review changes before applying them, operate on isolated git branches to prevent conflicts."

**Technology Stack**:
- **Language**: Go
- **Session Isolation**: tmux (terminal multiplexer)
- **Workspace Isolation**: git worktrees (one per task)
- **Interface**: Terminal UI (TUI) with keyboard-driven navigation
- **State Persistence**: JSON files (config.json, state.json per instance)
- **License**: AGPL-3.0 (derivative works must be open source)

**Target Users**: Individual developers or small teams working on codebases with GitHub integration, comfortable with terminal workflows.

---

## 1.2 Core Patterns

### 1.2.1 Instance Management

**PURPOSE**: Track and manage multiple concurrent AI agent sessions as first-class objects.

**MECHANISM**:
- Each "instance" represents one AI agent session working on a specific task
- Instances are created with: `title`, `path` (working directory), `program` (e.g., "claude", "aider")
- Instances persist across application restarts via `storage.SaveInstances()`
- Global limit of 10 concurrent instances to prevent resource exhaustion
- Instance states: `running`, `paused`, `ready` (not started), `terminated`

**STRENGTHS**:
- **Clear abstraction**: An "instance" is a well-defined unit of work with lifecycle management
- **Persistence**: Sessions survive application crashes/restarts
- **Resource management**: Hard limits prevent runaway resource consumption
- **Metadata tracking**: Each instance tracks diff stats, prompt history, and git state

**WEAKNESSES**:
- **Implicit state**: State transitions aren't formally defined (no state machine)
- **Instance limit is arbitrary**: No dynamic resource-based scaling
- **No prioritization**: All instances are equal; no concept of urgency or dependencies
- **Tight coupling to tmux**: Instance lifecycle is bound to tmux session lifecycle

---

### 1.2.2 Git Worktree Per Task

**PURPOSE**: Provide complete isolation between concurrent tasks by using git's worktree feature.

**MECHANISM**:
- Each instance creates a new git worktree (separate working directory on a new branch)
- Worktrees are named/branched based on task identifier
- Changes in one worktree don't affect others
- Before destructive operations (delete instance), validates that branch isn't checked out elsewhere
- Push operations commit changes with timestamped messages

**STRENGTHS**:
- **True isolation**: File changes in different tasks cannot conflict
- **Safe parallelism**: Multiple agents can edit the same file conceptually (in different worktrees)
- **Branch management**: Automatic branch creation per task
- **Cleanup safety**: Validates branch state before deletion

**WEAKNESSES**:
- **Disk overhead**: Each worktree is a full working directory (not space-efficient)
- **Git-only**: Assumes all work happens in a git repository
- **No merging strategy**: No guidance on how to integrate changes from multiple worktrees
- **Orphan risk**: If cleanup fails, worktrees can be left behind

---

### 1.2.3 Tmux Session Per Instance

**PURPOSE**: Provide isolated terminal sessions for each AI agent, allowing attach/detach workflows.

**MECHANISM**:
- Each instance spawns or attaches to a named tmux session
- User can attach to a session to view agent output or provide input
- User can detach (Ctrl-Q) and return later
- Sessions persist independently of the main TUI application
- Daemon can send input to tmux sessions for AutoYes mode

**STRENGTHS**:
- **Session persistence**: Agent continues running even if TUI is closed
- **Interactive access**: User can jump into any session on demand
- **Standard tooling**: Leverages existing tmux ecosystem (panes, scrollback, etc.)
- **Detach/reattach**: Familiar workflow for terminal users

**WEAKNESSES**:
- **tmux dependency**: Hard requirement; won't work on systems without tmux
- **Not portable**: Relies on UNIX-style session management (won't work on Windows without WSL)
- **Process management complexity**: Parent/child process coordination with tmux adds fragility
- **No session logs**: Output only exists in tmux scrollback (ephemeral)

---

### 1.2.4 TUI (Terminal User Interface)

**PURPOSE**: Provide a keyboard-driven interface for managing multiple instances and reviewing changes.

**MECHANISM**:
- List view shows all instances with status, title, and diff stats
- Keyboard shortcuts for common operations:
  - `n`: New instance
  - `N`: New instance with initial prompt
  - `tab`: Switch between preview/diff view
  - `c`: Commit changes and pause
  - `s`: Commit and push to GitHub
  - `r`: Resume paused session
  - `D`: Delete instance
- State-based overlays (new instance form, help screen, confirmation dialogs)
- 500ms polling ticker to update instance metadata

**STRENGTHS**:
- **Keyboard-first**: Fast workflow for power users
- **Visual feedback**: Diff stats and status updates visible at a glance
- **Modal interactions**: Overlays for multi-step operations
- **Real-time updates**: Polling keeps UI current

**WEAKNESSES**:
- **Terminal-only**: No web UI, no graphical option
- **Polling overhead**: 500ms ticks for all instances can be inefficient
- **No filtering/search**: With many instances, navigation becomes difficult
- **State management complexity**: Overlays and state transitions are implicit, not formalized

---

### 1.2.5 Daemon / Background Execution

**PURPOSE**: Enable unattended execution where the daemon automatically responds to prompts without user intervention.

**MECHANISM**:
- `LaunchDaemon()` spawns a detached background process
- Daemon loads all instances and continuously polls them
- "AutoYes mode": Automatically sends input (Enter) when an instance has a new prompt
- Daemon updates diff stats after handling prompts
- PID file tracks daemon process for lifecycle management (`StopDaemon()` kills by PID)
- Graceful shutdown on SIGINT/SIGTERM

**STRENGTHS**:
- **Unattended operation**: Tasks can progress without user presence
- **Continuous progress**: No need for user to manually approve each step
- **Process isolation**: Daemon runs independently of TUI
- **Graceful shutdown**: Signal handling for clean termination

**WEAKNESSES**:
- **AutoYes risk**: Blindly accepting all prompts can be dangerous (no quality gates)
- **Polling-based**: Continuous polling wastes CPU when instances are idle
- **No logging**: Daemon actions aren't logged to disk (hard to debug)
- **PID file fragility**: If PID file is deleted or process crashes, daemon becomes orphaned

---

### 1.2.6 Config/State Persistence (JSON)

**PURPOSE**: Store instance configuration and runtime state to survive application restarts.

**MECHANISM**:
- Each instance has config/state stored in JSON files
- `storage.SaveInstances()` persists all instances
- On startup, `storage.LoadInstances()` restores previous session state
- Metadata includes: title, path, program, diff stats, git branch info

**STRENGTHS**:
- **Simple format**: JSON is human-readable and easy to debug
- **Portable**: State files can be copied/backed up
- **Stateful sessions**: Resuming work after a restart is seamless

**WEAKNESSES**:
- **No schema validation**: JSON structure is implicit (no JSON schema)
- **Concurrent access**: No locking; if TUI and daemon both write, corruption is possible
- **No versioning**: Schema changes could break old state files
- **No event history**: Only current state is saved; no audit trail of transitions

---

## 1.3 Strengths and Limitations

### Strengths

| Strength | Impact |
|----------|--------|
| **Session Isolation** | Parallel tasks don't interfere with each other |
| **Git Integration** | Automatic branch management per task |
| **Interactive Workflow** | User can attach/detach from sessions flexibly |
| **Background Mode** | Unattended execution for long-running tasks |
| **Terminal-Native** | Fast, lightweight, no browser required |

### Limitations

| Limitation | Impact on MINI_PIPE Adoption |
|------------|------------------------------|
| **AGPL-3.0 License** | Cannot copy code; must reimplement concepts |
| **Go Language** | No direct code reuse in Python ecosystem |
| **Tmux Dependency** | Portability issues (Windows, headless environments) |
| **Polling-Based Architecture** | Inefficient compared to event-driven systems |
| **No Formal State Machine** | State transitions are implicit and undocumented |
| **No Dependency Management** | Instances are independent; no task dependencies |
| **No Quality Gates** | AutoYes mode accepts all changes without validation |
| **GitHub-Specific** | Assumes GitHub for PR creation and push operations |
| **No Structured Plans** | Tasks are ad-hoc; no multi-phase execution plans |

---

# 2. MINI_PIPE – Architecture and Existing Strengths

## 2.1 Core Modules and Responsibilities

MINI_PIPE is a **deterministic, pattern-based orchestration engine** designed for multi-phase, multi-tool AI development workflows. It operates on **structured execution plans** (JSON-based) and enforces **state machines, quality gates, and event-driven coordination**.

### Module Hierarchy

```
MINI_PIPE Architecture
│
├── ACMS Layer (AI Code Management System)
│   ├── controller.py          # Golden path orchestrator
│   ├── gap_registry.py        # Gap analysis and storage
│   ├── execution_planner.py   # Workstream clustering
│   ├── phase_plan_compiler.py # Plan generation
│   ├── guardrails.py          # Pattern enforcement
│   └── minipipe_adapter.py    # Adapter to core engine
│
├── Core Engine
│   ├── orchestrator.py        # Run lifecycle, state machine
│   ├── scheduler.py           # Dependency resolution, task waves
│   ├── router.py              # Task-to-tool routing
│   ├── executor.py            # Task execution, adapter integration
│   ├── tools.py               # Tool adapter layer
│   └── process_spawner.py     # Worker process management
│
├── Resilience Layer
│   ├── circuit_breaker.py     # Failure isolation
│   ├── retry.py               # Exponential backoff
│   ├── resilient_executor.py  # Combined patterns
│   └── recovery.py            # Recovery orchestration
│
├── Patch Management
│   ├── patch_converter.py     # Normalize patches
│   └── patch_ledger.py        # Patch state machine
│
└── Automation Triggers
    ├── monitoring_trigger.py       # Auto-launch monitoring
    ├── request_builder_trigger.py  # Phase 1→2 transition
    └── router_trigger.py           # Phase 3→4 transition
```

---

## 2.2 Execution Model (Plans, Runs, Steps, Tasks)

MINI_PIPE operates on a **four-level hierarchy**:

### 1. **Plan** (Static Definition)
- **What**: A JSON file defining steps, dependencies, commands, and metadata
- **Schema**: Validated against `Plan` Pydantic model
- **Variable Substitution**: Supports `${VAR}` placeholders resolved at runtime
- **Example**: `plans/phase1_bootstrap.json`

### 2. **Run** (Execution Instance)
- **What**: A single execution of a plan
- **Lifecycle**: `pending → running → succeeded/failed/quarantined/canceled`
- **State Machine**: Enforced by `RunStateMachine` with validated transitions
- **Persistence**: Stored in `orchestration.db` (SQLite)
- **Immutability**: Runs are append-only; no retroactive edits

### 3. **Step Attempt** (Task Execution Unit)
- **What**: A single invocation of a tool (e.g., run pytest, run aider)
- **Lifecycle**: `running → succeeded/failed/canceled`
- **Retry Logic**: Configurable via plan globals or per-step `retries` field
- **Output**: Produces `output_patch_id` (file path to patch artifact)

### 4. **Task** (Scheduled Work)
- **What**: A unit of work in the scheduler with dependencies
- **Status**: `pending → ready → running → completed/failed`
- **Dependency Graph**: DAG-based; scheduler finds runnable tasks
- **Routing**: Router selects tool based on `task_kind` and capabilities

---

## 2.3 Where MINI_PIPE is Already Strong

### Strength 1: **Deterministic Execution**

**What**: Plans are DAG-based, repeatable, and fully specified upfront.

**Why It Matters**:
- No ad-hoc decisions during execution
- Reproducible across environments
- Testable and predictable

**Contrast with Claude Squad**:
- Claude Squad: Interactive, user-driven, no predetermined execution path
- MINI_PIPE: Plan-driven, deterministic, machine-executable

**Verdict**: **KEEP-AS-IS**. This is MINI_PIPE's core identity.

---

### Strength 2: **State Machine Enforcement**

**What**: All state transitions (runs, steps, patches) are validated against explicit state machines.

**Why It Matters**:
- Prevents invalid transitions (e.g., completing a canceled run)
- Auditability: Every transition is logged
- Debugging: Easy to trace why a run is in a certain state

**Contrast with Claude Squad**:
- Claude Squad: Implicit states, transitions handled in UI logic
- MINI_PIPE: Formal state machines (`RunStateMachine`, `StepStateMachine`, `PatchLedger`)

**Verdict**: **KEEP-AS-IS**. Critical for correctness and auditability.

---

### Strength 3: **Event-Driven Architecture**

**What**: `EventBus` emits typed events (`run_started`, `step_completed`, etc.) for observability and automation.

**Why It Matters**:
- Decouples components (orchestrator doesn't need to know about monitoring UI)
- Enables automation triggers (e.g., `PLANNING_COMPLETE` → auto-start execution)
- Telemetry and logging are first-class

**Contrast with Claude Squad**:
- Claude Squad: Polling-based (500ms ticker), event handling implicit in UI
- MINI_PIPE: Event-driven, with `EventBus` as SSOT for events

**Verdict**: **KEEP-AS-IS**. Superior to polling for scalability and reactivity.

---

### Strength 4: **Separation of Concerns**

**What**: Clear boundaries between planning, routing, scheduling, execution, and tooling.

**Why It Matters**:
- Each component has a single responsibility
- Easy to test in isolation
- Swappable implementations (e.g., mock vs real adapters)

**Modules**:
- **Controller**: High-level orchestration
- **Planner**: Converts gaps → workstreams → plans
- **Router**: Task → tool mapping
- **Scheduler**: Dependency resolution
- **Executor**: Tool invocation
- **Adapters**: Tool-specific integration

**Contrast with Claude Squad**:
- Claude Squad: UI, session management, and execution are intertwined in `app.go`
- MINI_PIPE: Clear layers with adapter pattern for extensibility

**Verdict**: **KEEP-AS-IS**. Architectural foundation for maintainability.

---

### Strength 5: **Quality Gates and Guardrails**

**What**: Guardrails system enforces patterns and detects anti-patterns during execution.

**Why It Matters**:
- Prevents common mistakes (e.g., hallucinated files, infinite loops)
- Pattern-based validation ensures compliance with best practices
- Anti-pattern detection catches problematic behaviors early

**Features**:
- `PatternGuardrails`: Enforces expected patterns (e.g., "all patches must be validated")
- `AntiPatternDetector`: Flags dangerous behaviors (e.g., "same error 3 times in a row")
- `PatchLedger`: State machine for patch lifecycle with quarantine support

**Contrast with Claude Squad**:
- Claude Squad: AutoYes mode accepts all changes without validation
- MINI_PIPE: Multi-layer validation with quarantine fallback

**Verdict**: **KEEP-AS-IS**. Critical for production safety.

---

### Strength 6: **Patch Lifecycle Management**

**What**: `PatchLedger` tracks patches through a formal state machine: `created → validated → queued → applied → verified → committed`.

**Why It Matters**:
- Ensures patches go through validation and testing before commit
- Rollback support for failed patches
- Quarantine mechanism for unsafe patches

**States**:
- `created`, `validated`, `queued`, `applied`, `verified`, `committed`, `rolled_back`, `quarantined`, `dropped`

**Contrast with Claude Squad**:
- Claude Squad: Changes are either accepted or rejected; no intermediate validation states
- MINI_PIPE: Full lifecycle with gates and rollback

**Verdict**: **KEEP-AS-IS**. Superior safety model.

---

### Strength 7: **Multi-Tool Support with Routing**

**What**: `TaskRouter` routes tasks to tools based on capabilities, strategies (fixed, round-robin, metrics), and operation kinds.

**Why It Matters**:
- Tool-agnostic orchestration (works with Aider, pytest, Black, etc.)
- Load balancing and failover
- Contract-based tool integration via UET tool profiles

**Routing Strategies**:
- `fixed`: Always use the same tool
- `round_robin`: Distribute tasks evenly
- `metrics`: Select based on success rate and latency

**Contrast with Claude Squad**:
- Claude Squad: One tool per instance; no dynamic routing
- MINI_PIPE: Dynamic, capability-based routing with metrics

**Verdict**: **KEEP-AS-IS**. More flexible and scalable.

---

### Strength 8: **Resilience Patterns**

**What**: Circuit breakers, retries with exponential backoff, recovery coordination.

**Why It Matters**:
- Transient failures don't abort entire runs
- Cascading failures are prevented
- Auto-recovery when services come back online

**Components**:
- `CircuitBreaker`: Opens after N failures, prevents further requests
- `RetryStrategy`: Exponential backoff with jitter
- `RecoveryCoordinator`: Orchestrates retries across failed tasks

**Contrast with Claude Squad**:
- Claude Squad: No retry logic; instances fail and require manual restart
- MINI_PIPE: Production-grade resilience patterns

**Verdict**: **KEEP-AS-IS**. Essential for production deployments.

---

# 3. Pattern Mapping: Claude Squad → MINI_PIPE

This section categorizes each major Claude Squad pattern into:
- **ADOPT-AS-IS (CONCEPTUALLY)**: Valuable pattern; MINI_PIPE lacks equivalent → Adopt the idea
- **ADAPT-WITH-CONSTRAINTS**: Useful pattern but must fit MINI_PIPE's deterministic model → Adapt carefully
- **REJECT / DO-NOT-ADOPT**: Conflicts with MINI_PIPE's goals or is already inferior to MINI_PIPE's approach

---

## Pattern 1: Instance Management (Session Tracking)

**Claude Squad Pattern**:
- Track AI agent sessions as first-class objects with persistence
- Store session metadata (title, path, program, diff stats, git state)
- Session lifecycle: create, start, pause, resume, delete

**Category**: **ADAPT-WITH-CONSTRAINTS**

**Rationale**:
- **Value**: MINI_PIPE currently treats tasks as ephemeral (they exist only during a run). Adding session persistence would enable:
  - Resume long-running AI tasks after restarts
  - Track multiple AI agents working on different parts of a project
  - Associate patches/runs with specific sessions
- **Constraint**: Must fit into MINI_PIPE's deterministic model:
  - Sessions should be tied to runs (not independent)
  - Session state must be part of the formal state machine
  - No interactive prompts during execution (conflicts with determinism)

**Recommended Adaptation**:
- Create a `SessionRegistry` that tracks long-lived AI agent sessions
- Each session is associated with a `project_id`, `workstream_id`, and optional `run_id`
- Session state: `created`, `active`, `paused`, `completed`, `failed`
- Sessions persist in SQLite (same DB as runs)
- Sessions are **read-only during execution** (no interactive modifications)

---

## Pattern 2: Git Worktree Per Task

**Claude Squad Pattern**:
- Each instance creates a git worktree on a new branch
- Worktrees provide complete isolation between concurrent tasks
- Cleanup validates branch state before deletion

**Category**: **ADOPT-AS-IS (CONCEPTUALLY)**

**Rationale**:
- **Value**: MINI_PIPE currently executes all tasks in the same working directory. This causes conflicts when:
  - Multiple tasks modify the same files
  - A task fails and leaves the working directory dirty
  - Parallel execution of git-based tasks (e.g., Aider on different features)
- **No Conflict**: Worktrees don't interfere with determinism; they're just isolated workspaces
- **Implementation**: Add a `WorktreeManager` component to MINI_PIPE

**Recommended Adoption**:
- Create `WorktreeManager` class in `src/minipipe/worktree_manager.py`
- Managed by orchestrator: creates worktree before task execution, cleans up after
- Worktree naming: `{run_id}_{step_id}` for traceability
- Integrates with executor: each step gets a `workspace_path` (worktree directory)
- Cleanup strategy: Archive worktrees on failure (for debugging), delete on success

---

## Pattern 3: Tmux Session Per Instance

**Claude Squad Pattern**:
- Each instance runs in a named tmux session
- User can attach/detach interactively
- Sessions persist independently of main application

**Category**: **REJECT / DO-NOT-ADOPT**

**Rationale**:
- **Conflict with Determinism**: Interactive attach/detach breaks MINI_PIPE's principle of unattended, reproducible execution
- **Portability Issues**: tmux is UNIX-only; MINI_PIPE must work on Windows
- **Already Solved**: MINI_PIPE has `process_spawner.py` for subprocess management and captures stdout/stderr to logs
- **Event Bus is Better**: MINI_PIPE's event bus provides real-time updates without tmux

**Alternative**:
- Keep subprocess-based execution (no tmux)
- Use `EventBus` for real-time progress updates
- Store stdout/stderr in DB or log files (already implemented)
- For interactive debugging, users can run tools directly (outside MINI_PIPE)

---

## Pattern 4: TUI (Terminal User Interface)

**Claude Squad Pattern**:
- Keyboard-driven UI for managing instances
- List view, diff view, overlays for operations
- Real-time status updates via polling

**Category**: **ADAPT-WITH-CONSTRAINTS**

**Rationale**:
- **Value**: MINI_PIPE currently has a CLI (`orchestrator_cli.py`) but no interactive UI for monitoring runs
- **Existing Work**: Monitoring UI exists (`monitoring_trigger.py`) but isn't a TUI
- **Constraint**: TUI must be **read-only** during execution (no interactive modifications to runs)
- **Use Case**: Developers want to see real-time progress without tailing logs

**Recommended Adaptation**:
- Build a **read-only TUI** using a Python library (e.g., `textual`, `urwid`)
- TUI shows:
  - List of active runs (status, progress, step count)
  - Current step details (tool, status, elapsed time)
  - Event stream (recent events from `EventBus`)
  - Patch ledger status (validated, queued, applied, etc.)
- **No modification commands**: TUI is for observability only
- Poll `orchestration.db` for updates (or subscribe to `EventBus` events)

---

## Pattern 5: Daemon / Background Execution

**Claude Squad Pattern**:
- Daemon runs as a detached process
- AutoYes mode: automatically responds to prompts
- Continuous polling of instances
- PID file for lifecycle management

**Category**: **ADAPT-WITH-CONSTRAINTS**

**Rationale**:
- **Value**: MINI_PIPE runs are currently foreground processes. A daemon mode would enable:
  - Long-running executions without keeping terminal open
  - Multiple runs in parallel (managed by daemon)
  - Auto-resume on system restart
- **Constraint**: No "AutoYes" prompts (conflicts with determinism)
- **Existing Work**: MINI_PIPE has triggers (`monitoring_trigger.py`) that are daemon-like

**Recommended Adaptation**:
- Create `DaemonOrchestrator` in `src/minipipe/daemon_orchestrator.py`
- Responsibilities:
  - Monitor `.acms_runs/` directory for new runs
  - Auto-start runs that are in `pending` state
  - Coordinate multiple concurrent runs (respect max concurrency)
  - Emit events to `EventBus` for monitoring
- **No AutoYes**: All execution is unattended and deterministic (no prompts)
- Use systemd/launchd for process management (not PID files)

---

## Pattern 6: Config/State Persistence (JSON)

**Claude Squad Pattern**:
- Store instance config/state in JSON files
- Persist across restarts
- LoadInstances() / SaveInstances() pattern

**Category**: **REJECT / DO-NOT-ADOPT**

**Rationale**:
- **Already Superior in MINI_PIPE**: MINI_PIPE uses SQLite (`orchestration.db`) for state persistence
  - SQLite provides ACID guarantees (no corruption risk)
  - Structured schema with foreign keys
  - Queryable with SQL
  - Better concurrency support than file-based JSON
- **JSON is Inferior**:
  - No schema enforcement
  - Concurrent writes can corrupt files
  - No transactional updates
  - Harder to query (no SQL)

**Alternative**:
- Continue using SQLite for runs, steps, patches
- If session tracking is added, store sessions in SQLite too
- Keep JSON only for configuration files (not runtime state)

---

## Pattern 7: Diff Stats Tracking

**Claude Squad Pattern**:
- Track file changes per instance (files added, modified, deleted)
- Update diff stats periodically
- Display in UI for quick status assessment

**Category**: **ADOPT-AS-IS (CONCEPTUALLY)**

**Rationale**:
- **Value**: MINI_PIPE tracks patches but doesn't summarize changes at a glance
- **Use Case**: Users want to know "how much changed" without reading full patches
- **No Conflict**: Diff stats are metadata, don't affect execution logic

**Recommended Adoption**:
- Add `diff_summary` field to `step_attempts` table: JSON with `{files_added, files_modified, files_deleted, lines_added, lines_deleted}`
- Compute during patch conversion (`patch_converter.py`)
- Display in TUI and monitoring UI
- Aggregate at run level for total change summary

---

## Pattern 8: Change Review Workflow

**Claude Squad Pattern**:
- Users can view diffs before committing
- Commit-and-pause: Agent stops after generating changes
- User approves, then changes are pushed

**Category**: **ADAPT-WITH-CONSTRAINTS**

**Rationale**:
- **Value**: Human-in-the-loop review is valuable for high-risk changes
- **Constraint**: MINI_PIPE is designed for unattended execution
- **Conflict**: Interactive review breaks determinism

**Recommended Adaptation**:
- **No interactive review during execution**
- Instead, use **Patch Ledger states** for review:
  - Patches transition to `validated` (automated gates)
  - Patches can be marked for `manual_review_required` (metadata flag)
  - Runs with manual review patches pause in `quarantined` state
  - Separate CLI command: `minipipe review --run-id <id>` to approve/reject patches
  - Once reviewed, run resumes from `quarantined` → `running`
- **Benefit**: Async review (doesn't block execution of other runs)

---

## Summary Table: Pattern Categorization

| Pattern | Category | Adopt? | Notes |
|---------|----------|--------|-------|
| Instance Management | ADAPT-WITH-CONSTRAINTS | ✅ Yes | Add `SessionRegistry` tied to runs |
| Git Worktree Per Task | ADOPT-AS-IS | ✅ Yes | Create `WorktreeManager` |
| Tmux Session Per Instance | REJECT | ❌ No | Use subprocess + EventBus instead |
| TUI (Terminal UI) | ADAPT-WITH-CONSTRAINTS | ✅ Yes | Read-only TUI for observability |
| Daemon / Background Execution | ADAPT-WITH-CONSTRAINTS | ✅ Yes | `DaemonOrchestrator` for multi-run management |
| Config/State Persistence (JSON) | REJECT | ❌ No | SQLite is superior |
| Diff Stats Tracking | ADOPT-AS-IS | ✅ Yes | Add diff summary metadata |
| Change Review Workflow | ADAPT-WITH-CONSTRAINTS | ✅ Yes | Async review via Patch Ledger |

---

# 4. Patterns to Copy or Adapt into MINI_PIPE

This section provides implementation-level guidance for adopting the approved patterns.

---

## 4.1 Recommended Patterns with Implementation Notes

### Pattern A: Session Registry (Adapted Instance Management)

**What to Adopt**:
- Track long-lived AI agent sessions as first-class entities
- Persist session metadata and state across runs
- Associate sessions with projects, workstreams, and runs

**Integration Target**: New module `src/minipipe/session_registry.py`

**Schema** (SQLite table):
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    workstream_id TEXT,
    agent_type TEXT NOT NULL,  -- 'aider', 'claude', 'codex', etc.
    title TEXT,
    workspace_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    state TEXT NOT NULL,  -- 'created', 'active', 'paused', 'completed', 'failed'
    metadata TEXT,  -- JSON
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

**API**:
```python
class SessionRegistry:
    def create_session(self, project_id, agent_type, title, workspace_path) -> str
    def get_session(self, session_id) -> Dict
    def list_sessions(self, project_id=None, state=None) -> List[Dict]
    def update_session_state(self, session_id, new_state) -> bool
    def pause_session(self, session_id) -> bool
    def resume_session(self, session_id) -> bool
    def complete_session(self, session_id, success: bool) -> bool
```

**Integration with Orchestrator**:
- Executor can optionally attach a `session_id` to step attempts
- Session state updates when runs start/complete
- TUI can list sessions and their associated runs

**Dependencies**:
- SQLite schema migration to add `sessions` table
- Update `orchestrator.py` to track session_id in run metadata

---

### Pattern B: Worktree Manager

**What to Adopt**:
- Create and manage git worktrees for isolated task execution
- Automatic worktree creation per run or per step
- Cleanup strategy: archive on failure, delete on success

**Integration Target**: New module `src/minipipe/worktree_manager.py`

**API**:
```python
class WorktreeManager:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.worktrees_dir = repo_root / ".minipipe_worktrees"

    def create_worktree(self, run_id: str, step_id: str, branch_name: str) -> Path:
        """Create a worktree and return its path."""
        # git worktree add .minipipe_worktrees/{run_id}_{step_id} -b {branch_name}

    def cleanup_worktree(self, worktree_path: Path, archive_on_failure: bool = True):
        """Remove worktree. Optionally archive if task failed."""
        # git worktree remove {worktree_path}

    def list_worktrees(self) -> List[Dict]:
        """List all active worktrees."""
        # git worktree list --porcelain

    def is_branch_checked_out(self, branch_name: str) -> bool:
        """Check if branch is active in any worktree."""
```

**Integration with Executor**:
- **Option 1 (Run-Level)**: Create one worktree per run
  - All steps in the run execute in the same worktree
  - Pro: Simpler, fewer worktrees
  - Con: Steps can conflict if they modify the same files

- **Option 2 (Step-Level)**: Create one worktree per step
  - Each step is fully isolated
  - Pro: Maximum isolation
  - Con: More overhead (disk space, git operations)

**Recommended**: Start with **Option 1** (run-level), add Option 2 if needed.

**Executor Changes**:
```python
# In executor.py, before running a task:
if config.get("use_worktrees", False):
    worktree_path = worktree_manager.create_worktree(run_id, step_id, branch_name)
    task.metadata["workspace_path"] = str(worktree_path)
    # Update subprocess cwd to worktree_path

# After task completion:
if task.exit_code == 0:
    worktree_manager.cleanup_worktree(worktree_path, archive_on_failure=False)
else:
    worktree_manager.cleanup_worktree(worktree_path, archive_on_failure=True)
```

**Dependencies**:
- Git must be available on PATH
- Repository must be a git repo
- Add config flag `use_worktrees` to plan globals or router config

---

### Pattern C: Diff Stats Tracking

**What to Adopt**:
- Compute summary stats for patches (files/lines added/modified/deleted)
- Store in step metadata for quick status assessment

**Integration Target**: Enhance `src/minipipe/patch_converter.py`

**Implementation**:
```python
from dataclasses import dataclass

@dataclass
class DiffStats:
    files_added: int = 0
    files_modified: int = 0
    files_deleted: int = 0
    lines_added: int = 0
    lines_deleted: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "files_added": self.files_added,
            "files_modified": self.files_modified,
            "files_deleted": self.files_deleted,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
        }

def compute_diff_stats(patch_content: str) -> DiffStats:
    """Parse unified diff and compute stats."""
    stats = DiffStats()

    for line in patch_content.splitlines():
        if line.startswith("+++") and line != "+++ /dev/null":
            if "/dev/null" in line:
                stats.files_deleted += 1
            else:
                stats.files_modified += 1  # Could be added or modified
        elif line.startswith("+") and not line.startswith("+++"):
            stats.lines_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            stats.lines_deleted += 1

    return stats
```

**Integration with Patch Ledger**:
```python
# In patch_ledger.py, when creating an entry:
patch_content = read_patch_file(patch_id)
diff_stats = compute_diff_stats(patch_content)

entry_data["metadata"] = {
    "diff_stats": diff_stats.to_dict()
}
```

**Display in TUI**:
- Show diff stats in step list: `[+5 files, +120 -30 lines]`
- Aggregate at run level for total impact

---

### Pattern D: Read-Only TUI for Observability

**What to Adopt**:
- Interactive terminal UI for monitoring runs in real-time
- Read-only: no modifications to runs during execution
- Show runs, steps, events, patch status

**Integration Target**: New module `src/minipipe/tui_monitor.py`

**Technology**: Use `textual` library (modern Python TUI framework)

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  MINI_PIPE Monitor                              [Q]uit       │
├─────────────────────────────────────────────────────────────┤
│  Runs                                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ RUN-001  [RUNNING]  Phase 1  5/10 steps  60s          │  │
│  │ RUN-002  [SUCCEEDED] Phase 2  10/10 steps  120s       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Current Step (RUN-001)                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ STEP-03  [RUNNING]  Tool: aider  30s                   │  │
│  │ Diff: +3 files, +85 -12 lines                          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  Event Stream                                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 12:34:56  step_started  STEP-03                        │  │
│  │ 12:34:45  step_completed  STEP-02  (exit_code=0)       │  │
│  │ 12:34:30  run_started  RUN-001                         │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Implementation**:
```python
from textual.app import App
from textual.widgets import DataTable, Static

class MiniPipeTUI(App):
    def __init__(self, db_path: str):
        super().__init__()
        self.db = Database(db_path)

    def on_mount(self):
        self.set_interval(1.0, self.refresh_data)  # Poll every 1s

    def refresh_data(self):
        runs = self.db.list_runs(limit=20)
        # Update DataTable with runs
```

**CLI Integration**:
```bash
# New command:
minipipe monitor --run-id RUN-001

# Or monitor all active runs:
minipipe monitor
```

---

### Pattern E: Daemon Orchestrator (Multi-Run Management)

**What to Adopt**:
- Background process that manages multiple concurrent runs
- Auto-start runs from queue
- Coordinate concurrency limits

**Integration Target**: New module `src/minipipe/daemon_orchestrator.py`

**Responsibilities**:
1. Poll for new runs in `pending` state
2. Start runs up to `max_concurrent_runs` limit
3. Monitor running runs and emit events
4. Cleanup completed runs (archive logs, etc.)

**API**:
```python
class DaemonOrchestrator:
    def __init__(self, db: Database, max_concurrent_runs: int = 4):
        self.db = db
        self.max_concurrent_runs = max_concurrent_runs
        self.running_processes: Dict[str, subprocess.Popen] = {}

    def start(self):
        """Start daemon main loop."""
        while True:
            self.poll_and_start_runs()
            self.check_running_processes()
            time.sleep(5)  # Poll every 5s

    def poll_and_start_runs(self):
        """Find pending runs and start them if capacity available."""
        if len(self.running_processes) >= self.max_concurrent_runs:
            return

        pending_runs = self.db.list_runs(state="pending", limit=10)
        for run in pending_runs:
            if len(self.running_processes) >= self.max_concurrent_runs:
                break
            self.start_run(run["run_id"])

    def start_run(self, run_id: str):
        """Spawn subprocess to execute run."""
        proc = subprocess.Popen([
            "minipipe", "execute-plan", "--run-id", run_id
        ])
        self.running_processes[run_id] = proc

    def check_running_processes(self):
        """Poll running processes and cleanup completed ones."""
        for run_id, proc in list(self.running_processes.items()):
            if proc.poll() is not None:  # Process finished
                del self.running_processes[run_id]
```

**Systemd Service** (Linux):
```ini
[Unit]
Description=MINI_PIPE Daemon Orchestrator
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/minipipe daemon --max-concurrent 4
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**CLI**:
```bash
minipipe daemon --max-concurrent 4
minipipe daemon stop
minipipe daemon status
```

---

### Pattern F: Async Patch Review Workflow

**What to Adopt**:
- Mark patches as requiring manual review
- Pause runs until patches are reviewed
- Separate review command for async approval

**Integration Target**: Enhance `src/minipipe/patch_ledger.py`

**Schema Update**:
```python
# Add to PatchLedger entry metadata:
entry_data["metadata"] = {
    "manual_review_required": bool,
    "review_status": "pending" | "approved" | "rejected",
    "reviewed_by": str,
    "reviewed_at": str,
}
```

**Patch Ledger State Machine Update**:
```python
# New state: awaiting_review
VALID_STATES = {
    ...,
    "awaiting_review",  # Patch requires manual review before apply
}

STATE_TRANSITIONS = {
    "validated": ["queued", "awaiting_review", "quarantined", "dropped"],
    "awaiting_review": ["queued", "dropped"],  # After review
}
```

**Review CLI**:
```bash
# List patches needing review:
minipipe review list

# Show patch details:
minipipe review show --ledger-id PATCH-001

# Approve patch:
minipipe review approve --ledger-id PATCH-001

# Reject patch:
minipipe review reject --ledger-id PATCH-001 --reason "Too risky"
```

**Orchestrator Integration**:
- When a patch transitions to `awaiting_review`, pause the run (set run state to `paused`)
- After review (approved → `queued`, rejected → `dropped`), resume the run

---

## 4.2 Suggested Modules/Abstractions

### New Modules to Create

1. **`src/minipipe/session_registry.py`**
   - Manages long-lived AI agent sessions
   - SQLite-backed persistence
   - State machine: created → active → paused → completed/failed

2. **`src/minipipe/worktree_manager.py`**
   - Git worktree creation and cleanup
   - Branch validation and cleanup
   - Archive worktrees on failure

3. **`src/minipipe/tui_monitor.py`**
   - Read-only TUI for run monitoring
   - Real-time updates from EventBus or DB polling
   - Keyboard navigation and filtering

4. **`src/minipipe/daemon_orchestrator.py`**
   - Multi-run coordination
   - Auto-start pending runs
   - Concurrency limit enforcement

### Modules to Enhance

1. **`src/minipipe/patch_converter.py`**
   - Add `compute_diff_stats()` function
   - Return DiffStats along with converted patches

2. **`src/minipipe/patch_ledger.py`**
   - Add `awaiting_review` state
   - Add review metadata fields
   - Add state transitions for review workflow

3. **`src/minipipe/executor.py`**
   - Integrate `WorktreeManager` for workspace isolation
   - Store diff stats in step metadata
   - Support session_id attachment

4. **`src/minipipe/orchestrator.py`**
   - Add `pause_run()` and `resume_run()` methods
   - Emit events when runs pause for review

---

## 4.3 Dependencies and Configuration Implications

### External Dependencies

| Dependency | Purpose | Installation | Portability |
|------------|---------|--------------|-------------|
| **Git** | Worktree management | `git` on PATH | ✅ Cross-platform |
| **textual** | TUI library | `pip install textual` | ✅ Cross-platform |
| **None for daemon** | Use stdlib subprocess | Built-in | ✅ Cross-platform |

### Configuration Updates

**1. Router Config** (`router_config.json`):
```json
{
  "defaults": {
    "use_worktrees": true,
    "worktree_cleanup_on_success": true,
    "worktree_archive_on_failure": true
  }
}
```

**2. Plan Globals** (in plan JSON):
```json
{
  "globals": {
    "use_worktrees": true,
    "max_concurrent_steps": 4,
    "manual_review_required": false
  }
}
```

**3. Daemon Config** (new file `.minipipe/daemon_config.json`):
```json
{
  "max_concurrent_runs": 4,
  "poll_interval_seconds": 5,
  "auto_cleanup_completed_runs": true,
  "log_dir": ".minipipe/daemon_logs"
}
```

### Schema Migrations

**SQLite Migrations** (in `schema/migrations/`):

1. **`004_add_sessions_table.sql`**:
```sql
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
);

CREATE INDEX idx_sessions_project_id ON sessions(project_id);
CREATE INDEX idx_sessions_state ON sessions(state);
```

2. **`005_add_diff_stats_to_step_attempts.sql`**:
```sql
ALTER TABLE step_attempts ADD COLUMN diff_stats TEXT;
```

3. **`006_add_review_metadata_to_patch_ledger.sql`**:
```sql
ALTER TABLE patch_ledger ADD COLUMN review_metadata TEXT;
```

---

# 5. MINI_PIPE – Things Done Better (KEEP-AS-IS)

This section highlights areas where MINI_PIPE's architecture is **strictly superior** to Claude Squad's approach and **must not be weakened or replaced**.

---

## 5.1 List of KEEP-AS-IS Areas

### 1. **Deterministic, Plan-Based Execution**

**MINI_PIPE Approach**:
- Execution is driven by JSON plans with explicit steps, dependencies, and commands
- Plans are validated before execution (schema, DAG cycles, variable substitution)
- Execution is repeatable and testable

**Why Superior**:
- **Reproducibility**: Same plan + same inputs = same execution path
- **Version Control**: Plans are text files; can be tracked in git
- **Testing**: Plans can be tested in isolation without running full pipelines
- **Auditability**: Execution trace is deterministic and reconstructible

**Why Claude Squad is Inferior**:
- Ad-hoc, interactive execution; no predetermined plan
- User decisions during execution make it non-reproducible
- No way to "replay" a session with the same inputs

**What Would Be Lost**:
- If we adopted Claude Squad's interactive model, we'd lose:
  - CI/CD integration (can't run interactive workflows in CI)
  - Automated testing of plans
  - Ability to review/approve plans before execution
  - Deterministic debugging (can't reproduce exact execution)

**Verdict**: **KEEP-AS-IS**. This is MINI_PIPE's core identity and must not be compromised.

---

### 2. **Formal State Machines**

**MINI_PIPE Approach**:
- All state transitions (runs, steps, patches) are governed by explicit state machines
- State transitions are validated: `RunStateMachine.validate_transition(from_state, to_state)`
- Invalid transitions are rejected with clear error messages

**Why Superior**:
- **Correctness**: Impossible to reach invalid states
- **Debugging**: State history is logged; easy to trace how a run reached a certain state
- **Predictability**: Clear documentation of what states exist and how to transition

**Why Claude Squad is Inferior**:
- Instance states are implicit (inferred from UI logic and tmux session status)
- No validation of state transitions
- Hard to debug: "Why is this instance paused?" requires reading UI code

**What Would Be Lost**:
- If we adopted Claude Squad's implicit states:
  - Bug risk: Invalid state transitions could go undetected
  - Harder debugging: No formal model to reference
  - Auditability: Can't prove a run followed valid transitions

**Verdict**: **KEEP-AS-IS**. Formal state machines are essential for correctness and maintainability.

---

### 3. **Event-Driven Architecture (EventBus)**

**MINI_PIPE Approach**:
- `EventBus` is the SSOT for all runtime events
- Components emit typed events: `run_started`, `step_completed`, `patch_quarantined`, etc.
- Triggers and monitoring UI subscribe to events for automation

**Why Superior**:
- **Decoupling**: Components don't need to know about each other
- **Scalability**: Events can be consumed by multiple listeners
- **Real-Time**: No polling lag; events are instant
- **Extensibility**: New features can subscribe to existing events without modifying core

**Why Claude Squad is Inferior**:
- Polling-based (500ms ticker updates instance metadata)
- Tight coupling between UI and instances (UI directly polls instance state)
- No event stream for automation

**What Would Be Lost**:
- If we adopted polling:
  - Increased latency (up to 500ms delay before UI updates)
  - Higher CPU usage (continuous polling even when idle)
  - Harder to add automation (triggers would need to poll too)

**Verdict**: **KEEP-AS-IS**. Event-driven is superior in every dimension.

---

### 4. **Separation of Concerns (Layered Architecture)**

**MINI_PIPE Approach**:
- Clear boundaries: Controller → Planner → Router → Scheduler → Executor → Adapters
- Each layer has a single responsibility
- Adapter pattern enables swappable implementations (mock vs real)

**Why Superior**:
- **Testability**: Each layer can be tested in isolation
- **Maintainability**: Changes to one layer don't ripple to others
- **Extensibility**: New tools/adapters can be added without modifying core
- **Clarity**: Easy to understand what each module does

**Why Claude Squad is Inferior**:
- UI, session management, and git operations are intertwined in `app.go`
- Hard to test: UI logic and business logic are coupled
- Hard to extend: Adding a new feature requires touching multiple concerns

**What Would Be Lost**:
- If we merged layers (like Claude Squad):
  - Test complexity: Would need to mock UI for business logic tests
  - Change risk: Refactoring one feature could break unrelated features
  - Onboarding difficulty: New developers can't understand one layer at a time

**Verdict**: **KEEP-AS-IS**. Layered architecture is fundamental to maintainability.

---

### 5. **Quality Gates and Guardrails**

**MINI_PIPE Approach**:
- `PatternGuardrails`: Enforces expected patterns (e.g., "all patches must pass validation")
- `AntiPatternDetector`: Flags dangerous behaviors (e.g., "same error 3 times = loop")
- `PatchLedger`: Multi-state validation before commit (validated → queued → applied → verified)

**Why Superior**:
- **Safety**: Catches errors before they become commits
- **Production-Ready**: Designed for unattended, high-stakes execution
- **Pattern Enforcement**: Ensures best practices are followed

**Why Claude Squad is Inferior**:
- AutoYes mode blindly accepts all changes without validation
- No anti-pattern detection (infinite loops can run forever)
- No intermediate validation states (changes go straight from generation to commit)

**What Would Be Lost**:
- If we adopted AutoYes:
  - Risk of committing broken code
  - No circuit breaker for failing tasks
  - No quarantine mechanism for unsafe patches

**Verdict**: **KEEP-AS-IS**. Guardrails are critical for production use.

---

### 6. **Patch Lifecycle State Machine**

**MINI_PIPE Approach**:
- `PatchLedger` tracks patches through: `created → validated → queued → applied → verified → committed`
- Each transition is a quality gate
- Rollback and quarantine support for failed patches

**Why Superior**:
- **Multi-Layer Validation**: Patches are validated at multiple stages
- **Rollback Support**: Failed patches can be reverted cleanly
- **Audit Trail**: Full history of patch states
- **Safety**: Unsafe patches are quarantined, not committed

**Why Claude Squad is Inferior**:
- Changes are either accepted or rejected; no intermediate states
- No rollback mechanism (if a change breaks something, user must manually revert)
- No quarantine (unsafe changes could be committed)

**What Would Be Lost**:
- If we simplified to accept/reject:
  - No incremental validation (all-or-nothing)
  - Harder to debug failed patches (no state history)
  - Risky: No safety net for partially-applied patches

**Verdict**: **KEEP-AS-IS**. Patch lifecycle is a core safety feature.

---

### 7. **Multi-Tool Routing with Strategies**

**MINI_PIPE Approach**:
- `TaskRouter` supports multiple routing strategies: fixed, round-robin, metrics-based
- Tools are selected based on capabilities (task_kind → tool mapping)
- Success metrics tracked per tool (success rate, latency)
- Dynamic failover: If a tool fails repeatedly, circuit breaker opens

**Why Superior**:
- **Flexibility**: Can route different tasks to different tools
- **Load Balancing**: Round-robin distributes work evenly
- **Auto-Optimization**: Metrics-based routing chooses the best tool
- **Resilience**: Circuit breaker prevents cascading failures

**Why Claude Squad is Inferior**:
- One tool per instance (no dynamic routing)
- No load balancing
- No success metrics or failover

**What Would Be Lost**:
- If we simplified to one-tool-per-task:
  - No optimization: Can't choose the best tool for a task
  - No resilience: If Aider fails, can't fallback to another tool
  - Harder to scale: Can't distribute load across multiple tools

**Verdict**: **KEEP-AS-IS**. Routing is essential for multi-tool orchestration.

---

### 8. **Resilience Patterns (Circuit Breakers, Retries, Recovery)**

**MINI_PIPE Approach**:
- `CircuitBreaker`: Opens after N failures, prevents further requests
- `RetryStrategy`: Exponential backoff with jitter
- `RecoveryCoordinator`: Orchestrates retries for failed tasks

**Why Superior**:
- **Production-Grade**: Handles transient failures gracefully
- **Cascading Failure Prevention**: Circuit breaker isolates failing tools
- **Auto-Recovery**: Tasks retry automatically when conditions improve

**Why Claude Squad is Inferior**:
- No retry logic (instances fail and stop)
- No circuit breaker (failing tools continue to be called)
- Manual recovery required (user must restart instances)

**What Would Be Lost**:
- If we removed resilience patterns:
  - Higher failure rate: Transient network errors would abort runs
  - Manual intervention: Operators would need to restart failed tasks
  - Cascading failures: One failing tool could take down the whole pipeline

**Verdict**: **KEEP-AS-IS**. Resilience is critical for production deployments.

---

## 5.2 Summary: Why These Should Not Be Changed

| Area | MINI_PIPE Approach | Claude Squad Approach | Risk of Weakening |
|------|--------------------|-----------------------|-------------------|
| Execution Model | Plan-driven, deterministic | Interactive, ad-hoc | Loss of reproducibility, CI/CD integration |
| State Management | Formal state machines | Implicit states in UI | Correctness bugs, harder debugging |
| Event System | Event-driven (EventBus) | Polling-based (500ms ticker) | Latency, CPU waste, harder automation |
| Architecture | Layered, separated concerns | Monolithic UI+logic | Test complexity, change risk |
| Safety | Guardrails, anti-pattern detection | AutoYes (no validation) | Risk of committing broken code |
| Patch Lifecycle | Multi-state validation | Accept/reject only | No rollback, no quarantine |
| Routing | Multi-strategy, capability-based | One tool per instance | No optimization, no failover |
| Resilience | Circuit breakers, retries, recovery | Manual restart | Higher failure rate, manual work |

**Conclusion**: These 8 areas represent MINI_PIPE's **architectural advantages** over Claude Squad. Adopting Claude Squad patterns must **not weaken** these foundations.

---

# 6. Integration Plan, Risks, and Next Steps

## 6.1 High-Level Integration Design

### Integration Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     MINI_PIPE Enhanced Architecture            │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  NEW: Session Layer (Inspired by Claude Squad)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  SessionRegistry                                       │  │
│  │  - Long-lived AI agent sessions                        │  │
│  │  - State: created → active → paused → completed        │  │
│  │  - Tied to projects and workstreams                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ENHANCED: Workspace Isolation (Worktree Manager)          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  WorktreeManager                                       │  │
│  │  - Create/cleanup git worktrees per run               │  │
│  │  - Branch validation and archival                     │  │
│  │  - Integrated with executor for workspace isolation   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  EXISTING: ACMS Controller (KEEP-AS-IS)                     │
│  Gap Analysis → Planning → Execution                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  EXISTING: Core Engine (KEEP-AS-IS)                         │
│  Orchestrator → Scheduler → Router → Executor → Tools      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ENHANCED: Patch Management (Diff Stats Added)             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  PatchLedger + DiffStats                               │  │
│  │  - Track file/line changes per patch                  │  │
│  │  - Manual review workflow (awaiting_review state)     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  NEW: Observability & Management (TUI + Daemon)             │
│  ┌───────────────────┐  ┌─────────────────────────────────┐│
│  │  TUI Monitor      │  │  Daemon Orchestrator            ││
│  │  - Read-only UI   │  │  - Multi-run management         ││
│  │  - Run/step view  │  │  - Auto-start pending runs      ││
│  │  - Event stream   │  │  - Concurrency control          ││
│  └───────────────────┘  └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**Scenario**: User creates a new AI coding session to fix a bug

1. **Session Creation**:
   ```python
   session_id = session_registry.create_session(
       project_id="PROJ-001",
       agent_type="aider",
       title="Fix login bug",
       workspace_path="/repo"
   )
   ```

2. **Worktree Creation** (if enabled):
   ```python
   worktree_path = worktree_manager.create_worktree(
       run_id=run_id,
       step_id=step_id,
       branch_name=f"fix-login-bug-{run_id}"
   )
   ```

3. **Run Execution** (Orchestrator):
   - Plan defines steps: `analyze_code`, `generate_fix`, `run_tests`
   - Each step executes in the worktree
   - Patches are tracked in `PatchLedger` with diff stats

4. **Patch Review** (if manual_review_required):
   - Run pauses when patch reaches `awaiting_review` state
   - User runs: `minipipe review approve --ledger-id PATCH-001`
   - Run resumes

5. **Monitoring** (TUI):
   - User launches: `minipipe monitor`
   - TUI shows real-time progress: steps completed, diff stats, events

6. **Daemon Management** (for long-running tasks):
   - Daemon detects pending run
   - Auto-starts run in background
   - User detaches terminal; run continues

---

## 6.2 Risks and Mitigations

### Risk 1: Git Worktree Overhead

**Risk**: Worktrees consume significant disk space (one full working directory per task).

**Impact**: High

**Likelihood**: High (for large repositories with many concurrent tasks)

**Mitigation**:
- **Make worktrees optional**: Add config flag `use_worktrees` (default: false)
- **Cleanup strategy**: Delete worktrees immediately after task completion (unless failed)
- **Sparse checkouts**: Use git sparse-checkout to reduce worktree size
- **Limit concurrent worktrees**: Max N worktrees at a time

**Residual Risk**: Medium (still disk overhead, but bounded)

---

### Risk 2: AGPL License Contamination

**Risk**: Accidentally copying code from Claude Squad would require MINI_PIPE to be AGPL-licensed.

**Impact**: Critical (license change would affect all users)

**Likelihood**: Low (if guidelines are followed)

**Mitigation**:
- **Zero code copying**: All patterns are reimplemented from scratch in Python
- **Concept-only adoption**: Document patterns in this analysis, then implement independently
- **Code review**: All PRs adding Claude Squad-inspired features must be reviewed for license compliance

**Residual Risk**: Very Low

---

### Risk 3: Complexity Increase

**Risk**: Adding sessions, worktrees, TUI, and daemon increases system complexity.

**Impact**: Medium (harder to maintain and debug)

**Likelihood**: High

**Mitigation**:
- **Incremental rollout**: Add one pattern at a time (start with worktrees, then TUI, etc.)
- **Feature flags**: All new features are opt-in via configuration
- **Comprehensive tests**: Each new component has 90%+ test coverage
- **Documentation**: Update architecture docs with each addition

**Residual Risk**: Medium (complexity is inherent in multi-feature systems)

---

### Risk 4: Determinism vs Interactivity Trade-Off

**Risk**: Adding session management and review workflows could encourage interactive usage, breaking determinism.

**Impact**: High (loss of MINI_PIPE's core value)

**Likelihood**: Medium (if not carefully designed)

**Mitigation**:
- **Read-only TUI**: TUI is strictly observability; no modifications allowed
- **Async review**: Review commands are separate from execution (don't block determinism)
- **No runtime prompts**: All execution is unattended; sessions are for tracking, not interaction
- **Guardrail enforcement**: Guardrails reject any attempt to modify runs during execution

**Residual Risk**: Low (if guidelines are strictly enforced)

---

## 6.3 Concrete Next Steps (Small, Testable Increments)

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Add worktree support and diff stats (low-risk, high-value)

**Tasks**:
1. **Implement WorktreeManager** (`src/minipipe/worktree_manager.py`):
   - `create_worktree()`, `cleanup_worktree()`, `list_worktrees()`
   - Unit tests with mock git commands
   - Integration test with real git repo

2. **Integrate with Executor**:
   - Add `use_worktrees` flag to executor config
   - Create worktree before task execution
   - Cleanup worktree after task completion
   - Test with Aider adapter (real-world use case)

3. **Add Diff Stats**:
   - Implement `compute_diff_stats()` in `patch_converter.py`
   - Add `diff_stats` field to `step_attempts` table
   - Update executor to store diff stats
   - Test with sample patches

**Success Criteria**:
- [ ] Worktrees created and cleaned up correctly
- [ ] Diff stats computed and stored in DB
- [ ] No regression in existing tests (100% pass rate)

---

### Phase 2: Observability (Weeks 3-4)

**Goal**: Add TUI for monitoring and daemon for multi-run management

**Tasks**:
1. **Implement TUI Monitor** (`src/minipipe/tui_monitor.py`):
   - Basic layout: run list, step details, event stream
   - Poll DB every 1s for updates
   - Read-only (no modification commands)
   - Keyboard shortcuts: `q` (quit), `r` (refresh), `j/k` (navigate)

2. **Implement Daemon Orchestrator** (`src/minipipe/daemon_orchestrator.py`):
   - Poll for pending runs
   - Auto-start up to `max_concurrent_runs`
   - Monitor running processes
   - Graceful shutdown

3. **CLI Integration**:
   - `minipipe monitor` command
   - `minipipe daemon` command (start/stop/status)

**Success Criteria**:
- [ ] TUI displays runs and steps correctly
- [ ] Daemon starts and manages multiple runs
- [ ] No conflicts between daemon and manual runs

---

### Phase 3: Sessions and Review (Weeks 5-6)

**Goal**: Add session tracking and async patch review

**Tasks**:
1. **Implement SessionRegistry** (`src/minipipe/session_registry.py`):
   - SQLite schema for sessions
   - CRUD operations: create, get, list, update state
   - Integration with orchestrator (attach session_id to runs)

2. **Enhance Patch Ledger for Review**:
   - Add `awaiting_review` state
   - Add review metadata fields
   - Implement `pause_run()` when patch needs review

3. **Review CLI**:
   - `minipipe review list`
   - `minipipe review approve/reject --ledger-id <id>`

**Success Criteria**:
- [ ] Sessions persist across restarts
- [ ] Review workflow pauses and resumes runs correctly
- [ ] No race conditions in review state updates

---

### Phase 4: Integration Testing (Week 7)

**Goal**: End-to-end testing of all new features together

**Tasks**:
1. **E2E Test Scenario**:
   - Create session
   - Run plan with worktrees enabled
   - Monitor via TUI
   - Review patch
   - Resume run
   - Verify final state

2. **Performance Testing**:
   - 10 concurrent runs with worktrees
   - Measure disk usage, CPU, memory
   - Identify bottlenecks

3. **Documentation**:
   - Update architecture docs
   - Write user guide for new features
   - Create migration guide for existing users

**Success Criteria**:
- [ ] E2E scenario passes without manual intervention
- [ ] Performance meets SLOs (e.g., <1s overhead per worktree)
- [ ] Documentation is clear and complete

---

### Phase 5: Rollout (Week 8)

**Goal**: Deploy to production with feature flags

**Tasks**:
1. **Feature Flags**:
   - `enable_worktrees`: default false
   - `enable_sessions`: default false
   - `enable_tui`: default true (read-only, low risk)

2. **Canary Deployment**:
   - Roll out to 10% of users
   - Monitor error rates and performance
   - Iterate based on feedback

3. **Full Rollout**:
   - Enable for 100% of users
   - Update default flags to true (for new users)

**Success Criteria**:
- [ ] No regressions in production
- [ ] User feedback is positive
- [ ] Adoption rate >50% within 1 month

---

## 6.4 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Worktree Overhead** | <10% disk increase | Measure disk usage before/after enabling worktrees |
| **TUI Responsiveness** | <100ms update lag | Measure time from event emit to TUI update |
| **Daemon Reliability** | 99.9% uptime | Monitor daemon crashes over 1 month |
| **Review Workflow Adoption** | >30% of runs | Count runs with manual_review_required flag |
| **Test Coverage** | >90% for new modules | Run coverage report on new code |
| **Zero License Issues** | No AGPL code copied | Manual code review + legal audit |

---

# AGENT_SUMMARY (JSON)

```json
{
  "patterns_to_copy": [
    {
      "name": "Session Registry (Instance Management)",
      "summary": "Track long-lived AI agent sessions with state persistence across runs",
      "integration_target": "New module: src/minipipe/session_registry.py. SQLite table for sessions. Integration with orchestrator to attach session_id to runs.",
      "category": "ADAPT-WITH-CONSTRAINTS"
    },
    {
      "name": "Worktree Manager (Git Worktree Per Task)",
      "summary": "Create isolated git worktrees per run/step to prevent file conflicts during parallel execution",
      "integration_target": "New module: src/minipipe/worktree_manager.py. Integration with executor to create worktree before task, cleanup after completion.",
      "category": "ADOPT-AS-IS"
    },
    {
      "name": "Diff Stats Tracking",
      "summary": "Compute summary stats for patches (files/lines added/modified/deleted) for quick status assessment",
      "integration_target": "Enhance src/minipipe/patch_converter.py with compute_diff_stats(). Add diff_stats field to step_attempts table.",
      "category": "ADOPT-AS-IS"
    },
    {
      "name": "Read-Only TUI for Observability",
      "summary": "Interactive terminal UI for monitoring runs in real-time (read-only, no modifications)",
      "integration_target": "New module: src/minipipe/tui_monitor.py using textual library. Poll DB or subscribe to EventBus for updates.",
      "category": "ADAPT-WITH-CONSTRAINTS"
    },
    {
      "name": "Daemon Orchestrator (Multi-Run Management)",
      "summary": "Background process that manages multiple concurrent runs, auto-starts pending runs, enforces concurrency limits",
      "integration_target": "New module: src/minipipe/daemon_orchestrator.py. Polls for pending runs, spawns subprocesses, monitors completion.",
      "category": "ADAPT-WITH-CONSTRAINTS"
    },
    {
      "name": "Async Patch Review Workflow",
      "summary": "Mark patches as requiring manual review, pause runs until reviewed, separate review CLI for async approval",
      "integration_target": "Enhance src/minipipe/patch_ledger.py with awaiting_review state. Add review CLI commands. Orchestrator pauses runs when patches need review.",
      "category": "ADAPT-WITH-CONSTRAINTS"
    }
  ],
  "mini_pipe_strengths_keep_as_is": [
    {
      "name": "Deterministic, Plan-Based Execution",
      "reason": "MINI_PIPE's plan-driven model is reproducible and testable. Claude Squad's interactive model would break CI/CD integration and make execution non-deterministic."
    },
    {
      "name": "Formal State Machines",
      "reason": "Explicit state machines (RunStateMachine, StepStateMachine) prevent invalid transitions and provide auditability. Claude Squad's implicit states are error-prone."
    },
    {
      "name": "Event-Driven Architecture (EventBus)",
      "reason": "Event-driven is superior to polling in latency, CPU efficiency, and extensibility. Claude Squad's 500ms polling is wasteful."
    },
    {
      "name": "Separation of Concerns (Layered Architecture)",
      "reason": "MINI_PIPE's clear module boundaries (Controller → Planner → Router → Scheduler → Executor) are easier to test and maintain than Claude Squad's monolithic app."
    },
    {
      "name": "Quality Gates and Guardrails",
      "reason": "Guardrails enforce patterns and detect anti-patterns. Claude Squad's AutoYes mode blindly accepts all changes without validation, risking broken commits."
    },
    {
      "name": "Patch Lifecycle State Machine",
      "reason": "Multi-state validation (created → validated → queued → applied → verified → committed) with rollback support is safer than Claude Squad's accept/reject model."
    },
    {
      "name": "Multi-Tool Routing with Strategies",
      "reason": "Dynamic routing (fixed, round-robin, metrics-based) enables load balancing and failover. Claude Squad's one-tool-per-instance model lacks flexibility."
    },
    {
      "name": "Resilience Patterns (Circuit Breakers, Retries, Recovery)",
      "reason": "Production-grade resilience handles transient failures gracefully. Claude Squad requires manual restart on failures."
    }
  ],
  "key_risks": [
    {
      "risk": "Git Worktree Overhead: Disk space consumption for large repos with many concurrent tasks",
      "mitigation": "Make worktrees optional (config flag). Cleanup immediately after completion. Use sparse checkouts. Limit concurrent worktrees."
    },
    {
      "risk": "AGPL License Contamination: Copying code from Claude Squad would force MINI_PIPE to be AGPL",
      "mitigation": "Zero code copying. All patterns reimplemented from scratch. Code review for license compliance."
    },
    {
      "risk": "Complexity Increase: Adding sessions, worktrees, TUI, daemon increases maintenance burden",
      "mitigation": "Incremental rollout. Feature flags (opt-in). Comprehensive tests (90%+ coverage). Updated documentation."
    },
    {
      "risk": "Determinism vs Interactivity Trade-Off: Session management could encourage interactive usage",
      "mitigation": "Read-only TUI. Async review (separate from execution). No runtime prompts. Guardrail enforcement."
    }
  ]
}
```

---

**End of Analysis**

---

## Appendix: Quick Reference Tables

### Table A: Adoption Decision Matrix

| Pattern | MINI_PIPE Has Equivalent? | Adopt? | Priority | Risk |
|---------|---------------------------|--------|----------|------|
| Instance Management | ❌ No | ✅ Yes (Adapt) | Medium | Low |
| Git Worktree Per Task | ❌ No | ✅ Yes | High | Medium |
| Tmux Sessions | ✅ Yes (subprocess) | ❌ No | N/A | N/A |
| TUI | ⚠️ Partial (CLI only) | ✅ Yes (Adapt) | Medium | Low |
| Daemon | ⚠️ Partial (triggers) | ✅ Yes (Adapt) | Low | Low |
| JSON State | ✅ Yes (SQLite) | ❌ No | N/A | N/A |
| Diff Stats | ❌ No | ✅ Yes | High | Low |
| Review Workflow | ⚠️ Partial (Patch Ledger) | ✅ Yes (Adapt) | Medium | Low |

### Table B: Implementation Timeline

| Phase | Duration | Features | Risk Level |
|-------|----------|----------|------------|
| **Phase 1: Foundation** | 2 weeks | Worktree Manager, Diff Stats | Low |
| **Phase 2: Observability** | 2 weeks | TUI Monitor, Daemon Orchestrator | Medium |
| **Phase 3: Sessions & Review** | 2 weeks | Session Registry, Review Workflow | Medium |
| **Phase 4: Integration Testing** | 1 week | E2E tests, performance tests | Low |
| **Phase 5: Rollout** | 1 week | Canary deployment, full rollout | Low |

**Total**: 8 weeks (2 months)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-07
**Authors**: AI Systems Architect (Claude Sonnet 4.5)
**Review Status**: Draft for Human + Agent Consumption
