# Process Steps Schema-Based Documentation Guide

## Version 3.0 - Schema-Based Process Steps

### Overview

This document demonstrates how to transform the existing `MINI_PIPE_Process_steps.txt` into a **standardized schema-based format** that aligns with the MASTER_SPLINTER `execution_plan_steps` schema.

### Key Improvements

1. **Standard Schema for Every Step**: All steps follow the same structure
2. **Files Associated with Steps**: Clear artifact tracking
3. **Step Deliverables**: Explicit inputs/outputs
4. **Enhanced Metadata**: Lenses, automation levels, guardrail checkpoints

---

## Standard Step Schema

Every step now follows this canonical schema (aligned with MASTER_SPLINTER):

```yaml
step_id: "P0-STEP-001"                    # Unique ID (phase-prefixed)
phase: "INIT"                             # INIT | GAP_ANALYSIS | PLANNING | EXECUTION | SUMMARY | DONE
name: "Initialize run ledger"             # Short label (4-8 words max)
responsible_component: "acms_controller"  # Component/tool executing this step
operation_kind: "initialization"          # High-level category (see below)
description: |                            # One precise paragraph
  Create append-only JSONL ledger...
inputs:                                   # What this step consumes
  - "run_id"
  - "Run directory path"
expected_outputs:                         # What this step produces (deliverables)
  - "Ledger file created with initial INIT event"
requires_human_confirmation: false        # Boolean

# Optional but recommended fields:
pattern_ids: ["PAT-001"]                  # Related patterns
anti_pattern_ids: ["AP_PLANNING_LOOP"]    # Related anti-patterns
implementation_files:                     # Source code implementing this
  - "acms_controller.py"
artifacts_created:                        # Files/DB records created
  - ".acms_runs/<RUN_ID>/run.ledger.jsonl"
artifacts_updated:                        # Files/DB records modified
  - "run_stats (in-memory)"
state_transition:                         # If state machine transition occurs
  from_state: "INIT"
  to_state: "GAP_ANALYSIS"
preconditions:                            # What must be true before
  - "Run directory exists"
postconditions:                           # What must be true after
  - "Ledger file exists and has INIT event"
error_handling: "Log error and transition to FAILED state"
guardrail_checkpoint_id: "GC-INIT"        # If this is a guardrail checkpoint
metrics_emitted:                          # What gets logged/tracked
  - "Ledger entry: enter_state(INIT)"
  - "Console: [STATE] transition message"
lens: "process"                           # Primary lens (logical/performance/architecture/process/automation)
automation_level: "fully_automatic"       # fully_automatic | operator_assisted | manual_only
estimated_duration: "0.1 seconds"         # Typical execution time
retry_strategy: "No retry"                # How failures are retried
dependencies: []                          # Other step_ids this depends on
```

### Operation Kinds

Standardized operation categories:

- **state_transition**: State machine transitions
- **gap_discovery**: AI-driven gap finding
- **gap_normalization**: Gap registry operations
- **planning**: Workstream generation, clustering
- **plan_compilation**: Task generation, DAG building
- **dag_build**: Scheduler DAG construction
- **task_execution**: Actual task running
- **guardrail_check**: Pattern/anti-pattern validation
- **summary_generation**: Report/summary creation
- **initialization**: Bootstrap, setup operations
- **persistence**: Save/load operations
- **event_emission**: Logging, event bus operations

---

## Example: Complete Step Documentation

### Step P0-STEP-005: Initialize Run Ledger

```yaml
step_id: "P0-STEP-005"
phase: "INIT"
name: "Initialize run ledger"
responsible_component: "acms_controller"
operation_kind: "initialization"

description: |
  Create append-only JSONL ledger at .acms_runs/<RUN_ID>/run.ledger.jsonl.
  First entry: {"event": "enter_state", "state": "INIT", "ts": "...", "run_id": "..."}.
  This ledger tracks all state transitions and events throughout the run lifecycle.

inputs:
  - "run_id (ULID format)"
  - "Run directory path (.acms_runs/<RUN_ID>/)"
  - "Initial state: INIT"

expected_outputs:
  - "Ledger file created on disk"
  - "First JSONL entry written: enter_state(INIT)"
  - "Ledger file handle ready for append operations"

requires_human_confirmation: false

implementation_files:
  - "acms_controller.py"

artifacts_created:
  - ".acms_runs/<RUN_ID>/run.ledger.jsonl"

preconditions:
  - "Run directory .acms_runs/<RUN_ID>/ exists"
  - "run_id has been generated"

postconditions:
  - "Ledger file exists"
  - "Ledger contains exactly one JSONL entry"
  - "Entry has event='enter_state' and state='INIT'"

error_handling: |
  If file creation fails (permissions, disk space), log error to console
  and transition run to FAILED state. No retry.

metrics_emitted:
  - "Ledger entry: {event: enter_state, state: INIT, ts: <ISO8601>, run_id: <ULID>}"
  - "Console: [INIT] Run ledger initialized"

lens: "process"
automation_level: "fully_automatic"
estimated_duration: "0.05 seconds"
retry_strategy: "No retry (fatal error if fails)"
```

