# TODO: Overlap & Deprecation Cleanup Tasks

**Created:** 2025-12-07  
**Status:** 🔴 Not Started  
**Source:** OVERLAP_DEPRECATION_ANALYSIS.md  
**Estimated Total Effort:** 12-16 hours

---

## Overview

This document tracks the remaining cleanup tasks identified in the overlap and deprecation analysis. Tasks are organized by priority and phase, with checkboxes for tracking completion.

### Quick Stats
- [ ] **7 overlap findings** (2 require action, 2 are correct patterns)
- [ ] **2 deprecated code areas** to clean up
- [ ] **3 unused code sections** to archive
- [ ] **12 total actionable items**

---

## 🔴 HIGH PRIORITY (Complete First)

### TODO-001: Consolidate load_tool_profiles() Functions
**Finding:** OVLP-002  
**Risk:** High  
**Effort:** 4-6 hours  
**Status:** ⬜ Not Started

**Problem:**
Two implementations of `load_tool_profiles()` exist:
- `src/minipipe/tools.py:57` - Current (loads from invoke.yaml)
- `src/acms/uet_tool_adapters.py:384` - Legacy (loads from config/tool_profiles.json)

**Tasks:**

#### Phase 1: Update Imports (Week 1)
- [ ] Update `src/minipipe/router.py`:
  ```python
  # Change:
  from src.acms.uet_tool_adapters import load_tool_profiles
  # To:
  from src.minipipe.tools import load_tool_profiles
  ```
  - File: `src/minipipe/router.py`
  - Search for: `from src.acms.uet_tool_adapters import load_tool_profiles`

- [ ] Update `tests/test_integration_uet_alignment.py`
  - Change import to `from src.minipipe.tools import load_tool_profiles`
  - Run test to verify: `pytest tests/test_integration_uet_alignment.py -v`

- [ ] Update `tests/test_uet_tool_adapters.py`
  - Change import to `from src.minipipe.tools import load_tool_profiles`
  - Run test to verify: `pytest tests/test_uet_tool_adapters.py -v`

#### Phase 2: Add Deprecation Warning (Week 2)
- [ ] Edit `src/acms/uet_tool_adapters.py:384`
  - Add deprecation warning (see code below)
  - Keep existing implementation temporarily
  - Test warning appears when called

**Code to add:**
```python
def load_tool_profiles(profile_path: str = "config/tool_profiles.json") -> Dict[str, Any]:
    """DEPRECATED: Use src.minipipe.tools.load_tool_profiles() instead.
    
    This function loads from legacy config/tool_profiles.json.
    New code should use invoke.yaml via src.minipipe.tools module.
    
    Will be removed in Phase G+1.
    """
    import warnings
    warnings.warn(
        "load_tool_profiles from uet_tool_adapters is deprecated. "
        "Use src.minipipe.tools.load_tool_profiles() instead. "
        "This will be removed in Phase G+1.",
        DeprecationWarning,
        stacklevel=2
    )
    # Keep existing implementation...
```

#### Phase 3: Configuration Migration (Week 3)
- [ ] Verify `invoke.yaml` has all tool profiles
  - Compare with `config/tool_profiles.json`
  - Migrate any missing profiles to invoke.yaml
  - Validate structure matches expected format

- [ ] Update documentation
  - Remove references to `config/tool_profiles.json`
  - Document tool profiles section in invoke.yaml
  - Add migration guide to CHANGELOG.md

#### Phase 4: Final Removal (Phase G+1)
- [ ] Remove `load_tool_profiles()` from `src/acms/uet_tool_adapters.py`
- [ ] Remove `get_tool_profile()` from same file (also duplicate)
- [ ] Run full test suite: `pytest -v`
- [ ] Consider deleting `config/tool_profiles.json` (if no other usage)

**Acceptance Criteria:**
- ✅ All imports use `src.minipipe.tools.load_tool_profiles`
- ✅ All tests passing
- ✅ Deprecation warning shows when old function called
- ✅ Documentation updated

