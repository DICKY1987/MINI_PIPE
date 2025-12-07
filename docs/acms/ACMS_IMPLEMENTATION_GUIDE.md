# ACMS Implementation Guide

**Automated Code Modification System - Gap Phase Execution Pipeline**

Version: 0.1.0  
Status: Implementation Complete  
Date: 2025-12-06

---

## Overview

The ACMS (Automated Code Modification System) implements the GAP_PHASE_EXECUTION_MINI_PIPE specification, providing a complete pipeline from gap analysis through automated code execution.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ACMS Controller                          │
│                 (acms_controller.py)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Gap Registry │ │  Execution  │ │ Phase Plan  │
│             │ │   Planner   │ │  Compiler   │
└─────────────┘ └─────────────┘ └─────────────┘
       │               │               │
       └───────────────┼───────────────┘
                       ▼
            ┌──────────────────┐
            │   MINI_PIPE      │
            │   Orchestrator   │
            └──────────────────┘
```

## Components

### 1. Gap Registry (`gap_registry.py`)

**Purpose:** Normalized storage and query layer for gap findings.

**Key Features:**
- Gap lifecycle tracking (discovered → clustered → planned → resolved)
- Severity levels (critical, high, medium, low, info)
- Query API by status, cluster, category, severity, workstream
- JSON persistence

**Usage:**
```python
from gap_registry import GapRegistry, GapRecord, GapStatus, GapSeverity

# Initialize registry
registry = GapRegistry(storage_path=Path("gap_registry.json"))

# Load from gap analysis report
count = registry.load_from_report(Path("gap_report.json"))

# Query gaps
unresolved = registry.get_unresolved()
critical = registry.get_by_severity(GapSeverity.CRITICAL)

# Update status
registry.update_status("GAP_0001", GapStatus.RESOLVED)

# Save
registry.save()
```

### 2. Execution Planner (`execution_planner.py`)

**Purpose:** Clusters gaps into workstreams with dependency resolution.

**Clustering Strategies:**
- **Category-based:** Groups gaps by category (testing, documentation, etc.)
- **File proximity:** Groups gaps affecting related files

**Key Features:**
- Priority scoring based on severity
- File scope limiting (max files per workstream)
- Dependency extraction between workstreams
- Effort estimation (low/medium/high)

**Usage:**
```python
from execution_planner import ExecutionPlanner, Workstream

planner = ExecutionPlanner(gap_registry)

# Cluster by category
workstreams = planner.cluster_gaps(
    max_files_per_workstream=10,
    category_based=True
)

# Get prioritized workstreams
prioritized = planner.get_prioritized_workstreams()

# Save to JSON
planner.save_workstreams(Path("workstreams.json"))
```

### 3. Phase Plan Compiler (`phase_plan_compiler.py`)

**Purpose:** Compiles phase plans and workstreams into MINI_PIPE execution plans.

**Compilation Modes:**
- From workstreams (auto-generates analysis → implementation → test)
- From phase plan files (MASTER_SPLINTER format)

**Task Types:**
- `analysis` - Code analysis and review
- `implementation` - Code changes and fixes
- `test` - Testing and validation
- `refactor` - Code refactoring

**Usage:**
```python
from phase_plan_compiler import PhasePlanCompiler

compiler = PhasePlanCompiler()

# From workstreams
plan = compiler.compile_from_workstreams(
    workstreams=workstreams,
    repo_root=Path("/path/to/repo")
)

# From phase plan files
plan = compiler.compile_from_phase_plan_files(
    phase_plan_paths=[Path("plan1.json"), Path("plan2.json")],
    repo_root=Path("/path/to/repo")
)

# Save plan
compiler.save_plan(plan, Path("execution_plan.json"))
```

### 4. ACMS Controller (`acms_controller.py`)

**Purpose:** Top-level orchestrator for all 6 phases.

**Execution Modes:**
- `full` - Run all phases (gap → plan → execute → summary)
- `analyze_only` - Phase 0-1 only (gap discovery)
- `plan_only` - Phase 0-3 (gap → plan)
- `execute_only` - Phase 4-5 (execute → summary)

**CLI Usage:**
```bash
# Full pipeline
python acms_controller.py /path/to/repo --mode full

# Analysis only
python acms_controller.py /path/to/repo --mode analyze_only

# With custom run ID
python acms_controller.py /path/to/repo --run_id MY_RUN_001

# Help
python acms_controller.py --help
```

**Python Usage:**
```python
from acms_controller import ACMSController

controller = ACMSController(
    repo_root=Path("/path/to/repo"),
    run_id="CUSTOM_RUN_ID"  # Optional
)

