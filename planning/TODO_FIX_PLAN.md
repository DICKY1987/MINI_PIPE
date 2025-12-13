# ACMS Project - Actual Fix Plan

**Analysis Date:** 2025-12-07  
**Python Version:** 3.12.10  
**Project Root:** C:\Users\richg\ALL_AI\MINI_PIPE

---

## EXECUTIVE SUMMARY

After thorough analysis, identified **5 CRITICAL** and **3 MEDIUM** issues that need fixing.
The original evaluation was **partially inaccurate** - many claimed issues don't exist.

**Critical Issues:**
1. Legacy `core.*` imports in `src/minipipe/` files (broken imports)
2. Missing `pyproject.toml` (prevents proper installation)
3. Deprecated `datetime.utcnow()` in production code (4 locations)
4. Missing schema field in `run_status.schema.json`
5. Wrong schema path in `schema_utils.py`

**Medium Issues:**
6. Fragile `sys.path` manipulation in 12 test files
7. Missing imports in demo CLI files
8. Missing `__init__.py` files for proper package structure

---

## 🔴 CRITICAL FIXES

### Fix 1: Remove Legacy `core.*` Imports (BLOCKING)

**Problem:** Files in `src/minipipe/` import from non-existent `core.*` modules

**Affected Files:**
- `src/minipipe/executor.py` (lines 16-24)
- `src/minipipe/circuit_breakers.py`
- `src/minipipe/orchestrator.py` (line 15)
- `src/minipipe/recovery.py` (line 8)

**Evidence:**
```python
# src/minipipe/executor.py line 16-24
from core.adapters.base import ToolConfig                    # ❌ BROKEN
from core.adapters.subprocess_adapter import SubprocessAdapter # ❌ BROKEN
from core.contracts.decorators import enforce_entry_contract   # ❌ BROKEN
from core.engine.execution_request_builder import ExecutionRequestBuilder # ❌ BROKEN
from src.minipipe.orchestrator import Orchestrator           # ✅ CORRECT
from src.minipipe.router import TaskRouter                   # ✅ CORRECT
```

**Root Cause:** These appear to be OLD/LEGACY files that haven't been updated to new structure

**Solution Strategy:**
Two options:
1. **DELETE legacy files** (if not used) - RECOMMENDED
2. **Stub out core imports** (if needed for future work)

**Action Plan:**
```bash
# Step 1: Check if these files are imported anywhere
grep -r "from src.minipipe.executor import" .
grep -r "import src.minipipe.executor" .

# Step 2a: If NOT used - DELETE them
rm src/minipipe/executor.py
rm src/minipipe/circuit_breakers.py  # Note: circuit_breaker.py exists separately
# Keep: orchestrator.py, recovery.py (may be used)

# Step 2b: If USED - Comment out broken imports and stub classes
```

**Files to Review:**
- `src/minipipe/executor.py` - Has `core.*` imports
- `src/minipipe/circuit_breakers.py` - Has `core.config_loader` import
- `src/minipipe/orchestrator.py` - Mixed: has both core and src imports
- `src/minipipe/recovery.py` - Has `core.engine.scheduler` import

---

### Fix 2: Create `pyproject.toml` (BLOCKING)

**Problem:** No package configuration exists - cannot install project properly

**Impact:**
- `pip install -e .` fails
- Tests may not run reliably
- Module imports inconsistent
- CI/CD will fail

**Solution:**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "acms"
version = "0.2.0"
description = "AI-Centric Methodology System with MINI_PIPE integration"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "jsonschema>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["src*", "contracts*", "schemas*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

**After Creating:**
```bash
pip install -e ".[dev]"
pytest tests/ --collect-only  # Verify tests are discovered
```

---

### Fix 3: Replace Deprecated `datetime.utcnow()` (URGENT)

**Problem:** Using deprecated `datetime.utcnow()` - will be removed in Python 3.13+

**Python 3.12 Status:** Still works but issues `DeprecationWarning`  
**Python 3.13+:** Will be REMOVED entirely

**Affected Files (4 locations):**

