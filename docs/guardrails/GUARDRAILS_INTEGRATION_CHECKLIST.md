# Guardrails Integration Checklist

## Phase 1: MINI_PIPE Executor Integration

### Pre-Execution Hook (CRITICAL)

**File**: `MINI_PIPE_executor.py`

**Location**: Before any task execution

```python
# Add at top of file
from pathlib import Path
from guardrails import PatternGuardrails, GuardrailViolation

# Initialize once (module level or in __init__)
PATTERN_INDEX = Path(__file__).parent / "PATTERN_INDEX.yaml"
guardrails = PatternGuardrails(PATTERN_INDEX)

# In execute_task() or similar
def execute_task(task: Dict) -> Dict:
    """Execute a task with guardrail enforcement"""
    
    # 1. Extract pattern_id
    pattern_id = task.get("pattern_id")
    if not pattern_id:
        return {
            "status": "FAILED",
            "error": "No pattern_id specified (violates invariant PG-1)"
        }
    
    # 2. Pre-execution checks
    task_data = {
        "file_paths": task.get("file_paths", []),
        "tools_used": task.get("tools", []),
        "operations": task.get("operations", [])
    }
    
    passed, violations = guardrails.pre_execution_checks(
        pattern_id=pattern_id,
        task_data=task_data
    )
    
    if not passed:
        # Log violations
        for violation in violations:
            log.error(f"Guardrail violation: {violation.rule_id} - {violation.message}")
        
        # Block execution
        return {
            "status": "BLOCKED",
            "error": f"Pre-execution guardrail violations: {len(violations)}",
            "violations": [
                {
                    "rule_id": v.rule_id,
                    "severity": v.severity,
                    "message": v.message
                }
                for v in violations
            ]
        }
    
    # 3. Execute task (existing logic)
    try:
        result = _execute_task_impl(task)
    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e)
        }
    
    # 4. Post-execution checks
    task_result = {
        "status": result.get("status", "unknown"),
        "changes": result.get("changes", {}),
        "verification": result.get("verification", {}),
        "expected_outputs": task.get("expected_outputs", [])
    }
    
    passed, violations = guardrails.post_execution_checks(
        pattern_id=pattern_id,
        task_result=task_result
    )
    
    if not passed:
        # Log violations
        for violation in violations:
            log.error(f"Post-execution violation: {violation.rule_id} - {violation.message}")
        
        # Override status if AI hallucinated success
        if result.get("status") == "success":
            log.warning("Overriding claimed success due to guardrail violations")
            result["status"] = "FAILED"
            result["failure_reason"] = "Post-execution guardrail violations"
        
        result["violations"] = [
            {
                "rule_id": v.rule_id,
                "severity": v.severity,
                "message": v.message
            }
            for v in violations
        ]
    
    return result
```

**Checklist**:
- [ ] Import guardrails module
- [ ] Initialize PatternGuardrails
- [ ] Add pre_execution_checks before task execution
- [ ] Block task if pre-checks fail
- [ ] Add post_execution_checks after task execution
- [ ] Override status if post-checks fail
- [ ] Log all violations

---

## Phase 2: ACMS Controller Integration

### Anti-Pattern Detection Hook

**File**: `acms_controller.py`

**Location**: After each phase, after each task batch

```python
# Add at top
from guardrails import AntiPatternDetector
from pathlib import Path

# Initialize once
ANTI_PATTERNS_DIR = Path(__file__).parent / "anti_patterns"
detector = AntiPatternDetector(ANTI_PATTERNS_DIR)

# After each task completes
def on_task_complete(task: Dict, run_stats: Dict) -> None:
    """Called after each task completes"""
    
    # Run anti-pattern detection
    detections = detector.detect_all({
        "task_status": task.get("status"),
        "verification": task.get("verification", {}),
        "run_stats": run_stats
    })
    
    # Handle detections
    for detection in detections:
        anti_pattern_id = detection["anti_pattern_id"]
        rule = detection["rule"]
        evidence = detection["evidence"]
        
        log.warning(f"Anti-pattern detected: {anti_pattern_id} ({rule})")
        log.warning(f"Evidence: {evidence}")
        
        # Record in run status
        run_stats.setdefault("anti_patterns_detected", []).append({
            "id": anti_pattern_id,
            "rule": rule,
            "evidence": evidence,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Trigger automatic response
        handle_anti_pattern(anti_pattern_id, task, run_stats)

# Anti-pattern response handler
def handle_anti_pattern(anti_pattern_id: str, task: Dict, run_stats: Dict) -> None:
    """Handle detected anti-pattern"""
    
    if anti_pattern_id == "AP_HALLUCINATED_SUCCESS":
        # Override task status
        if task.get("status") == "success":
            task["status"] = "FAILED"
            task["failure_reason"] = "Hallucinated success (tests failed)"
        
        # Increment counter
        run_stats["hallucination_count"] = run_stats.get("hallucination_count", 0) + 1
        
        # If repeated, trigger self-heal
        if run_stats["hallucination_count"] >= 3:
            log.critical("Repeated hallucinations detected - triggering self-heal")
            trigger_pattern("self_heal", reason="repeated_hallucinations")
    
    elif anti_pattern_id == "AP_PLANNING_LOOP":
        # Force plan commitment
        log.warning("Planning loop detected - forcing plan commitment")
        force_plan_commit(run_stats)
```