---

## Example: Guardrail Checkpoint Step

### Step P3-STEP-038: GUARDRAILS - Validate Pattern IDs

```yaml
step_id: "P3-STEP-038"
phase: "PLANNING"
name: "GUARDRAILS: Validate pattern_ids in task metadata"
responsible_component: "guardrails"
operation_kind: "guardrail_check"

description: |
  For each task with pattern_id in metadata, validate:
  - Pattern exists in PATTERN_INDEX.yaml
  - Pattern is enabled
  - File paths within pattern's path_scope
  - Tools in pattern's allowed_tools list
  - No forbidden operations
  Halt compilation if critical violations found.

inputs:
  - "List[MiniPipeTask] with pattern_id metadata"
  - "PATTERN_INDEX.yaml loaded in memory"

expected_outputs:
  - "Validation result: pass | warnings | errors"
  - "List of violations (if any)"
  - "Compilation proceeds or halts based on severity"

requires_human_confirmation: false

pattern_ids: []  # This IS the pattern enforcement step
anti_pattern_ids: []

implementation_files:
  - "guardrails.py"
  - "phase_plan_compiler.py"

artifacts_updated:
  - "run_stats.guardrail_violations (in-memory counter)"

preconditions:
  - "PATTERN_INDEX.yaml loaded successfully"
  - "Tasks have been generated from workstreams"

postconditions:
  - "All tasks validated against patterns"
  - "No critical violations present (or compilation halted)"

error_handling: |
  Critical violations: Halt compilation, transition to FAILED, log violations.
  Warnings: Log to console and ledger, allow compilation to proceed.

guardrail_checkpoint_id: "GC-PLAN-COMPILATION"

metrics_emitted:
  - "Ledger: {event: guardrail_checkpoint, checkpoint_id: GC-PLAN-COMPILATION, violations: <count>}"
  - "Console: [GUARDRAILS] Pattern validation complete (N violations)"

lens: "automation"
automation_level: "fully_automatic"
estimated_duration: "0.5 seconds per task"
```

---

## Artifact Registry

A separate artifact registry maps files to the steps that create/update them:

```yaml
artifact_registry:
  description: |
    Maps runtime artifacts to lifecycle (created_by, updated_by steps).

  artifacts:
    run_ledger:
      path: ".acms_runs/<RUN_ID>/run.ledger.jsonl"
      created_by: "P0-STEP-005"
      updated_by:
        - "P0-STEP-009"   # State transitions
        - "P1-STEP-022"   # Gap discovery events
        - "P2-STEP-035"   # Planning events
        - "P3-STEP-044"   # Plan compilation events
        # ... all steps that log events
      description: "Append-only JSONL event log"

    gap_registry:
      path: ".acms_runs/<RUN_ID>/gap_registry.json"
      created_by: "P1-STEP-020"
      updated_by:
        - "P1-STEP-020"   # Initial creation
        - "P6-STEP-087"   # Status updates after execution
      description: "Normalized gap records with lifecycle tracking"

    execution_plan:
      path: ".acms_runs/<RUN_ID>/mini_pipe_execution_plan.json"
      created_by: "P3-STEP-042"
      updated_by: []
      description: "Compiled MINI_PIPE execution plan (immutable after creation)"

    pattern_index:
      path: "PATTERN_INDEX.yaml"
      created_by: "external"
      updated_by: []
      description: "Pattern definitions (pre-existing, not modified by runs)"
```

---

## State Transition Steps

Steps that change the state machine get explicit `state_transition` metadata:

```yaml
step_id: "P0-STEP-009"
phase: "INIT"
name: "Transition to GAP_ANALYSIS"
responsible_component: "acms_controller"
operation_kind: "state_transition"

state_transition:
  from_state: "INIT"
  to_state: "GAP_ANALYSIS"

expected_outputs:
  - "current_state updated to GAP_ANALYSIS"
  - "Ledger entry: enter_state(GAP_ANALYSIS)"

metrics_emitted:
  - "Ledger: {event: enter_state, state: GAP_ANALYSIS, previous_state: INIT}"
  - "Console: [STATE] INIT → GAP_ANALYSIS"
```

