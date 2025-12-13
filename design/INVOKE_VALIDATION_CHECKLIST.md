# Phase G Invoke Adoption - Validation Checklist

**Purpose**: Systematic validation of Phase 1 Invoke adoption implementation  
**Date**: 2025-12-07  
**Status**: READY FOR VALIDATION

---

## Pre-Validation Setup

- [ ] Invoke installed: `python -m pip show invoke`
- [ ] Working directory: `C:\Users\richg\ALL_AI\MINI_PIPE`
- [ ] Git status clean (or changes staged)

---

## 1. Task Discovery Validation

### Commands to run:

```powershell
# Test task listing
inv --list

# Test help system
inv --help validate.phase1
inv --help test.unit
inv --help lint.black
```

### Expected Results:

- [ ] `inv --list` shows 28 tasks
- [ ] Tasks organized into namespaces (validate, test, lint, clean)
- [ ] All top-level convenience tasks visible (bootstrap, ci, reset, etc.)
- [ ] `inv --help <task>` shows docstring and parameters
- [ ] No import errors or syntax errors

---

## 2. Validation Tasks (INV-001)

### Commands to run:

```powershell
# Individual phase validation
inv validate.phase1
inv validate.phase2

# Combined validation
inv validate_all
```

### Expected Results:

- [ ] `inv validate.phase1` outputs "11/11 checks passed"
- [ ] `inv validate.phase1` exits with code 0
- [ ] `inv validate.phase2` runs (may have warnings for optional AI providers)
- [ ] `inv validate_all` runs both Phase 1 and Phase 2
- [ ] All checkmarks (✓) display correctly in output

---

## 3. Test Tasks (INV-006)

### Commands to run:

```powershell
# Individual test suites
inv test.unit
inv test.integration
inv test.e2e
inv test.performance

# With flags
inv test.unit --coverage
inv test.unit --verbose

# All tests
inv test_all
```

### Expected Results:

- [ ] `inv test.unit` discovers and runs unit tests
- [ ] `inv test.unit --coverage` generates coverage report
- [ ] PYTHONPATH set correctly (imports from `src/` work)
- [ ] `inv test.integration` runs integration tests with parallelism
- [ ] `inv test.e2e` runs sequentially (no -n auto)
- [ ] `inv test.performance` runs performance tests
- [ ] `inv test_all` runs unit + integration + e2e (not performance)
- [ ] Exit codes are correct (0 for pass, 1 for fail)

---

## 4. Linting Tasks (INV-007)

### Commands to run:

```powershell
# Individual linters
inv lint.black
inv lint.isort
inv lint.flake8
inv lint.mypy

# Auto-fix
inv lint.fix

# All linters
inv lint_all
```

### Expected Results:

- [ ] `inv lint.black` checks formatting (may fail if code unformatted)
- [ ] `inv lint.black --fix` applies formatting
- [ ] `inv lint.isort` checks import sorting
- [ ] `inv lint.isort --fix` applies sorting
- [ ] `inv lint.flake8` checks style (uses max-line-length=120)
- [ ] `inv lint.mypy` runs type checking
- [ ] `inv lint.fix` applies black + isort fixes
- [ ] `inv lint_all` runs all 4 linters
- [ ] Error messages are clear and actionable

---

## 5. Environment Setup Tasks (INV-009, INV-008)

### Commands to run:

```powershell
# Dependency installation
inv install
inv install-dev

# Full bootstrap
inv bootstrap
```

### Expected Results:

- [ ] `inv install` installs packages from `requirements.txt`
- [ ] `inv install-dev` installs dev packages (pytest, black, flake8, etc.)
- [ ] `inv bootstrap` runs 4 steps:
  - [ ] Step 1: Installs dependencies
  - [ ] Step 2: Installs pre-commit hooks
  - [ ] Step 3: Creates directories (logs, state, .acms_runs, .benchmarks)
  - [ ] Step 4: Shows "Bootstrap complete" message
- [ ] No errors during dependency installation
- [ ] Pre-commit hooks installed successfully

---

## 6. Cleanup Tasks (INV-010)

### Commands to run:

```powershell
# Individual cleanup
inv clean.pycache
inv clean.logs
inv clean.state
inv clean.acms-runs

# Full cleanup
inv clean_all

# Reset
inv reset
```

### Expected Results:

- [ ] `inv clean.pycache` removes `__pycache__` and `*.pyc` files
- [ ] `inv clean.logs` removes `logs/*.log`
- [ ] `inv clean.state` removes `state/*.db`, `.benchmarks`, `.pytest_cache`
- [ ] `inv clean.acms-runs` removes `.acms_runs/*`
- [ ] `inv clean_all` runs all cleanup tasks
- [ ] `inv reset` runs cleanup + reinstall dependencies
- [ ] No errors from missing directories
- [ ] Cleanup is idempotent (can run multiple times)

---

## 7. CI Task (Composite)

### Commands to run:

```powershell
# Full CI suite
inv ci
```

### Expected Results:

- [ ] Runs `validate_all` first
- [ ] Then runs `lint_all`
- [ ] Then runs `test_all`
- [ ] Shows "CI VALIDATION COMPLETE" on success
- [ ] Exit code 0 if all pass, 1 if any fail

---

## 8. Configuration Validation (INV-012)

### Files to check:

```powershell
# Verify invoke.yaml exists and is valid
Get-Content invoke.yaml

# Test config loading
python -c "from invoke import Config; c = Config(project_location='.'); print(c.tools.pytest.timeout)"
```

