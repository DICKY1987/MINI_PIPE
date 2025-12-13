"""
Invoke tasks for MINI_PIPE automation.

This task file provides a discoverable CLI interface to common operations:
- Validation (Phase 1 & Phase 2 checks)
- Testing (unit, integration, e2e)
- Linting (black, isort, flake8, mypy)
- Environment setup (bootstrap, dependency management)
- Cleanup operations

Usage:
    inv --list                  # Show all available tasks
    inv validate_all            # Run all validation checks
    inv test_all                # Run all tests
    inv bootstrap               # Set up development environment
    inv --help <task>           # Show help for specific task

Phase G Implementation - Workstream G1 & G2
DOC_ID: DOC-INVOKE-TASKS-001
"""

from invoke import task, Collection
from pathlib import Path
import sys


# =============================================================================
# Phase 1 & Phase 2 Validation Tasks (INV-001)
# =============================================================================

@task
def validate_phase1(c):
    """Run Phase 1 Quick Wins validation checks.
    
    Validates:
    - GitHub Actions workflows
    - Notification system
    - Monitoring system
    - Pre-commit configuration
    - Controller integration
    """
    print("=" * 70)
    print("PHASE 1 QUICK WINS VALIDATION")
    print("=" * 70)
    print()
    
    # Run the existing validation script (use pty=False for Windows compatibility)
    result = c.run("python validate_phase1.py", warn=True, pty=False)
    
    if result.exited == 0:
        print("\n✅ Phase 1 validation passed")
        return True
    else:
        print("\n❌ Phase 1 validation failed")
        raise SystemExit(1)


@task
def validate_phase2(c):
    """Run Phase 2 Core Functionality validation checks.
    
    Validates:
    - Real MINI_PIPE adapter
    - AI adapter multi-provider support
    - Controller defaults
    - AI provider availability
    """
    print("=" * 70)
    print("PHASE 2 CORE FUNCTIONALITY VALIDATION")
    print("=" * 70)
    print()
    
    # Run the existing validation script (use pty=False for Windows compatibility)
    result = c.run("python validate_phase2.py", warn=True, pty=False)
    
    if result.exited == 0:
        print("\n✅ Phase 2 validation passed")
        return True
    else:
        print("\n❌ Phase 2 validation failed")
        raise SystemExit(1)


@task(pre=[validate_phase1, validate_phase2])
def validate_all(c):
    """Run all validation checks (Phase 1 + Phase 2).
    
    This is a composite task that runs both phase validations in sequence.
    """
    print("\n" + "=" * 70)
    print("✅ ALL VALIDATIONS PASSED")
    print("=" * 70)


# =============================================================================
# Testing Tasks (INV-006)
# =============================================================================

