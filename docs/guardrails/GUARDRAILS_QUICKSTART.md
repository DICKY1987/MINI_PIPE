# Guardrails Quick Start Guide

## 5-Minute Setup

### 1. Verify Installation

```bash
cd C:\Users\richg\ALL_AI\MINI_PIPE

# Check core files exist
ls PATTERN_INDEX.yaml
ls SYSTEM_INVARIANTS.md
ls guardrails.py
ls -r patterns/
ls -r anti_patterns/
```

### 2. Test Guardrails Module

```bash
# Run self-test
python guardrails.py
```

Expected output:
```
Testing Guardrails Enforcement...
✓ Pattern 'atomic_create' exists: True
✗ Pattern 'nonexistent' exists: False
✓ Path scope test: ...

Testing Anti-Pattern Detection...
Loaded 2 runbooks
✓ Detected: AP_HALLUCINATED_SUCCESS
```

### 3. Validate Everything

```bash
# Run full validation
python validate_everything.py --verbose
```

This validates:
- Schema files
- Pattern specs
- Pattern index
- Any existing run artifacts

### 4. Review Core Patterns

```bash
# Check what patterns are available
cat PATTERN_INDEX.yaml | grep "pattern_id:"
```

Current patterns:
- `atomic_create` - Create files with validation
- `refactor_patch` - Apply surgical refactors
- `bulk_rename` - Rename symbols safely
- `pytest_green` - Run tests and verify pass
- `schema_validate` - Validate JSON/YAML
- `lint_check` - Run linters
- `worktree_create` - Create isolated worktrees
- `worktree_cleanup` - Clean up worktrees
- `self_heal` - Auto-recover from failures
- `rollback` - Rollback to last good state
- `gap_analysis` - Discover gaps
- `plan_compile` - Compile execution plans

### 5. Read the Invariants

```bash
cat SYSTEM_INVARIANTS.md
```

Understand the 7 categories of invariants that MUST be true.

---

## Using Guardrails in Your Code

### In ACMS Controller

```python
from pathlib import Path
from guardrails import PatternGuardrails, AntiPatternDetector

# Initialize
pattern_index = Path(__file__).parent / "PATTERN_INDEX.yaml"
guardrails = PatternGuardrails(pattern_index)

# Validate pattern exists before planning
is_valid, error = guardrails.validate_pattern_exists("atomic_create")
if not is_valid:
    raise ValueError(f"Pattern validation failed: {error}")

# Validate plan references only valid patterns
for task in execution_plan.tasks:
    is_valid, error = guardrails.validate_pattern_exists(task.pattern_id)
    if not is_valid:
        raise PlanValidationError(f"Invalid pattern in task {task.id}: {error}")
```

### In MINI_PIPE Executor

```python
from guardrails import PatternGuardrails

# Before executing task
guardrails = PatternGuardrails(Path("PATTERN_INDEX.yaml"))

passed, violations = guardrails.pre_execution_checks(
    pattern_id=task.pattern_id,
    task_data={
        "file_paths": task.target_files,
        "tools_used": task.tools,
        "operations": task.operations
    }
)

if not passed:
    # Log violations
    for violation in violations:
        log_violation(violation)
    
    # Block task
    task.status = "BLOCKED"
    task.failure_reason = f"{len(violations)} guardrail violations"
    return task

# ... execute task ...

# After executing task
passed, violations = guardrails.post_execution_checks(
    pattern_id=task.pattern_id,
    task_result={
        "status": task.status,
        "changes": {
            "files": len(task.modified_files),
            "lines": task.lines_changed
        },
        "verification": {
            "exit_code": task.exit_code,
            "tests_run": task.tests_run,
            "tests_passed": task.tests_passed
        },
        "expected_outputs": task.expected_outputs
    }
)

if not passed:
    # Override status even if AI claimed success
    task.status = "FAILED"
    task.failure_reason = "Post-execution guardrail violations"
    
    # Check if this is hallucinated success
    for violation in violations:
        if violation.rule_id == "AP_HALLUCINATED_SUCCESS":
            log_antipattern(violation)
            trigger_recovery_pattern("rollback", task)
```

### Anti-Pattern Detection

```python
from guardrails import AntiPatternDetector

# Initialize detector
detector = AntiPatternDetector(Path("anti_patterns"))

# After each task
detections = detector.detect_all({
    "task_status": task.status,
    "verification": task.verification,
    "run_stats": {
        "planning_attempts": run.planning_attempts,
        "patches_applied": run.patches_applied
    }
})

# Handle detections
for detection in detections:
    anti_pattern_id = detection["anti_pattern_id"]
    
    if anti_pattern_id == "AP_HALLUCINATED_SUCCESS":
        # Override task status
        task.status = "FAILED"
        log_antipattern(detection)
        
    elif anti_pattern_id == "AP_PLANNING_LOOP":
        # Force plan commitment
        force_plan_commit(run)
        log_antipattern(detection)
```

---

## Adding a New Pattern

### Step 1: Create Pattern Spec

Create `patterns/my_pattern.spec.yaml`:

```yaml
pattern_id: my_pattern
version: "1.0.0"
description: "What this pattern does"
category: code_modification
stability: beta
executor: "MINI_PIPE_executor.execute_my_pattern"
schema_path: "schemas/my_pattern.schema.json"

guardrails:
  allowed_tools:
    - tool1
    - tool2
  
  path_scope:
    include:
      - "**/*.py"
    exclude:
      - ".git/**"
  
  max_changes:
    files: 5
    lines: 100
  
  required_prechecks:
    - git_status_clean
  
  required_postchecks:
    - tests_pass
  
  forbidden_operations:
    - git_push
  
  timeout_minutes: 10
```

