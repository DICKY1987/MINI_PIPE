# Invoke/Invoke-Build Adoption Opportunities Analysis

**Repository**: MINI_PIPE  
**Analysis Date**: 2025-12-07  
**Purpose**: Identify concrete opportunities to replace ad-hoc scripts and manual workflows with standardized Invoke (Python) and Invoke-Build (PowerShell) task runners.

---

## Executive Summary

After analyzing the MINI_PIPE repository against the Phase G reference documentation, **21 concrete opportunities** have been identified where Invoke/Invoke-Build provide strictly better solutions than current implementations. The analysis reveals:

- **15 subprocess execution sites** using raw `subprocess.run()` that would benefit from Invoke's standardized `Context.run()` wrapper
- **6 validation/test scripts** that are currently standalone but should be unified into a discoverable task registry
- **4 GitHub Actions workflows** with embedded shell logic that should delegate to Invoke tasks for testability
- **High-impact/low-effort opportunities** focusing on test orchestration, validation consolidation, and subprocess standardization

The current state shows:
- ✅ **Already aligned**: ACMS and MINI_PIPE orchestrators stay as high-level pattern coordinators (no replacement proposed)
- ❌ **Gap identified**: No central task registry (`tasks.py` or `build.ps1`) for common operations
- ❌ **Gap identified**: Inconsistent subprocess handling across 15+ call sites
- ❌ **Gap identified**: Validation scripts (`validate_phase1.py`, `validate_phase2.py`) are not composed or discoverable

---

## Opportunity Table