---

## Guardrail Checkpoints Summary

All guardrail checkpoints collected in one place:

```yaml
guardrail_checkpoints:
  GC-INIT:
    step_id: "P0-STEP-008"
    phase: "INIT"
    description: "Initialize guardrails system"
    validation_type: "initialization"

  GC-PLANNING-INCREMENT:
    step_id: "P2-STEP-034"
    phase: "PLANNING"
    description: "Increment planning_attempts counter"
    validation_type: "metric_tracking"

  GC-PLAN-COMPILATION:
    step_id: "P3-STEP-038"
    phase: "PLANNING"
    description: "Validate pattern_ids in task metadata"
    validation_type: "pre_execution"

  GC-PLANNING-LOOP-CHECK:
    step_id: "P3-STEP-043"
    phase: "PLANNING"
    description: "Detect AP_PLANNING_LOOP anti-pattern"
    validation_type: "anti_pattern_detection"
    anti_patterns: ["AP_PLANNING_LOOP"]

  GC-PRE-TASK:
    step_id: "P5-STEP-069"
    phase: "EXECUTION"
    description: "Pre-execution guardrail checks per task"
    validation_type: "pre_execution"

  GC-POST-TASK:
    step_id: "P5-STEP-071"
    phase: "EXECUTION"
    description: "Post-execution guardrail checks (hallucination detection)"
    validation_type: "post_execution"
    anti_patterns: ["AP_HALLUCINATED_SUCCESS"]

  GC-FINAL-SUMMARY:
    step_id: "P6-STEP-089"
    phase: "SUMMARY"
    description: "Final anti-pattern detection across entire run"
    validation_type: "comprehensive"
```

---

## Component Registry

Centralized component documentation:

```yaml
components:
  acms_controller:
    file: "acms_controller.py"
    role: "Main orchestrator, golden path entrypoint"
    responsibilities:
      - "CLI parsing and configuration"
      - "State machine enforcement"
      - "Gap discovery coordination"
      - "Planning coordination"
      - "MINI_PIPE integration"
      - "Summary report generation"
    steps_responsible_for:
      - "P0-STEP-001" # User invokes
      - "P0-STEP-002" # Parse CLI
      - "P0-STEP-003" # Generate run_id
      - "P0-STEP-004" # Create directories
      - "P0-STEP-005" # Initialize ledger
      - "P0-STEP-006" # Create run record
      - "P0-STEP-009" # State transitions
      # ... etc.

  gap_registry:
    file: "gap_registry.py"
    role: "Gap normalization and lifecycle tracking"
    responsibilities:
      - "Raw gap report parsing"
      - "GapRecord normalization"
      - "Status tracking (DISCOVERED → RESOLVED)"
      - "Gap querying and filtering"
    steps_responsible_for:
      - "P1-STEP-019" # Normalize findings
      - "P1-STEP-020" # Persist gaps
      - "P1-STEP-021" # Return in-memory view
      # ... etc.
```

---

## Lens-Based Filtering

With lens tagging, you can filter steps by concern:

```yaml
# All architecture-related steps:
steps_by_lens:
  architecture:
    - "P0-STEP-006"  # Create run record (state management)
    - "P0-STEP-007"  # Initialize components (component boundaries)
    - "P1-STEP-018"  # Pass to gap_registry (boundary crossing)
    - "P3-STEP-036"  # Call compiler (boundary crossing)
    - "P3-STEP-040"  # Create execution plan (state structure)

  automation:
    - "P0-STEP-008"  # Guardrails init
    - "P1-STEP-013"  # AI adapter call
    - "P2-STEP-034"  # Guardrail metric tracking
    - "P3-STEP-038"  # Pattern validation
    - "P3-STEP-043"  # Anti-pattern detection

  process:
    - "P0-STEP-001"  # User invokes (workflow start)
    - "P0-STEP-004"  # Directory setup (orchestration)
    - "P0-STEP-005"  # Ledger init (event tracking)
    - "P0-STEP-009"  # State transition
    - "P1-STEP-022"  # Log completion (event emission)
```

---

## Automation Level Filtering

Identify manual intervention points:

```yaml
steps_by_automation_level:
  fully_automatic:
    # 99% of steps are fully automatic
    - "P0-STEP-001" through "P6-STEP-100"
    # (excluding any operator_assisted steps)

  operator_assisted:
    # Currently none, but could be added for:
    # - Critical failure recovery
    # - High-risk patch application
    # - Security-sensitive operations

  manual_only:
    # Currently none
```

---

## Benefits of Schema-Based Approach

### 1. **Consistency**
Every step has the same structure → easier to understand, query, and validate.

