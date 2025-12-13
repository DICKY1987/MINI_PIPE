# MINI_PIPE - AI-Driven Code Transformation Pipeline

**Status**: Production Ready  
**Version**: 2.0  
**Last Updated**: 2025-12-07

A sophisticated, pattern-driven code transformation pipeline leveraging ACMS (Autonomous Code Modification System) for automated repository analysis, gap detection, and intelligent code generation.

---

## Quick Start

### New Developer Setup

```bash
# 1. Install Invoke (Python task runner)
pip install invoke

# 2. Bootstrap environment (one command does everything)
inv bootstrap

# 3. Verify installation
inv validate_all
```

**That's it!** You're ready to develop.

---

## Common Tasks

Discover all available automation tasks:

```bash
inv --list
```

### Daily Development Workflow

```bash
# Validate your environment
inv validate_all

# Run tests
inv test_all

# Run linters
inv lint_all

# Full CI suite (before committing)
inv ci
```

### Task Categories

**Validation**:
- `inv validate.phase1` - Phase 1 Quick Wins validation
- `inv validate.phase2` - Phase 2 Core Functionality validation
- `inv validate_all` - All validation checks

**Testing**:
- `inv test.unit` - Unit tests (with `--coverage` and `--verbose` options)
- `inv test.integration` - Integration tests
- `inv test.e2e` - End-to-end tests
- `inv test.performance` - Performance benchmarks
- `inv test_all` - All test suites

**Linting**:
- `inv lint.black` - Code formatting (with `--fix` option)
- `inv lint.isort` - Import sorting (with `--fix` option)
- `inv lint.flake8` - Style checking
- `inv lint.mypy` - Type checking
- `inv lint.fix` - Auto-fix formatting and imports
- `inv lint_all` - All linters

**Maintenance**:
- `inv clean.all` - Cleanup generated files
- `inv reset` - Full reset (cleanup + reinstall)
- `inv bootstrap` - Set up development environment

**CI/CD**:
- `inv ci` - Full CI validation (validate + lint + test)
- `inv pre-commit` - Run pre-commit hooks

---

## Project Structure

```
MINI_PIPE/
├── src/                    # Source code
│   ├── acms/               # ACMS (Autonomous Code Modification System)
│   │   ├── controller.py   # Main orchestration logic
│   │   ├── ai_adapter.py   # AI provider integrations
│   │   ├── gap_registry.py # Gap detection and tracking
│   │   └── guardrails.py   # Safety and validation
│   ├── minipipe/           # MINI_PIPE execution engine
│   │   ├── orchestrator.py # Task orchestration
│   │   ├── tools.py        # Tool execution primitives
│   │   └── process_spawner.py # Worker process management
│   └── cli/                # Command-line interface
├── tests/                  # Test suites
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── e2e/                # End-to-end tests
│   └── performance/        # Performance benchmarks
├── docs/                   # Documentation
│   ├── acms/               # ACMS documentation
│   ├── minipipe/           # MINI_PIPE documentation
│   ├── guardrails/         # Guardrails documentation
│   ├── uet_alignment/      # UET alignment documentation
│   └── specs/              # Technical specifications
├── config/                 # Configuration files
│   ├── process_steps.json  # Process step definitions
│   └── tool_profiles.json  # Tool configurations
├── scripts/                # Utility scripts
│   ├── acms_test_harness.py # E2E test harness
│   └── multi_agent_orchestrator.py # Multi-agent orchestration
├── reports/                # Completion and progress reports
├── planning/               # TODO lists and planning documents
├── design/                 # Analysis and design documents
│   └── analysis_frameworks/ # Gap analysis frameworks
├── patterns/               # Reusable patterns
├── schemas/                # JSON schemas
├── tools/                  # Development tools
├── examples/               # Usage examples
├── .github/workflows/      # CI/CD workflows
├── tasks.py                # Invoke task definitions
├── invoke.yaml             # Invoke configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Key Features

### 🤖 ACMS (Autonomous Code Modification System)

- **Pattern-driven transformations**: Recognizes code patterns and applies transformations
- **Gap detection**: Automatically identifies missing functionality
- **AI-powered**: Integrates with OpenAI, Anthropic, GitHub Copilot CLI
- **Safety first**: Built-in guardrails prevent unsafe modifications

### 🔄 MINI_PIPE Orchestrator

- **Multi-tool support**: Orchestrates pytest, aider, black, mypy, and more
- **Parallel execution**: Runs independent tasks concurrently
- **Sandboxed execution**: Isolates tool execution for safety
- **Comprehensive logging**: Full audit trail of all operations

### 📊 Monitoring & Notifications

- **Real-time health checks**: Continuous system monitoring
- **Multi-channel notifications**: Slack, Email, GitHub Issues
- **Performance tracking**: Baseline tracking and regression detection
- **Detailed metrics**: JSONL-formatted historical data

### ✅ Quality Assurance

- **Automated testing**: Unit, integration, E2E, and performance tests
- **Continuous linting**: Black, isort, flake8, mypy
- **Pre-commit hooks**: Catch issues before commit
- **GitHub Actions CI**: Automated validation on every push

---

## Configuration

### Project Configuration (`invoke.yaml`)

Global settings for the project. Defines tool profiles, runner settings, and paths.

```yaml
tools:
  pytest:
    timeout: 600
    parallel: true
  black:
    max_line_length: 120