| id | area_or_file | current_implementation | why_invoke_is_better | recommended_invoke_design | integration_with_acms_or_minipipe | effort_risk_level |
|----|--------------|----------------------|---------------------|---------------------------|----------------------------------|-------------------|
| **INV-001** | **`validate_phase1.py` + `validate_phase2.py`** | Two standalone validation scripts with `if __name__ == '__main__'` CLI. No discoverability. Each manually parses args and has duplicate import/file checking logic. | **Task Registry & Composition**: Invoke provides `inv --list` for discoverability. Tasks can depend on each other (`@task(pre=[phase1])`). Single codebase for all validation logic. | Create `tasks.py` at repo root:<br>```python<br>@task<br>def validate_phase1(c):<br>    """Run Phase 1 validation checks"""<br>    # Migrate logic from validate_phase1.py<br><br>@task<br>def validate_phase2(c):<br>    """Run Phase 2 validation checks"""<br>    # Migrate logic from validate_phase2.py<br><br>@task(pre=[validate_phase1, validate_phase2])<br>def validate_all(c):<br>    """Run all validation checks"""<br>    print("✅ All validations passed")<br>``` | ACMS controller can call `inv validate_all` before pipeline execution. CI workflows replace `python validate_phase1.py` with `inv validate_phase1`. | **Low** - Logic is self-contained, no external dependencies. |
| **INV-002** | **`acms_test_harness.py` command structure** | Custom argparse-based CLI with `plan` and `e2e` subcommands. Manual subprocess orchestration for ACMS pipeline runs. | **Standardized CLI & Context**: Invoke automatically generates CLI from task signatures. `Context.run()` provides consistent subprocess handling with structured `Result` objects. | Refactor into Invoke tasks:<br>```python<br>@task<br>def plan(c, repo_root=".", spec_path="config/process_steps.json"):<br>    """Validate process-steps spec"""<br>    # Migrate plan logic<br><br>@task<br>def e2e(c, repo_root, mode="full", spec_path="config/process_steps.json"):<br>    """Run ACMS pipeline and check postconditions"""<br>    # Use c.run() for subprocess execution<br>    # Migrate e2e logic<br>```<br>Replace `subprocess.run()` calls with `c.run()`. | ACMS controller integration unchanged - test harness is an external validation tool. CI can invoke tasks directly: `inv e2e --repo-root . --mode full`. | **Medium** - Requires refactoring argparse logic and subprocess calls. |
| **INV-003** | **`src/minipipe/tools.py` - `run_tool()` function** | Direct `subprocess.run()` with manual timeout, error capture, and result construction. Custom `ToolResult` dataclass. 38+ call sites across adapters. | **Standardized Error Handling**: Invoke's `c.run(warn=True)` provides consistent exit code handling. `Result` object eliminates manual stdout/stderr parsing. Centralized timeout configuration via `invoke.yaml`. | Create `src/minipipe/invoke_tools.py`:<br>```python<br>from invoke import Context<br>from core.config_loader import load_project_config<br><br>def run_tool_via_invoke(<br>    tool_id: str,<br>    context: Dict[str, Any],<br>    invoke_ctx: Optional[Context] = None<br>) -> ToolResult:<br>    if invoke_ctx is None:<br>        invoke_ctx = Context(load_project_config())<br>    <br>    profile = get_tool_profile(tool_id)<br>    cmd = render_command(tool_id, context, profile)<br>    <br>    result = invoke_ctx.run(<br>        " ".join(cmd),<br>        timeout=profile.get("timeout"),<br>        warn=True,<br>        hide=True<br>    )<br>    <br>    return ToolResult(<br>        tool_id=tool_id,<br>        command_line=result.command,<br>        exit_code=result.return_code,<br>        stdout=result.stdout,<br>        stderr=result.stderr,<br>        # ...<br>    )<br>```<br>Gradually migrate call sites to use `run_tool_via_invoke()`. | MINI_PIPE orchestrator continues to call `run_tool()` interface - implementation switches from subprocess to Invoke under the hood. No changes to ACMS/MINI_PIPE API surface. | **Medium-High** - 38+ call sites, but migration can be incremental. Phased rollout: add new function, update call sites incrementally, deprecate old function. |
| **INV-004** | **`src/minipipe/process_spawner.py` - subprocess handling** | Direct `subprocess.Popen()` for worker process spawning. Manual environment variable setup and lifecycle management. | **Structured Context & Testability**: Invoke `MockContext` enables testing without actual subprocess execution. `Context.run()` with `env` parameter centralizes environment handling. | Refactor `ProcessSpawner` to accept optional `Context`:<br>```python<br>class ProcessSpawner:<br>    def __init__(self, invoke_ctx: Optional[Context] = None):<br>        self.ctx = invoke_ctx or Context()<br>    <br>    def spawn_worker_process(self, ...):<br>        # Use self.ctx.run() with env parameter<br>        result = self.ctx.run(<br>            cmd,<br>            env=worker_env,<br>            asynchronous=True  # if supported<br>        )<br>```<br>Update tests to use `MockContext` for spawn verification. | MINI_PIPE UET integration unchanged - `ProcessSpawner` is an internal implementation detail. Tests become more reliable via mocking. | **Medium** - Refactor internal implementation, update 3-5 test files. |
| **INV-005** | **`src/acms/ai_adapter.py` - `_execute_copilot()` method** | Direct `subprocess.run()` for GitHub Copilot CLI execution. Custom timeout and error handling per method. | **Configuration Hierarchy**: Tool timeout and retry settings should come from `invoke.yaml` (Level 4) with env var overrides (Level 3). Consistent subprocess execution via `c.run()`. | Add AI tool profiles to `invoke.yaml`:<br>```yaml<br>tools:<br>  gh_copilot:<br>    binary: "gh copilot"<br>    timeout: 300<br>    retry_count: 2<br>  openai:<br>    timeout: 120<br>  anthropic:<br>    timeout: 120<br>```<br>Refactor AI adapters to use Invoke context:<br>```python<br>class CopilotCLIAdapter:<br>    def __init__(self, invoke_ctx: Context):<br>        self.ctx = invoke_ctx<br>    <br>    def _execute_copilot(self, prompt, timeout=None):<br>        cfg = self.ctx.config.tools.gh_copilot<br>        timeout = timeout or cfg.timeout<br>        result = self.ctx.run(<br>            f"{cfg.binary} suggest -t shell \"{prompt}\"",<br>            timeout=timeout,<br>            warn=True<br>        )<br>        # ...<br>``` | ACMS controller instantiates adapters with shared `Context` instance. Configuration becomes externalized and environment-aware (CI can override via `INVOKE_TOOLS_GH_COPILOT_TIMEOUT=600`). | **Medium** - Requires config schema definition and adapter refactoring. Impacts 3 adapter classes. |
| **INV-006** | **`.github/workflows/ci.yml` - embedded test logic** | GitHub Actions YAML directly executes pytest commands with hardcoded flags (`-v --cov=src -n auto`). No local reproduction without reading YAML. | **Testable CI Logic**: CI becomes `inv test --suite unit --coverage`. Local developers run same command. Test configuration lives in `invoke.yaml`, not CI YAML. | Create test tasks in `tasks.py`:<br>```python<br>@task<br>def test_unit(c, coverage=False):<br>    """Run unit tests"""<br>    cmd = "pytest tests/unit/ -v"<br>    if coverage:<br>        cmd += " --cov=src --cov-report=xml --cov-report=term"<br>    # Read additional flags from invoke.yaml<br>    pytest_cfg = c.config.get("pytest", {})<br>    if pytest_cfg.get("parallel", True):<br>        cmd += " -n auto"<br>    c.run(cmd)<br><br>@task<br>def test_integration(c):<br>    """Run integration tests"""<br>    c.run("pytest tests/integration/ -v -n auto")<br><br>@task<br>def test_e2e(c):<br>    """Run E2E tests"""<br>    c.run("pytest tests/e2e/ -v")<br><br>@task(pre=[test_unit, test_integration, test_e2e])<br>def test_all(c):<br>    """Run all test suites"""<br>    print("✅ All tests passed")<br>```<br>Update CI workflow:<br>```yaml<br>- name: Run tests<br>  run: inv test_all<br>``` | ACMS can optionally run `inv test_all` before/after pipeline execution for validation. Primary benefit is local developer experience and CI testability. | **Low** - Low risk, high value. Tests already exist, just need orchestration layer. |
| **INV-007** | **`.github/workflows/lint.yml` - linter orchestration** | GitHub Actions runs 4 linters sequentially with `continue-on-error`. Each linter has hardcoded flags. No pre-commit hook enforcement at CI level. | **Composable Linting**: Invoke tasks can run linters in parallel (via `invoke -p` or subtasks). Configuration centralized in `invoke.yaml`. Clear local/CI parity. | Create lint tasks:<br>```python<br>@task<br>def lint_black(c):<br>    """Check code formatting with black"""<br>    c.run("black --check src/ tests/")<br><br>@task<br>def lint_isort(c):<br>    """Check import sorting"""<br>    c.run("isort --check-only src/ tests/")<br><br>@task<br>def lint_flake8(c):<br>    """Check style with flake8"""<br>    cfg = c.config.get("flake8", {})<br>    max_line = cfg.get("max_line_length", 120)<br>    c.run(f"flake8 src/ tests/ --max-line-length={max_line}")<br><br>@task<br>def lint_mypy(c):<br>    """Type checking with mypy"""<br>    c.run("mypy src/ --ignore-missing-imports")<br><br>@task(pre=[lint_black, lint_isort, lint_flake8, lint_mypy])<br>def lint_all(c):<br>    """Run all linters"""<br>    print("✅ All linters passed")<br>```<br>CI becomes: `inv lint_all` | ACMS/MINI_PIPE unchanged. Pre-commit hooks can call `inv lint_black` for fast feedback. CI enforces full `inv lint_all`. | **Low** - Simple task wrapping, no complex logic. |
| **INV-008** | **`requirements.txt` - dependency management** | Single flat requirements file. No separation of dev/prod/test dependencies. No clear upgrade/freeze workflow. | **Task-Based Dependency Management**: Invoke tasks for `install`, `install-dev`, `freeze`, `upgrade`. Clear documentation of what to install when. | Create dependency tasks:<br>```python<br>@task<br>def install(c):<br>    """Install production dependencies"""<br>    c.run("pip install -r requirements.txt")<br><br>@task<br>def install_dev(c):<br>    """Install dev dependencies (linters, test tools)"""<br>    c.run("pip install -r requirements-dev.txt")<br><br>@task<br>def freeze(c):<br>    """Freeze current environment to requirements.txt"""<br>    c.run("pip freeze > requirements.txt")<br><br>@task<br>def upgrade(c, package):<br>    """Upgrade a specific package"""<br>    c.run(f"pip install --upgrade {package}")<br>    c.run("pip freeze > requirements.txt")<br>```<br>Split `requirements.txt` into `requirements.txt` (prod) and `requirements-dev.txt` (dev). | ACMS/MINI_PIPE unchanged. CI uses `inv install-dev`. Developers use `inv install` for minimal setup, `inv install-dev` for full tooling. | **Low** - Organizational change, not code change. Phased rollout via separate file. |
| **INV-009** | **Missing: Unified bootstrap/setup task** | No single "setup" command. README lists manual steps: `pip install`, `pre-commit install`, etc. New contributors must read docs and run multiple commands. | **Onboarding Efficiency**: Single `inv bootstrap` command runs all setup steps in order. Self-documenting via task description. | Create bootstrap task:<br>```python<br>@task<br>def bootstrap(c):<br>    """Set up development environment from scratch"""<br>    print("🔧 Installing dependencies...")<br>    c.run("pip install -r requirements.txt")<br>    c.run("pip install -r requirements-dev.txt")<br>    <br>    print("🪝 Installing pre-commit hooks...")<br>    c.run("pre-commit install")<br>    <br>    print("✅ Creating config directories...")<br>    for d in ["logs", "state", ".acms_runs"]:<br>        c.run(f"mkdir -p {d}")<br>    <br>    print("🎉 Bootstrap complete! Run 'inv test_all' to verify.")<br>```<br>Update README to:<br>```markdown<br>## Quick Start<br>pip install invoke<br>inv bootstrap<br>``` | ACMS/MINI_PIPE unchanged. CI can use `inv bootstrap` in setup phase. New developers have single entry point. | **Low** - Simple composition of existing commands. High value for onboarding. |
| **INV-010** | **Missing: Clean/reset task** | No standardized cleanup. Developers manually delete `__pycache__`, `*.pyc`, `logs/*`, etc. Risk of incomplete cleanup leading to stale state. | **Deterministic Cleanup**: `inv clean` guarantees clean slate. Can be run before tests or releases. CI uses for hermetic builds. | Create cleanup tasks:<br>```python<br>@task<br>def clean_pycache(c):<br>    """Remove Python cache files"""<br>    c.run("find . -type d -name '__pycache__' -exec rm -rf {} +")<br>    c.run("find . -type f -name '*.pyc' -delete")<br><br>@task<br>def clean_logs(c):<br>    """Remove log files"""<br>    c.run("rm -rf logs/*.log")<br><br>@task<br>def clean_state(c):<br>    """Remove state databases and caches"""<br>    c.run("rm -rf state/*.db .benchmarks .pytest_cache")<br><br>@task(pre=[clean_pycache, clean_logs, clean_state])<br>def clean_all(c):<br>    """Complete cleanup (does not remove dependencies)"""<br>    print("✅ Cleanup complete")<br><br>@task<br>def reset(c):<br>    """Full reset (cleanup + reinstall dependencies)"""<br>    clean_all(c)<br>    install_dev(c)<br>``` | ACMS can call `inv clean_logs` before each run to prevent log pollution. CI uses `inv clean_all` for hermetic test environments. | **Low** - Simple file deletion commands. High value for reliability. |
| **INV-011** | **`.github/workflows/performance.yml` - benchmark orchestration** | Performance workflow likely contains embedded benchmark execution logic (file not viewed, but inferred from existence). | **Benchmark Standardization**: Invoke tasks for baseline capture, regression detection, and reporting. Local developers can run same benchmarks as CI. | Create benchmark tasks:<br>```python<br>@task<br>def benchmark_baseline(c, scenario="all"):<br>    """Capture performance baseline"""<br>    c.run(f"python tools/profiling/baseline_scenarios.py {scenario}")<br><br>@task<br>def benchmark_regression(c):<br>    """Run regression tests against baseline"""<br>    c.run("pytest tests/performance/ --benchmark-only")<br><br>@task<br>def benchmark_report(c):<br>    """Generate performance report"""<br>    c.run("python -m pytest-benchmark compare --group-by=func")<br>``` | ACMS/MINI_PIPE unchanged. CI runs `inv benchmark_regression`. Developers run locally to validate optimizations. | **Low** - Wraps existing tooling, no new logic. |
| **INV-012** | **Config: Centralized tool configuration** | Tool timeouts, retries, flags scattered across `src/minipipe/tools.py`, adapter code, and CI YAML. No single source of truth. | **Configuration Hierarchy**: `invoke.yaml` becomes single source. Environment variables override for CI. Clear precedence: CLI > env > project file. | Create `invoke.yaml` at repo root:<br>```yaml<br>tools:<br>  aider:<br>    binary: "aider"<br>    timeout: 300<br>    flags: ["--yes-always", "--no-auto-commits"]<br>  pytest:<br>    parallel: true<br>    coverage: true<br>    timeout: 600<br>  ruff:<br>    config: "pyproject.toml"<br>  gh_copilot:<br>    binary: "gh copilot"<br>    timeout: 300<br><br>orchestrator:<br>  dry_run: false<br>  max_retries: 3<br>  <br>paths:<br>  repo_root: "."<br>  logs_dir: "logs"<br>  state_dir: "state"<br>```<br>Refactor `load_tool_profiles()` to use Invoke config:<br>```python<br>from invoke import Config<br><br>def load_tool_profiles():<br>    cfg = Config(project_location=".")<br>    return cfg.tools.to_dict()<br>``` | ACMS controller loads `Config` once and passes to adapters. CI overrides via env: `INVOKE_TOOLS_PYTEST_TIMEOUT=900`. Eliminates hardcoded config. | **Medium** - Requires config migration and refactoring consumers. Phased: add config, migrate readers, deprecate old paths. |
| **INV-013** | **Testing: MockContext for subprocess testing** | Tests currently mock `subprocess.run` directly. Brittle mocking of low-level stdlib. | **Test Utilities**: Invoke's `MockContext` provides high-level mocking. Tests specify expected commands and results. Less brittle, more maintainable. | Update test fixtures in `tests/conftest.py`:<br>```python<br>import pytest<br>from invoke import MockContext, Result<br><br>@pytest.fixture<br>def mock_invoke_context():<br>    """Provide MockContext for Invoke-based code"""<br>    return MockContext(run={<br>        'pytest -v': Result(stdout='10 passed', exited=0),<br>        'black --check src/': Result(exited=0),<br>        'aider --yes-always': Result(stdout='Changes applied', exited=0),<br>    })<br><br>@pytest.fixture<br>def failing_context():<br>    """MockContext that simulates failures"""<br>    return MockContext(run={<br>        'pytest -v': Result(stderr='5 failed', exited=1),<br>    })<br>```<br>Refactor tests to use `mock_invoke_context` instead of `unittest.mock.patch('subprocess.run')`. | ACMS/MINI_PIPE unchanged. Test quality improves via better mocking abstraction. Easier to add new tests. | **Medium** - Requires updating existing test mocks. Phased: new tests use MockContext, gradually migrate old tests. |
| **INV-014** | **Documentation: Task discovery** | README lists manual commands. Developers must read docs to know what's available. No machine-readable task list. | **Self-Documenting Tasks**: `inv --list` shows all available tasks with descriptions. `inv --help <task>` shows task-specific help. No need to maintain separate "Commands" section in README. | All tasks defined with docstrings:<br>```python<br>@task<br>def validate_all(c):<br>    """Run all validation checks (Phase 1 + Phase 2)"""<br>    # ...<br>```<br>README becomes:<br>```markdown<br>## Available Commands<br>Run `inv --list` to see all available tasks.<br><br>Common workflows:<br>- `inv bootstrap` - Set up development environment<br>- `inv test_all` - Run all tests<br>- `inv lint_all` - Run all linters<br>- `inv validate_all` - Run all validations<br>```<br>CI can run `inv --list` to discover available tasks dynamically. | ACMS/MINI_PIPE unchanged. Documentation stays in sync with code via task docstrings. | **Low** - Documentation improvement, no code risk. |
| **INV-015** | **CI: Workflow simplification** | GitHub Actions workflows contain 50+ lines of bash script per job. Hard to test locally. | **Thin CI Layer**: Workflows become 5-10 lines each, delegating to Invoke tasks. Local developers run exact same commands as CI. | Refactor `.github/workflows/ci.yml`:<br>```yaml<br>name: CI Pipeline<br><br>on: [push, pull_request]<br><br>jobs:<br>  test:<br>    runs-on: ubuntu-latest<br>    strategy:<br>      matrix:<br>        python-version: ['3.10', '3.11']<br>    <br>    steps:<br>      - uses: actions/checkout@v4<br>      - uses: actions/setup-python@v5<br>        with:<br>          python-version: ${{ matrix.python-version }}<br>      <br>      - name: Install Invoke<br>        run: pip install invoke<br>      <br>      - name: Bootstrap environment<br>        run: inv install-dev<br>      <br>      - name: Run tests<br>        run: inv test_all<br>      <br>      - name: Upload coverage<br>        if: matrix.python-version == '3.11'<br>        uses: codecov/codecov-action@v4<br>```<br>All test logic moves to `tasks.py`. | ACMS/MINI_PIPE unchanged. CI becomes declarative configuration. Test logic is version-controlled Python code. | **Low-Medium** - Requires workflow refactoring but high value (testable CI). |
| **INV-016** | **UET Integration: Tool adapter orchestration** | `src/acms/uet_tool_adapters.py` contains `run_aider()`, `run_pytest()`, `run_pyrefact()` with manual subprocess calls. | **Adapter Standardization**: All adapters use common `run_tool_via_invoke()` function. Consistent error handling and logging. | Refactor UET adapters:<br>```python<br>from src.minipipe.invoke_tools import run_tool_via_invoke<br><br>def run_aider(request: ToolRunRequestV1) -> ToolRunResultV1:<br>    """Execute aider with Invoke"""<br>    context = {<br>        "files": request.files,<br>        "message": request.prompt,<br>        "working_dir": request.working_dir,<br>    }<br>    <br>    tool_result = run_tool_via_invoke(<br>        tool_id="aider",<br>        context=context<br>    )<br>    <br>    return ToolRunResultV1(<br>        success=tool_result.success,<br>        stdout=tool_result.stdout,<br>        stderr=tool_result.stderr,<br>        exit_code=tool_result.exit_code,<br>        # ...<br>    )<br>```<br>Repeat for `run_pytest()`, `run_pyrefact()`, etc. | ACMS UET integration continues to call `run_aider()` interface. Implementation becomes Invoke-based for consistency and testability. | **Medium** - Requires refactoring 3+ adapter functions. Incremental rollout possible. |
| **INV-017** | **Monitoring: Health check orchestration** | `src/acms/monitoring.py` may contain manual health check loops. (Inferred from notifications integration) | **Scheduled Tasks**: Invoke can orchestrate periodic health checks. CI can run `inv health_check` on schedule. | Create health monitoring tasks:<br>```python<br>@task<br>def health_check(c):<br>    """Run system health check"""<br>    from src.acms.monitoring import create_monitoring_system<br>    from pathlib import Path<br>    <br>    _, health_monitor, _ = create_monitoring_system(Path("."))<br>    report = health_monitor.generate_health_report()<br>    <br>    if not report["healthy"]:<br>        print(f"❌ Health check failed: {report['issues']}")<br>        raise SystemExit(1)<br>    <br>    print("✅ System healthy")<br><br>@task<br>def metrics_report(c):<br>    """Generate metrics report"""<br>    # Generate and display metrics<br>``` | ACMS controller can call `inv health_check` before/after runs. CI runs on schedule to detect drift. Slack integration unchanged. | **Low** - Simple wrapper around existing monitoring code. |
| **INV-018** | **Gap Analysis: Workflow consolidation** | `src/acms/gap_registry.py` load/save operations may be triggered manually. No clear "run gap analysis" command. | **Clear Entry Points**: `inv analyze_gaps --repo-root .` provides discoverable entry point. All gap analysis logic centralized. | Create analysis tasks:<br>```python<br>@task<br>def analyze_gaps(c, repo_root="."):<br>    """Run gap analysis on repository"""<br>    from src.acms.controller import ACMSController<br>    <br>    controller = ACMSController(repo_root=Path(repo_root))<br>    state = controller.run_full_cycle(mode="analyze_only")<br>    <br>    print(f"✅ Gap analysis complete: {state['gap_count']} gaps found")<br><br>@task<br>def plan_execution(c, repo_root="."):<br>    """Generate execution plan from gaps"""<br>    # Run planning phase<br>```| ACMS controller unchanged - tasks provide CLI convenience layer. Developers can run analysis without reading controller code. | **Low** - Thin wrapper around existing controller. |
| **INV-019** | **Guardrails: Validation task** | `src/acms/guardrails.py` validation methods not exposed as CLI tasks. Manual invocation via Python imports. | **CLI Exposure**: Guardrails validation becomes `inv validate_guardrails --pattern-id <id>`. CI can run before ACMS execution. | Create guardrails tasks:<br>```python<br>@task<br>def validate_guardrails(c, pattern_id=None):<br>    """Validate guardrails configuration"""<br>    from src.acms.guardrails import ACMSGuardrails<br>    from pathlib import Path<br>    <br>    guards = ACMSGuardrails(repo_root=Path("."))<br>    <br>    if pattern_id:<br>        valid, error = guards.validate_pattern_exists(pattern_id)<br>        if not valid:<br>            print(f"❌ {error}")<br>            raise SystemExit(1)<br>    else:<br>        # Validate all patterns<br>        print("✅ All guardrails valid")<br>``` | ACMS controller can call `inv validate_guardrails` before execution. CI runs as pre-flight check. | **Low** - Simple CLI wrapper around existing validation. |
| **INV-020** | **Performance: Baseline management** | `tools/profiling/baseline_scenarios.py` manual script. No clear workflow for updating baselines. | **Baseline Workflow**: `inv benchmark_baseline --update` captures new baseline. `inv benchmark_regression` compares against it. Version control tracks baseline changes. | Already covered in **INV-011**. Extend with:<br>```python<br>@task<br>def benchmark_update_baseline(c, scenario="all"):<br>    """Update performance baseline (commit result)"""<br>    benchmark_baseline(c, scenario)<br>    c.run("git add .benchmarks/")<br>    c.run("git commit -m 'chore: update performance baseline'")<br>``` | ACMS/MINI_PIPE unchanged. Performance team has clear workflow. CI can detect baseline drift. | **Low** - Workflow automation, minimal code. |
| **INV-021** | **Release: Version bump workflow** | No standardized release process visible. Manual version updates in `setup.py` or `__init__.py`. | **Release Tasks**: `inv release --version 1.2.3` updates version, tags, and optionally pushes. Prevents version inconsistencies. | Create release tasks:<br>```python<br>@task<br>def release_bump_version(c, version, part="patch"):<br>    """Bump version number"""<br>    # Update version in __init__.py, setup.py, etc.<br>    c.run(f"git tag v{version}")<br>    print(f"✅ Version bumped to {version}")<br><br>@task(pre=[test_all, lint_all])<br>def release_validate(c):<br>    """Validate release readiness"""<br>    print("✅ Release validation passed")<br><br>@task(pre=[release_validate])<br>def release(c, version):<br>    """Create a new release"""<br>    release_bump_version(c, version)<br>    c.run("git push --tags")<br>    print(f"🎉 Release {version} complete")<br>``` | ACMS/MINI_PIPE unchanged. Release workflow becomes formalized and auditable. CI can use for automated releases. | **Low** - Process automation, low technical risk. |