**Dependencies:**
- Requires invoke.yaml to have complete tool profiles
- May affect router and UET tests

---

### TODO-002: Complete Legacy Configuration Migration
**Finding:** DEPR-001  
**Risk:** Medium  
**Effort:** 6-8 hours  
**Status:** ⬜ Not Started

**Problem:**
Legacy configuration files still supported with deprecation warnings:
- `config/circuit_breakers.yaml` (or .json)
- `config/tool_profiles.json`

Fallback code exists in:
- `src/minipipe/circuit_breakers.py:89-100`
- `src/minipipe/tools.py:72-82`

**Tasks:**

#### Phase 1: Verify invoke.yaml Completeness (Week 1)
- [ ] Check if legacy config files exist:
  ```powershell
  Get-ChildItem config -Filter "circuit_breakers.*"
  Get-ChildItem config -Filter "tool_profiles.json"
  ```

- [ ] Audit invoke.yaml for circuit breaker config:
  - [ ] `max_attempts_per_step`
  - [ ] `max_fix_attempts_per_step`
  - [ ] `max_attempts_per_error_signature`
  - [ ] `oscillation_window`
  - [ ] `oscillation_threshold`
  - [ ] `enable_fix_for_steps`
  - [ ] `per_step` overrides

- [ ] Migrate missing content from legacy files to invoke.yaml
- [ ] Validate invoke.yaml with schema (if available)

#### Phase 2: Update Tests (Week 1-2)
- [ ] Find tests referencing legacy config:
  ```powershell
  grep -r "config/circuit_breakers" tests/
  grep -r "config/tool_profiles" tests/
  ```

- [ ] Update tests to:
  - Load from invoke.yaml via `core.config_loader`
  - OR mock `config_loader` functions
  - Remove direct file path references

- [ ] Run affected tests: `pytest tests/ -k "config" -v`

