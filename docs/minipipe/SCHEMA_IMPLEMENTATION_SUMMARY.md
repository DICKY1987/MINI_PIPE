# Process Steps Schema Implementation Summary

## What Was Delivered

I've created a **standardized schema-based approach** for documenting all ACMS/MINI_PIPE process steps, aligned with the MASTER_SPLINTER `execution_plan_steps` schema.

### Files Created

1. **`PROCESS_STEPS_SCHEMA_GUIDE.md`** - Comprehensive guide explaining the schema approach
2. **`PROCESS_STEPS_SCHEMA.yaml`** - Schema-based documentation (Phases 0-3 as proof-of-concept)

---

## Key Improvements Over v2.0

### 1. ✅ Standard Schema for Every Step

Every step now follows this canonical structure (from MASTER_SPLINTER):

```yaml
step_id: "P0-STEP-001"                    # Unique identifier
phase: "INIT"                             # State machine phase
name: "Initialize run ledger"             # Short label
responsible_component: "acms_controller"  # Who executes this
operation_kind: "initialization"          # Category (see taxonomy)
description: |                            # Precise paragraph
  Create append-only JSONL ledger...
inputs:                                   # What this consumes
  - "run_id"
  - "Run directory path"
expected_outputs:                         # What this produces
  - "Ledger file created with INIT event"
requires_human_confirmation: false        # Boolean
```

**Before**: Steps had different levels of detail, inconsistent structure  
**After**: Every step has identical schema, fully queryable

---

### 2. ✅ Files Associated with Steps (Artifact Registry)

New `artifact_registry` section maps every file to:
- `created_by`: Which step creates it
- `updated_by`: Which steps modify it
- `description`: What it contains
- `schema`: Data format

**Example**:
```yaml
artifact_registry:
  run_ledger:
    path: ".acms_runs/<RUN_ID>/run.ledger.jsonl"
    created_by: "P0-STEP-005"
    updated_by: ["P0-STEP-009", "P1-STEP-022", "P2-STEP-035", ...]
    description: "Append-only JSONL event log"
```

**Before**: File creation mentioned in narrative, but not systematically tracked  
**After**: Complete artifact lifecycle visible in one place

---

### 3. ✅ Step Deliverables (Expected Outputs)

Every step now explicitly lists deliverables in `expected_outputs`:

**Example**:
```yaml
step_id: "P1-STEP-020"
name: "Persist normalized gaps"
expected_outputs:
  - "gap_registry.json persisted to disk"
  - "Atomic write completed (temp file + rename)"
```

**Before**: Deliverables implied in description  
**After**: Explicit, queryable deliverable list per step

---

### 4. ✅ Implementation Files (Source Code Mapping)

Each step lists source files implementing it:

```yaml
implementation_files:
  - "acms_controller.py"
  - "gap_registry.py"
```

**Before**: Component list at top of document  
**After**: Per-step mapping of code to behavior

---

### 5. ✅ Enhanced Metadata

#### Lenses (Concern Areas)
Every step tagged with primary lens:
- **logical**: Correctness, validation, data integrity
- **performance**: Optimization, concurrency, efficiency
- **architecture**: Boundaries, state management, modularity
- **process**: Workflow, state transitions, orchestration
- **automation**: Guardrails, anti-patterns, autonomous execution

```yaml
lens: "automation"  # This step is automation-focused
```

**Use case**: Filter steps by concern area  
**Example**: "Show me all automation steps" → query `lens: automation`

#### Automation Levels
```yaml
automation_level: "fully_automatic"  # vs operator_assisted | manual_only
```

**Use case**: Identify where human intervention may be needed

#### Guardrail Checkpoints
```yaml
guardrail_checkpoint_id: "GC-PLAN-COMPILATION"
anti_pattern_ids: ["AP_PLANNING_LOOP"]
```

**Use case**: Direct link from step → guardrail enforcement

#### State Transitions
```yaml
state_transition:
  from_state: "INIT"
  to_state: "GAP_ANALYSIS"
```