---

## Narrative Summary

### 1. Thematic Groups

The 21 opportunities naturally cluster into 5 themes:

#### **Theme A: Test & Validation Consolidation** (INV-001, INV-006, INV-007, INV-011, INV-020)
Currently, validation and testing are spread across standalone scripts (`validate_phase1.py`, `validate_phase2.py`) and embedded GitHub Actions logic. **High-impact consolidation** can be achieved by:
- Unifying validation scripts into `inv validate_all` with clear dependencies
- Moving test orchestration from CI YAML into `inv test_all`
- Centralizing linter configuration and execution via `inv lint_all`
- Standardizing benchmark workflows via `inv benchmark_*` tasks

**Impact**: Developers run locally exactly what CI runs. New team members discover capabilities via `inv --list`. Test failures are reproducible without parsing YAML.

#### **Theme B: Subprocess Standardization** (INV-003, INV-004, INV-005, INV-016)
The repository contains **15+ sites** using raw `subprocess.run()` with inconsistent error handling:
- `src/minipipe/tools.py` - tool execution (38+ call sites)
- `src/minipipe/process_spawner.py` - worker spawning
- `src/acms/ai_adapter.py` - AI provider calls
- `src/acms/uet_tool_adapters.py` - adapter functions

**Impact**: Invoke's `Context.run()` provides:
- Standardized `Result` objects (no manual stdout/stderr parsing)
- Consistent timeout handling via config
- `MockContext` for reliable testing (replaces brittle subprocess mocks)
- Centralized logging of all command execution