#### Phase 3: Remove Fallback Code (Week 2-3)
- [ ] Edit `src/minipipe/circuit_breakers.py`:
  - [ ] Remove lines 89-110 (legacy file loading)
  - [ ] Keep only invoke.yaml path via `core.config_loader`
  - [ ] Return `DEFAULTS` if invoke.yaml missing (don't search for old files)
  - [ ] Test circuit breaker loading still works

- [ ] Edit `src/minipipe/tools.py`:
  - [ ] Remove `profile_path` parameter from `load_tool_profiles()` signature
  - [ ] Remove deprecation warning code (lines 72-82)
  - [ ] Keep only invoke.yaml loading
  - [ ] Test tool profile loading still works

- [ ] Run full test suite: `pytest -v`

#### Phase 4: Delete Legacy Files (Week 3)
- [ ] Archive legacy config files:
  ```powershell
  mkdir archive/legacy_config
  Move-Item config/circuit_breakers.* archive/legacy_config/
  Move-Item config/tool_profiles.json archive/legacy_config/
  ```

- [ ] Update `.gitignore` if needed
- [ ] Update CHANGELOG.md:
  ```markdown
  ## [Unreleased]
  ### Removed
  - Legacy config files (circuit_breakers.yaml, tool_profiles.json)
  - Fallback loading from config/ directory
  - All configuration now in invoke.yaml
  
  ### Migration Guide
  - Tool profiles: Move from config/tool_profiles.json to invoke.yaml tools section
  - Circuit breakers: Move from config/circuit_breakers.* to invoke.yaml circuit_breakers section
  ```

#### Phase 5: Documentation (Week 3)
- [ ] Update README.md:
  - Remove references to config/circuit_breakers.*
  - Remove references to config/tool_profiles.json
  - Document invoke.yaml configuration structure

- [ ] Create migration guide (if external users exist):
  - Document old → new config mapping
  - Provide examples
  - List all breaking changes

**Acceptance Criteria:**
- ✅ invoke.yaml has all configuration
- ✅ No fallback code remains
- ✅ Legacy files archived/deleted
- ✅ All tests passing
- ✅ Documentation updated

**Testing Commands:**
```powershell
# Test circuit breaker loading
pytest tests/ -k "circuit" -v

# Test tool profile loading
pytest tests/ -k "tool_profile" -v

# Full suite
pytest -v
```

---

## 🟡 MEDIUM PRIORITY

### TODO-003: Rename ValidationResult Classes
**Finding:** OVLP-001  
**Risk:** Low  
**Effort:** 1 hour  
**Status:** ⬜ Not Started

**Problem:**
Two classes named `ValidationResult` exist:
- `src/minipipe/patch_ledger.py:27` - Patch validation
- `src/acms/result_validation.py:18` - Task validation

**Tasks:**

- [ ] Rename in `src/minipipe/patch_ledger.py`:
  ```python
  # Line 27: Change class name
  @dataclass
  class PatchValidationResult:  # Was: ValidationResult
      """Patch validation results"""
      # ... rest of class
  ```

- [ ] Update all references in `patch_ledger.py`:
  - [ ] Method signatures returning `ValidationResult`
  - [ ] Method parameters accepting `ValidationResult`
  - [ ] Import statements (if any)
  - [ ] Type hints
  - Search pattern: `ValidationResult` (replace with `PatchValidationResult`)

- [ ] Rename in `src/acms/result_validation.py`:
  ```python
  # Line 18: Change class name
  @dataclass
  class TaskValidationResult:  # Was: ValidationResult
      """Result of validating a task execution"""
      # ... rest of class
  ```

- [ ] Update all references in `result_validation.py`:
  - [ ] Method signatures
  - [ ] Type hints
  - Search pattern: `ValidationResult` (replace with `TaskValidationResult`)

- [ ] Add clarifying docstrings:
  ```python
  # In patch_ledger.py
  class PatchValidationResult:
      """Validation results for patch format, scope, and constraints.
      
      Used by PatchLedger to track whether patches meet quality standards.
      NOT for task execution validation (see TaskValidationResult).
      """
  
  # In result_validation.py
  class TaskValidationResult:
      """Validation results for task execution outcomes.
      
      Used by ResultValidator to verify tasks completed correctly.
      NOT for patch validation (see PatchValidationResult).
      """
  ```

- [ ] Run tests:
  ```powershell
  pytest tests/ -v
  ```

- [ ] Verify no naming collisions:
  ```powershell
  grep -rn "class ValidationResult" src/
  # Should return 0 results
  ```

**Acceptance Criteria:**
- ✅ No classes named `ValidationResult`
- ✅ Clear, distinct names (`PatchValidationResult`, `TaskValidationResult`)
- ✅ All tests passing
- ✅ Docstrings clarify purpose

---

### TODO-004: Rename Circuit Breaker Modules
**Finding:** OVLP-003  
**Risk:** Medium  
**Effort:** 2-3 hours  
**Status:** ⬜ Not Started

**Problem:**
Confusing module names:
- `src/minipipe/circuit_breaker.py` - OOP circuit breaker pattern
- `src/minipipe/circuit_breakers.py` - Functional retry/oscillation detection

**Option A: Rename Both (Recommended)**

#### Tasks:
- [ ] Rename `circuit_breaker.py` → `circuit_breaker_pattern.py`
  ```powershell
  git mv src/minipipe/circuit_breaker.py src/minipipe/circuit_breaker_pattern.py
  ```

- [ ] Rename `circuit_breakers.py` → `retry_config.py`
  ```powershell
  git mv src/minipipe/circuit_breakers.py src/minipipe/retry_config.py
  ```

- [ ] Update import in `src/minipipe/resilient_executor.py:10`:
  ```python
  # Change:
  from .circuit_breaker import CircuitBreaker
  # To:
  from .circuit_breaker_pattern import CircuitBreaker
  ```

- [ ] Search for other imports:
  ```powershell
  grep -rn "from.*circuit_breaker" src/ tests/
  grep -rn "import.*circuit_breaker" src/ tests/
  ```

- [ ] Update any references found in tests

- [ ] Run tests:
  ```powershell
  pytest tests/ -v
  ```

- [ ] Update documentation/comments referencing old names

**Alternative Option B: Rename One**
- [ ] Keep `circuit_breaker.py` as-is
- [ ] Rename `circuit_breakers.py` → `execution_guardrails.py`
- [ ] Update imports accordingly

**Acceptance Criteria:**
- ✅ No naming confusion between modules
- ✅ All imports updated
- ✅ All tests passing
- ✅ Git history preserved (using git mv)

---

### TODO-005: Document Legacy Task Mode Timeline
**Finding:** DEPR-002  
**Risk:** Low  
**Effort:** 2 hours  
**Status:** ⬜ Not Started

**Problem:**
Legacy mode allows tasks without `pattern_id`, but no removal timeline exists.

**Tasks:**

#### Phase 1: Add Documentation (Week 1)
- [ ] Add docstring to `src/minipipe/executor.py` (near line 159):
  ```python
  """
  LEGACY MODE SUPPORT
  ===================
  Tasks without pattern_id are supported for backward compatibility.
  This mode bypasses pattern guardrails and should only be used during
  migration to the pattern-based system.
  
  DEPRECATION NOTICE:
  - Deprecated: Phase F (2025-12-07)
  - Warning Level: Phase G (Current)
  - Removal: Phase H (Target: Q1 2026)
  
  All new tasks MUST include pattern_id from PATTERN_INDEX.yaml.
  
  Migration Guide:
  1. Identify tasks without pattern_id
  2. Match task to appropriate pattern in PATTERN_INDEX.yaml
  3. Add pattern_id to task definition
  4. Test with guardrails enabled
  """
  ```

- [ ] Add to `src/acms/phase_plan_compiler.py` (near line 462):
  ```python
  # Warn but don't fail for legacy tasks
  # DEPRECATED: Legacy mode will be removed in Phase H
  # All tasks should have pattern_id by then
  print(f"  ⚠ Task {task.task_id} has no pattern_id (LEGACY MODE - DEPRECATED)")
  ```

- [ ] Update CHANGELOG.md:
  ```markdown
  ## [Unreleased - Phase H]
  ### Breaking Changes
  - Legacy mode removed: All tasks MUST have pattern_id
  - Tasks without pattern_id will fail validation
  
  ## [Current - Phase G]
  ### Deprecated
  - Legacy task mode (tasks without pattern_id)
  - Use pattern_id from PATTERN_INDEX.yaml for all tasks
  ```

#### Phase 2: Audit Usage (Week 2)
- [ ] Search for tasks without pattern_id:
  ```powershell
  # Find JSON task definitions
  Get-ChildItem -Recurse -Filter "*.json" | Select-String '"task_id"' | ForEach-Object {
      $file = $_.Path
      $content = Get-Content $file -Raw
      if ($content -notmatch '"pattern_id"') {
          Write-Host "Missing pattern_id: $file"
      }
  }
  ```

- [ ] Document legitimate legacy task usage
- [ ] Create migration plan for each legacy task

#### Phase 3: Stricter Warning (Week 3-4)
- [ ] Change warning to ERROR level in executor.py:
  ```python
  import logging
  logging.error(
      f"Task {task.task_id} has no pattern_id (DEPRECATED). "
      f"This will fail in Phase H. Add pattern_id from PATTERN_INDEX.yaml."
  )
  ```

- [ ] Add metric tracking:
  ```python
  # Track legacy mode usage
  if not task.pattern_id:
      event_bus.emit(
          EventType.DEPRECATION_WARNING,
          {
              "task_id": task.task_id,
              "issue": "missing_pattern_id",
              "removal_phase": "H"
          }
      )
  ```

#### Phase 4: Removal (Phase H - Future)
- [ ] Make pattern_id required in task schema
- [ ] Remove legacy mode check from executor.py
- [ ] Update validation to fail if pattern_id missing
- [ ] Remove legacy task tests from `tests/test_guardrails_integration.py:229-245`

**Acceptance Criteria:**
- ✅ Deprecation timeline documented
- ✅ Warning messages reference Phase H removal
- ✅ CHANGELOG updated
- ✅ Audit completed (no undocumented legacy tasks)

---

## 🟢 LOW PRIORITY

### TODO-006: Archive Unused Trigger Scripts
**Finding:** DEAD-001  
**Risk:** Safe  
**Effort:** 1-2 hours  
**Status:** ⬜ Not Started

**Problem:**
Three trigger scripts are never imported:
- `src/minipipe/monitoring_trigger.py` (150+ lines)
- `src/minipipe/router_trigger.py` (120+ lines)
- `src/minipipe/request_builder_trigger.py` (110+ lines)

**Decision Required:**
Choose ONE option:

#### Option A: Archive (Recommended)
- [ ] Create archive directory:
  ```powershell
  mkdir archive/ws1_automation_triggers
  ```

- [ ] Move trigger scripts:
  ```powershell
  git mv src/minipipe/monitoring_trigger.py archive/ws1_automation_triggers/
  git mv src/minipipe/router_trigger.py archive/ws1_automation_triggers/
  git mv src/minipipe/request_builder_trigger.py archive/ws1_automation_triggers/
  ```

- [ ] Create README in archive:
  ```markdown
  # WS1 Automation Triggers (Archived)
  
  **Archived:** 2025-12-07
  **Reason:** Never integrated into main execution flow
  
  ## Files
  - monitoring_trigger.py - Auto-start monitoring on RUN_CREATED (WS1-005)
  - router_trigger.py - Auto-trigger router on task_queue.json changes (WS1-004)
  - request_builder_trigger.py - Auto-trigger on PLANNING_COMPLETE (WS1-003)
  
  ## Status
  These were part of WS1 (Workstream 1) automation design but were never
  wired into the orchestrator. Manual invocation proved sufficient.
  
  ## Restoration
  If automation is needed in the future, these can be restored from git history
  or this archive and integrated into the event bus system.
  ```

- [ ] Update WS1 documentation (if exists)
- [ ] Commit with message: "Archive unused WS1 trigger scripts"

#### Option B: Integrate (If Automation Needed)
- [ ] Wire triggers into orchestrator lifecycle
- [ ] Add to event bus subscriptions
- [ ] Add tests for trigger functionality
- [ ] Update documentation
- **Effort: 8-12 hours**

#### Option C: Convert to Invoke Tasks
- [ ] Convert to `tasks.py` invoke tasks
- [ ] Remove file watching logic
- [ ] Document usage in README
- **Effort: 4-6 hours**

**Recommended:** Option A (Archive)

**Acceptance Criteria:**
- ✅ Trigger scripts moved to archive/ or deleted
- ✅ Archive README created (if archived)
- ✅ No broken imports
- ✅ Decision documented

---

### TODO-007: Evaluate ResilientExecutor
**Finding:** OVLP-004  
**Risk:** Low  
**Effort:** 1-6 hours  
**Status:** ⬜ Not Started

**Problem:**
`src/minipipe/resilient_executor.py` (188 lines) is never imported or used.

**Decision Required:**
Choose ONE option:

#### Option A: Archive as Unused
- [ ] Verify no imports:
  ```powershell
  grep -rn "ResilientExecutor" src/ tests/
  # Should only find definition in resilient_executor.py
  ```

- [ ] Move to archive:
  ```powershell
  mkdir archive/resilience_patterns
  git mv src/minipipe/resilient_executor.py archive/resilience_patterns/
  ```

- [ ] Create README:
  ```markdown
  # Resilience Patterns (Archived)
  
  ## resilient_executor.py
  **Archived:** 2025-12-07
  **Reason:** Never integrated into execution flow
  
  Implementation of WS-03-03A (Circuit Breaker + Retry pattern).
  Executor.py already has circuit breaker integration via guardrails.
  
  Can be restored if needed for enhanced resilience features.
  ```

#### Option B: Integrate into Executor
- [ ] Add `enable_resilience` flag to Executor.__init__()
- [ ] Wire ResilientExecutor for adapter calls
- [ ] Add tests for resilience features
- [ ] Update documentation
- **Effort: 6-8 hours**

#### Option C: Document as Reference
- [ ] Add comment to resilient_executor.py:
  ```python
  """
  REFERENCE IMPLEMENTATION: WS-03-03A Resilience Pattern
  
  This module is a reference implementation and is not currently used.
  Executor.py has integrated circuit breaker functionality via guardrails.
  
  Kept for:
  - Future resilience enhancements
  - Pattern documentation
  - Reference for retry logic
  
  Status: Not in use, but maintained for reference
  """
  ```

**Recommended:** Option A (Archive)

**Acceptance Criteria:**
- ✅ Decision made and documented
- ✅ No broken imports
- ✅ If archived, README created

---

### TODO-008: Document Adapter Architecture Patterns
**Finding:** OVLP-005, OVLP-006  
**Risk:** None  
**Effort:** 1 hour  
**Status:** ⬜ Not Started

**Problem:**
Correct architectural patterns might be mistaken for duplication.

**Tasks:**

- [ ] Create `docs/ARCHITECTURE_PATTERNS.md`:
  ```markdown
  # Architecture Patterns in MINI_PIPE
  
  ## Strategy Pattern: MiniPipe Adapters
  
  **Location:** `src/acms/minipipe_adapter.py` + `src/acms/real_minipipe_adapter.py`
  
  **Purpose:** Allow ACMS to execute plans via different backends (Mock vs Real)
  
  **Pattern:**
  - `minipipe_adapter.py` - Abstract interface + factory + mock implementation
  - `real_minipipe_adapter.py` - Real orchestrator integration
  - `create_minipipe_adapter()` - Factory auto-selects based on environment
  
  **Usage:**
  ```python
  # Factory selects appropriate implementation
  adapter = create_minipipe_adapter(repo_root)
  
  # In tests: uses MockMiniPipeAdapter
  # In production: uses RealMiniPipeAdapter
  ```
  
  **Why separate files:**
  - Clean separation of concerns
  - Mock can be used without MINI_PIPE dependencies
  - Real adapter can evolve independently
  - Easy to add new adapters (e.g., RemoteMiniPipeAdapter)
  
  ## Multiple Strategy Pattern: AI Adapters
  
  **Location:** `src/acms/ai_adapter.py` + `src/acms/api_adapters.py`
  
  **Purpose:** Support multiple AI integration methods
  
  **Pattern:**
  - `ai_adapter.py` - Base interface + CLI-based adapters + Mock
  - `api_adapters.py` - Direct API adapters (OpenAI, Anthropic)
  
  **When to use:**
  - CLI adapters: No API keys required, use local tools
  - API adapters: Direct integration, faster, more control
  - Mock adapter: Testing without AI services
  
  **Why separate files:**
  - Different dependency sets (openai, anthropic packages)
  - CLI adapters work without any API keys
  - API adapters require package installation
  - Clear separation of integration strategies
  
  ## Anti-Pattern: Not Everything Similar is Duplicate
  
  **Legitimate separate implementations:**
  1. Different backends (Strategy pattern)
  2. Different integration methods (CLI vs API)
  3. Domain-specific implementations (PatchValidation vs TaskValidation)
  
  **Actual duplicates to consolidate:**
  1. Same function, same purpose, different locations
  2. Copy-paste code with minor variations
  3. Legacy + new implementations of same feature
  ```

- [ ] Add inline comments to adapter files:
  
  In `minipipe_adapter.py`:
  ```python
  """
  MiniPipe Adapter - Strategy Pattern
  
  This file is intentionally separate from real_minipipe_adapter.py.
  See docs/ARCHITECTURE_PATTERNS.md for rationale.
  """
  ```

  In `real_minipipe_adapter.py`:
  ```python
  """
  Real MiniPipe Adapter - Strategy Pattern Implementation
  
  This file implements the real execution strategy.
  See docs/ARCHITECTURE_PATTERNS.md for architecture overview.
  """
  ```

- [ ] Update README.md with link to architecture docs

**Acceptance Criteria:**
- ✅ Architecture patterns documented
- ✅ Inline comments added
- ✅ README references architecture docs

---

## ✅ VALIDATION TASKS

### TODO-009: Run Full Test Suite
**Status:** ⬜ Not Started

After each major change:

- [ ] Run unit tests:
  ```powershell
  pytest tests/unit/ -v
  ```

- [ ] Run integration tests:
  ```powershell
  pytest tests/integration/ -v
  ```

- [ ] Run E2E tests:
  ```powershell
  pytest tests/e2e/ -v
  ```

- [ ] Run performance tests (if affected):
  ```powershell
  pytest tests/performance/ -v
  ```

- [ ] Check test coverage:
  ```powershell
  pytest --cov=src --cov-report=term-missing
  ```

---

### TODO-010: Manual Smoke Tests
**Status:** ⬜ Not Started

After configuration migration:

- [ ] Test router execution:
  ```powershell
  python -m core.engine.router --help
  # Verify tool profiles load correctly
  ```

- [ ] Test config loading:
  ```python
  from src.minipipe.tools import load_tool_profiles
  from src.minipipe.circuit_breakers import load_config
  
  tools = load_tool_profiles()
  breakers = load_config()
  
  # Verify loaded from invoke.yaml
  assert tools is not None
  assert breakers is not None
  ```

- [ ] Test adapter selection:
  ```python
  from src.acms.minipipe_adapter import create_minipipe_adapter
  adapter = create_minipipe_adapter(".")
  # Verify correct adapter type
  ```

- [ ] Run ACMS pipeline:
  ```powershell
  python src/cli/demo_acms_pipeline.py
  # Verify end-to-end functionality
  ```

---

### TODO-011: Update Documentation
**Status:** ⬜ Not Started

After all changes:

- [ ] Update CHANGELOG.md:
  ```markdown
  ## [Unreleased]
  ### Changed
  - Consolidated load_tool_profiles() to single implementation
  - Renamed ValidationResult classes for clarity
  - Renamed circuit breaker modules to clarify purpose
  
  ### Removed
  - Legacy configuration file loading (use invoke.yaml)
  - Unused trigger scripts (archived)
  - ResilientExecutor (archived as unused)
  
  ### Deprecated
  - Tasks without pattern_id (removal in Phase H)
  
  ### Added
  - Architecture patterns documentation
  - Migration guide for configuration changes
  ```

- [ ] Update README.md:
  - [ ] Remove references to legacy config files
  - [ ] Document invoke.yaml as single config source
  - [ ] Link to architecture patterns doc

- [ ] Update contributing guide (if affected)

- [ ] Update any API documentation

---

### TODO-012: Generate Metrics Report
**Status:** ⬜ Not Started

After all cleanup:

- [ ] Calculate lines of code removed:
  ```powershell
  # Before cleanup (baseline)
  $before = (Get-ChildItem src -Recurse -Filter "*.py" | Get-Content | Measure-Object -Line).Lines
  
  # After cleanup
  $after = (Get-ChildItem src -Recurse -Filter "*.py" | Get-Content | Measure-Object -Line).Lines
  
  # Difference
  $removed = $before - $after
  Write-Host "Lines removed: $removed"
  ```

- [ ] Count files removed/archived:
  ```powershell
  Get-ChildItem archive -Recurse -Filter "*.py" | Measure-Object
  ```

- [ ] Verify naming collisions eliminated:
  ```powershell
  # Should find no duplicate class names
  grep -rn "class ValidationResult" src/  # Should be 0
  ```

- [ ] Generate summary report:
  ```markdown
  # Cleanup Summary Report
  
  **Completed:** [DATE]
  **Duration:** [HOURS]
  
  ## Metrics
  - Lines of code removed: XXX
  - Files archived: X
  - Legacy config files removed: X
  - Naming collisions fixed: X
  - Tests still passing: ✅
  
  ## Impact
  - Single configuration source (invoke.yaml) ✅
  - Clear module naming ✅
  - No duplicate implementations ✅
  - Cleaner architecture ✅
  ```

---

## 📋 CHECKLIST BY PHASE

### Phase 1: Safe Cleanup (Week 1) - 2-3 hours
- [ ] TODO-003: Rename ValidationResult classes
- [ ] TODO-008: Document architecture patterns
- [ ] TODO-006: Archive unused trigger scripts
- [ ] TODO-009: Run full test suite

### Phase 2: Configuration Migration (Week 2-3) - 8-10 hours
- [ ] TODO-001: Consolidate load_tool_profiles()
- [ ] TODO-002: Complete legacy config migration
- [ ] TODO-004: Rename circuit breaker modules
- [ ] TODO-009: Run full test suite
- [ ] TODO-010: Manual smoke tests

### Phase 3: Deprecation Cleanup (Week 4-5) - 4-6 hours
- [ ] TODO-005: Document legacy mode timeline
- [ ] TODO-007: Evaluate ResilientExecutor
- [ ] TODO-011: Update documentation
- [ ] TODO-009: Run full test suite

### Phase 4: Verification (Week 6) - 3-4 hours
- [ ] TODO-009: Final full test suite run
- [ ] TODO-010: Complete smoke tests
- [ ] TODO-012: Generate metrics report
- [ ] TODO-011: Final documentation updates

---

## 🎯 SUCCESS CRITERIA

### Must Complete
- ✅ All HIGH priority tasks done (TODO-001, TODO-002)
- ✅ All tests passing
- ✅ Configuration migrated to invoke.yaml
- ✅ Documentation updated

### Should Complete
- ✅ All MEDIUM priority tasks done (TODO-003, TODO-004, TODO-005)
- ✅ Naming collisions eliminated
- ✅ Deprecation timeline set

### Nice to Have
- ✅ All LOW priority tasks done (TODO-006, TODO-007, TODO-008)
- ✅ Architecture documented
- ✅ Unused code archived

---

## 📊 PROGRESS TRACKING

**Overall Progress:** 0/12 tasks complete (0%)

**By Priority:**
- 🔴 HIGH: 0/2 (0%)
- 🟡 MEDIUM: 0/3 (0%)
- 🟢 LOW: 0/3 (0%)
- ✅ VALIDATION: 0/4 (0%)

**Estimated Completion:** Week 6 (if started now)

**Blocker Status:** None

---

## 🚀 QUICK START

To begin cleanup:

1. **Start with Phase 1 (Safe Cleanup):**
   ```powershell
   # TODO-003: Rename ValidationResult classes
   # Edit files, update references, run tests
   
   # TODO-006: Archive trigger scripts
   mkdir archive/ws1_automation_triggers
   git mv src/minipipe/*_trigger.py archive/ws1_automation_triggers/
   
   # TODO-008: Document architecture
   # Create docs/ARCHITECTURE_PATTERNS.md
   ```

2. **Then move to Phase 2 (Config Migration):**
   ```powershell
   # TODO-001 & TODO-002: High priority, requires testing
   # Review invoke.yaml first
   # Update imports carefully
   # Test frequently
   ```

3. **Track progress:**
   - Update checkboxes in this file as you complete tasks
   - Update progress percentages
   - Note any blockers or issues

---

## 📝 NOTES

### Dependencies Between Tasks
- TODO-001 should complete before TODO-002 (both config-related)
- TODO-009 (testing) runs after each major task
- TODO-011 (docs) runs after all code changes
- TODO-012 (metrics) runs last

### Risk Mitigation
- Create feature branch: `git checkout -b cleanup/overlap-deprecation`
- Commit frequently: After each TODO completion
- Run tests after each change
- Keep legacy files until fully verified

### Rollback Plan
If issues arise:
```powershell
# Revert to main branch
git checkout main

# Cherry-pick successful changes
git cherry-pick <commit-hash>

# Fix issues and retry
```

---

**Document Status:** ✅ Complete  
**Last Updated:** 2025-12-07  
**Next Review:** After Phase 1 completion