**Use case**: Visualize state machine from steps alone

#### Metrics & Events
```yaml
metrics_emitted:
  - "Ledger: {event: enter_state, state: GAP_ANALYSIS}"
  - "Console: [STATE] INIT → GAP_ANALYSIS"
```

**Use case**: Know exactly what observability data is generated

---

### 6. ✅ Preconditions & Postconditions

Steps now specify pre/post conditions explicitly:

```yaml
preconditions:
  - "Run directory .acms_runs/<RUN_ID>/ exists"
  - "run_id has been generated"

postconditions:
  - "Ledger file exists"
  - "Ledger contains exactly one JSONL entry"
```

**Use case**: Validate step completion, debug failures

---

### 7. ✅ Error Handling Strategy

Each step documents error behavior:

```yaml
error_handling: |
  If file creation fails (permissions, disk space), log error to console
  and transition run to FAILED state. No retry.
```

**Use case**: Understand failure modes and recovery paths

---

## Schema Alignment with MASTER_SPLINTER

The schema directly implements MASTER_SPLINTER's `execution_plan_steps` required fields:

| MASTER_SPLINTER Field | Our Implementation | Notes |
|-----------------------|-------------------|-------|
| `id` | `step_id` | Unique identifier (e.g., "P0-STEP-001") |
| `name` | `name` | Short label |
| `operation_kind` | `operation_kind` | From standardized taxonomy |
| `pattern_ids` | `pattern_ids` (optional) | Links to PAT-* patterns |
| `description` | `description` | One-paragraph summary |
| `tool_id` | `responsible_component` | Component executing step |
| `inputs` | `inputs` | List of consumed artifacts/data |
| `expected_outputs` | `expected_outputs` | List of produced artifacts/data |
| `requires_human_confirmation` | `requires_human_confirmation` | Boolean |

**Additional fields** we added for ACMS/MINI_PIPE context:
- `phase` (state machine phase)
- `implementation_files` (source code mapping)
- `artifacts_created/updated` (runtime file tracking)
- `state_transition` (for state machine steps)
- `guardrail_checkpoint_id` (for guardrail steps)
- `anti_pattern_ids` (for anti-pattern detection steps)
- `lens` (concern area tagging)
- `automation_level` (human intervention flagging)
- `metrics_emitted` (observability tracking)
- `preconditions/postconditions` (contract specification)
- `error_handling` (failure behavior documentation)

---

## Operation Kind Taxonomy

Standardized `operation_kind` values (reusable across all steps):

| Operation Kind | Description | Example Steps |
|---------------|-------------|---------------|
| `state_transition` | State machine transitions | P0-STEP-009 (INIT → GAP_ANALYSIS) |
| `gap_discovery` | AI-driven gap finding | P1-STEP-013 (Call AI adapter) |
| `gap_normalization` | Gap registry operations | P1-STEP-019 (Normalize findings) |
| `planning` | Workstream generation, clustering | P2-STEP-027 (Cluster gaps) |
| `plan_compilation` | Task generation, DAG building | P3-STEP-037 (Transform to tasks) |
| `dag_build` | Scheduler DAG construction | P5-STEP-056 (Build task DAG) |
| `task_execution` | Actual task running | P5-STEP-063 (Execute tool) |
| `guardrail_check` | Pattern/anti-pattern validation | P3-STEP-038 (Validate pattern_ids) |
| `summary_generation` | Report creation | P6-STEP-092 (Generate summary) |
| `initialization` | Bootstrap, setup | P0-STEP-004 (Create directories) |
| `persistence` | File I/O, save/load | P1-STEP-020 (Persist gaps) |
| `event_emission` | Logging, events, metrics | P1-STEP-022 (Log completion) |

---

## Artifact Registry

Centralized tracking of all runtime artifacts:

