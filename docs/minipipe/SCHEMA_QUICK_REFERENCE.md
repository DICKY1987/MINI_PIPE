# Process Steps Schema - Quick Reference Card

## Schema Fields

### Required Fields (MASTER_SPLINTER-aligned)

```yaml
step_id: "P0-STEP-001"                    # Unique ID with phase prefix
phase: "INIT"                             # INIT | GAP_ANALYSIS | PLANNING | EXECUTION | SUMMARY | DONE
name: "Short descriptive label"           # 4-8 words max
responsible_component: "acms_controller"  # Component executing this step
operation_kind: "initialization"          # From taxonomy (see below)
description: |                            # One precise paragraph
  What this step does in detail...
inputs:                                   # What this consumes
  - "Input 1"
  - "Input 2"
expected_outputs:                         # What this produces
  - "Output 1"
  - "Output 2"
requires_human_confirmation: false        # Boolean
```

### Optional but Recommended Fields

```yaml
pattern_ids: ["PAT-001"]                  # Related pattern IDs
anti_pattern_ids: ["AP_PLANNING_LOOP"]    # Related anti-pattern IDs
implementation_files:                     # Source code files
  - "acms_controller.py"
artifacts_created:                        # Files/DB records created
  - ".acms_runs/<RUN_ID>/file.json"
artifacts_updated:                        # Files/DB records modified
  - "gap_registry.json"
state_transition:                         # If state change occurs
  from_state: "INIT"
  to_state: "GAP_ANALYSIS"
preconditions:                            # Must be true before
  - "Directory exists"
postconditions:                           # Must be true after
  - "File created"
error_handling: "How failures handled"    # Failure behavior
guardrail_checkpoint_id: "GC-INIT"        # If guardrail checkpoint
metrics_emitted:                          # What gets logged/tracked
  - "Ledger: event_name"
lens: "process"                           # Primary concern area
automation_level: "fully_automatic"       # Human intervention level
estimated_duration: "0.1 seconds"         # Typical execution time
retry_strategy: "No retry"                # Retry behavior
dependencies: ["P0-STEP-001"]             # Other step_ids needed first
```

---

## Operation Kind Taxonomy

| Operation Kind | Use For |
|---------------|---------|
| `state_transition` | State machine phase changes |
| `gap_discovery` | AI-driven gap finding |
| `gap_normalization` | Gap registry operations |
| `planning` | Workstream generation, clustering |
| `plan_compilation` | Task generation, DAG building |
| `dag_build` | Scheduler DAG construction |
| `task_execution` | Actual task running |
| `guardrail_check` | Pattern/anti-pattern validation |
| `summary_generation` | Report/summary creation |
| `initialization` | Bootstrap, component setup |
| `persistence` | File I/O, database operations |
| `event_emission` | Logging, metrics collection |

---

## Lenses (Concern Areas)

| Lens | Focus |
|------|-------|
| `logical` | Correctness, validation, data integrity |
| `performance` | Optimization, concurrency, efficiency |
| `architecture` | Boundaries, state management, modularity |
| `process` | Workflow, state transitions, orchestration |
| `automation` | Guardrails, anti-patterns, autonomous execution |

---

## Automation Levels

| Level | Meaning |
|-------|---------|
| `fully_automatic` | No human intervention required |
| `operator_assisted` | Human review/approval gates exist |
| `manual_only` | Requires manual execution |

---

## State Machine Phases

```
INIT → GAP_ANALYSIS → PLANNING → EXECUTION → SUMMARY → DONE
  ↓         ↓            ↓
FAILED    DONE         DONE
        (analyze)    (plan_only)
```

Valid transitions:
- `INIT → GAP_ANALYSIS`
- `GAP_ANALYSIS → PLANNING | DONE`
- `PLANNING → EXECUTION | DONE`
- `EXECUTION → SUMMARY`
- `SUMMARY → DONE`
- `* → FAILED` (any state can fail)

---