**Checklist**:
- [ ] Import AntiPatternDetector
- [ ] Initialize detector with anti_patterns directory
- [ ] Call detect_all() after each task
- [ ] Log detections
- [ ] Record in run_stats
- [ ] Implement automatic response handlers
- [ ] Add escalation logic for repeated detections

---

## Phase 3: Plan Compilation Integration

### Pattern Validation in Planner

**File**: `execution_planner.py` or `phase_plan_compiler.py`

**Location**: During plan compilation

```python
from guardrails import PatternGuardrails

# Initialize
guardrails = PatternGuardrails(Path("PATTERN_INDEX.yaml"))

def compile_plan(gaps: Dict, workstreams: List[Dict]) -> Dict:
    """Compile execution plan from gaps and workstreams"""
    
    plan = {
        "tasks": []
    }
    
    # Generate tasks from gaps/workstreams
    for gap in gaps.values():
        for resolution_step in gap.get("resolution_steps", []):
            task = {
                "task_id": generate_task_id(),
                "gap_id": gap["gap_id"],
                "pattern_id": resolution_step.get("pattern_id"),
                "description": resolution_step.get("description"),
                # ... other fields
            }
            
            # CRITICAL: Validate pattern exists
            pattern_id = task.get("pattern_id")
            if not pattern_id:
                raise PlanValidationError(
                    f"Task {task['task_id']} has no pattern_id (violates invariant PG-1)"
                )
            
            is_valid, error = guardrails.validate_pattern_exists(pattern_id)
            if not is_valid:
                raise PlanValidationError(
                    f"Task {task['task_id']} references invalid pattern '{pattern_id}': {error}"
                )
            
            # Check pattern dependencies
            pattern = guardrails.get_pattern(pattern_id)
            for required_pattern in pattern.get("requires_patterns", []):
                req_is_valid, req_error = guardrails.validate_pattern_exists(required_pattern)
                if not req_is_valid:
                    raise PlanValidationError(
                        f"Pattern '{pattern_id}' requires '{required_pattern}' which is not available"
                    )
            
            plan["tasks"].append(task)
    
    # Detect circular dependencies
    if has_circular_dependencies(plan["tasks"]):
        raise PlanValidationError("Plan has circular dependencies (anti-pattern AP_PLANNING_LOOP)")
    
    return plan
```

**Checklist**:
- [ ] Validate every task has pattern_id
- [ ] Validate pattern exists in PATTERN_INDEX
- [ ] Validate pattern is enabled
- [ ] Check pattern dependencies are satisfied
- [ ] Detect circular dependencies
- [ ] Raise PlanValidationError if invalid

---

## Phase 4: Schema Validation Integration

### Pre-Run Validation

**File**: `acms_controller.py` or dedicated validation script

**Location**: Before run starts