| File | Line | Current Code | Fix |
|------|------|-------------|-----|
| `src/acms/guardrails.py` | 34 | `datetime.utcnow()` | `datetime.now(UTC)` |
| `contracts/uet_submodule_io_contracts.py` | 38 | `datetime.utcnow().isoformat() + "Z"` | `datetime.now(UTC).isoformat()` |
| `contracts/uet_submodule_io_contracts.py` | 170 | `datetime.utcnow().isoformat() + "Z"` | `datetime.now(UTC).isoformat()` |
| `tests/unit/test_gap_registry.py` | 89 | `datetime.utcnow().isoformat()` | `datetime.now(UTC).isoformat()` |

**Import Fix Required:**
```python
# Add to imports:
from datetime import UTC, datetime

# Change code:
- datetime.utcnow()
+ datetime.now(UTC)

# Note: datetime.now(UTC).isoformat() already includes 'Z', don't append it
```

**Changes:**

**File 1: `src/acms/guardrails.py`**
```python
# Line 34
- self.timestamp = datetime.utcnow()
+ self.timestamp = datetime.now(UTC)

# Ensure import at top:
from datetime import UTC, datetime  # Add UTC
```

**File 2: `contracts/uet_submodule_io_contracts.py`**
```python
# Line 1: Add imports
from datetime import UTC, datetime

# Line 38:
- self.created_at = datetime.utcnow().isoformat() + "Z"
+ self.created_at = datetime.now(UTC).isoformat()

# Line 170:
- self.created_at = datetime.utcnow().isoformat() + "Z"
+ self.created_at = datetime.now(UTC).isoformat()
```

**File 3: `tests/unit/test_gap_registry.py`**
```python
# Line 89:
- discovered_at=datetime.utcnow().isoformat()
+ discovered_at=datetime.now(UTC).isoformat()

# Add to imports:
from datetime import UTC, datetime
```

---

### Fix 4: Add Missing Schema Field (BLOCKING TESTS)

**Problem:** `run_status.schema.json` missing `workstreams_created` field

**Evidence:**
- Schema has: `gaps_discovered`, `tasks_executed`
- Test expects: `workstreams_created` (line 187 in `test_full_run.py`)

**Current Schema:**
```json
{
  "metrics": {
    "properties": {
      "gaps_discovered": {"type": "integer", "minimum": 0},
      "tasks_executed": {"type": "integer", "minimum": 0}
    }
  }
}
```

**Fixed Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Run Status",
  "type": "object",
  "required": ["run_id", "final_status", "metrics"],
  "properties": {
    "run_id": {"type": "string"},
    "final_status": {"type": "string", "enum": ["success", "failed", "partial"]},
    "metrics": {
      "type": "object",
      "properties": {
        "gaps_discovered": {"type": "integer", "minimum": 0},
        "workstreams_created": {"type": "integer", "minimum": 0},
        "tasks_executed": {"type": "integer", "minimum": 0},
        "tasks_failed": {"type": "integer", "minimum": 0}
      },
      "required": ["gaps_discovered", "workstreams_created", "tasks_executed"]
    }
  }
}
```

**File:** `schemas/acms/run_status.schema.json`

---

### Fix 5: Fix Schema Path in `schema_utils.py` (WILL FAIL SILENTLY)

**Problem:** `schema_utils.py` looks for schemas in wrong location

**Current Code (line 24):**
```python
self.schema_dir = schema_dir or (Path(__file__).parent / "schemas")
```

**Where `__file__` is:** `src/acms/schema_utils.py`  
**Looks for schemas at:** `src/acms/schemas/` ❌  
**Actual schema location:** `schemas/` (project root) ✅

**Fix:**
```python
# Line 24:
- self.schema_dir = schema_dir or (Path(__file__).parent / "schemas")
+ self.schema_dir = schema_dir or (Path(__file__).parent.parent.parent / "schemas")
```

**Verification:**
```python
# Test:
from src.acms.schema_utils import SchemaValidator
validator = SchemaValidator()
print(validator.schema_dir)  # Should print: /path/to/MINI_PIPE/schemas
print(list(validator.schemas.keys()))  # Should list loaded schemas
```

---

## 🟡 MEDIUM PRIORITY FIXES

### Fix 6: Remove Fragile `sys.path` Manipulation (TECHNICAL DEBT)

**Problem:** 12 test files use fragile `sys.path.append(str(Path(__file__).parent.parent.parent))`

**Affected Files:**
```
tests/e2e/test_full_run.py:10
tests/integration/test_phase_summary.py:9
tests/e2e/test_failure_paths.py:10
tests/integration/test_phase_planning.py:8
tests/e2e/test_determinism.py:11
tests/integration/test_phase_gap_discovery.py:8
tests/unit/test_acms_minipipe_adapter.py:9
tests/integration/test_phase_execution.py:8
tests/unit/test_controller_init.py:10
tests/unit/test_execution_planner.py:7
tests/unit/test_phase_plan_compiler.py:8
tests/unit/test_gap_registry.py:8
```

**Root Cause:** No `pyproject.toml` - tests can't rely on package installation

**Solution:**
After creating `pyproject.toml` and running `pip install -e .`:

```python
# REMOVE these lines from all test files:
- import sys
- from pathlib import Path
- sys.path.append(str(Path(__file__).parent.parent.parent))