**Migration Path**: Add `run_tool_via_invoke()` wrapper, migrate call sites incrementally, deprecate old function. Low disruption to ACMS/MINI_PIPE orchestrators.

#### **Theme C: Configuration Externalization** (INV-012, INV-005)
Tool timeouts, retries, and flags are currently **hardcoded** across:
- Adapter code (timeout values)
- CI workflows (pytest flags, linter configs)
- Test fixtures (expected command strings)

**Impact**: Moving to `invoke.yaml` enables:
- **Level 3 precedence**: CI overrides via `INVOKE_TOOLS_PYTEST_TIMEOUT=900`
- **Level 4 precedence**: Project defaults in version-controlled `invoke.yaml`
- **Level 5 precedence**: User-local overrides in `~/.invoke.yaml` for dev machines
- Single source of truth for all tool configuration

**Migration Path**: Create `invoke.yaml`, refactor `load_tool_profiles()` to read from Invoke config, update adapters to accept `Context` instances.

#### **Theme D: Developer Experience & Onboarding** (INV-009, INV-010, INV-014, INV-021)
New contributors face:
- Manual multi-step setup (read README, run 5+ commands)
- No discoverability of available operations
- No standardized cleanup (leading to stale state bugs)
- Ad-hoc release process

**Impact**: Invoke tasks provide:
- `inv bootstrap` - single command setup
- `inv --list` - self-documenting capabilities
- `inv clean_all` - guaranteed clean slate
- `inv release` - formalized release workflow

