# MINI_PIPE - Invoke Task Runner Quick Start

## Overview

MINI_PIPE now uses [Invoke](https://www.pyinvoke.org/) as its standardized task runner, providing a unified CLI interface for all automation operations. This replaces scattered standalone scripts with a discoverable, composable task system.

**Benefits**:
- ✅ **Discoverable**: `inv --list` shows all available commands
- ✅ **Composable**: Tasks depend on other tasks automatically
- ✅ **Testable**: Consistent subprocess handling via `Context.run()`
- ✅ **Configurable**: Centralized tool configuration in `invoke.yaml`
- ✅ **CI Parity**: Same commands work locally and in GitHub Actions

---

## Quick Start

### 1. Install Invoke (if not already installed)

```bash
pip install invoke
```

### 2. See All Available Commands

```bash
inv --list
```

Output:
```
Available tasks:

  bootstrap          Set up development environment from scratch.
  ci                 Run full CI validation suite (validate + lint + test).
  install            Install production dependencies.
  install-dev        Install development dependencies.
  lint-all           Run all linters (black, isort, flake8, mypy).
  test-all           Run all test suites (unit + integration + e2e).
  validate-all       Run all validation checks (Phase 1 + Phase 2).
  clean.all          Complete cleanup.
  [... 21 more tasks ...]
```

### 3. Bootstrap Your Environment

```bash
inv bootstrap
```

This single command:
- Installs all production + development dependencies
- Configures pre-commit hooks
- Creates required directories (logs, state, .acms_runs)
- Validates installation

### 4. Run Validation

```bash
inv validate_all
```

Runs Phase 1 + Phase 2 validation checks. Exit code 0 if all pass.

### 5. Run Tests

```bash
# All tests
inv test_all

# Specific test suites
inv test.unit
inv test.integration
inv test.e2e
inv test.performance
```

### 6. Run Linters

```bash
# All linters
inv lint_all

# Auto-fix formatting issues
inv lint.fix

# Specific linters
inv lint.black
inv lint.isort
inv lint.flake8
inv lint.mypy
```

### 7. Full CI Suite (Before Pushing)

```bash
inv ci
```

Runs: `validate_all` → `lint_all` → `test_all`  
This is what CI runs in GitHub Actions.

---

## Common Workflows

### New Developer Setup

```bash
# Clone repository
git clone <repo-url>
cd MINI_PIPE

# One-command setup
pip install invoke
inv bootstrap

# Verify installation
inv validate_all
```

### Daily Development

```bash
# Start work
inv clean.logs  # Clean old logs
inv validate_all  # Verify environment

# Make changes
# ...

# Before committing
inv lint.fix  # Auto-fix formatting
inv lint_all  # Check all linters
inv test_all  # Run all tests

# Or run full CI suite
inv ci
```

### Cleanup & Reset

```bash
# Clean generated files (keeps dependencies)
inv clean_all

# Full reset (clean + reinstall dependencies)
inv reset
```

### Testing

```bash
# Run specific test suite with coverage
inv test.unit --coverage --verbose

# Run integration tests
inv test.integration --verbose

# Run performance benchmarks
inv test.performance
```

---

## Task Reference

### Top-Level Commands

| Command | Description |
|---------|-------------|
| `inv bootstrap` | Set up development environment from scratch |
| `inv validate_all` | Run all validation checks (Phase 1 + Phase 2) |
| `inv test_all` | Run all test suites (unit + integration + e2e) |
| `inv lint_all` | Run all linters (black, isort, flake8, mypy) |
| `inv ci` | Run full CI suite (validate + lint + test) |
| `inv clean_all` | Complete cleanup (does not remove dependencies) |
| `inv reset` | Full reset (cleanup + reinstall dependencies) |
| `inv install` | Install production dependencies |
| `inv install-dev` | Install development dependencies |
| `inv pre-commit` | Run pre-commit hooks on all files |

### Validation Tasks (`validate.*`)

| Command | Description |
|---------|-------------|
| `inv validate.phase1` | Run Phase 1 Quick Wins validation checks |
| `inv validate.phase2` | Run Phase 2 Core Functionality validation checks |
| `inv validate.all` | Run all validation checks |

### Test Tasks (`test.*`)

| Command | Description | Flags |
|---------|-------------|-------|
| `inv test.unit` | Run unit tests | `--coverage`, `--verbose` |
| `inv test.integration` | Run integration tests | `--verbose` |
| `inv test.e2e` | Run end-to-end tests | `--verbose` |
| `inv test.performance` | Run performance regression tests | `--verbose` |
| `inv test.all` | Run all test suites (except performance) | |

### Linting Tasks (`lint.*`)

| Command | Description | Flags |
|---------|-------------|-------|
| `inv lint.black` | Check code formatting with black | `--fix` |
| `inv lint.isort` | Check import sorting with isort | `--fix` |
| `inv lint.flake8` | Check code style with flake8 | |
| `inv lint.mypy` | Run type checking with mypy | |
| `inv lint.all` | Run all linters | |
| `inv lint.fix` | Apply auto-fixes for black and isort | |

### Cleanup Tasks (`clean.*`)

| Command | Description |
|---------|-------------|
| `inv clean.pycache` | Remove Python cache files |
| `inv clean.logs` | Remove log files |
| `inv clean.state` | Remove state databases and caches |
| `inv clean.acms-runs` | Remove ACMS run directories |
| `inv clean.all` | Complete cleanup |

---

## Configuration

Invoke uses a hierarchical configuration system. Configuration is loaded from multiple sources in precedence order:

### Configuration Hierarchy

1. **Command-line flags** (highest precedence)  
   `inv test.unit --coverage`

2. **Environment variables**  
   `INVOKE_TOOLS_PYTEST_TIMEOUT=900 inv test.unit`

3. **Project configuration** (`invoke.yaml`)  
   ```yaml
   tools:
     pytest:
       timeout: 600
       parallel: true
   ```

4. **User configuration** (`~/.invoke.yaml`)  
   *Create this file for user-specific overrides*

5. **Internal defaults** (lowest precedence)

### Project Configuration (`invoke.yaml`)

The repository includes `invoke.yaml` with:

**Runner Configuration**:
```yaml
run:
  shell: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
  pty: false  # Windows compatibility
```

**Tool Profiles**:
```yaml
tools:
  pytest:
    timeout: 600
    parallel: true
    coverage: true
  black:
    max_line_length: 120
  flake8:
    max_line_length: 120
    ignore: ["E203", "W503"]
```

**Orchestrator Settings**:
```yaml
orchestrator:
  dry_run: false
  max_retries: 3
  timeout: 300
```

### User Configuration (Optional)

Create `~/.invoke.yaml` or `./.invoke.yaml` for local overrides:

```yaml
# Example: Override pytest timeout locally
tools:
  pytest:
    timeout: 900

# Example: Enable dry-run mode by default
orchestrator:
  dry_run: true
```

---

## CI/CD Integration

### GitHub Actions

Workflows now delegate to Invoke tasks for consistency:

```yaml
# .github/workflows/ci.yml (future state)
- name: Bootstrap environment
  run: inv install-dev

- name: Run tests
  run: inv test_all

- name: Run linters
  run: inv lint_all
```

### Local CI Simulation

Run the same validation that CI runs:

```bash
inv ci
```

---

## Advanced Usage

### Task Help

Get detailed help for any task:

```bash
inv --help test.unit
```

Output:
```
Usage: inv[oke] [--core-opts] test.unit [--options] [other tasks here ...]

Docstring:
  Run unit tests.

  Args:
      coverage: Generate coverage report (default: False)
      verbose: Verbose output (default: False)

Options:
  -c, --coverage
  -v, --verbose
```

### Parallel Linting (Future)

Run multiple linters in parallel:

```bash
# Run all linters concurrently (planned feature)
inv lint.black lint.isort lint.flake8 lint.mypy
```

### Custom Task Execution

Import tasks programmatically:

```python
from invoke import Context
from tasks import validate_all, test_all

c = Context()
validate_all(c)
test_all(c)
```

---

## Migration Guide

### From Old Scripts to Invoke

**Before (Ad-hoc scripts)**:
```bash
python validate_phase1.py
python validate_phase2.py
pytest tests/unit/ -v --cov=src
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
```

**After (Invoke tasks)**:
```bash
inv validate_all
inv test.unit --coverage --verbose
inv lint_all
```

**Before (Manual setup)**:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy isort pre-commit
pre-commit install
mkdir logs state .acms_runs
```

**After (Bootstrap)**:
```bash
inv bootstrap
```

---

## Troubleshooting

### "Command not found: inv"

**Solution**: Install Invoke:
```bash
pip install invoke
```

### "FileNotFoundError" on Windows

**Solution**: Already configured in `invoke.yaml`. If you still see this, check that PowerShell is installed at:
```
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
```

### Task fails with non-zero exit code

**Solution**: Check the output for error details. Tasks set `warn=True`, so they capture output even on failure. Look for:
- Missing dependencies: `inv install-dev`
- Import errors: Check `PYTHONPATH` setup
- Test failures: Review test output

### Want to see commands before they run

**Solution**: Edit `invoke.yaml`:
```yaml
run:
  echo: true  # Print commands before executing
```

---

## Development

### Adding New Tasks

Edit `tasks.py`:

```python
@task
def my_task(c):
    """My custom task description."""
    c.run("echo 'Hello from my task'", pty=False)
```

Then run:
```bash
inv my-task
```

### Testing Task Changes

After editing `tasks.py`, immediately test:

```bash
inv --list  # Verify task appears
inv --help my-task  # Check docstring
inv my-task  # Execute
```

---

## Related Documentation

- **Invoke Official Docs**: https://www.pyinvoke.org/
- **Phase G Plan**: `INVOKE_ADOPTION_OPPORTUNITIES.md`
- **Implementation Progress**: `INVOKE_IMPLEMENTATION_PROGRESS.md`
- **Original Quick Start**: `AUTOMATION_QUICK_START.md` (legacy)

---

## Summary

MINI_PIPE now provides a **unified, discoverable, testable automation layer** via Invoke. Key commands:

```bash
inv --list          # Discover all available tasks
inv bootstrap       # One-command setup
inv validate_all    # Validation checks
inv test_all        # All tests
inv lint_all        # All linters
inv ci              # Full CI suite
```

**Next Steps**:
1. Install Invoke: `pip install invoke`
2. Bootstrap: `inv bootstrap`
3. Validate: `inv validate_all`
4. Explore: `inv --list`

For questions or issues, see `INVOKE_IMPLEMENTATION_PROGRESS.md` or run `inv --help <task>`.