### Step 2: Add to PATTERN_INDEX.yaml

```yaml
patterns:
  my_pattern:
    enabled: true
    spec_path: "patterns/my_pattern.spec.yaml"
    schema_path: "schemas/my_pattern.schema.json"
    executor: "MINI_PIPE_executor.execute_my_pattern"
    description: "What this pattern does"
    category: "code_modification"
    stability: "beta"
    guardrails:
      # ... (copy from spec file)
```

### Step 3: Validate

```bash
python validate_everything.py
```

### Step 4: Implement Executor

In `MINI_PIPE_executor.py`:

```python
def execute_my_pattern(task_data: Dict) -> Dict:
    """Execute my_pattern"""
    # Implementation
    result = {
        "status": "success",
        "changes": {
            "files": 2,
            "lines": 50
        },
        "verification": {
            "exit_code": 0,
            "tests_run": 10,
            "tests_passed": 10
        },
        "expected_outputs": ["path/to/file.py"]
    }
    return result
```

### Step 5: Test

```python
from guardrails import PatternGuardrails

guardrails = PatternGuardrails(Path("PATTERN_INDEX.yaml"))

# Test pre-execution
passed, violations = guardrails.pre_execution_checks(
    "my_pattern",
    {"file_paths": ["test.py"]}
)
print(f"Pre-checks passed: {passed}")

# Test post-execution
passed, violations = guardrails.post_execution_checks(
    "my_pattern",
    {
        "status": "success",
        "changes": {"files": 1, "lines": 20},
        "verification": {"exit_code": 0}
    }
)
print(f"Post-checks passed: {passed}")
```

---

## Adding an Anti-Pattern Runbook

### Step 1: Create Runbook

Create `anti_patterns/AP_MY_ANTIPATTERN.yaml`:

```yaml
meta:
  id: "AP_MY_ANTIPATTERN"
  title: "Brief description"
  severity: "HIGH"
  category: "execution_flow"
  version: "1.0.0"
  created: "2025-12-07"

description: |
  Detailed description of the anti-pattern

symptoms:
  log_patterns:
    - "error pattern 1"
    - "error pattern 2"
  
  metric_conditions:
    - condition: "metric > threshold"
      description: "What this means"

detection_rules:
  rule_1:
    name: "Rule name"
    check: |
      condition to check
    priority: "HIGH"

automatic_response:
  detection_action:
    - step: "Log detection"
      code: |
        log_antipattern(...)
    
    - step: "Trigger recovery"
      code: |
        trigger_pattern("rollback")

verification:
  anti_pattern_resolved_checks:
    - check: "Verification check"
      description: "What to verify"
```

### Step 2: Implement Detection

In `guardrails.py`, add to `AntiPatternDetector`:

```python
def detect_my_antipattern(self, context: Dict) -> Optional[Dict]:
    """Detect AP_MY_ANTIPATTERN"""
    if context.get("some_metric") > threshold:
        return {
            "anti_pattern_id": "AP_MY_ANTIPATTERN",
            "rule": "rule_1",
            "evidence": "Evidence description"
        }
    return None
```

Add to `detect_all()`:

```python
detection = self.detect_my_antipattern(run_context)
if detection:
    detections.append(detection)
    self.detections.append(detection)
```

### Step 3: Test

```python
from guardrails import AntiPatternDetector

detector = AntiPatternDetector(Path("anti_patterns"))

# Simulate condition
detection = detector.detect_my_antipattern({
    "some_metric": 100  # Above threshold
})

print(f"Detected: {detection}")
```

---

## Troubleshooting

### "Pattern not found in PATTERN_INDEX.yaml"

Check:
1. Pattern ID matches exactly (snake_case)
2. Pattern is listed under `patterns:` section
3. Pattern has `enabled: true`

### "Path not in pattern's include scope"

Check:
1. File path matches at least one `include` glob pattern
2. File path doesn't match any `exclude` glob pattern
3. File path not in global `protected_paths`

### "Tool not in pattern's allowed_tools list"

Check:
1. Tool ID matches exactly
2. Tool is listed in pattern's `allowed_tools`
3. Tool actually exists in tool registry

### Validation Fails

```bash
# Get detailed error
python validate_everything.py --verbose

# Check specific pattern spec
python -c "
from guardrails import validate_pattern_spec
from pathlib import Path
is_valid, error = validate_pattern_spec(Path('patterns/my_pattern.spec.yaml'))
print(f'Valid: {is_valid}')
if error:
    print(f'Error: {error}')
"
```

---

## Checklist Before First Run

- [ ] `PATTERN_INDEX.yaml` exists and validates
- [ ] `SYSTEM_INVARIANTS.md` reviewed
- [ ] At least 3 core patterns have specs
- [ ] At least 2 anti-pattern runbooks exist
- [ ] `guardrails.py` self-test passes
- [ ] `validate_everything.py` passes
- [ ] Executor has pre/post hooks (see integration guide)
- [ ] Git worktree strategy decided
- [ ] Protected paths confirmed
- [ ] Manual review thresholds set

---

## Next Steps

1. **Read**: `GUARDRAILS_README.md` for full documentation
2. **Review**: `SYSTEM_INVARIANTS.md` for invariant details
3. **Explore**: Pattern specs in `patterns/` directory
4. **Study**: Anti-pattern runbooks in `anti_patterns/` directory
5. **Integrate**: Add guardrail hooks to your executor
6. **Test**: Run a small pilot with guardrails enabled
7. **Monitor**: Watch for anti-pattern detections
8. **Iterate**: Add new patterns and runbooks as needed

---

**You're ready to run with guardrails! 🚀**