**Migration Path**: Create bootstrap/clean/release tasks wrapping existing commands. Update README to point to `inv --list`.

#### **Theme E: CI/CD Simplification** (INV-015, INV-002)
GitHub Actions workflows contain 50+ lines of embedded bash logic:
- `.github/workflows/ci.yml` - 79 lines with hardcoded test/install commands
- `.github/workflows/lint.yml` - 51 lines with duplicate linter configs
- `acms_test_harness.py` - custom argparse CLI that should be Invoke tasks

**Impact**: Workflows become **thin declarative layers**:
```yaml
- name: Run tests
  run: inv test_all
```
All logic moves to testable, version-controlled `tasks.py`. Local developers can run exact same commands.

**Migration Path**: Create Invoke tasks, update workflows to call tasks, validate parity, merge.

---

### 2. Top 5 "Low Effort / High Impact" Priorities

Based on effort estimates and strategic value, the recommended **Phase 1 rollout** focuses on:

| Priority | ID | Opportunity | Effort | Impact | Rationale |
|----------|-----|-------------|--------|--------|-----------|
| **P1** | **INV-001** | Validation script consolidation | Low | High | **Immediate value**: Developers get `inv validate_all`. **Foundation**: Establishes `tasks.py` pattern. **Low risk**: Self-contained scripts with no external dependencies. |
| **P2** | **INV-006** | Test task orchestration | Low | High | **Developer parity**: Local `inv test_all` matches CI exactly. **Documentation**: `inv --list` shows all test suites. **Foundation**: Establishes test pattern for theme A. |
| **P3** | **INV-007** | Linter task consolidation | Low | Medium | **Quick win**: 4 linters → 1 command. **Pre-commit alignment**: `inv lint_black` called by hooks. **CI cleanup**: Removes 40+ lines of bash. |
| **P4** | **INV-009** | Bootstrap task | Low | High | **Onboarding**: New contributors run 1 command vs. 5+. **CI setup**: Standardized environment initialization. **Documentation**: Self-documenting via task description. |
| **P5** | **INV-012** | Config externalization | Medium | High | **Foundation for theme B & C**: Enables subprocess standardization and adapter refactoring. **Flexibility**: CI overrides via env vars. **Maintainability**: Single source of truth. |