## Artifact Registry Entry

```yaml
artifact_name:
  path: ".acms_runs/<RUN_ID>/file.json"
  type: "file"                    # file | directory | append_only_log | database
  format: "JSON"                  # JSON | YAML | JSONL | Markdown | etc.
  created_by: "P0-STEP-005"       # Step that creates it
  updated_by:                     # Steps that modify it
    - "P0-STEP-009"
    - "P1-STEP-022"
  description: "What it contains"
  schema:                         # Optional: data format spec
    format: "{field: type, ...}"
```

---

## Guardrail Checkpoint Entry

```yaml
checkpoint_id:
  checkpoint_id: "GC-INIT"
  step_id: "P0-STEP-008"
  phase: "INIT"
  name: "Checkpoint Name"
  description: "What gets validated"
  validation_type: "initialization"  # initialization | pre_execution | post_execution | anti_pattern_detection | metric_tracking | comprehensive
  anti_patterns: ["AP_PLANNING_LOOP"]  # Optional: related anti-patterns
  actions:                        # What this checkpoint does
    - "Action 1"
    - "Action 2"
```

---

## Component Entry

```yaml
component_name:
  file: "component.py"
  role: "Brief role description"
  responsibilities:
    - "Responsibility 1"
    - "Responsibility 2"
  interfaces:                     # Optional: key interfaces/APIs
    - "Interface 1"
  data_structures:                # Optional: key data structures
    - "Structure 1"
```

---

## Quick Examples

### Simple Initialization Step

```yaml
step_id: "P0-STEP-004"
phase: "INIT"
name: "Create run directory structure"
responsible_component: "acms_controller"
operation_kind: "initialization"
description: |
  Create .acms_runs/<RUN_ID>/ with subdirectories: workstreams/, logs/, reports/, patches/.
inputs:
  - "run_id"
  - "repo_root"
expected_outputs:
  - "Run directory structure created on disk"
requires_human_confirmation: false
implementation_files: ["acms_controller.py"]
artifacts_created:
  - ".acms_runs/<RUN_ID>/"
  - ".acms_runs/<RUN_ID>/workstreams/"
  - ".acms_runs/<RUN_ID>/logs/"
  - ".acms_runs/<RUN_ID>/reports/"
  - ".acms_runs/<RUN_ID>/patches/"
lens: "process"
automation_level: "fully_automatic"
```

### State Transition Step

```yaml
step_id: "P0-STEP-009"
phase: "INIT"
name: "Transition to GAP_ANALYSIS"
responsible_component: "acms_controller"
operation_kind: "state_transition"
description: |
  Log state transition INIT → GAP_ANALYSIS to ledger and console.
inputs:
  - "current_state: INIT"
expected_outputs:
  - "current_state: GAP_ANALYSIS"
  - "Ledger entry: enter_state(GAP_ANALYSIS)"
requires_human_confirmation: false
state_transition:
  from_state: "INIT"
  to_state: "GAP_ANALYSIS"
metrics_emitted:
  - "Ledger: {event: enter_state, state: GAP_ANALYSIS}"
  - "Console: [STATE] INIT → GAP_ANALYSIS"
lens: "process"
automation_level: "fully_automatic"
```

### Guardrail Checkpoint Step

```yaml
step_id: "P3-STEP-038"
phase: "PLANNING"
name: "GUARDRAILS: Validate pattern_ids in task metadata"
responsible_component: "guardrails"
operation_kind: "guardrail_check"
description: |
  For each task with pattern_id, validate: pattern exists, enabled,
  file paths in scope, tools allowed. Halt if critical violations.
inputs:
  - "List[MiniPipeTask] with pattern_id metadata"
  - "PATTERN_INDEX.yaml"
expected_outputs:
  - "Validation result: pass | warnings | errors"
  - "List of violations (if any)"
requires_human_confirmation: false
implementation_files: ["guardrails.py", "phase_plan_compiler.py"]
artifacts_updated:
  - "run_stats.guardrail_violations (in-memory)"
guardrail_checkpoint_id: "GC-PLAN-COMPILATION"
error_handling: |
  Critical violations: Halt compilation, transition to FAILED.
  Warnings: Log and continue.
metrics_emitted:
  - "Ledger: {event: guardrail_checkpoint, checkpoint_id: GC-PLAN-COMPILATION}"
lens: "automation"
automation_level: "fully_automatic"
```