```

### User Configuration (`~/.invoke.yaml` or `./.invoke.yaml`)

Override project settings for your local environment.

```bash
# Copy example template
cp .invoke.yaml.example ~/.invoke.yaml

# Edit to customize
vim ~/.invoke.yaml
```

See `.invoke.yaml.example` for all available options.

### Environment Variables

Override any setting via environment variables:

```bash
export INVOKE_TOOLS_PYTEST_TIMEOUT=900
export INVOKE_ORCHESTRATOR_DRY_RUN=true
export INVOKE_RUN_ECHO=true

inv test_all
```

---

## Development

### Adding New Tasks

Edit `tasks.py`:

```python
from invoke import task

@task
def my_task(c):
    """My custom task description."""
    c.run("echo 'Hello from my task'", pty=False)
```

Then run:

```bash
inv my-task
```

### Running Specific Tests

```bash
# Run specific test file
inv test.unit --verbose  # or: pytest tests/unit/test_specific.py

# Run with coverage
inv test.unit --coverage

# Run integration tests only
inv test.integration
```

### Linting and Formatting

```bash
# Check formatting
inv lint.black

# Auto-fix formatting
inv lint.black --fix

# Fix all auto-fixable issues
inv lint.fix

# Run all linters
inv lint_all
```

---

## CI/CD

### GitHub Actions

Workflows automatically run on push/PR:

- **CI Pipeline** (`.github/workflows/ci.yml`): Runs `inv test_all`
- **Lint** (`.github/workflows/lint.yml`): Runs `inv lint_all`
- **ACMS Pipeline** (`.github/workflows/acms-pipeline.yml`): Nightly ACMS runs

### Local CI Simulation

Run the exact same checks that CI runs:

```bash
inv ci
```

This runs:
1. `inv validate_all` - Validation checks
2. `inv lint_all` - All linters
3. `inv test_all` - All test suites

---

## Troubleshooting

### "Command not found: inv"

Install Invoke:

```bash
pip install invoke
```

### Task fails with "FileNotFoundError"

Ensure you're using the correct shell (PowerShell on Windows):

```yaml
# invoke.yaml (already configured)
run:
  shell: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
  pty: false
```

### Tests fail with import errors

Run bootstrap to set up PYTHONPATH correctly:

```bash
inv bootstrap
```

Or manually:

```bash
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

### Want to see commands before they run

Enable echo in your user config (`~/.invoke.yaml`):

```yaml
run:
  echo: true
```

Or via environment variable:

```bash
export INVOKE_RUN_ECHO=true
```

---

## Documentation

### Comprehensive Guides

- **`INVOKE_QUICK_START.md`** - Complete Invoke usage guide
- **`INVOKE_DOCUMENT_INDEX.md`** - Navigation hub for all docs
- **`INVOKE_VALIDATION_CHECKLIST.md`** - QA testing procedures
- **`INVOKE_IMPLEMENTATION_PROGRESS.md`** - Current status and roadmap
- **`TODO_INVOKE_REMAINING_TASKS.md`** - Remaining work items

### Architecture Documentation

- **`docs/`** - Technical architecture and design docs
- **`config/`** - Configuration schemas and examples

### Getting Help

```bash
# List all tasks
inv --list

# Get help for specific task
inv --help test.unit

# See task source code
cat tasks.py
```

---

## Contributing

### Before Submitting a PR

```bash
# Run full CI suite
inv ci

# Or run steps individually
inv validate_all
inv lint_all
inv test_all
```

### Code Style

- **Formatting**: Black (120 character line length)
- **Import sorting**: isort (black-compatible)
- **Style**: flake8
- **Type hints**: mypy (optional but recommended)

### Commit Guidelines

- Clear, descriptive commit messages
- Reference issue numbers where applicable
- One logical change per commit
- Run `inv ci` before pushing

---

## System Requirements

- **Python**: 3.10 or 3.11
- **OS**: Windows (primary), Linux, macOS (tested)
- **Shell**: PowerShell (Windows), bash (Linux/Mac)
- **Tools**: Git, pytest, black, flake8, mypy, isort

---

## License

[Add your license here]

---

## Contact

[Add contact information here]

---

## Acknowledgments

Built with:
- **Invoke** - Python task execution (https://www.pyinvoke.org/)
- **pytest** - Testing framework
- **GitHub Actions** - CI/CD automation
- **Various AI providers** - OpenAI, Anthropic, GitHub Copilot CLI

---

**Quick Reference**:

```bash
inv --list          # Discover all tasks
inv bootstrap       # One-command setup
inv validate_all    # Validate environment
inv test_all        # Run all tests
inv lint_all        # Run all linters
inv ci              # Full CI suite
inv --help <task>   # Get help for any task
```

For detailed documentation, see **`INVOKE_QUICK_START.md`** and **`INVOKE_DOCUMENT_INDEX.md`**.