```python
from validate_everything import ArtifactValidator

def validate_before_run(run_id: str, repo_root: Path) -> bool:
    """Validate all artifacts before starting run"""
    
    print("Running pre-run validation...")
    
    # 1. Validate PATTERN_INDEX.yaml
    pattern_index = repo_root / "PATTERN_INDEX.yaml"
    if not pattern_index.exists():
        print("✗ PATTERN_INDEX.yaml not found")
        return False
    
    # 2. Validate pattern specs
    patterns_dir = repo_root / "patterns"
    if not patterns_dir.exists():
        print("✗ patterns/ directory not found")
        return False
    
    from guardrails import validate_pattern_spec
    
    for spec_file in patterns_dir.glob("*.spec.yaml"):
        is_valid, error = validate_pattern_spec(spec_file)
        if not is_valid:
            print(f"✗ Pattern spec invalid: {spec_file.name}")
            print(f"  Error: {error}")
            return False
    
    # 3. Validate schemas
    schemas_dir = repo_root / "schemas"
    if not schemas_dir.exists():
        print("✗ schemas/ directory not found")
        return False
    
    # 4. Validate gap registry (if exists)
    gap_registry = repo_root / ".acms_runs" / run_id / "gap_registry.json"
    if gap_registry.exists():
        from schema_utils import validate_gap_record
        import json
        
        with open(gap_registry) as f:
            registry = json.load(f)
        
        for gap_id, gap_data in registry.get("gaps", {}).items():
            is_valid, error = validate_gap_record(gap_data)
            if not is_valid:
                print(f"✗ Gap {gap_id} invalid: {error}")
                return False
    
    # 5. Validate execution plan (if exists)
    plan_file = repo_root / ".acms_runs" / run_id / "mini_pipe_execution_plan.json"
    if plan_file.exists():
        from schema_utils import validate_execution_plan
        
        with open(plan_file) as f:
            plan = json.load(f)
        
        is_valid, error = validate_execution_plan(plan)
        if not is_valid:
            print(f"✗ Execution plan invalid: {error}")
            return False
        
        # Validate all pattern_ids in plan
        for task in plan.get("tasks", []):
            pattern_id = task.get("pattern_id")
            is_valid, error = guardrails.validate_pattern_exists(pattern_id)
            if not is_valid:
                print(f"✗ Task references invalid pattern: {pattern_id}")
                return False
    
    print("✓ Pre-run validation passed")
    return True
```

**Checklist**:
- [ ] Validate PATTERN_INDEX.yaml exists
- [ ] Validate all pattern specs
- [ ] Validate schemas exist
- [ ] Validate gap registry (if exists)
- [ ] Validate execution plan (if exists)
- [ ] Validate all pattern_ids in plan
- [ ] Block run if validation fails

---

## Phase 5: Audit Trail Implementation

### Pattern Execution Logging

**File**: `MINI_PIPE_executor.py`

**Location**: In execute_task() after execution

```python
import json
from datetime import datetime

def log_pattern_execution(
    pattern_id: str,
    task_id: str,
    inputs: Dict,
    outputs: Dict,
    guardrail_checks: Dict,
    status: str,
    run_id: str
) -> None:
    """Log pattern execution to audit trail"""
    
    audit_file = Path(".acms_runs") / run_id / "pattern_audit.jsonl"
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "pattern_id": pattern_id,
        "task_id": task_id,
        "status": status,
        "inputs": inputs,
        "outputs": outputs,
        "guardrail_checks": guardrail_checks,
        "runtime_seconds": outputs.get("runtime_seconds")
    }
    
    # Append to JSONL file (one JSON object per line)
    with open(audit_file, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")
```

**Call after task execution**:

```python
# After post-execution checks
log_pattern_execution(
    pattern_id=task["pattern_id"],
    task_id=task["task_id"],
    inputs=task_data,
    outputs=result,
    guardrail_checks={
        "pre_execution_passed": pre_checks_passed,
        "pre_execution_violations": [v.rule_id for v in pre_violations],
        "post_execution_passed": post_checks_passed,
        "post_execution_violations": [v.rule_id for v in post_violations]
    },
    status=result["status"],
    run_id=current_run_id
)
```

**Checklist**:
- [ ] Create log_pattern_execution() function
- [ ] Log to pattern_audit.jsonl
- [ ] Include all required fields
- [ ] Log guardrail check results
- [ ] Call after every task execution

---

## Phase 6: Testing

### Unit Tests

**File**: `tests/test_guardrails.py`