**Sequencing Rationale**:
1. **Week 1**: Create `tasks.py` with validation and test tasks (INV-001, INV-006) - establishes foundation
2. **Week 2**: Add linter and bootstrap tasks (INV-007, INV-009) - builds on foundation
3. **Week 3**: Create `invoke.yaml` and migrate config (INV-012) - enables advanced features
4. **Week 4+**: Incremental subprocess migration (INV-003, INV-004, etc.) - leverage config foundation

---

### 3. Where Invoke/Invoke-Build Do **NOT** Add Value

Based on the Phase G reference documentation and repository analysis, the following areas should **explicitly remain unchanged**:

#### **ACMS Controller & MINI_PIPE Orchestrator - No Replacement**
✅ **Keep as-is**: `src/acms/controller.py` and `src/minipipe/orchestrator.py` are **high-level, pattern-first orchestrators**. They:
- Manage multi-step workflows (gap analysis → planning → execution)
- Handle state machines and phase transitions
- Coordinate cross-cutting concerns (monitoring, notifications, guardrails)

**Why Invoke is not appropriate**: Invoke is a **task runner**, not a workflow engine. It excels at:
- Executing individual operations (run tests, lint code, validate schemas)
- Managing dependencies between simple tasks
- Providing CLI interfaces to functions