### Expected Results:

- [ ] `invoke.yaml` exists at repo root
- [ ] YAML syntax is valid (no parse errors)
- [ ] Contains `run:` section with shell configuration
- [ ] Contains `tools:` section with pytest, black, flake8, isort, mypy
- [ ] Contains `orchestrator:` section with dry_run, max_retries, timeout
- [ ] Contains `paths:` section with repo structure
- [ ] Config loads without errors
- [ ] Tool timeout reads as 600

---

## 9. Windows Compatibility

### System checks:

```powershell
# Verify PowerShell is available
$PSVersionTable

# Check shell configuration
python -c "from invoke import Config; c = Config(project_location='.'); print(c.run.shell)"

# Test command execution
inv validate.phase1
```

### Expected Results:

- [ ] PowerShell version 5.1+ or PowerShell 7+
- [ ] Shell configured to PowerShell path in `invoke.yaml`
- [ ] `pty: false` in configuration
- [ ] Commands execute without PTY errors
- [ ] PYTHONPATH uses `os.pathsep` (not hardcoded `:`)
- [ ] No "FileNotFoundError" exceptions

---

## 10. Documentation Validation

### Files to review:

```
INVOKE_ADOPTION_OPPORTUNITIES.md
INVOKE_IMPLEMENTATION_PROGRESS.md
INVOKE_QUICK_START.md
INVOKE_SESSION_SUMMARY.md
invoke.yaml
tasks.py
```

### Expected Results:

- [ ] All documentation files exist
- [ ] Markdown syntax is valid (no broken links)
- [ ] Code examples are accurate
- [ ] File paths are correct
- [ ] Inline comments in `invoke.yaml` are clear
- [ ] Docstrings in `tasks.py` are comprehensive
- [ ] Quick Start guide matches actual task behavior

---

## 11. Integration Points (Architecture)

### Verify boundaries:

```powershell
# Check that ACMS controller is unchanged
git diff src/acms/controller.py

# Check that MINI_PIPE orchestrator is unchanged
git diff src/minipipe/orchestrator.py

# Check that original scripts still work
python validate_phase1.py
python validate_phase2.py
```

### Expected Results:

- [ ] `src/acms/controller.py` has no changes
- [ ] `src/minipipe/orchestrator.py` has no changes
- [ ] `validate_phase1.py` still works as standalone script
- [ ] `validate_phase2.py` still works as standalone script
- [ ] Backward compatibility maintained
- [ ] Invoke is additive, not replacement

---

## 12. Regression Testing

### Run existing workflows:

```powershell
# Existing validation (should still work)
python validate_phase1.py
python validate_phase2.py

# Existing test execution (should still work)
pytest tests/unit/ -q

# Existing linting (should still work)
black --check src/
```

### Expected Results:

- [ ] All existing scripts work unchanged
- [ ] `python validate_phase1.py` produces same output as before
- [ ] `python validate_phase2.py` works
- [ ] Direct pytest execution works
- [ ] Direct black execution works
- [ ] No functionality broken by Invoke addition

---

## 13. Error Handling

### Test failure scenarios:

```powershell
# Force a test failure (create a broken test temporarily)
# Verify task reports failure correctly

# Force a lint failure (add unformatted code temporarily)
# Verify linter reports failure correctly

# Test with missing dependency
# Verify clear error message
```

### Expected Results:

- [ ] Test failures set exit code 1
- [ ] Error messages are clear and actionable
- [ ] Stack traces are visible when needed
- [ ] `warn=True` allows tasks to capture output even on failure
- [ ] No silent failures

---

## Validation Summary

**Total Checks**: 100+

### Critical (Must Pass)

- [ ] Task discovery works (`inv --list`)
- [ ] Validation tasks work (`inv validate_all`)
- [ ] Windows compatibility confirmed
- [ ] Configuration loads correctly
- [ ] No changes to ACMS/MINI_PIPE orchestrators
- [ ] Backward compatibility maintained

### Important (Should Pass)

- [ ] All test tasks work
- [ ] All lint tasks work
- [ ] Bootstrap completes successfully
- [ ] Cleanup tasks work
- [ ] CI task runs full suite

### Nice to Have (Can Fix Later)

- [ ] All documentation reviewed
- [ ] All code examples tested
- [ ] Error handling validated
- [ ] Regression tests pass

---

## Sign-Off

**Validation Date**: _____________  
**Validated By**: _____________  
**Result**: ☐ PASS  ☐ FAIL  ☐ PASS WITH NOTES

**Notes**:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

**Approved for Phase 2**: ☐ YES  ☐ NO  ☐ WITH CHANGES

---

## Quick Validation Script

Run this PowerShell one-liner to test the most critical functionality:

```powershell
# Quick validation (run in MINI_PIPE root)
inv --list; inv validate.phase1; inv test.unit; inv lint.black; inv clean.pycache; echo "✅ Quick validation complete"
```

Expected: All commands succeed, output looks correct, no errors.

---

## Issue Tracking

### Known Issues

*(Document any issues found during validation)*

| Issue # | Description | Severity | Status | Resolution |
|---------|-------------|----------|--------|------------|
|         |             |          |        |            |

### Future Improvements

*(Document enhancement opportunities)*

| Idea | Benefit | Effort | Priority |
|------|---------|--------|----------|
|      |         |        |          |

---

*Checklist version: 1.0*  
*Last updated: 2025-12-07*
