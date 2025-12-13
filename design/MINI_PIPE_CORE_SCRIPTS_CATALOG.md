# Core Scripts Catalog - MINI_PIPE

**Generated**: 2025-12-07  
**Version**: 2.0  
**Scope**: `src/acms`, `src/minipipe`, `src/cli`, Root Level, `tools`

This document provides a comprehensive listing of all core scripts in the MINI_PIPE project with descriptions of their functionality.

---

## Table of Contents

- [Root Level Scripts](#root-level-scripts)
- [src/acms - Autonomous Code Modification System](#srcacms---autonomous-code-modification-system)
  - [Core Components](#core-components)
  - [Execution & Workflow](#execution--workflow)
  - [Gap Analysis & Planning](#gap-analysis--planning)
  - [Safety & Validation](#safety--validation)
  - [Monitoring & Notifications](#monitoring--notifications)
- [src/minipipe - Execution Engine](#srcminipipe---execution-engine)
  - [Orchestration & Execution](#orchestration--execution)
  - [Resilience Components](#resilience-components)
  - [Process & Session Management](#process--session-management)
  - [Patch Management](#patch-management)
  - [Routing & Scheduling](#routing--scheduling)
  - [Monitoring & UI](#monitoring--ui)
- [src/cli - Command Line Interfaces](#srccli---command-line-interfaces)
- [tools - Development & Profiling](#tools---development--profiling)
- [Summary Statistics](#summary-statistics)
- [Key Integration Points](#key-integration-points)

---

## Root Level Scripts

### `tasks.py`
**DOC_ID**: `DOC-INVOKE-TASKS-001`  
**Workstreams**: G1, G2

Invoke automation task file providing discoverable CLI interface for all project operations. Central automation hub using Python Invoke framework.

**Task Categories**:
- **Validation**: `validate.phase1`, `validate.phase2`, `validate_all`
- **Testing**: `test.unit`, `test.integration`, `test.e2e`, `test.performance`, `test_all`
- **Linting**: `lint.black`, `lint.isort`, `lint.flake8`, `lint.mypy`, `lint.fix`, `lint_all`
- **Maintenance**: `clean.all`, `reset`, `bootstrap`
- **CI/CD**: `ci`, `pre-commit`

**Usage**:
```bash
inv --list              # Show all tasks
inv validate_all        # Run all validations
inv test_all            # Run all tests
inv ci                  # Full CI suite
```

---

### `multi_agent_orchestrator.py`

Multi-agent orchestration system for coordinating parallel AI agents. Manages agent lifecycles and result aggregation.

**Key Features**:
- Agent pool management
- Parallel task distribution
- Result consolidation
- Cross-agent coordination

---

### `acms_test_harness.py`

Test harness for ACMS system validation. Provides structured testing framework for ACMS components.

**Key Features**:
- ACMS component testing
- Integration test support
- Result validation
- Test scenario management

---

### `validate_phase1.py`

Phase 1 Quick Wins validation script. Validates first-wave features and integrations.

**Validates**:
- GitHub Actions workflows
- Notification system
- Monitoring system
- Pre-commit configuration
- Controller integration

---

### `validate_phase2.py`

Phase 2 Core Functionality validation script. Validates second-wave improvements.

**Validates**:
- ACMS documentation
- Retry mechanism
- Loop detection
- Rollback functionality
- Result validation

---

### `validate_wave1.py`

Wave 1 baseline validation script. Validates foundational capabilities.

**Validates**:
- Core orchestration
- Basic tool execution
- State management
- Event bus functionality

---

## src/acms - Autonomous Code Modification System

### Core Components

#### `controller.py`
**Workstream**: Gap Phase Execution

Top-level CLI orchestrator for gap analysis → planning → execution. GOLDEN PATH ORCHESTRATOR - single recommended entrypoint for ACMS → MINI_PIPE.

**6-Phase Pipeline**:
1. **Gap Discovery**: Repository analysis and gap detection
2. **Gap Filtering**: Pattern matching and prioritization
3. **Plan Compilation**: UET execution plan generation
4. **Guardrail Validation**: Safety checks and anti-pattern detection
5. **Execution**: MINI_PIPE integration and task execution
6. **Result Validation**: Output verification and metrics

**Key Features**:
- Pattern-based execution with anti-pattern detection
- State persistence and recovery
- Comprehensive logging and metrics
- Integration with all ACMS subsystems

**CLI Usage**:
```bash
python -m src.acms.controller --repo /path/to/repo --phase all
python -m src.acms.controller --gaps gaps.json --plan plan.yaml
```

---

#### `ai_adapter.py`

AI provider abstraction layer. Unified interface for multiple AI backends (OpenAI, Anthropic, local models).

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (via adapter pattern)

**Key Features**:
- Provider-agnostic requests
- Retry logic with backoff
- Cost tracking
- Response streaming support
- Context window management

**Functions**:
- `create_ai_adapter()`: Factory for AI provider instances
- `AIRequest`: Standardized request format
- `AIResponse`: Unified response structure

---

#### `minipipe_adapter.py`

Adapter interface for MINI_PIPE execution engine. Bridges ACMS planning phase to MINI_PIPE execution.

**Key Features**:
- ExecutionRequest formatting
- Tool routing configuration
- Result capture and parsing
- Error translation

**Functions**:
- `create_minipipe_adapter()`: Factory for adapter instances
- `ExecutionRequest`: MINI_PIPE request format
- Result validation and extraction

---

#### `real_minipipe_adapter.py`

Production MINI_PIPE adapter implementation. Actual subprocess integration with MINI_PIPE orchestrator.

**Key Features**:
- Real process spawning
- Live output streaming
- Timeout handling
- Error recovery
- State synchronization

---

### Execution & Workflow

#### `execution_planner.py`

Execution plan construction from gap analysis. Transforms gap registry into executable task sequences.

**Key Features**:
- Dependency graph construction
- Parallel execution planning
- Resource estimation
- Priority scheduling
- Constraint validation

---

#### `uet_execution_planner.py`

UET (Unified Execution Template) execution planning. Converts UET specs into MINI_PIPE-compatible plans.

**Key Features**:
- UET template parsing
- Step decomposition
- Tool capability matching
- Execution wave planning
- Contract validation

---

#### `uet_workstream_adapter.py`

Adapter for UET workstream execution. Bridges UET specification to workstream execution format.

**Key Features**:
- UET-to-workstream translation
- Workstream validation
- Dependency resolution
- Context injection

---

#### `uet_tool_adapters.py`

Tool adapters for UET execution. Specific adapters for tools used in UET workflows.

**Supported Tools**:
- Aider (code generation)
- Custom analysis tools
- Git operations
- File system operations

---

#### `uet_submodule_io_contracts.py`

I/O contracts for UET submodules. Defines standardized input/output formats for UET components.

**Contracts**:
- `GitWorkspaceRefV1`: Git workspace reference format
- Tool input/output schemas
- State transition formats
- Error reporting structures

---

### Gap Analysis & Planning

#### `gap_registry.py`

Gap detection and tracking system. Central registry for discovered gaps and their metadata.

**Key Features**:
- Gap registration and lookup
- Priority scoring
- Category classification
- Status tracking (discovered → planned → executed → verified)
- Persistence layer

**Gap Categories**:
- Missing implementations
- Incomplete tests
- Documentation gaps
- Performance issues
- Code quality issues

---

#### `phase_plan_compiler.py`

Phase plan compilation from gap registry. Generates phased execution plans with dependencies.

**Key Features**:
- Multi-phase plan generation
- Dependency ordering
- Resource balancing
- Risk assessment
- Phase gating

---

#### `golden_path.py`

Golden path architecture and workflow definitions. Documents recommended execution paths and patterns.

**Key Concepts**:
- `RunState`: State machine for run lifecycle
- `DEFAULT_CONFIG`: Configuration defaults
- Best practice patterns
- Anti-pattern warnings

---

#### `path_registry.py`

Path management and resolution utilities. Centralizes path handling across ACMS components.

**Key Features**:
- Standard path locations
- Directory creation (`ensure_dir()`)
- Path validation
- Cross-platform compatibility

---

### Safety & Validation

#### `guardrails.py`

Safety guardrails and validation rules. Enforces pattern-based execution with anti-pattern detection.

**Key Features**:
- Pre-execution validation
- Anti-pattern detection
- Resource limit enforcement
- Dangerous operation blocking
- Execution throttling

**Guardrail Types**:
- Code modification limits
- File operation restrictions
- Dependency change validation
- Test coverage requirements
- Security checks

---

#### `result_validation.py`

Result validation and verification system. Validates execution outputs against expected contracts.

**Key Features**:
- Output format validation
- Contract compliance checking
- Quality metrics calculation
- Regression detection
- Diff analysis

---

#### `schema_utils.py`

JSON schema validation utilities. Provides schema validation for all ACMS data structures.

**Key Features**:
- Schema loading and caching
- Validation error formatting
- Schema composition
- Custom validator support

---

### Monitoring & Notifications

#### `monitoring.py`

Pipeline monitoring and metrics collection. Comprehensive observability for ACMS execution.

**Metrics Tracked**:
- Execution duration
- Gap discovery rate
- Plan compilation time
- Execution success rate
- Resource usage

**Key Features**:
- Real-time metric collection
- Historical trend analysis
- Alert generation
- Dashboard data export

---

#### `notifications.py`

Notification system for pipeline events. Multi-channel notification delivery.

**Supported Channels**:
- Console output
- File logging
- Email (SMTP)
- Webhook callbacks
- Slack integration (planned)

**Event Types**:
- Phase transitions
- Error conditions
- Completion notifications
- Progress updates

**Functions**:
- `create_notifier_from_env()`: Environment-based notifier setup

---

#### `show_run.py`

Run status display and reporting utility. Pretty-prints run state and progress.

**Key Features**:
- Formatted run summaries
- Progress visualization
- Metric display
- Error highlighting
- Timeline rendering

---

### Additional Components

#### `api_adapters.py`

External API adapter implementations. Standardized interfaces for third-party services.

**Supported APIs**:
- GitHub API
- GitLab API
- CI/CD platforms
- Code analysis services

---

#### `loop_detection.py`

Infinite loop detection for autonomous execution. Prevents runaway automation.

**Key Features**:
- Pattern recognition
- Oscillation detection
- Similarity hashing
- Threshold-based breaking
- Historical comparison

---

#### `rollback.py`

Rollback and recovery mechanisms. Handles execution failures and state restoration.

**Key Features**:
- Checkpoint creation
- State snapshots
- Incremental rollback
- Git integration
- Verification after rollback

---

## src/minipipe - Execution Engine

### Orchestration & Execution

#### `orchestrator.py`
**DOC_ID**: `DOC-CORE-ENGINE-ORCHESTRATOR-151`  
**Workstream**: WS-03-01A

Main orchestration logic for executing workstreams. Manages run lifecycle, state transitions, and event emission.

**State Machine**:
- `PENDING` → `RUNNING` → `SUCCEEDED`/`FAILED`
- Support for `QUARANTINED` and `CANCELED` states

**Key Features**:
- Run lifecycle management
- ULID generation (deterministic mode support)
- Event emission and handling
- Step execution coordination
- Database integration

---

#### `daemon_orchestrator.py`

Long-running orchestrator daemon for continuous execution. Manages persistent orchestration tasks.

**Key Features**:
- Daemon lifecycle management
- Continuous workstream processing
- Signal handling
- Health monitoring
- Auto-restart on failure

---

#### `executor.py`
**DOC_ID**: `DOC-CORE-ENGINE-EXECUTOR-149`

Parallel execution workers that run scheduled workstream tasks with isolation and telemetry capture.

**Key Features**:
- Parallel task execution
- Tool adapter integration
- Result capture and telemetry
- Subprocess adapter support
- Timeout enforcement

---

#### `tools.py`
**DOC_ID**: `DOC-CORE-ENGINE-TOOLS-161`

Tool adapter layer for AI Development Pipeline. Config-driven external tool execution with subprocess handling.

**Key Features**:
- Template-based command rendering
- Subprocess handling
- Timeout management
- Standardized result reporting
- Environment isolation

---

#### `invoke_tools.py`

Integration layer for Invoke task framework. Bridges Invoke tasks with MINI_PIPE execution.

**Key Features**:
- Task registration
- Context passing
- Result collection
- Error handling

---

### Resilience Components

#### `circuit_breaker.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-CIRCUIT-BREAKER-186`  
**Workstream**: WS-03-03A

Circuit breaker pattern implementation. Prevents cascading failures by stopping requests to failing services.

**States**:
- `CLOSED`: Normal operation, requests pass through
- `OPEN`: Too many failures, requests blocked
- `HALF_OPEN`: Testing if service recovered

**Key Features**:
- Configurable failure threshold
- Automatic recovery attempts
- State transition callbacks
- Per-service tracking

---

#### `circuit_breakers.py`
**DOC_ID**: `DOC-CORE-ENGINE-CIRCUIT-BREAKERS-144`  
**Workstream**: Phase 6 (PH-06)

Circuit breakers, retries, and oscillation detection utilities. Lightweight pure Python implementation.

**Key Features**:
- Deterministic defaults when config missing
- Error signature computation
- Diff hash calculation
- Oscillation detection
- Pure stdlib implementation

---

#### `retry.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-RETRY-189`  
**Workstream**: WS-03-03A

Retry logic with exponential backoff and jitter. Provides retry strategies for failed operations.

**Key Features**:
- Exponential backoff
- Jitter for collision avoidance
- Configurable max attempts
- Strategy pattern implementation
- Per-operation retry policies

---

#### `resilient_executor.py`
**DOC_ID**: `DOC-CORE-RESILIENCE-RESILIENT-EXECUTOR-188`  
**Workstream**: WS-03-03A

Combines circuit breakers and retry logic for robust task execution.

**Key Features**:
- Circuit breaker integration
- Retry strategy management
- Per-tool failure tracking
- Auto-recovery
- Comprehensive error handling

---

#### `recovery.py`

Failure handling and retry orchestration. Coordinates retries after error recovery.

**Key Features**:
- Recovery policy configuration
- Task retry coordination
- Event-driven recovery
- Backoff strategy support
- Failure analysis

---

### Process & Session Management

#### `process_spawner.py`
**DOC_ID**: `DOC-CORE-ENGINE-PROCESS-SPAWNER-154`  
**Workstream**: Phase I-1 WS-I2

Worker process spawning for parallel execution. Manages subprocess creation, sandboxing, and lifecycle.

**Key Features**:
- Worker process spawning
- Sandbox environment creation
- Process lifecycle management
- Environment variable handling
- Resource limiting

---

#### `session_registry.py`

Session tracking and management. Central registry for active execution sessions.

**Key Features**:
- Session creation and lookup
- Session state tracking
- Resource association
- Cleanup on session end
- Multi-session support

---

#### `worktree_manager.py`

Git worktree management for isolated execution. Creates and manages separate worktrees for parallel tasks.

**Key Features**:
- Worktree creation and deletion
- Branch isolation
- Cleanup automation
- Path resolution
- Conflict prevention

---

### Patch Management

#### `patch_converter.py`
**DOC_ID**: `DOC-CORE-ENGINE-PATCH-CONVERTER-152`

Converts tool outputs to unified diff format. Standardizes patches from different tools.

**Key Features**:
- Tool-specific to unified patch conversion
- Patch format standardization
- Metadata tracking
- Multi-tool support (aider, custom tools)

---

#### `patch_ledger.py`
**DOC_ID**: `DOC-CORE-ENGINE-PATCH-LEDGER-153`  
**Workstream**: WS-NEXT-002-002

Manages patch lifecycle with state machine transitions. Tracks patch validation, application, verification, and quarantine.

**State Machine**:
- `created → validated → queued → applied → verified → committed`
- `any → apply_failed` (retry or quarantine)
- `any → quarantined` (safety)
- `any → dropped` (reject)

**Key Features**:
- Patch lifecycle tracking
- State persistence
- Conflict detection
- Rollback support

---

### Routing & Scheduling

#### `router.py`
**DOC_ID**: `DOC-CORE-ENGINE-ROUTER-157`  
**Workstream**: WS-03-01B

Routes tasks to appropriate tools based on `router_config.json`. Supports multiple routing strategies.

**Key Features**:
- Task-to-tool routing
- Multiple routing strategies
- Capability matching
- Round-robin and weighted routing
- File-backed state persistence

**Routing Strategies**:
- Capability-based
- Load-balanced
- Cost-optimized
- Latency-minimized

---

#### `scheduler.py`
**DOC_ID**: `DOC-CORE-ENGINE-SCHEDULER-158`  
**Workstream**: WS-03-01C

Schedules and executes tasks with dependency resolution. Handles parallel and sequential execution.

**Key Features**:
- Task dependency resolution
- Parallel execution coordination
- Sequential execution handling
- Task status tracking (pending, ready, running, completed, failed)
- Wave-based execution

---

### Monitoring & UI

#### `tui_monitor.py`

Terminal User Interface for monitoring execution. Rich terminal-based monitoring display.

**Key Features**:
- Real-time status updates
- Progress bars
- Log streaming
- Interactive controls
- Multi-pane layout

**UI Components**:
- Run status overview
- Task progress
- Resource utilization
- Recent logs
- Error highlighting

---

## src/cli - Command Line Interfaces

### `validate_everything.py`

Comprehensive validation suite runner. Executes all validation checks across the project.

**Validation Targets**:
- Phase 1 completeness
- Phase 2 completeness
- Schema compliance
- Integration points
- Documentation accuracy

---

### `demo_minimal_scenario.py`

Minimal demonstration scenario. Simple end-to-end example of MINI_PIPE execution.

**Demonstrates**:
- Basic orchestration
- Tool execution
- Result capture
- Minimal configuration

---

### `demo_acms_pipeline.py`

Full ACMS pipeline demonstration. Complete example showing all ACMS phases.

**Demonstrates**:
- Gap discovery
- Plan compilation
- Guardrail validation
- Execution
- Result validation

---

## tools - Development & Profiling

### `validate_process_steps_schema.py`

Schema validation for process step definitions. Ensures process schemas are valid and consistent.

**Key Features**:
- JSON schema validation
- Cross-reference checking
- Deprecation warnings
- Version compatibility

---

### `tools/profiling/`

#### `profile_runner.py`

Main profiling orchestration. Coordinates performance profiling runs.

**Key Features**:
- Profile scenario execution
- Metric collection
- Report generation
- Historical comparison

---

#### `establish_baseline.py`

Baseline performance establishment. Creates initial performance benchmarks.

**Key Features**:
- Benchmark execution
- Baseline data capture
- Statistical analysis
- Baseline storage

---

#### `create_minimal_baseline.py`

Minimal baseline creation for quick validation. Fast baseline for CI/CD pipelines.

**Key Features**:
- Lightweight benchmarks
- Fast execution
- Essential metrics only
- CI optimization

---

#### `compare_benchmarks.py`

Benchmark comparison and regression detection. Compares current performance against baselines.

**Key Features**:
- Statistical comparison
- Regression detection
- Performance trend analysis
- Report generation

---

#### `baseline_scenarios.py`

Predefined benchmark scenarios. Standard test cases for performance validation.

**Scenarios**:
- Basic orchestration
- Parallel execution
- Large workload
- Error handling
- Recovery paths

---

## Summary Statistics

| Directory | Script Count | Key Focus |
|-----------|--------------|-----------|
| `src/acms` | 25 | Autonomous gap analysis, planning, execution |
| `src/minipipe` | 18 | Orchestration, execution, resilience |
| `src/cli` | 3 | Command-line interfaces and demos |
| `Root level` | 6 | Validation, testing, automation |
| `tools/profiling` | 5 | Performance benchmarking and analysis |
| **Total** | **57** | **Complete AI-driven code transformation pipeline** |

---

## Key Integration Points

### ACMS → MINI_PIPE Flow

1. **Gap Discovery** (`gap_registry.py`, `controller.py`)
   - Repository analysis
   - Pattern matching
   - Gap classification

2. **Planning** (`phase_plan_compiler.py`, `uet_execution_planner.py`)
   - UET plan generation
   - Dependency resolution
   - Resource estimation

3. **Guardrails** (`guardrails.py`, `result_validation.py`)
   - Safety validation
   - Anti-pattern detection
   - Resource limits

4. **Execution** (`minipipe_adapter.py` → `orchestrator.py` → `executor.py`)
   - Task routing
   - Parallel execution
   - Result capture

5. **Monitoring** (`monitoring.py`, `tui_monitor.py`, `notifications.py`)
   - Progress tracking
   - Metric collection
   - Event notification

### Resilience Stack

- **Circuit Breakers**: `circuit_breaker.py`, `circuit_breakers.py`
- **Retry Logic**: `retry.py`, `resilient_executor.py`
- **Recovery**: `recovery.py`, `rollback.py`
- **Loop Detection**: `loop_detection.py`

### State Management

- **Persistence**: `session_registry.py`, `patch_ledger.py`
- **State Machines**: `orchestrator.py` (Run/Step states)
- **Path Management**: `path_registry.py`, `worktree_manager.py`

### Validation & Quality

- **Entry/Exit Contracts**: `uet_submodule_io_contracts.py`
- **Schema Validation**: `schema_utils.py`, `validate_process_steps_schema.py`
- **Result Validation**: `result_validation.py`
- **Phase Validation**: `validate_phase1.py`, `validate_phase2.py`

---

## Automation Entry Points

### Primary CLI Entry Point
```bash
# ACMS Controller - Main orchestration
python -m src.acms.controller --repo /path/to/repo --phase all
```

### Invoke Task Runner
```bash
# Show all available tasks
inv --list

# Common workflows
inv validate_all    # All validation checks
inv test_all        # All test suites
inv ci              # Full CI pipeline
inv bootstrap       # Environment setup
```

### Direct MINI_PIPE Orchestration
```bash
# Direct orchestrator invocation
python -m src.minipipe.orchestrator --plan plan.json
```

### Monitoring & Demos
```bash
# Terminal UI monitor
python src/minipipe/tui_monitor.py

# Demo scenarios
python src/cli/demo_minimal_scenario.py
python src/cli/demo_acms_pipeline.py
```

---

## Document Maintenance

- **Version**: 2.0
- **Last Updated**: 2025-12-07
- **Auto-Update**: Regenerate when new scripts are added to core directories
- **Review Cycle**: Quarterly or on major feature additions

---

## Related Documentation

- **README.md**: Quick start and common tasks
- **INVOKE_DOCUMENT_INDEX.md**: Invoke task documentation index
- **INVOKE_VALIDATION_CHECKLIST.md**: Validation requirements
- **REC_006_OPTIONAL_FEATURES_GUIDE.md**: Optional feature configuration
- **AUTOMATION_CHAIN_ANALYSIS_REPORT.md**: Automation architecture