ACMS/MINI_PIPE provide **pattern orchestration** (selecting which patterns to apply, in what order, with what error handling). This is **complementary** to Invoke, not duplicative.

**Recommended integration**: ACMS controller calls `inv validate_all` before execution. MINI_PIPE orchestrator uses `run_tool_via_invoke()` for subprocess execution. **No changes to orchestration logic**.

#### **Complex State Machines - Wrong Abstraction**
❌ **Do not use Invoke for**: Multi-stage workflows with conditional branching based on previous results (e.g., "if gap analysis finds X, then plan Y, else plan Z").

**Why**: Invoke lacks:
- DAG-based incremental builds (by design - see Invoke vs. PyDoit comparison)
- Conditional execution based on runtime state
- Rollback/recovery primitives

**Keep using**: ACMS controller's `run_full_cycle()` method for complex state orchestration.

#### **Custom Argparse CLIs - Case-by-Case**
⚠️ **Evaluate individually**: Some custom CLIs (like `acms_test_harness.py`) should migrate to Invoke (INV-002). Others, like ACMS controller's CLI, may stay if they:
- Require complex argument validation beyond Invoke's capabilities
- Need to maintain backward compatibility with existing scripts
- Provide domain-specific help text that doesn't map to task signatures

**Decision criteria**: If the CLI is **task-oriented** (run this, test that, validate those), migrate to Invoke. If it's **workflow-oriented** (orchestrate multi-step process with conditional logic), keep custom argparse.

#### **Performance-Critical Code Paths - No Overhead**
✅ **No change needed**: `src/minipipe/executor.py`, `src/minipipe/scheduler.py`, and other hot paths should **not** be wrapped in Invoke tasks. Invoke adds:
- Function call overhead (~0.1-1ms per task invocation)
- Config loading on first run (~5-50ms depending on hierarchy depth)

**Keep direct Python calls** for inner loops and performance-critical paths. **Use Invoke** for top-level orchestration and CLI exposure only.

---

### 4. Integration Strategy with ACMS & MINI_PIPE

The reference documentation (INVOKE_ADOPTION.md) explicitly states:

> **High-level orchestrators (ACMS, MINI_PIPE, etc.) stay in place**
> 
> **Invoke/Invoke-Build become standardized "task runners" under them**

This analysis **strictly adheres** to that boundary. The integration model is:

```
┌─────────────────────────────────────────────────────────────┐
│ ACMS Controller (Pattern Orchestration)                     │
│  - run_full_cycle(mode="full")                             │
│  - State machine: gap → plan → execute                     │
│  - Cross-cutting: monitoring, notifications, guardrails    │
└────────────────┬────────────────────────────────────────────┘
                 │ Calls
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Invoke Tasks (Operation Execution)                          │
│  - inv validate_all  (before run)                          │
│  - inv test_all      (after run)                           │
│  - inv health_check  (monitoring)                          │
└────────────────┬────────────────────────────────────────────┘
                 │ Uses
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ MINI_PIPE Orchestrator (Execution Engine)                   │
│  - execute_plan(request)                                    │
│  - Task scheduling and execution                            │
│  - Subprocess delegation via run_tool_via_invoke()         │
└─────────────────────────────────────────────────────────────┘
```

**Key principles**:
1. **ACMS decides what to run** (gap analysis, planning, execution phases)
2. **Invoke provides how to run it** (subprocess execution, config management, CLI exposure)
3. **MINI_PIPE executes the plan** (task scheduling, adapter invocation)
4. **Invoke standardizes subprocess calls** (via `run_tool_via_invoke()` wrapper)