```yaml
artifact_registry:
  run_ledger:
    path: ".acms_runs/<RUN_ID>/run.ledger.jsonl"
    type: "append_only_log"
    format: "JSONL"
    created_by: "P0-STEP-005"
    updated_by: ["P0-STEP-009", "P1-STEP-022", "P2-STEP-035", "P3-STEP-044", ...]
    description: "Append-only event log for state transitions and metrics"
    schema:
      event_format: "{ts: ISO8601, run_id: ULID, event: str, state: str, meta: dict}"

  gap_registry:
    path: ".acms_runs/<RUN_ID>/gap_registry.json"
    created_by: "P1-STEP-020"
    updated_by: ["P1-STEP-020", "P6-STEP-087"]
    description: "Normalized gap records with lifecycle status"
```

**Benefits**:
- **Traceability**: Know exactly which step creates/modifies each file
- **Lifecycle visibility**: See artifact evolution through pipeline
- **Schema documentation**: What's in each file
- **Audit trail**: Track all file mutations

---

## Guardrail Checkpoints Registry

Explicit tracking of all guardrail integration points:

```yaml
guardrail_checkpoints:
  GC-INIT:
    checkpoint_id: "GC-INIT"
    step_id: "P0-STEP-008"
    phase: "INIT"
    name: "Guardrails System Initialization"
    validation_type: "initialization"

  GC-PLAN-COMPILATION:
    checkpoint_id: "GC-PLAN-COMPILATION"
    step_id: "P3-STEP-038"
    phase: "PLANNING"
    name: "Pattern ID Validation in Tasks"
    validation_type: "pre_execution"

  GC-PLANNING-LOOP-CHECK:
    checkpoint_id: "GC-PLANNING-LOOP-CHECK"
    step_id: "P3-STEP-043"
    phase: "PLANNING"
    name: "AP_PLANNING_LOOP Detection"
    validation_type: "anti_pattern_detection"
    anti_patterns: ["AP_PLANNING_LOOP"]
```

**Benefits**:
- All 6 guardrail checkpoints in one registry
- Direct step linkage
- Anti-pattern tracking
- Validation type classification

---

## Tooling Opportunities

With schema-based steps, you can now build:

### 1. **Step Validator**
```python
def validate_step(step_dict):
    required = ["step_id", "phase", "name", "responsible_component", 
                "operation_kind", "description", "inputs", 
                "expected_outputs", "requires_human_confirmation"]
    for field in required:
        assert field in step_dict, f"Missing required field: {field}"
```

### 2. **Artifact Tracker**
```python
def get_artifact_lifecycle(artifact_name):
    artifact = artifact_registry[artifact_name]
    print(f"Created by: {artifact['created_by']}")
    print(f"Updated by: {', '.join(artifact['updated_by'])}")
```

### 3. **Dependency Graph Generator**
```python
import networkx as nx

def build_step_dag(steps):
    G = nx.DiGraph()
    for step in steps:
        G.add_node(step['step_id'])
        for dep in step.get('dependencies', []):
            G.add_edge(dep, step['step_id'])
    return G
```

### 4. **Guardrail Dashboard**
```python
def get_guardrail_checkpoints():
    return {cp_id: cp for cp_id, cp in guardrail_checkpoints.items()}
```

### 5. **Lens-Based Filtering**
```python
def get_steps_by_lens(lens_name):
    return [s for s in steps if s.get('lens') == lens_name]

# Example: get_steps_by_lens('automation')
# Returns all automation-focused steps
```

### 6. **State Machine Visualizer**
```python
def generate_state_diagram():
    transitions = [s['state_transition'] 
                  for s in steps 
                  if 'state_transition' in s]
    # Render as DOT/Graphviz diagram
```

### 7. **Metrics Collector**
```python
def collect_all_metrics():
    metrics = []
    for step in steps:
        metrics.extend(step.get('metrics_emitted', []))
    return metrics
```

### 8. **Test Generator**
```python
def generate_step_test(step):
    # Auto-generate integration test from step schema
    test_code = f"""
def test_{step['step_id']}():
    # Setup: ensure preconditions
    {generate_precondition_checks(step['preconditions'])}
    
    # Execute: run step
    result = execute_step('{step['step_id']}')
    
    # Assert: verify postconditions
    {generate_postcondition_checks(step['postconditions'])}
    
    # Assert: verify outputs
    {generate_output_checks(step['expected_outputs'])}
"""
    return test_code
```