### 2. **Discoverability**
Clear inputs/outputs → easy to trace data flow through the pipeline.

### 3. **Artifact Tracking**
Explicit `artifacts_created`/`artifacts_updated` → know exactly what files each step touches.

### 4. **Guardrail Integration**
`guardrail_checkpoint_id` and `anti_pattern_ids` → direct link to pattern enforcement.

### 5. **Lens-Based Analysis**
Tagging by lens (logical/performance/architecture/process/automation) → filter by concern area.

### 6. **Automation Visibility**
`automation_level` → identify where human intervention may be needed.

### 7. **State Machine Clarity**
`state_transition` fields → visualize state machine from steps alone.

### 8. **Metrics & Observability**
`metrics_emitted` → know exactly what events/metrics are generated.

### 9. **MASTER_SPLINTER Alignment**
Uses same schema as `execution_plan_steps` → compatible with MASTER_SPLINTER patterns.

### 10. **Queryability**
YAML format → can be parsed, queried, validated programmatically.

---

## Migration Path

### Option 1: Full YAML Conversion
Convert all 100 steps to YAML with full schema (recommended for long-term).

**File**: `PROCESS_STEPS_SCHEMA.yaml`
**Size**: ~3000-4000 lines
**Benefits**: Full queryability, validation, tooling support

### Option 2: Hybrid Approach
Keep human-readable text, add YAML frontmatter per section.

**Example**:
```markdown
## PHASE 0: RUN INITIALIZATION & BOOTSTRAP

```yaml
phase_metadata:
  phase_id: "P0"
  name: "INIT"
  steps_count: 10
  state_transitions: ["INIT → GAP_ANALYSIS"]
```

### Step 1: User invokes ACMS controller
```yaml
step_id: "P0-STEP-001"
phase: "INIT"
name: "User invokes ACMS controller"
responsible_component: "acms_controller"
operation_kind: "initialization"
```

Command: python acms_controller.py <REPO_ROOT> --mode full --ai-adapter <adapter>
...
```

**Benefits**: Human-readable text preserved, machine-parseable metadata added.

### Option 3: Separate Schema + Implementation
Keep `MINI_PIPE_Process_steps.txt` as narrative documentation, create separate `PROCESS_STEPS_SCHEMA.yaml` with just schema.

**Benefits**: Two views of the same process (narrative + structured).

---

## Tooling Opportunities

With schema-based steps, you can build:

1. **Step Validator**: Ensure all required fields present, references valid
2. **Artifact Tracker**: Visualize file creation/update timeline
3. **Dependency Graph**: Auto-generate step dependency DAG
4. **Guardrail Dashboard**: Show all checkpoints and violations
5. **Lens Filter**: Query steps by lens (e.g., "show all automation steps")
6. **State Machine Visualizer**: Auto-generate state diagram from `state_transition` fields
7. **Metrics Collector**: Auto-instrument based on `metrics_emitted`
8. **Documentation Generator**: Auto-generate docs from schema
9. **Test Generator**: Auto-generate integration tests for each step
10. **Runbook Generator**: Auto-generate troubleshooting runbooks

---

## Next Steps

1. **Decide on format**: Full YAML vs. hybrid vs. separate schema
2. **Complete Phase 4-6**: Document remaining ~54 steps in same schema
3. **Build validator**: Python script to validate schema compliance
4. **Auto-generate docs**: Convert YAML → Markdown for human consumption
5. **Integrate with MASTER_SPLINTER**: Ensure `operation_kind` values match MASTER_SPLINTER vocabulary

---

## Appendix: Full Schema Example (Phase 0)

See `PROCESS_STEPS_SCHEMA.yaml` for complete Phase 0 example (10 steps) demonstrating all schema fields in use.

**Key files**:
- `PROCESS_STEPS_SCHEMA.yaml` - Full schema-based documentation
- `PROCESS_STEPS_SCHEMA_GUIDE.md` - This guide
- `MINI_PIPE_Process_steps.txt` - Original narrative documentation (v2.0)

---

## Summary

The schema-based approach gives you:

✅ **Standard schema for every step** (aligned with MASTER_SPLINTER)  
✅ **Files associated with steps** (artifact_registry)  
✅ **Step deliverables** (expected_outputs)  
✅ **Enhanced metadata** (lenses, automation levels, guardrails)  
✅ **State machine clarity** (state_transition fields)  
✅ **Guardrail integration** (checkpoint_ids, anti_pattern_ids)  
✅ **Queryability** (YAML format, consistent structure)  
✅ **Tooling foundation** (validators, visualizers, generators)  

This transforms process documentation from **narrative text** into **executable specification**.