```python
import pytest
from pathlib import Path
from guardrails import PatternGuardrails, AntiPatternDetector

def test_pattern_exists_validation():
    guardrails = PatternGuardrails(Path("PATTERN_INDEX.yaml"))
    
    # Valid pattern
    is_valid, error = guardrails.validate_pattern_exists("atomic_create")
    assert is_valid
    assert error is None
    
    # Invalid pattern
    is_valid, error = guardrails.validate_pattern_exists("nonexistent")
    assert not is_valid
    assert "not found" in error.lower()

def test_path_scope_validation():
    guardrails = PatternGuardrails(Path("PATTERN_INDEX.yaml"))
    
    # Valid paths
    is_valid, violations = guardrails.validate_path_scope(
        "atomic_create",
        ["src/test.py", "config/settings.json"]
    )
    assert is_valid
    
    # Protected path
    is_valid, violations = guardrails.validate_path_scope(
        "atomic_create",
        ["PATTERN_INDEX.yaml"]
    )
    assert not is_valid
    assert len(violations) > 0

def test_hallucinated_success_detection():
    detector = AntiPatternDetector(Path("anti_patterns"))
    
    # Should detect
    detection = detector.detect_hallucinated_success(
        task_status="success",
        verification={"exit_code": 1}
    )
    assert detection is not None
    assert detection["anti_pattern_id"] == "AP_HALLUCINATED_SUCCESS"
    
    # Should not detect
    detection = detector.detect_hallucinated_success(
        task_status="success",
        verification={"exit_code": 0}
    )
    assert detection is None
```

**Checklist**:
- [ ] Test pattern validation
- [ ] Test path scope validation
- [ ] Test tool usage validation
- [ ] Test change limits validation
- [ ] Test hallucinated success detection
- [ ] Test planning loop detection
- [ ] Test pre-execution checks
- [ ] Test post-execution checks

### Integration Tests

**File**: `tests/integration/test_guardrails_workflow.py`

```python
def test_full_workflow_with_guardrails():
    """Test complete workflow with guardrails enabled"""
    
    # Setup
    run_id = "test_run_001"
    
    # 1. Validate before run
    assert validate_before_run(run_id, Path.cwd())
    
    # 2. Execute task with valid pattern
    task = {
        "task_id": "task_001",
        "pattern_id": "atomic_create",
        "file_paths": ["test_file.py"],
        "tools": ["file_create", "syntax_check"]
    }
    
    result = execute_task(task)
    assert result["status"] in ["success", "failed"]  # Not "blocked"
    
    # 3. Check audit trail
    audit_file = Path(".acms_runs") / run_id / "pattern_audit.jsonl"
    assert audit_file.exists()
    
    # 4. Execute task with invalid pattern
    bad_task = {
        "task_id": "task_002",
        "pattern_id": "nonexistent"
    }
    
    result = execute_task(bad_task)
    assert result["status"] == "FAILED"
```

**Checklist**:
- [ ] Test full workflow with valid patterns
- [ ] Test workflow blocks invalid patterns
- [ ] Test anti-pattern detection triggers
- [ ] Test recovery patterns execute
- [ ] Test audit trail is complete

---

## Phase 7: Documentation Updates

**Checklist**:
- [ ] Update README.md with guardrails section
- [ ] Document new CLI flags (--validate, --strict-mode)
- [ ] Add troubleshooting section for common violations
- [ ] Update architecture diagrams
- [ ] Document pattern development workflow

---

## Verification Checklist

Before declaring integration complete:

### Functional
- [ ] All tasks require pattern_id
- [ ] Invalid patterns are rejected at plan time
- [ ] Pre-execution checks block unsafe tasks
- [ ] Post-execution checks catch hallucinated success
- [ ] Anti-patterns are detected automatically
- [ ] Recovery patterns are triggered
- [ ] Audit trail is complete

### Performance
- [ ] Guardrails add <200ms per task
- [ ] No noticeable slowdown in overall run time
- [ ] Validation can run in <5 seconds

### Safety
- [ ] Protected paths are never modified
- [ ] No task exceeds pattern limits
- [ ] Forbidden operations are blocked
- [ ] Main branch is never modified directly

### Observability
- [ ] All violations are logged
- [ ] Audit trail has all executions
- [ ] Anti-pattern detections are visible
- [ ] Run status reflects guardrail state

---

## Success Criteria

The integration is complete when:

1. ✅ Every task execution goes through guardrails
2. ✅ No task can bypass pattern registry
3. ✅ Anti-patterns are detected within 1 task of occurring
4. ✅ Recovery happens automatically
5. ✅ Full audit trail exists for every run
6. ✅ Tests pass at >95% coverage
7. ✅ Documentation is complete

---

## Next Steps After Integration

1. **Run pilot** - Execute 5-10 real gap-fixing runs with guardrails
2. **Monitor** - Watch for new anti-patterns
3. **Tune** - Adjust limits and thresholds based on data
4. **Expand** - Add more patterns as needs emerge
5. **Harden** - Add more anti-pattern runbooks
6. **Automate** - Add more recovery strategies
7. **Scale** - Increase confidence, reduce manual oversight

---

**Remember**: Integration is not "turn everything on at once." It's gradual, tested, and validated at each step.