---

## Migration Recommendations

### Option 1: Full YAML Conversion (Recommended)
- Convert all 100 steps to YAML with full schema
- **File**: `PROCESS_STEPS_SCHEMA.yaml`
- **Size**: ~3000-4000 lines
- **Benefits**: Full queryability, validation, tooling support
- **Effort**: High (but one-time investment)

### Option 2: Hybrid Approach
- Keep human-readable text in `MINI_PIPE_Process_steps.txt`
- Add YAML frontmatter per phase
- **Benefits**: Readable narrative + machine-parseable metadata
- **Effort**: Medium

### Option 3: Separate Schema + Narrative
- Maintain both:
  - `MINI_PIPE_Process_steps.txt` (narrative, v2.0)
  - `PROCESS_STEPS_SCHEMA.yaml` (schema-based, v3.0)
- **Benefits**: Two views of same process
- **Effort**: Medium (keep in sync)

---

## Current Coverage

### Phases Documented in Schema Format

| Phase | Steps | Status | File |
|-------|-------|--------|------|
| P0: INIT | 10 steps | ✅ Complete | `PROCESS_STEPS_SCHEMA.yaml` |
| P1: GAP_ANALYSIS | 14 steps | ✅ Complete | `PROCESS_STEPS_SCHEMA.yaml` |
| P2: PLANNING | 11 steps | ✅ Complete | `PROCESS_STEPS_SCHEMA.yaml` |
| P3: PLAN_COMPILATION | 11 steps | ✅ Complete | `PROCESS_STEPS_SCHEMA.yaml` |
| P4: ACMS_MINIPIPE_BRIDGE | 4 steps | ❌ Not yet | (in v2.0 text only) |
| P5: EXECUTION | ~30 steps | ❌ Not yet | (in v2.0 text only) |
| P6: SUMMARY | ~20 steps | ❌ Not yet | (in v2.0 text only) |

**Total**: 46/100 steps documented in schema format (46% complete)

---

## Next Steps

1. **Complete remaining phases** (P4-P6) in schema format
2. **Build step validator** to enforce schema compliance
3. **Generate documentation** from YAML (auto-generate markdown views)
4. **Integrate with MASTER_SPLINTER** (ensure operation_kind alignment)
5. **Build tooling** (artifact tracker, DAG visualizer, test generator)
6. **Create schema.json** for JSON Schema validation of YAML

---

## Summary

### What You Got

✅ **Standard schema for every step** (MASTER_SPLINTER-aligned)  
✅ **Files associated with steps** (artifact_registry)  
✅ **Step deliverables** (expected_outputs)  
✅ **Enhanced metadata** (lenses, automation levels, guardrails, state transitions, metrics)  
✅ **Preconditions/postconditions** (contract specification)  
✅ **Error handling** (failure mode documentation)  
✅ **Component registry** (centralized component mapping)  
✅ **Guardrail checkpoints** (explicit tracking)  
✅ **Operation kind taxonomy** (standardized categories)  
✅ **Tooling foundation** (queryable, validatable, executable spec)

### Transformation

**Before (v2.0)**: Narrative documentation with implicit structure  
**After (v3.0)**: Executable specification with explicit schema

This transforms process documentation from **informative text** into **programmable infrastructure**.

---

## Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `MINI_PIPE_Process_steps.txt` | Original narrative doc (v2.0) | ✅ Complete |
| `PROCESS_STEPS_SCHEMA.yaml` | Schema-based doc (v3.0, partial) | 🟡 46% complete |
| `PROCESS_STEPS_SCHEMA_GUIDE.md` | Implementation guide | ✅ Complete |
| `SCHEMA_IMPLEMENTATION_SUMMARY.md` | This summary | ✅ Complete |

---

**Author**: GitHub Copilot CLI  
**Date**: 2025-12-07  
**Version**: 3.0