# Imports will work automatically via installed package
```

**Dependency:** Fix #2 must be completed first

---

### Fix 7: Fix Demo CLI Import Errors

**Problem:** Demo files use incorrect relative imports

**Affected File:** `src/cli/demo_acms_pipeline.py`

**Current Code (lines 11-13):**
```python
from gap_registry import GapRegistry, GapStatus
from execution_planner import ExecutionPlanner
from phase_plan_compiler import PhasePlanCompiler
```

**Fixed Code:**
```python
from src.acms.gap_registry import GapRegistry, GapStatus
from src.acms.execution_planner import ExecutionPlanner
from src.acms.phase_plan_compiler import PhasePlanCompiler
```

**Files to Check:**
- `src/cli/demo_acms_pipeline.py`
- `src/cli/demo_minimal_scenario.py` (if it has similar imports)

---

### Fix 8: Add Missing `__init__.py` Files (BEST PRACTICE)

**Problem:** Package directories missing `__init__.py` for proper Python packages

**Current Structure:**
```
src/
  acms/          # ❌ No __init__.py
  minipipe/      # ❌ No __init__.py
  cli/           # ❌ No __init__.py
contracts/       # ❌ No __init__.py
schemas/         # ⚠️  Not a code package (OK without it)
```

**Solution:**
```bash
# Create empty __init__.py files
touch src/__init__.py
touch src/acms/__init__.py
touch src/minipipe/__init__.py
touch src/cli/__init__.py
touch contracts/__init__.py
```

**Note:** `schemas/` doesn't need `__init__.py` since it only contains JSON files

---

## ❌ FALSE ISSUES FROM ORIGINAL EVALUATION

These were claimed as issues but **DO NOT EXIST**:

### ✅ "Missing contracts/ package" - FALSE
- **Claim:** "contracts package doesn't exist"
- **Reality:** `contracts/` directory EXISTS with all files
- **Files Present:** 
  - `path_registry.py`
  - `uet_execution_planner.py`
  - `uet_submodule_io_contracts.py`
  - `uet_tool_adapters.py`
  - `uet_workstream_adapter.py`

### ✅ "NameError in acms_controller.py" - FALSE
- **Claim:** "Uses `timezone.utc` but imports `UTC`"
- **Reality:** Code correctly uses `datetime.now(UTC)` everywhere
- **Actual file:** `src/acms/controller.py` (not `acms_controller.py`)
- **Line 17:** `from datetime import UTC, datetime` ✅
- **Line 127:** `datetime.now(UTC).isoformat()` ✅
- **Line 131:** `datetime.now(UTC).isoformat()` ✅

### ✅ "Schema files at wrong location" - FALSE
- **Claim:** "Schemas at root instead of schemas/ directory"
- **Reality:** Schemas ARE in `schemas/` subdirectories:
  - `schemas/acms/gap_record.schema.json`
  - `schemas/acms/run_status.schema.json`
  - `schemas/execution/*.schema.json`
  - `schemas/tools/*.schema.json`

### ✅ "path_index.yaml missing" - FALSE
- **Claim:** "File doesn't exist at config/path_index.yaml"
- **Reality:** File EXISTS at `config/path_index.yaml` ✅
- **Verified:** `Test-Path "config\path_index.yaml"` returns `True`

---

## IMPLEMENTATION ORDER

Execute fixes in this order to minimize dependency issues:

### Phase 1: Package Setup (Required for everything else)
1. ✅ Create `pyproject.toml` (Fix #2)
2. ✅ Add `__init__.py` files (Fix #8)
3. ✅ Run `pip install -e ".[dev]"`

### Phase 2: Critical Code Fixes
4. ✅ Fix `datetime.utcnow()` deprecated calls (Fix #3)
5. ✅ Fix schema path in `schema_utils.py` (Fix #5)
6. ✅ Add missing schema field (Fix #4)

### Phase 3: Clean Up Legacy Code
7. ✅ Analyze/remove legacy `core.*` imports (Fix #1)
8. ✅ Fix demo CLI imports (Fix #7)

### Phase 4: Test Cleanup (After package install works)
9. ✅ Remove `sys.path` manipulation from tests (Fix #6)

---

## VERIFICATION CHECKLIST

After all fixes, verify with these commands:

```bash
# 1. Package installs correctly
pip install -e ".[dev]"
# Expected: No errors

# 2. Imports work
python -c "from src.acms.controller import ACMSController; print('✅ Controller imports')"
python -c "from src.acms.gap_registry import GapRegistry; print('✅ GapRegistry imports')"
python -c "from contracts.uet_submodule_io_contracts import ExecutionRequestV1; print('✅ Contracts import')"
# Expected: All print ✅ messages

# 3. Schema validation works
python -c "from src.acms.schema_utils import SchemaValidator; v = SchemaValidator(); print(f'✅ Found {len(v.schemas)} schemas')"
# Expected: ✅ Found 2+ schemas

# 4. No deprecated datetime warnings
python -W error::DeprecationWarning -c "from src.acms.guardrails import PatternGuardrails"
# Expected: No warnings

# 5. Tests are discovered
pytest --collect-only tests/
# Expected: Shows collected test items

# 6. Run unit tests
pytest tests/unit/ -v
# Expected: Tests pass (or at least run without import errors)
```

---

## RISK ASSESSMENT

| Fix | Risk Level | Impact if Skipped |
|-----|-----------|-------------------|
| #1 - Remove core imports | LOW | Only affects unused legacy files |
| #2 - Add pyproject.toml | **HIGH** | Cannot install package, tests fail |
| #3 - Fix datetime.utcnow | **HIGH** | Will break in Python 3.13+ |
| #4 - Add schema field | MEDIUM | test_full_run.py fails |
| #5 - Fix schema path | MEDIUM | Schema validation silently fails |
| #6 - Remove sys.path | LOW | Tests work but fragile |
| #7 - Fix demo imports | LOW | Demo scripts don't run |
| #8 - Add __init__.py | MEDIUM | Imports may fail in some environments |

---

## ESTIMATED EFFORT

- **Phase 1 (Package Setup):** 15 minutes
- **Phase 2 (Critical Fixes):** 30 minutes
- **Phase 3 (Legacy Cleanup):** 45 minutes (requires analysis)
- **Phase 4 (Test Cleanup):** 20 minutes
- **Verification:** 15 minutes

**Total Estimated Time:** 2 hours

---

## SUCCESS CRITERIA

✅ All fixes implemented when:
1. `pip install -e ".[dev]"` succeeds
2. All `src.acms.*` imports work without sys.path hacks
3. No `DeprecationWarning` for datetime
4. Schema validation finds and loads schemas
5. `pytest tests/unit/` runs without import errors
6. No references to non-existent `core.*` modules

---

## NOTES

- **Python 3.12.10** supports `datetime.UTC` (added in 3.11)
- `datetime.now(UTC).isoformat()` automatically appends `+00:00` (equivalent to `Z`)
- Original evaluation appears to be from an older/different version of codebase
- Focus on ACTUAL issues, not claimed issues that don't exist