result = controller.run_full_cycle(mode="full")
print(result)
```

## Pipeline Phases

### Phase 0: Run Configuration
- Generate ULID run identifier
- Create run directory (`.acms_runs/{run_id}/`)
- Initialize state tracking

### Phase 1: Gap Discovery
- Load gap analysis prompt (`OVERLAP_AUTOMATION_AND_MASTER_GAP_ANALYSIS.merged.json`)
- Execute AI gap analysis (placeholder - integration pending)
- Parse gap report into registry
- Save normalized gap data

**Output:** `gap_analysis_report.json`, `gap_registry.json`

### Phase 2: Gap Consolidation and Clustering
- Cluster gaps into workstreams
- Calculate priority scores
- Extract dependencies
- Estimate effort levels

**Output:** `workstreams.json`

### Phase 3: Plan Generation
- Compile workstreams into MINI_PIPE tasks
- Create task dependency DAG
- Generate analysis → implementation → test chains
- Save execution plan

**Output:** `mini_pipe_execution_plan.json`

### Phase 4: Execution via MINI_PIPE
- Load execution plan
- Invoke MINI_PIPE orchestrator (integration pending)
- Execute tasks with dependency resolution
- Track results and failures

**Output:** Execution logs, patch files

### Phase 5: Summary and Snapshot
- Generate run summary
- Calculate statistics (gaps resolved, tasks completed)
- Save final state
- Optional: Patch ledger tracking

**Output:** `summary_report.json`, `acms_state.json`

## Run Directory Structure

Each run creates a self-contained directory:

```
.acms_runs/
└── {run_id}/
    ├── acms_state.json              # Controller state
    ├── gap_analysis_report.json     # Raw gap analysis
    ├── gap_registry.json            # Normalized gaps
    ├── workstreams.json             # Clustered workstreams
    ├── mini_pipe_execution_plan.json # Task execution plan
    └── summary_report.json          # Final summary
```

## Integration Points

### AI Prompt Integration

**Phase 1 - Gap Analysis:**
```python
# In _run_ai_gap_analysis()
# TODO: Invoke AI with OVERLAP_AUTOMATION_AND_MASTER_GAP_ANALYSIS.merged.json
# Expected output: JSON with gaps array following contract
```

**Phase 3 - Plan Generation:**
```python
# TODO: Use MASTER_SPLINTER_PHASE_PLAN_TEMPLATE_GUIDE.json
# To instruct AI in generating phase plans
```

**Phase 4 - Execution:**
```python
# TODO: Integrate with MINI_PIPE_orchestrator_cli.py
# Pass execution plan and await results
```

### MINI_PIPE Integration

The execution plan format is compatible with MINI_PIPE:

```json
{
  "plan_id": "PLAN_20251206_192330",
  "tasks": [
    {
      "task_id": "TASK_0001",
      "task_kind": "analysis",
      "description": "Analyze files for testing",
      "depends_on": [],
      "metadata": {
        "workstream_id": "WS_TESTING_0001",
        "gap_ids": ["GAP_0001"],
        "file_scope": ["file1.py", "file2.py"],
        "repo_root": "/path/to/repo"
      }
    }
  ]
}
```

## Configuration

### Gap Registry Configuration

```python
GapRegistry(
    storage_path=Path("gap_registry.json")  # Optional persistence
)
```

### Execution Planner Configuration

```python
planner.cluster_gaps(
    max_files_per_workstream=10,  # File scope limit
    category_based=True           # vs file_proximity
)
```

### ACMS Controller Configuration

Environment-based configuration (future):
- `ACMS_AI_ENDPOINT` - AI service endpoint
- `ACMS_MINI_PIPE_PATH` - MINI_PIPE installation path
- `ACMS_DEFAULT_MODE` - Default execution mode

## Testing

### Unit Tests

```bash
# Test gap registry
python -m pytest tests/test_gap_registry.py

# Test execution planner
python -m pytest tests/test_execution_planner.py

# Test phase plan compiler
python -m pytest tests/test_phase_plan_compiler.py
```

### Integration Test

```bash
# Run full pipeline on test repo
python acms_controller.py ./test_repo --mode full
```

### Manual Validation

```bash
# Check gap discovery
python acms_controller.py . --mode analyze_only
cat .acms_runs/{run_id}/gap_registry.json

# Check planning
python acms_controller.py . --mode plan_only
cat .acms_runs/{run_id}/mini_pipe_execution_plan.json
```

## Troubleshooting

### No gaps discovered
- Check gap analysis prompt exists
- Verify gap report JSON format
- Ensure `gaps` array in report

### Empty workstreams
- Check that gaps have unresolved status
- Verify gaps loaded into registry
- Check clustering parameters

### Task dependencies broken
- Verify workstream dependencies are valid
- Check task ID references
- Review compiler logic

### Execution fails
- Verify MINI_PIPE orchestrator available
- Check execution plan format
- Review task metadata completeness

## Development Roadmap

### Immediate (v0.2.0)
- [ ] AI gap analysis integration
- [ ] MINI_PIPE orchestrator integration
- [ ] Patch ledger integration
- [ ] Unit test coverage

### Short-term (v0.3.0)
- [ ] Multi-agent execution profiles
- [ ] Review gates and approval workflow
- [ ] Real-time progress monitoring
- [ ] Git branch management

### Long-term (v1.0.0)
- [ ] Continuous gap analysis mode
- [ ] Incremental execution
- [ ] Rollback and recovery
- [ ] Web UI for monitoring

## Contributing

When extending ACMS:

1. **Maintain phase isolation** - Each phase should be independently testable
2. **Preserve artifacts** - All intermediate outputs should be saved
3. **Follow naming conventions** - Use consistent ID prefixes (GAP_, WS_, TASK_)
4. **Document integration points** - Mark placeholders for AI/MINI_PIPE integration
5. **Test determinism** - Ensure same inputs produce same plans

## References

- **Specification:** `GAP_PHASE_EXECUTION_MINI_PIPE_SPEC_V1` (JSON provided)
- **Gap Analysis Framework:** `COMPREHENSIVE_GAP_FINDING_FRAMEWORK.json`
- **Phase Plan Guide:** `MASTER_SPLINTER_PHASE_PLAN_TEMPLATE_GUIDE.json`
- **MINI_PIPE Core:** `MINI_PIPE_CORE_COMPONENTS.md`

## License

(Specify license as appropriate)

---

**Implementation Status:** ✅ Core pipeline complete, AI/MINI_PIPE integration pending