---

## Validation Checklist

When creating a new step:

- [ ] `step_id` follows format `P<phase>-STEP-<number>`
- [ ] `phase` is valid (INIT | GAP_ANALYSIS | PLANNING | EXECUTION | SUMMARY | DONE)
- [ ] `name` is concise (4-8 words)
- [ ] `responsible_component` exists in components registry
- [ ] `operation_kind` exists in operation_kinds taxonomy
- [ ] `description` is one clear paragraph
- [ ] `inputs` is a list (even if empty)
- [ ] `expected_outputs` is a list (even if empty)
- [ ] `requires_human_confirmation` is boolean
- [ ] `lens` is specified (logical/performance/architecture/process/automation)
- [ ] `automation_level` is specified
- [ ] If creates files: listed in `artifacts_created`
- [ ] If modifies files: listed in `artifacts_updated`
- [ ] If state transition: `state_transition` fields present
- [ ] If guardrail: `guardrail_checkpoint_id` present
- [ ] If emits metrics: listed in `metrics_emitted`

---

## Files

| File | Purpose |
|------|---------|
| `PROCESS_STEPS_SCHEMA.yaml` | Schema-based documentation (Phases 0-3) |
| `PROCESS_STEPS_SCHEMA_GUIDE.md` | Comprehensive guide and examples |
| `SCHEMA_IMPLEMENTATION_SUMMARY.md` | Summary of improvements and benefits |
| `SCHEMA_QUICK_REFERENCE.md` | This quick reference card |
| `validate_process_steps_schema.py` | Schema validator tool |

---

## Common Patterns

### Pattern: File Creation Step

```yaml
operation_kind: "persistence"
artifacts_created:
  - "path/to/file.json"
postconditions:
  - "File exists at path"
```

### Pattern: State Transition Step

```yaml
operation_kind: "state_transition"
state_transition:
  from_state: "OLD_STATE"
  to_state: "NEW_STATE"
metrics_emitted:
  - "Ledger: enter_state(NEW_STATE)"
```

### Pattern: Guardrail Checkpoint

```yaml
operation_kind: "guardrail_check"
guardrail_checkpoint_id: "GC-<NAME>"
lens: "automation"
error_handling: "Halt if violations..."
```

### Pattern: Component Interaction

```yaml
inputs:
  - "Data from component A"
expected_outputs:
  - "Data for component B"
implementation_files:
  - "component_a.py"
  - "component_b.py"
```

---

## Quick Queries (Python)

```python
import yaml

# Load schema
with open('PROCESS_STEPS_SCHEMA.yaml') as f:
    schema = yaml.safe_load(f)

# Get all steps in a phase
def get_phase_steps(phase_id):
    return schema['phases'][phase_id]['steps']

# Get steps by lens
def get_steps_by_lens(lens):
    steps = []
    for phase in schema['phases'].values():
        for step in phase['steps']:
            if step.get('lens') == lens:
                steps.append(step)
    return steps

# Get artifact lifecycle
def get_artifact_lifecycle(artifact_name):
    artifact = schema['artifact_registry'][artifact_name]
    return {
        'created_by': artifact['created_by'],
        'updated_by': artifact.get('updated_by', [])
    }

# Get guardrail checkpoints
def get_guardrail_checkpoints():
    return schema['guardrail_checkpoints']
```

---

**Version**: 3.0  
**Last Updated**: 2025-12-07  
**Reference**: See `PROCESS_STEPS_SCHEMA_GUIDE.md` for detailed documentation