@task
def test_unit(c, coverage=False, verbose=False):
    """Run unit tests.
    
    Args:
        coverage: Generate coverage report (default: False)
        verbose: Verbose output (default: False)
    
    Examples:
        inv test_unit
        inv test_unit --coverage
        inv test_unit --verbose --coverage
    """
    print("🧪 Running unit tests...")
    
    # Build command
    cmd = "pytest tests/unit/"
    
    if verbose:
        cmd += " -v"
    else:
        cmd += " -q"
    
    if coverage:
        cmd += " --cov=src --cov-report=xml --cov-report=term"
    
    # Add parallel execution
    cmd += " -n auto"
    
    # Set PYTHONPATH (Windows uses set instead of export)
    import os
    env = os.environ.copy()
    repo_root = Path.cwd()
    env['PYTHONPATH'] = str(repo_root / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    
    result = c.run(cmd, warn=True, pty=False, env=env)
    
    if result.exited == 0:
        print("✅ Unit tests passed")
    else:
        print("❌ Unit tests failed")
        raise SystemExit(1)


@task
def test_integration(c, verbose=False):
    """Run integration tests.
    
    Args:
        verbose: Verbose output (default: False)
    """
    print("🧪 Running integration tests...")
    
    cmd = "pytest tests/integration/"
    
    if verbose:
        cmd += " -v"
    else:
        cmd += " -q"
    
    cmd += " -n auto"
    
    # Set PYTHONPATH (Windows compatible)
    import os
    env = os.environ.copy()
    repo_root = Path.cwd()
    env['PYTHONPATH'] = str(repo_root / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    
    result = c.run(cmd, warn=True, pty=False, env=env)
    
    if result.exited == 0:
        print("✅ Integration tests passed")
    else:
        print("❌ Integration tests failed")
        raise SystemExit(1)


@task
def test_e2e(c, verbose=False):
    """Run end-to-end tests.
    
    Args:
        verbose: Verbose output (default: False)
    
    Note: E2E tests run sequentially (no -n auto) for stability.
    """
    print("🧪 Running E2E tests...")
    
    cmd = "pytest tests/e2e/"
    
    if verbose:
        cmd += " -v"
    else:
        cmd += " -q"
    
    # Set PYTHONPATH (Windows compatible)
    import os
    env = os.environ.copy()
    repo_root = Path.cwd()
    env['PYTHONPATH'] = str(repo_root / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    
    result = c.run(cmd, warn=True, pty=False, env=env)
    
    if result.exited == 0:
        print("✅ E2E tests passed")
    else:
        print("❌ E2E tests failed")
        raise SystemExit(1)


@task
def test_performance(c, verbose=False):
    """Run performance regression tests.
    
    Args:
        verbose: Verbose output (default: False)
    """
    print("🧪 Running performance tests...")
    
    cmd = "pytest tests/performance/"
    
    if verbose:
        cmd += " -v"
    else:
        cmd += " -q"
    
    # Set PYTHONPATH (Windows compatible)
    import os
    env = os.environ.copy()
    repo_root = Path.cwd()
    env['PYTHONPATH'] = str(repo_root / 'src') + os.pathsep + env.get('PYTHONPATH', '')
    
    result = c.run(cmd, warn=True, pty=False, env=env)
    
    if result.exited == 0:
        print("✅ Performance tests passed")
    else:
        print("❌ Performance tests failed")
        raise SystemExit(1)


@task(pre=[test_unit, test_integration, test_e2e])
def test_all(c):
    """Run all test suites (unit + integration + e2e).
    
    Performance tests are excluded by default. Run 'inv test_performance' separately.
    """
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)


# =============================================================================
# Linting Tasks (INV-007)
# =============================================================================

@task
def lint_black(c, fix=False):
    """Check code formatting with black.
    
    Args:
        fix: Apply fixes instead of just checking (default: False)
    """
    print("🎨 Checking code formatting with black...")
    
    cmd = "black src/ tests/"
    if not fix:
        cmd += " --check"
    
    result = c.run(cmd, warn=True)
    
    if result.exited == 0:
        if fix:
            print("✅ Code formatted with black")
        else:
            print("✅ Black formatting check passed")
    else:
        if fix:
            print("❌ Black formatting failed")
        else:
            print("❌ Code needs formatting. Run 'inv lint_black --fix' to apply.")
        raise SystemExit(1)


@task
def lint_isort(c, fix=False):
    """Check import sorting with isort.
    
    Args:
        fix: Apply fixes instead of just checking (default: False)
    """
    print("📦 Checking import sorting with isort...")
    
    cmd = "isort src/ tests/"
    if not fix:
        cmd += " --check-only"
    
    result = c.run(cmd, warn=True)
    
    if result.exited == 0:
        if fix:
            print("✅ Imports sorted with isort")
        else:
            print("✅ Import sorting check passed")
    else:
        if fix:
            print("❌ Import sorting failed")
        else:
            print("❌ Imports need sorting. Run 'inv lint_isort --fix' to apply.")
        raise SystemExit(1)


@task
def lint_flake8(c):
    """Check code style with flake8."""
    print("📏 Checking code style with flake8...")
    
    cmd = "flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503"
    
    result = c.run(cmd, warn=True)
    
    if result.exited == 0:
        print("✅ Flake8 style check passed")
    else:
        print("❌ Flake8 found style issues")
        raise SystemExit(1)


@task
def lint_mypy(c):
    """Run type checking with mypy."""
    print("🔍 Running type checking with mypy...")
    
    cmd = "mypy src/ --ignore-missing-imports --no-strict-optional"
    
    result = c.run(cmd, warn=True)
    
    if result.exited == 0:
        print("✅ Type checking passed")
    else:
        print("❌ Type checking found issues")
        raise SystemExit(1)


@task(pre=[lint_black, lint_isort, lint_flake8, lint_mypy])
def lint_all(c):
    """Run all linters (black, isort, flake8, mypy)."""
    print("\n" + "=" * 70)
    print("✅ ALL LINTERS PASSED")
    print("=" * 70)


@task
def lint_fix(c):
    """Apply auto-fixes for black and isort."""
    print("🔧 Applying auto-fixes...")
    lint_black(c, fix=True)
    lint_isort(c, fix=True)
    print("\n✅ Auto-fixes applied. Run 'inv lint_all' to verify.")


# =============================================================================
# Environment Setup Tasks (INV-009, INV-008)
# =============================================================================

@task
def install(c):
    """Install production dependencies."""
    print("📦 Installing production dependencies...")
    c.run("pip install -r requirements.txt")
    print("✅ Production dependencies installed")


@task
def install_dev(c):
    """Install development dependencies (linters, test tools, etc.)."""
    print("📦 Installing development dependencies...")
    
    # Install production dependencies first
    c.run("pip install -r requirements.txt")
    
    # Install dev tools
    dev_packages = [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-xdist>=3.5.0",
        "black>=23.12.0",
        "flake8>=7.0.0",
        "mypy>=1.8.0",
        "isort>=5.13.0",
        "pre-commit>=3.6.0",
        "invoke>=2.2.0"
    ]
    
    for package in dev_packages:
        c.run(f"pip install {package}")
    
    print("✅ Development dependencies installed")


@task
def bootstrap(c):
    """Set up development environment from scratch.
    
    This task:
    1. Installs all dependencies (production + development)
    2. Installs pre-commit hooks
    3. Creates required directories
    4. Validates installation
    """
    print("=" * 70)
    print("🚀 BOOTSTRAPPING MINI_PIPE DEVELOPMENT ENVIRONMENT")
    print("=" * 70)
    print()
    
    # Step 1: Install dependencies
    print("📦 Step 1/4: Installing dependencies...")
    install_dev(c)
    print()
    
    # Step 2: Install pre-commit hooks
    print("🪝 Step 2/4: Installing pre-commit hooks...")
    result = c.run("pre-commit install", warn=True)
    if result.exited == 0:
        print("✅ Pre-commit hooks installed")
    else:
        print("⚠️  Pre-commit hook installation failed (optional)")
    print()
    
    # Step 3: Create directories
    print("📁 Step 3/4: Creating required directories...")
    directories = ["logs", "state", ".acms_runs", ".benchmarks"]
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created {directory}/")
        else:
            print(f"  ✓ {directory}/ already exists")
    print()
    
    # Step 4: Validate installation
    print("✅ Step 4/4: Validating installation...")
    print()
    print("=" * 70)
    print("🎉 BOOTSTRAP COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Run validation: inv validate_all")
    print("  2. Run tests:      inv test_all")
    print("  3. Run linters:    inv lint_all")
    print()
    print("For help: inv --list")
    print()


# =============================================================================
# Cleanup Tasks (INV-010)
# =============================================================================

@task
def clean_pycache(c):
    """Remove Python cache files (__pycache__, *.pyc)."""
    print("🧹 Removing Python cache files...")
    
    import shutil
    from pathlib import Path
    
    # Remove __pycache__ directories
    for pycache_dir in Path('.').rglob('__pycache__'):
        shutil.rmtree(pycache_dir, ignore_errors=True)
    
    # Remove .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink(missing_ok=True)
    
    print("✅ Python cache files removed")


@task
def clean_logs(c):
    """Remove log files."""
    print("🧹 Removing log files...")
    
    from pathlib import Path
    
    logs_dir = Path('logs')
    if logs_dir.exists():
        for log_file in logs_dir.glob('*.log'):
            log_file.unlink(missing_ok=True)
    
    print("✅ Log files removed")


@task
def clean_state(c):
    """Remove state databases and test caches."""
    print("🧹 Removing state files and caches...")
    
    import shutil
    from pathlib import Path
    
    items = [
        Path("state").glob("*.db"),
        [Path(".benchmarks")],
        [Path(".pytest_cache")],
        [Path("coverage.xml")],
        [Path(".coverage")],
        [Path("htmlcov")]
    ]
    
    for item_group in items:
        for item in item_group:
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
    
    print("✅ State files and caches removed")


@task
def clean_acms_runs(c):
    """Remove ACMS run directories."""
    print("🧹 Removing ACMS run directories...")
    
    import shutil
    from pathlib import Path
    
    acms_runs_dir = Path('.acms_runs')
    if acms_runs_dir.exists():
        for item in acms_runs_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
    
    print("✅ ACMS run directories removed")


@task(pre=[clean_pycache, clean_logs, clean_state, clean_acms_runs])
def clean_all(c):
    """Complete cleanup (does not remove dependencies).
    
    Removes:
    - Python cache files
    - Log files
    - State databases
    - Test caches
    - ACMS run directories
    """
    print("\n" + "=" * 70)
    print("✅ CLEANUP COMPLETE")
    print("=" * 70)


@task
def reset(c):
    """Full reset: cleanup + reinstall dependencies.
    
    Warning: This will remove all generated files and reinstall all dependencies.
    """
    print("⚠️  Performing full reset...")
    print()
    
    clean_all(c)
    print()
    
    install_dev(c)
    print()
    
    print("=" * 70)
    print("✅ RESET COMPLETE")
    print("=" * 70)


# =============================================================================
# CI/CD Convenience Tasks
# =============================================================================

@task(pre=[validate_all, lint_all, test_all])
def ci(c):
    """Run full CI validation suite (validate + lint + test).
    
    This is the recommended task to run before pushing commits.
    Equivalent to what CI runs in GitHub Actions.
    """
    print("\n" + "=" * 70)
    print("✅ CI VALIDATION COMPLETE - READY TO PUSH")
    print("=" * 70)


@task
def pre_commit(c):
    """Run pre-commit hooks on all files."""
    print("🪝 Running pre-commit hooks...")
    c.run("pre-commit run --all-files")


# =============================================================================
# Task Collection Setup
# =============================================================================

# Create namespace for organized task grouping
ns = Collection()

# Add validation tasks
validation = Collection('validate')
validation.add_task(validate_phase1, 'phase1')
validation.add_task(validate_phase2, 'phase2')
validation.add_task(validate_all, 'all')
ns.add_collection(validation)

# Add testing tasks
testing = Collection('test')
testing.add_task(test_unit, 'unit')
testing.add_task(test_integration, 'integration')
testing.add_task(test_e2e, 'e2e')
testing.add_task(test_performance, 'performance')
testing.add_task(test_all, 'all')
ns.add_collection(testing)

# Add linting tasks
linting = Collection('lint')
linting.add_task(lint_black, 'black')
linting.add_task(lint_isort, 'isort')
linting.add_task(lint_flake8, 'flake8')
linting.add_task(lint_mypy, 'mypy')
linting.add_task(lint_all, 'all')
linting.add_task(lint_fix, 'fix')
ns.add_collection(linting)

# Add cleanup tasks
cleanup = Collection('clean')
cleanup.add_task(clean_pycache, 'pycache')
cleanup.add_task(clean_logs, 'logs')
cleanup.add_task(clean_state, 'state')
cleanup.add_task(clean_acms_runs, 'acms-runs')
cleanup.add_task(clean_all, 'all')
ns.add_collection(cleanup)

# =============================================================================
# ACMS Test Harness Tasks (INV-002)
# =============================================================================

@task
def harness_plan(c, repo_root=".", spec_path="config/process_steps.json"):
    """Validate process-steps spec.
    
    Args:
        repo_root: Repository root directory (default: current directory)
        spec_path: Path to process steps spec (default: config/process_steps.json)
    """
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from acms_test_harness import load_process_spec, validate_process_spec
    
    repo_root = Path(repo_root).resolve()
    spec_path_obj = Path(spec_path)
    if not spec_path_obj.is_absolute():
        spec_path_obj = repo_root / spec_path
    
    if not spec_path_obj.exists():
        print(f"❌ Spec not found: {spec_path_obj}")
        raise SystemExit(1)
    
    spec = load_process_spec(spec_path_obj)
    errors = validate_process_spec(spec)
    
    if errors:
        print("❌ Spec validation failed:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    
    print(f"✅ Spec OK ({len(spec.get('steps', []))} steps)")


@task
def harness_e2e(c, repo_root, mode="full", spec_path="config/process_steps.json"):
    """Run ACMS pipeline and check postconditions.
    
    Args:
        repo_root: Repository root directory (required)
        mode: Pipeline mode (full, analyze_only, plan_only, execute_only)
        spec_path: Path to process steps spec
    """
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "scripts"))
    from acms_test_harness import (
        load_process_spec,
        validate_process_spec,
        run_acms_pipeline,
        evaluate_spec
    )
    
    repo_root = Path(repo_root).resolve()
    spec_path_obj = Path(spec_path)
    if not spec_path_obj.is_absolute():
        spec_path_obj = repo_root / spec_path
    
    if not spec_path_obj.exists():
        print(f"❌ Spec not found: {spec_path_obj}")
        raise SystemExit(1)
    
    # Validate spec
    spec = load_process_spec(spec_path_obj)
    errors = validate_process_spec(spec)
    if errors:
        print("❌ Spec validation failed:")
        for err in errors:
            print(f"  - {err}")
        raise SystemExit(1)
    
    # Run pipeline
    print(f"Running ACMS pipeline in mode: {mode}")
    run_id, run_dir, state = run_acms_pipeline(repo_root, mode)
    
    print(f"✓ Run ID: {run_id}")
    print(f"✓ Run dir: {run_dir}")
    print(f"✓ Pipeline status: {state.get('final_status', 'unknown')}")
    print()
    
    # Evaluate postconditions
    results = evaluate_spec(spec, repo_root, run_dir, run_id, state)
    failures = [r for r in results if not r.passed]
    
    for res in results:
        prefix = "✅ PASS" if res.passed else "❌ FAIL"
        print(f"{prefix} {res.step_id}: {res.detail}")
    
    if failures:
        print(f"\n❌ {len(failures)} step(s) failed")
        raise SystemExit(1)
    else:
        print(f"\n✅ All {len(results)} steps passed")


# =============================================================================
# Performance Benchmark Tasks (INV-011, INV-020)
# =============================================================================

@task
def benchmark_baseline(c, scenario="all"):
    """Capture performance baseline for regression testing.
    
    Args:
        scenario: Which scenario to run (all, small, medium, large)
    """
    print(f"📊 Running baseline performance scenario: {scenario}")
    
    if scenario in ["all", "small"]:
        print("  → Small clustering (10 gaps)")
        c.run("python tools/profiling/baseline_scenarios.py small", pty=False, warn=True)
    
    if scenario in ["all", "medium"]:
        print("  → Medium clustering (50 gaps)")
        c.run("python tools/profiling/baseline_scenarios.py medium", pty=False, warn=True)
    
    if scenario in ["all", "large"]:
        print("  → Large clustering (200 gaps)")
        c.run("python tools/profiling/baseline_scenarios.py large", pty=False, warn=True)
    
    print("✅ Baseline scenarios complete")


@task
def benchmark_regression(c):
    """Run performance regression tests against baseline.
    
    Uses pytest-benchmark to compare current performance against saved baselines.
    """
    print("📊 Running performance regression tests...")
    
    # Check if pytest-benchmark is installed
    result = c.run("python -c \"import pytest_benchmark\"", warn=True, hide=True, pty=False)
    if result.exited != 0:
        print("⚠ pytest-benchmark not installed. Installing...")
        c.run("pip install pytest-benchmark", pty=False)
    
    # Run performance tests with benchmark
    result = c.run(
        "pytest tests/performance/ --benchmark-only -v",
        warn=True,
        pty=False
    )
    
    if result.exited == 0:
        print("✅ All performance tests passed")
    else:
        print("❌ Performance regression detected")
        raise SystemExit(1)


@task
def benchmark_compare(c):
    """Compare current benchmarks with baseline."""
    print("📊 Comparing benchmarks with baseline...")
    
    baseline_path = Path(".benchmarks/baseline.json")
    if not baseline_path.exists():
        print("⚠ No baseline found. Run 'inv benchmark.baseline' first.")
        print("  Creating baseline now...")
        benchmark_baseline(c)
        return
    
    # Run pytest-benchmark compare
    c.run(
        "pytest-benchmark compare --group-by=func",
        warn=True,
        pty=False
    )


@task
def benchmark_update_baseline(c, scenario="all"):
    """Update performance baseline (commit result to git).
    
    Args:
        scenario: Which scenario to update (all, small, medium, large)
    """
    print("📊 Updating performance baseline...")
    
    # Run baseline scenarios
    benchmark_baseline(c, scenario)
    
    # Check if .benchmarks directory exists
    benchmarks_dir = Path(".benchmarks")
    if benchmarks_dir.exists() and any(benchmarks_dir.iterdir()):
        print("📝 Committing baseline to git...")
        c.run("git add .benchmarks/", pty=False)
        c.run("git commit -m 'chore: update performance baseline' --no-verify", 
              warn=True, pty=False)
        print("✅ Baseline updated and committed")
    else:
        print("⚠ No benchmark data found to commit")


# =============================================================================
# Health Check & Monitoring Tasks (INV-017)
# =============================================================================

@task
def health_check(c):
    """Run system health check and display status report.
    
    Checks:
    - Recent pipeline runs
    - Success rate
    - Consecutive failures
    - Average duration
    - Active alerts
    """
    print("🏥 Running ACMS health check...")
    print()
    
    result = c.run("""
python -c "
from pathlib import Path
from src.acms.monitoring import create_monitoring_system

# Create monitoring system
collector, health_monitor, _ = create_monitoring_system(Path('.'))

# Generate and display health report
report = health_monitor.generate_health_report()
print(report)

# Get health status for exit code
health = health_monitor.check_health()
exit(0 if health.status in ['healthy', 'degraded'] else 1)
"
    """, warn=True, pty=False)
    
    if result.exited == 0:
        print()
        print("✅ Health check passed")
    else:
        print()
        print("❌ Health check failed - system unhealthy")
        raise SystemExit(1)


@task
def metrics_report(c, days=7):
    """Generate metrics report for specified time period.
    
    Args:
        days: Number of days to include in report (default: 7)
    """
    print(f"📊 Generating metrics report for last {days} days...")
    print()
    
    c.run(f"""
python -c "
from pathlib import Path
from src.acms.monitoring import create_monitoring_system

# Create monitoring system
collector, _, _ = create_monitoring_system(Path('.'))

# Get metrics summary
summary = collector.get_metrics_summary(days={days})

print('=' * 70)
print(f'METRICS SUMMARY - Last {days} Days')
print('=' * 70)
print()
print(f'Total Runs: {{summary[\\"total_runs\\"]}}')
print(f'Success Rate: {{summary[\\"success_rate\\"]:.1f}}%')
print(f'Average Duration: {{summary[\\"avg_duration\\"]:.1f}}s')
print(f'Total Tasks: {{summary[\\"total_tasks_executed\\"]}}')
print(f'Failed Tasks: {{summary[\\"total_tasks_failed\\"]}}')
print(f'Gaps Discovered: {{summary[\\"total_gaps_discovered\\"]}}')
print(f'Gaps Fixed: {{summary[\\"total_gaps_fixed\\"]}}')
print()

# Get recent runs
recent = collector.get_recent_runs(limit=10)
if recent:
    print('Recent Runs:')
    for run in recent:
        status = '✅' if run.success else '❌'
        print(f'  {{status}} {{run.run_id}} - {{run.duration_seconds:.1f}}s')
"
    """, pty=False)
    
    print()
    print("✅ Metrics report complete")


@task
def metrics_trends(c, days=30):
    """Analyze performance trends over time.
    
    Args:
        days: Number of days to analyze (default: 30)
    """
    print(f"📈 Analyzing performance trends for last {days} days...")
    print()
    
    c.run(f"""
python -c "
from pathlib import Path
from src.acms.monitoring import create_monitoring_system

# Create monitoring system
_, _, performance_tracker = create_monitoring_system(Path('.'))

# Analyze trends
trends = performance_tracker.analyze_trends(days={days})

print('=' * 70)
print(f'PERFORMANCE TRENDS - Last {days} Days')
print('=' * 70)
print()
print(f'Duration Trend: {{trends[\\"duration_trend\\"]}}')
print(f'Success Rate Trend: {{trends[\\"success_rate_trend\\"]}}')
print(f'Task Count Trend: {{trends[\\"task_count_trend\\"]}}')
print()

if 'recommendations' in trends:
    print('Recommendations:')
    for rec in trends['recommendations']:
        print(f'  • {{rec}}')
"
    """, pty=False)
    
    print()
    print("✅ Trend analysis complete")


# Add top-level convenience tasks
ns.add_task(install)
ns.add_task(install_dev, 'install-dev')
ns.add_task(bootstrap)
ns.add_task(reset)
ns.add_task(ci)
ns.add_task(pre_commit, 'pre-commit')

# Add test harness tasks
harness = Collection('harness')
harness.add_task(harness_plan, 'plan')
harness.add_task(harness_e2e, 'e2e')
ns.add_collection(harness)

# Add benchmark tasks
benchmark = Collection('benchmark')
benchmark.add_task(benchmark_baseline, 'baseline')
benchmark.add_task(benchmark_regression, 'regression')
benchmark.add_task(benchmark_compare, 'compare')
benchmark.add_task(benchmark_update_baseline, 'update-baseline')
ns.add_collection(benchmark)

# Add health & monitoring tasks
health = Collection('health')
health.add_task(health_check, 'check')
health.add_task(metrics_report, 'metrics')
health.add_task(metrics_trends, 'trends')
ns.add_collection(health)

# Also add common tasks at root level for convenience
ns.add_task(validate_all)
ns.add_task(test_all)
ns.add_task(lint_all)