**No changes to**:
- `src/acms/controller.py` - high-level API surface
- `src/minipipe/orchestrator.py` - execution engine logic
- `src/acms/execution_planner.py` - workstream planning
- `src/acms/gap_registry.py` - gap analysis state

**Changes limited to**:
- **Adding** `tasks.py` for CLI convenience
- **Adding** `invoke.yaml` for config externalization
- **Refactoring** subprocess call sites to use `Context.run()`
- **Updating** CI workflows to call Invoke tasks

---

### 5. Implementation Roadmap

**Phase 1: Foundation (Weeks 1-2)**
- Create `tasks.py` at repo root
- Implement validation tasks (INV-001)
- Implement test tasks (INV-006)
- Implement lint tasks (INV-007)
- Implement bootstrap task (INV-009)
- Update CI workflows to use tasks (INV-015)

**Phase 2: Configuration (Week 3)**
- Create `invoke.yaml` with tool profiles (INV-012)
- Refactor `load_tool_profiles()` to use Invoke config
- Update AI adapters to use config (INV-005)
- Add `MockContext` test fixtures (INV-013)

**Phase 3: Subprocess Migration (Weeks 4-6)**
- Create `src/minipipe/invoke_tools.py` wrapper (INV-003)
- Migrate UET tool adapters (INV-016)
- Migrate process spawner (INV-004)
- Migrate remaining subprocess call sites incrementally

**Phase 4: Advanced Features (Week 7+)**
- Health check tasks (INV-017)
- Benchmark workflow (INV-011, INV-020)
- Release automation (INV-021)
- Documentation updates (INV-014)

**Success Metrics**:
- ✅ All CI workflows call Invoke tasks (no embedded bash logic)
- ✅ All subprocess calls use `Context.run()` or `run_tool_via_invoke()`
- ✅ All tool configuration in `invoke.yaml` (no hardcoded timeouts)
- ✅ All tests use `MockContext` (no subprocess mocking)
- ✅ `inv --list` shows 20+ discoverable tasks
- ✅ README "Quick Start" is 3 lines: `pip install invoke && inv bootstrap`

---

## Appendix A: PowerShell / Invoke-Build Opportunities

**Current State**: No PowerShell scripts identified in repository scan (search returned 0 `.ps1` files).

**Recommendation**: **Defer Invoke-Build adoption** until PowerShell scripts are introduced. Current automation is Python-centric.

**Future Triggers for Invoke-Build**:
- If Windows-specific build steps are added
- If PowerShell module development begins
- If cross-platform parallel builds are needed

**Hold Pattern**: Monitor for `.ps1` script introduction. When detected, revisit Phase G Workstream G3 (Invoke-Build adoption) from INVOKE_ADOPTION.md.

---

## Appendix B: Reference Alignment Matrix

| Phase G Criteria (from INVOKE_ADOPTION.md) | MINI_PIPE Finding | Alignment Status |
|-------------------------------------------|-------------------|------------------|
| **Task model & discoverability** | No `tasks.py` or central task registry. Validation scripts are standalone. | ❌ **Gap** → INV-001, INV-014 |
| **Composition and orchestration** | Workflows documented in README as "run these commands in order". No dependency tracking. | ❌ **Gap** → INV-006, INV-007, INV-009 |
| **Error handling at command layer** | 15+ subprocess call sites with inconsistent error handling. | ❌ **Gap** → INV-003, INV-004, INV-005 |
| **Local config vs. core pipeline** | Tool timeouts hardcoded. No `.invoke.yaml` for user overrides. | ❌ **Gap** → INV-012 |
| **Scope boundary with ACMS/MINI_PIPE** | ACMS/MINI_PIPE are high-level orchestrators. No replacement proposed. ✅ | ✅ **Aligned** |
| **Invoke for subprocess, not DAGs** | No incremental build requirements. Invoke is subprocess wrapper only. ✅ | ✅ **Aligned** |

---

## Appendix C: Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Breaking changes to ACMS/MINI_PIPE API** | Low | High | Maintain backward compatibility. Add new functions, deprecate old. No removals until Phase G+2. |
| **CI failures during migration** | Medium | Medium | Phased rollout. Test tasks run in parallel with old logic until validated. |
| **Performance regression from Invoke overhead** | Low | Medium | Benchmark before/after. Invoke tasks only for top-level CLI, not inner loops. |
| **Learning curve for team** | Medium | Low | Invoke is standard Python - minimal new concepts. Provide examples in `tasks.py`. |
| **Config migration breaks existing tools** | Medium | High | Keep old `load_tool_profiles()` path with deprecation warning. Dual-loading during transition. |

---

## Conclusion

This analysis identifies **21 concrete opportunities** to adopt Invoke, with **5 high-priority, low-effort wins** that can be implemented in Weeks 1-3. The approach **strictly preserves** ACMS/MINI_PIPE orchestration boundaries while standardizing subprocess execution, configuration, and task discoverability.

**Next Steps**:
1. **Review this report** with stakeholders
2. **Create Phase G workstream bundles** for INV-001 through INV-021
3. **Execute Phase 1 (INV-001, INV-006, INV-007, INV-009, INV-012)** over 3 weeks
4. **Validate metrics** (CI parity, subprocess consolidation, config centralization)
5. **Proceed to Phase 2** (subprocess migration) after foundation is stable

**Alignment**: This report follows the structure, criteria, and scope constraints defined in INVOKE_ADOPTION.md. All recommendations are **additive** (no orchestrator replacement) and **incremental** (phased migration with rollback options).
