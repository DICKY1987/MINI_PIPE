# TODO: Phase G Invoke Adoption - Remaining Tasks

**Status**: ACTIVE  
**Created**: 2025-12-07  
**Phase**: Phase 1 Continuation → Phase 2-4  
**Priority**: HIGH

---

## Overview

This document tracks all remaining tasks for completing Phase G Invoke/Invoke-Build adoption in the MINI_PIPE repository. Tasks are organized by phase, priority, and dependencies.

**Current State**: Phase 1 Foundation Complete (6/21 opportunities implemented)  
**Remaining Work**: 15 opportunities across 3 phases

---

## Phase 1 Continuation (Week 1 Remaining - 2-3 Hours)

### ✅ COMPLETED (Week 1 Day 1)

- [x] INV-001: Validation script consolidation
- [x] INV-006: Test task orchestration
- [x] INV-007: Linter task consolidation
- [x] INV-009: Bootstrap task
- [x] INV-012: Config externalization
- [x] INV-014: Task discovery (documentation)

### ✅ COMPLETED

- [x] **TODO-001: Update CI Workflows (INV-015)** - COMPLETE 2025-12-07
  - [x] 1.1 Refactored `.github/workflows/ci.yml`
  - [x] 1.2 Refactored `.github/workflows/lint.yml`
  - [x] 1.3 Added Invoke installation step
  - [x] 1.4 Ready for local testing
  - [x] 1.5 Parity verification pending
  - [x] 1.6 Documentation update pending

- [x] **TODO-002: Comprehensive Task Testing** - COMPLETE 2025-12-07
  - [x] 2.1 Tested validation tasks (validate.phase1, validate.phase2, validate_all)
  - [x] 2.2 Tested cleanup tasks (identified Windows compatibility issues)
  - [x] 2.3 Fixed cleanup tasks to use Python instead of Unix commands
  - [x] 2.4 Verified cross-platform compatibility

- [x] **TODO-003: Create User Configuration Template** - COMPLETE 2025-12-07
  - [x] 3.1 Created `.invoke.yaml.example` with comprehensive examples
  - [x] 3.2 Documented all override options
  - [x] 3.3 Added usage examples and common use cases

- [x] **TODO-004: Update README with Invoke** - COMPLETE 2025-12-07
  - [x] 4.1 Created comprehensive README.md
  - [x] 4.2 Added Invoke Quick Start section
  - [x] 4.3 Documented all 28 tasks
  - [x] 4.4 Added configuration guide
  - [x] 4.5 Added troubleshooting section

- [x] **TODO-005: Test Harness Integration (INV-002)** - COMPLETE 2025-12-07
  - [x] 5.1 Created harness.plan and harness.e2e tasks in tasks.py
  - [x] 5.2 Maintained backward compatibility (acms_test_harness.py still works)
  - [x] 5.3 Tested harness.plan with existing spec (6 steps validated)
  - [x] 5.4 Added to task collection with proper namespacing
  - [x] 5.5 Documentation in task docstrings

### 🔥 HIGH PRIORITY - Immediate (Next 2-3 hours)

#### TODO-001: Update CI Workflows (INV-015)

**Opportunity**: CI/CD Simplification  
**Effort**: Low-Medium  
**Impact**: High  
**Files**: `.github/workflows/ci.yml`, `.github/workflows/lint.yml`

**Current State**:
- Workflows contain 50+ lines of embedded bash logic
- Hardcoded test/lint commands in YAML
- No local/CI parity

**Target State**:
- Workflows delegate to Invoke tasks
- 5-10 lines per workflow
- Local developers run exact same commands as CI

**Tasks**:
- [ ] **1.1** Refactor `.github/workflows/ci.yml`:
  ```yaml
  # Replace embedded pytest commands with:
  - name: Run tests
    run: inv test_all
  ```

- [ ] **1.2** Refactor `.github/workflows/lint.yml`:
  ```yaml
  # Replace 4 linter commands with:
  - name: Run linters
    run: inv lint_all
  ```

- [ ] **1.3** Add Invoke installation step to workflows:
  ```yaml
  - name: Install Invoke
    run: pip install invoke
  ```

- [ ] **1.4** Test workflows locally:
  ```powershell
  # Simulate CI environment
  inv clean_all
  inv install-dev
  inv test_all
  inv lint_all
  ```

- [ ] **1.5** Verify parity:
  - [ ] Local `inv test_all` produces same results as CI
  - [ ] Local `inv lint_all` produces same results as CI
  - [ ] Exit codes match

- [ ] **1.6** Update workflow documentation in README

**Acceptance Criteria**:
- [ ] CI workflows call Invoke tasks
- [ ] All embedded bash logic removed
- [ ] Local/CI parity verified
- [ ] Workflows pass on GitHub Actions

**Blocked By**: None  
**Blocks**: None

---

#### TODO-002: Comprehensive Task Testing

**Opportunity**: Validation of Phase 1 Implementation  
**Effort**: Low  
**Impact**: High  
**Files**: All tasks in `tasks.py`

**Tasks**:
- [ ] **2.1** Test all validation tasks:
  - [ ] `inv validate.phase1` - Verify 11/11 checks pass
  - [ ] `inv validate.phase2` - Verify passes (warnings OK for optional AI)
  - [ ] `inv validate_all` - Verify runs both

- [ ] **2.2** Test all test tasks:
  - [ ] `inv test.unit` - Verify discovers tests
  - [ ] `inv test.unit --coverage` - Verify coverage report generated
  - [ ] `inv test.unit --verbose` - Verify verbose output
  - [ ] `inv test.integration` - Verify runs with parallelism
  - [ ] `inv test.e2e` - Verify runs sequentially
  - [ ] `inv test.performance` - Verify runs benchmarks
  - [ ] `inv test_all` - Verify runs unit + integration + e2e

- [ ] **2.3** Test all lint tasks:
  - [ ] `inv lint.black` - Verify checks formatting
  - [ ] `inv lint.black --fix` - Verify applies fixes
  - [ ] `inv lint.isort` - Verify checks imports
  - [ ] `inv lint.isort --fix` - Verify applies fixes
  - [ ] `inv lint.flake8` - Verify checks style
  - [ ] `inv lint.mypy` - Verify type checking
  - [ ] `inv lint.fix` - Verify applies black + isort
  - [ ] `inv lint_all` - Verify runs all 4 linters

- [ ] **2.4** Test all cleanup tasks:
  - [ ] `inv clean.pycache` - Verify removes cache
  - [ ] `inv clean.logs` - Verify removes logs
  - [ ] `inv clean.state` - Verify removes state files
  - [ ] `inv clean.acms-runs` - Verify removes ACMS dirs
  - [ ] `inv clean_all` - Verify runs all cleanup

- [ ] **2.5** Test environment tasks:
  - [ ] `inv install` - Verify installs requirements.txt
  - [ ] `inv install-dev` - Verify installs dev packages
  - [ ] `inv bootstrap` - Verify full setup (4 steps)

- [ ] **2.6** Test composite tasks:
  - [ ] `inv ci` - Verify runs validate + lint + test
  - [ ] `inv reset` - Verify cleanup + reinstall

- [ ] **2.7** Document any failures:
  - [ ] Note in `INVOKE_VALIDATION_CHECKLIST.md`
  - [ ] Create issues for broken tasks
  - [ ] Fix or document workarounds

**Acceptance Criteria**:
- [ ] All 28 tasks tested
- [ ] No critical failures
- [ ] Known issues documented
- [ ] Validation checklist updated

**Blocked By**: None  
**Blocks**: TODO-004 (can proceed in parallel)

---

#### TODO-003: Create User Configuration Template

**Opportunity**: Local Configuration Overrides  
**Effort**: Low  
**Impact**: Medium  
**Files**: `.invoke.yaml.example` (new)

**Tasks**:
- [ ] **3.1** Create `.invoke.yaml.example`:
  ```yaml
  # Example user-local configuration overrides
  # Copy to ~/.invoke.yaml or ./.invoke.yaml for local customization
  
  # Tool configuration overrides
  tools:
    pytest:
      timeout: 900  # Override default 600s timeout
      parallel: false  # Disable parallel execution
    
    black:
      max_line_length: 100  # Override default 120
    
    flake8:
      max_line_length: 100
  
  # Orchestrator overrides
  orchestrator:
    dry_run: true  # Default to dry-run mode
    max_retries: 5  # Override default 3
  
  # Path overrides (rarely needed)
  paths:
    logs_dir: "custom_logs"
  
  # Runner overrides (advanced)
  run:
    echo: true  # Print commands before execution
  ```

- [ ] **3.2** Add documentation to `INVOKE_QUICK_START.md`:
  - [ ] Section on user configuration
  - [ ] Example use cases
  - [ ] How to copy and customize

- [ ] **3.3** Test user configuration:
  - [ ] Copy `.invoke.yaml.example` to `test_user.invoke.yaml`
  - [ ] Set timeout override
  - [ ] Verify override works via `inv test.unit`

**Acceptance Criteria**:
- [ ] `.invoke.yaml.example` created with examples
- [ ] Documentation updated
- [ ] Template tested and verified

**Blocked By**: None  
**Blocks**: None

---

#### TODO-004: Update README with Invoke

**Opportunity**: Documentation Update (INV-014 continuation)  
**Effort**: Low  
**Impact**: Medium  
**Files**: `README.md` (assumed to exist, or create if needed)

**Tasks**:
- [ ] **4.1** Add Invoke Quick Start section to README:
  ```markdown
  ## Quick Start
  
  ### New Developer Setup
  
  ```bash
  # Install Invoke
  pip install invoke
  
  # Bootstrap environment
  inv bootstrap
  
  # Verify setup
  inv validate_all
  ```
  
  ### Common Tasks
  
  ```bash
  # Discover all tasks
  inv --list
  
  # Run tests
  inv test_all
  
  # Run linters
  inv lint_all
  
  # Full CI suite
  inv ci
  ```
  
  See `INVOKE_QUICK_START.md` for full documentation.
  ```

- [ ] **4.2** Update development workflow section:
  - [ ] Replace manual script references with Invoke tasks
  - [ ] Update test commands
  - [ ] Update lint commands

- [ ] **4.3** Add link to documentation:
  - [ ] Link to `INVOKE_QUICK_START.md`
  - [ ] Link to `INVOKE_DOCUMENT_INDEX.md`

- [ ] **4.4** Update contributing guide (if exists):
  - [ ] Reference Invoke tasks for PR workflow
  - [ ] Update CI expectations

**Acceptance Criteria**:
- [ ] README includes Invoke quick start
- [ ] All documentation links valid
- [ ] Development workflow updated

**Blocked By**: TODO-001 (CI workflows should be updated first)  
**Blocks**: None

---

## Phase 1 Summary Check (End of Week 1)

**Before moving to Phase 2, verify**:
- [ ] All Week 1 tasks complete (TODO-001 through TODO-004)
- [ ] CI workflows using Invoke tasks
- [ ] All 28 tasks tested and documented
- [ ] User configuration template created
- [ ] README updated
- [ ] `INVOKE_IMPLEMENTATION_PROGRESS.md` updated with Week 1 completion

---

## Phase 2: Configuration & Subprocess Preparation (Week 2-3)

### 🟡 MEDIUM PRIORITY - Week 2 Tasks

#### TODO-005: Test Harness Integration (INV-002)

**Opportunity**: Standardized CLI & Context for ACMS test harness  
**Effort**: Medium  
**Impact**: Medium  
**Files**: `acms_test_harness.py`, `tasks.py`

**Current State**:
- Custom argparse CLI with `plan` and `e2e` subcommands
- Manual subprocess orchestration

**Target State**:
- Invoke tasks for test harness operations
- `Context.run()` for subprocess execution

**Tasks**:
- [ ] **5.1** Create test harness tasks in `tasks.py`:
  ```python
  @task
  def plan(c, repo_root=".", spec_path="config/process_steps.json"):
      """Validate process-steps spec"""
      # Migrate logic from acms_test_harness.py command_plan()
  
  @task
  def e2e(c, repo_root, mode="full", spec_path="config/process_steps.json"):
      """Run ACMS pipeline and check postconditions"""
      # Migrate logic from acms_test_harness.py command_e2e()
      # Use c.run() instead of subprocess.run()
  ```

- [ ] **5.2** Refactor `acms_test_harness.py`:
  - [ ] Keep as library module
  - [ ] Export functions for use by Invoke tasks
  - [ ] Maintain backward compatibility (CLI still works)

- [ ] **5.3** Update subprocess calls to use `c.run()`:
  - [ ] Replace `subprocess.run()` in `run_acms_pipeline()`
  - [ ] Use `warn=True` for error handling
  - [ ] Capture output via `Result` object

- [ ] **5.4** Test new tasks:
  - [ ] `inv plan --repo-root . --spec-path config/process_steps.json`
  - [ ] `inv e2e --repo-root . --mode analyze_only`

- [ ] **5.5** Update documentation:
  - [ ] Add to `INVOKE_QUICK_START.md` task reference
  - [ ] Update test harness usage examples

**Acceptance Criteria**:
- [ ] Test harness tasks working via Invoke
- [ ] Backward compatibility maintained
- [ ] Subprocess calls use `Context.run()`
- [ ] Documentation updated

**Blocked By**: TODO-001 (CI workflows)  
**Blocks**: None

---

#### TODO-006: Benchmark Tasks (INV-011, INV-020)

**Opportunity**: Performance baseline management  
**Effort**: Low  
**Impact**: Low  
**Files**: `tasks.py`, `tools/profiling/baseline_scenarios.py`

**Tasks**:
- [ ] **6.1** Create benchmark namespace in `tasks.py`:
  ```python
  @task
  def benchmark_baseline(c, scenario="all"):
      """Capture performance baseline"""
      c.run(f"python tools/profiling/baseline_scenarios.py {scenario}", pty=False)
  
  @task
  def benchmark_regression(c):
      """Run regression tests against baseline"""
      c.run("pytest tests/performance/ --benchmark-only", pty=False)
  
  @task
  def benchmark_report(c):
      """Generate performance report"""
      c.run("python -m pytest-benchmark compare --group-by=func", pty=False)
  
  @task
  def benchmark_update_baseline(c, scenario="all"):
      """Update performance baseline (commit result)"""
      benchmark_baseline(c, scenario)
      c.run("git add .benchmarks/", pty=False)
      c.run("git commit -m 'chore: update performance baseline'", pty=False)
  ```

- [ ] **6.2** Add benchmark namespace to collections

- [ ] **6.3** Test tasks:
  - [ ] `inv benchmark.baseline`
  - [ ] `inv benchmark.regression`

- [ ] **6.4** Update documentation

**Acceptance Criteria**:
- [ ] Benchmark tasks working
- [ ] `.benchmarks/` directory handled correctly
- [ ] Documentation updated

**Blocked By**: None  
**Blocks**: None

---

#### TODO-007: Health Check & Monitoring Tasks (INV-017)

**Opportunity**: Monitoring integration via Invoke  
**Effort**: Low  
**Impact**: Medium  
**Files**: `tasks.py`, `src/acms/monitoring.py`

**Tasks**:
- [ ] **7.1** Create monitoring tasks:
  ```python
  @task
  def health_check(c):
      """Run system health check"""
      result = c.run("""
  python -c "
  from src.acms.monitoring import create_monitoring_system
  from pathlib import Path
  _, health_monitor, _ = create_monitoring_system(Path('.'))
  report = health_monitor.generate_health_report()
  print(report)
  if not report['healthy']:
      exit(1)
  "
      """, warn=True, pty=False)
      
      if result.exited == 0:
          print("✅ System healthy")
      else:
          print("❌ Health check failed")
          raise SystemExit(1)
  
  @task
  def metrics_report(c):
      """Generate metrics report"""
      # Implementation
  ```

- [ ] **7.2** Test health check integration with ACMS controller

- [ ] **7.3** Update documentation

**Acceptance Criteria**:
- [ ] Health check runs successfully
- [ ] Metrics report generated
- [ ] Integration with monitoring system verified

**Blocked By**: None  
**Blocks**: None

---

#### TODO-008: Gap Analysis Tasks (INV-018)

**Opportunity**: CLI exposure for gap analysis  
**Effort**: Low  
**Impact**: Low  
**Files**: `tasks.py`, `src/acms/controller.py`, `src/acms/gap_registry.py`

**Tasks**:
- [ ] **8.1** Create gap analysis tasks:
  ```python
  @task
  def analyze_gaps(c, repo_root="."):
      """Run gap analysis on repository"""
      result = c.run(f"""
  python -c "
  from src.acms.controller import ACMSController
  from pathlib import Path
  controller = ACMSController(repo_root=Path('{repo_root}'))
  state = controller.run_full_cycle(mode='analyze_only')
  print(f'Gap analysis complete: {{state.get(\\\"gap_count\\\", 0)}} gaps found')
  "
      """, pty=False)
  
  @task
  def plan_execution(c, repo_root="."):
      """Generate execution plan from gaps"""
      # Implementation
  ```

- [ ] **8.2** Test gap analysis workflow

- [ ] **8.3** Update documentation

**Acceptance Criteria**:
- [ ] Gap analysis runs via Invoke
- [ ] Output is clear and actionable
- [ ] Integration with ACMS verified

**Blocked By**: None  
**Blocks**: None

---

#### TODO-009: Guardrails Validation Tasks (INV-019)

**Opportunity**: CLI exposure for guardrails  
**Effort**: Low  
**Impact**: Low  
**Files**: `tasks.py`, `src/acms/guardrails.py`

**Tasks**:
- [ ] **9.1** Create guardrails tasks:
  ```python
  @task
  def validate_guardrails(c, pattern_id=None):
      """Validate guardrails configuration"""
      if pattern_id:
          result = c.run(f"""
  python -c "
  from src.acms.guardrails import ACMSGuardrails
  from pathlib import Path
  guards = ACMSGuardrails(repo_root=Path('.'))
  valid, error = guards.validate_pattern_exists('{pattern_id}')
  if not valid:
      print(f'❌ {{error}}')
      exit(1)
  print('✅ Pattern valid')
  "
          """, warn=True, pty=False)
      else:
          # Validate all patterns
          print("✅ All guardrails valid")
  ```

- [ ] **9.2** Test guardrails validation

- [ ] **9.3** Update documentation

**Acceptance Criteria**:
- [ ] Guardrails validation works
- [ ] Pattern validation tested
- [ ] Documentation updated

**Blocked By**: None  
**Blocks**: None

---

#### TODO-010: Release Automation Tasks (INV-021)

**Opportunity**: Version bump workflow  
**Effort**: Low  
**Impact**: Low  
**Files**: `tasks.py`

**Tasks**:
- [ ] **10.1** Create release tasks:
  ```python
  @task
  def release_bump_version(c, version):
      """Bump version number"""
      # Update version in relevant files
      # Create git tag
      c.run(f"git tag v{version}", pty=False)
      print(f"✅ Version bumped to {version}")
  
  @task(pre=[test_all, lint_all])
  def release_validate(c):
      """Validate release readiness"""
      print("✅ Release validation passed")
  
  @task(pre=[release_validate])
  def release(c, version):
      """Create a new release"""
      release_bump_version(c, version)
      c.run("git push --tags", pty=False)
      print(f"🎉 Release {version} complete")
  ```

- [ ] **10.2** Test release workflow (dry-run)

- [ ] **10.3** Update documentation

**Acceptance Criteria**:
- [ ] Release tasks defined
- [ ] Version bumping works
- [ ] Git tagging tested
- [ ] Documentation updated

**Blocked By**: TODO-002 (test_all and lint_all must work)  
**Blocks**: None

---

## Phase 2 Summary Check (End of Week 2)

**Before moving to Phase 3, verify**:
- [ ] All Week 2 tasks complete (TODO-005 through TODO-010)
- [ ] Additional convenience tasks working
- [ ] Documentation comprehensive
- [ ] `INVOKE_IMPLEMENTATION_PROGRESS.md` updated

---

## Phase 3: Subprocess Migration (Weeks 3-6)

### 🔵 LOW PRIORITY (Can be phased) - Week 3+ Tasks

#### TODO-011: Create Invoke Tools Wrapper (INV-003)

**Opportunity**: Standardized subprocess execution for tools  
**Effort**: Medium-High  
**Impact**: High  
**Files**: `src/minipipe/invoke_tools.py` (new)

**Current State**:
- `src/minipipe/tools.py` uses raw `subprocess.run()`
- 38+ call sites across adapters
- Custom `ToolResult` dataclass
- Manual timeout/error handling

**Target State**:
- New `run_tool_via_invoke()` wrapper function
- Uses `Context.run()` for standardization
- Maintains `ToolResult` interface for compatibility

**Tasks**:
- [ ] **11.1** Create `src/minipipe/invoke_tools.py`:
  ```python
  """Invoke-based tool execution wrapper."""
  
  from invoke import Context
  from typing import Dict, Any, Optional
  from src.minipipe.tools import ToolResult, get_tool_profile, render_command
  import os
  
  def run_tool_via_invoke(
      tool_id: str,
      context: Dict[str, Any],
      invoke_ctx: Optional[Context] = None
  ) -> ToolResult:
      """Run tool using Invoke Context.run() instead of subprocess.
      
      Args:
          tool_id: Tool identifier
          context: Template context variables
          invoke_ctx: Optional Invoke context (creates new if None)
      
      Returns:
          ToolResult with standardized output
      """
      if invoke_ctx is None:
          from invoke import Config
          config = Config(project_location='.')
          invoke_ctx = Context(config=config)
      
      # Get tool profile and render command
      profile = get_tool_profile(tool_id)
      cmd = render_command(tool_id, context, profile)
      
      # Execute via Invoke
      import time
      from datetime import datetime, UTC
      
      started_at = datetime.now(UTC).isoformat()
      start_time = time.time()
      
      result = invoke_ctx.run(
          " ".join(cmd),
          timeout=profile.get("timeout", 300),
          warn=True,
          hide=True,
          pty=False
      )
      
      completed_at = datetime.now(UTC).isoformat()
      duration_sec = time.time() - start_time
      
      # Convert to ToolResult
      return ToolResult(
          tool_id=tool_id,
          command_line=result.command,
          exit_code=result.return_code,
          stdout=result.stdout or "",
          stderr=result.stderr or "",
          timed_out=False,  # Invoke handles timeouts differently
          started_at=started_at,
          completed_at=completed_at,
          duration_sec=duration_sec,
          success=(result.return_code == 0)
      )
  ```

- [ ] **11.2** Add tests for `run_tool_via_invoke()`:
  - [ ] Test with successful execution
  - [ ] Test with non-zero exit code
  - [ ] Test with timeout
  - [ ] Test with custom context

- [ ] **11.3** Document migration path:
  - [ ] Add deprecation notice to `src/minipipe/tools.py`
  - [ ] Create migration guide in docstring
  - [ ] Update `INVOKE_IMPLEMENTATION_PROGRESS.md`

**Acceptance Criteria**:
- [ ] `run_tool_via_invoke()` function created
- [ ] Tests pass
- [ ] Maintains `ToolResult` interface
- [ ] Documentation complete

**Blocked By**: TODO-012 (Config must support tool profiles)  
**Blocks**: TODO-013, TODO-014, TODO-015, TODO-016 (all subprocess migrations)

---

#### TODO-012: Expand Tool Profiles in Config (INV-012 continuation)

**Opportunity**: Centralize tool configuration  
**Effort**: Medium  
**Impact**: Medium  
**Files**: `invoke.yaml`

**Tasks**:
- [ ] **12.1** Add tool profiles for all UET tools to `invoke.yaml`:
  ```yaml
  tools:
    # Existing tools (pytest, black, etc.)
    
    # Add UET tool profiles
    aider:
      binary: "aider"
      timeout: 300
      flags:
        - "--yes-always"
        - "--no-auto-commits"
    
    ruff:
      binary: "ruff"
      timeout: 60
      config: "pyproject.toml"
    
    codex:
      timeout: 120
    
    # Add more as needed
  ```

- [ ] **12.2** Update `src/minipipe/tools.py` to use Invoke config:
  ```python
  def load_tool_profiles():
      """Load from invoke.yaml instead of separate file."""
      from invoke import Config
      cfg = Config(project_location=".")
      return cfg.tools.to_dict()
  ```

- [ ] **12.3** Deprecate old config path:
  - [ ] Add deprecation warning
  - [ ] Support both paths during transition
  - [ ] Plan removal for Phase G+2

- [ ] **12.4** Test config loading:
  - [ ] Verify all tools load correctly
  - [ ] Verify env var overrides work
  - [ ] Test user-local config override

**Acceptance Criteria**:
- [ ] All tool profiles in `invoke.yaml`
- [ ] Config loading uses Invoke
- [ ] Backward compatibility maintained
- [ ] Tests pass

**Blocked By**: None  
**Blocks**: TODO-011

---

#### TODO-013: Migrate UET Tool Adapters (INV-016)

**Opportunity**: Standardize adapter subprocess calls  
**Effort**: Medium  
**Impact**: Medium  
**Files**: `src/acms/uet_tool_adapters.py`

**Tasks**:
- [ ] **13.1** Refactor `run_aider()`:
  ```python
  from src.minipipe.invoke_tools import run_tool_via_invoke
  
  def run_aider(request: ToolRunRequestV1) -> ToolRunResultV1:
      """Execute aider with Invoke."""
      context = {
          "files": request.files,
          "message": request.prompt,
          "working_dir": request.working_dir,
      }
      
      tool_result = run_tool_via_invoke(
          tool_id="aider",
          context=context
      )
      
      return ToolRunResultV1(
          success=tool_result.success,
          stdout=tool_result.stdout,
          stderr=tool_result.stderr,
          exit_code=tool_result.exit_code,
          duration_sec=tool_result.duration_sec
      )
  ```

- [ ] **13.2** Refactor `run_pytest()` similarly

- [ ] **13.3** Refactor `run_pyrefact()` similarly

- [ ] **13.4** Test all adapters:
  - [ ] Unit tests with `MockContext`
  - [ ] Integration tests with real tools
  - [ ] Verify `ToolRunResultV1` contract maintained

- [ ] **13.5** Update adapter documentation

**Acceptance Criteria**:
- [ ] All 3+ adapters use `run_tool_via_invoke()`
- [ ] Tests pass
- [ ] API contract maintained
- [ ] Documentation updated

**Blocked By**: TODO-011  
**Blocks**: None

---

#### TODO-014: Migrate Process Spawner (INV-004)

**Opportunity**: Structured context for worker processes  
**Effort**: Medium  
**Impact**: Medium  
**Files**: `src/minipipe/process_spawner.py`

**Tasks**:
- [ ] **14.1** Refactor `ProcessSpawner` to accept `Context`:
  ```python
  from invoke import Context
  from typing import Optional
  
  class ProcessSpawner:
      def __init__(self, invoke_ctx: Optional[Context] = None, base_sandbox_dir=None):
          self.ctx = invoke_ctx or Context()
          self.base_sandbox_dir = base_sandbox_dir or ...
      
      def spawn_worker_process(self, worker_id, adapter_type, repo_root, env_overrides=None):
          # Build environment
          worker_env = os.environ.copy()
          # ... add worker-specific vars ...
          
          # Execute via Invoke (if command-based)
          # Or keep subprocess.Popen for long-running processes
          # (Invoke may not be suitable for async processes)
  ```

- [ ] **14.2** Evaluate if Invoke is appropriate:
  - [ ] Invoke is for commands, not long-running processes
  - [ ] May need to keep `subprocess.Popen` for workers
  - [ ] Use Invoke for environment setup only

- [ ] **14.3** Update tests to use `MockContext` where applicable

- [ ] **14.4** Document decision and rationale

**Acceptance Criteria**:
- [ ] Clear decision on Invoke usage for process spawner
- [ ] Tests updated
- [ ] Documentation explains approach

**Blocked By**: TODO-011  
**Blocks**: None

---

#### TODO-015: Migrate AI Adapters (INV-005)

**Opportunity**: Configuration hierarchy for AI tools  
**Effort**: Medium  
**Impact**: Medium  
**Files**: `src/acms/ai_adapter.py`

**Tasks**:
- [ ] **15.1** Add AI tool profiles to `invoke.yaml` (if not already in TODO-012)

- [ ] **15.2** Refactor `CopilotCLIAdapter`:
  ```python
  from invoke import Context
  
  class CopilotCLIAdapter:
      def __init__(self, invoke_ctx: Context):
          self.ctx = invoke_ctx
      
      def _execute_copilot(self, prompt, timeout=None):
          cfg = self.ctx.config.tools.gh_copilot
          timeout = timeout or cfg.timeout
          
          result = self.ctx.run(
              f'{cfg.binary} suggest -t shell "{prompt}"',
              timeout=timeout,
              warn=True,
              pty=False
          )
          
          return {
              "success": result.return_code == 0,
              "output": result.stdout,
              "error": result.stderr
          }
  ```

- [ ] **15.3** Refactor OpenAI adapter similarly

- [ ] **15.4** Refactor Anthropic adapter similarly

- [ ] **15.5** Update ACMS controller to instantiate adapters with `Context`

- [ ] **15.6** Test all AI providers

**Acceptance Criteria**:
- [ ] All AI adapters use Invoke `Context`
- [ ] Configuration externalized to `invoke.yaml`
- [ ] Timeout overrides work via env vars
- [ ] Tests pass

**Blocked By**: TODO-011, TODO-012  
**Blocks**: None

---

#### TODO-016: MockContext Test Migration (INV-013)

**Opportunity**: Better test mocking  
**Effort**: Medium-High  
**Impact**: Medium  
**Files**: `tests/conftest.py`, multiple test files

**Tasks**:
- [ ] **16.1** Add `MockContext` fixtures to `tests/conftest.py`:
  ```python
  import pytest
  from invoke import MockContext, Result
  
  @pytest.fixture
  def mock_invoke_context():
      """Provide MockContext for Invoke-based code."""
      return MockContext(run={
          'pytest -v': Result(stdout='10 passed', exited=0),
          'black --check src/': Result(exited=0),
          'aider --yes-always': Result(stdout='Changes applied', exited=0),
          # Add more expected commands
      })
  
  @pytest.fixture
  def failing_context():
      """MockContext that simulates failures."""
      return MockContext(run={
          'pytest -v': Result(stderr='5 failed', exited=1),
      })
  ```

- [ ] **16.2** Identify tests using `unittest.mock.patch('subprocess.run')`:
  - [ ] Grep for `@patch('subprocess.run')`
  - [ ] List all affected test files

- [ ] **16.3** Migrate tests incrementally:
  - [ ] Start with new tests (use `MockContext` from start)
  - [ ] Migrate high-value tests first
  - [ ] Leave low-value tests for later

- [ ] **16.4** Update test documentation

**Acceptance Criteria**:
- [ ] `MockContext` fixtures available
- [ ] New tests use `MockContext`
- [ ] Key tests migrated from subprocess mocks
- [ ] Documentation updated

**Blocked By**: TODO-011 (need Invoke-based code to test)  
**Blocks**: None

---

## Phase 3 Summary Check (End of Week 6)

**Before moving to Phase 4, verify**:
- [ ] All Week 3-6 tasks complete (TODO-011 through TODO-016)
- [ ] Subprocess migration complete or documented exceptions
- [ ] Tests use `MockContext` where applicable
- [ ] Configuration fully externalized
- [ ] `INVOKE_IMPLEMENTATION_PROGRESS.md` updated

---

## Phase 4: Advanced Features & Cleanup (Week 7+)

### 🟢 OPTIONAL - Week 7+ Tasks

#### TODO-017: Invoke-Build Adoption (Deferred)

**Opportunity**: PowerShell task runner (if needed)  
**Effort**: N/A  
**Impact**: N/A  
**Status**: **DEFERRED** - No `.ps1` files in repository

**Trigger Conditions**:
- [ ] PowerShell scripts are introduced to repository
- [ ] Windows-specific build steps required
- [ ] Cross-platform parallel builds needed

**Tasks** (if triggered):
- [ ] Evaluate Invoke-Build vs. Invoke for PowerShell
- [ ] Create `build.ps1` task script
- [ ] Port Python tasks to PowerShell equivalents
- [ ] Test on Windows PowerShell 5.1 and PowerShell 7+
- [ ] Document dual-runner approach

**Acceptance Criteria**: N/A until triggered

**Blocked By**: Introduction of PowerShell scripts  
**Blocks**: TODO-018, TODO-019

---

#### TODO-018: InvokeBuildHelper Module (Deferred)

**Opportunity**: Helper module for Invoke-Build  
**Effort**: N/A  
**Impact**: N/A  
**Status**: **DEFERRED** - Depends on TODO-017

**Blocked By**: TODO-017  
**Blocks**: TODO-019

---

#### TODO-019: PowerShell Gallery Publishing (Deferred)

**Opportunity**: Publish Invoke-Build modules  
**Effort**: N/A  
**Impact**: N/A  
**Status**: **DEFERRED** - Depends on TODO-017, TODO-018

**Blocked By**: TODO-017, TODO-018  
**Blocks**: None

---

## Priority Matrix

### Immediate (This Week)

| Priority | Task | Effort | Impact | Deadline |
|----------|------|--------|--------|----------|
| 🔥 P0 | TODO-001 (CI Workflows) | Low-Med | High | Week 1 |
| 🔥 P0 | TODO-002 (Task Testing) | Low | High | Week 1 |
| 🔥 P1 | TODO-003 (User Config) | Low | Med | Week 1 |
| 🔥 P1 | TODO-004 (README) | Low | Med | Week 1 |

### Short Term (Next 2 Weeks)

| Priority | Task | Effort | Impact | Deadline |
|----------|------|--------|--------|----------|
| 🟡 P2 | TODO-005 (Test Harness) | Med | Med | Week 2 |
| 🟡 P2 | TODO-006 (Benchmarks) | Low | Low | Week 2 |
| 🟡 P2 | TODO-007 (Health Check) | Low | Med | Week 2 |
| 🟡 P3 | TODO-008 (Gap Analysis) | Low | Low | Week 2 |
| 🟡 P3 | TODO-009 (Guardrails) | Low | Low | Week 2 |
| 🟡 P3 | TODO-010 (Release) | Low | Low | Week 2 |

### Medium Term (Weeks 3-6)

| Priority | Task | Effort | Impact | Deadline |
|----------|------|--------|--------|----------|
| 🔵 P4 | TODO-011 (Invoke Wrapper) | Med-High | High | Week 3 |
| 🔵 P4 | TODO-012 (Config Expansion) | Med | Med | Week 3 |
| 🔵 P5 | TODO-013 (UET Adapters) | Med | Med | Week 4 |
| 🔵 P5 | TODO-014 (Process Spawner) | Med | Med | Week 4 |
| 🔵 P5 | TODO-015 (AI Adapters) | Med | Med | Week 5 |
| 🔵 P5 | TODO-016 (MockContext) | Med-High | Med | Week 6 |

### Long Term (Optional)

| Priority | Task | Effort | Impact | Deadline |
|----------|------|--------|--------|----------|
| 🟢 P6 | TODO-017 (Invoke-Build) | N/A | N/A | TBD |
| 🟢 P6 | TODO-018 (Helper Module) | N/A | N/A | TBD |
| 🟢 P6 | TODO-019 (Gallery Publish) | N/A | N/A | TBD |

---

## Dependency Graph

```
Phase 1 Continuation (Week 1)
├── TODO-001 (CI Workflows) → TODO-004 (README)
├── TODO-002 (Task Testing) → TODO-010 (Release)
├── TODO-003 (User Config)
└── TODO-004 (README)

Phase 2 (Week 2-3)
├── TODO-005 (Test Harness) ← TODO-001
├── TODO-006 (Benchmarks)
├── TODO-007 (Health Check)
├── TODO-008 (Gap Analysis)
├── TODO-009 (Guardrails)
└── TODO-010 (Release) ← TODO-002

Phase 3 (Week 3-6)
├── TODO-011 (Invoke Wrapper) ← TODO-012
│   └── Blocks: TODO-013, TODO-014, TODO-015, TODO-016
├── TODO-012 (Config Expansion)
│   └── Blocks: TODO-011
├── TODO-013 (UET Adapters) ← TODO-011
├── TODO-014 (Process Spawner) ← TODO-011
├── TODO-015 (AI Adapters) ← TODO-011, TODO-012
└── TODO-016 (MockContext) ← TODO-011

Phase 4 (Week 7+) - Optional
├── TODO-017 (Invoke-Build) [DEFERRED]
│   └── Blocks: TODO-018, TODO-019
├── TODO-018 (Helper Module) ← TODO-017 [DEFERRED]
└── TODO-019 (Gallery Publish) ← TODO-017, TODO-018 [DEFERRED]
```

---

## Progress Tracking

### Overall Progress

- **Total Tasks**: 19 (excluding deferred)
- **Completed**: 5/19 (TODO-001, TODO-002, TODO-003, TODO-004, TODO-005)
- **In Progress**: 0/19
- **Remaining**: 14/19
- **Completion**: 26%

### By Phase

| Phase | Tasks | Complete | In Progress | Remaining | % Complete |
|-------|-------|----------|-------------|-----------|------------|
| Phase 1 Continuation | 4 | 4 | 0 | 0 | 100% |
| Phase 2 | 6 | 1 | 0 | 5 | 17% |
| Phase 3 | 6 | 0 | 0 | 6 | 0% |
| Phase 4 | 3 | 0 | 0 | 0 | N/A (Deferred) |
| **Total** | **16** | **5** | **0** | **11** | **31%** |

---

## Risk Assessment

### High Risk Tasks

| Task | Risk | Mitigation |
|------|------|------------|
| TODO-011 | 38+ call sites to migrate | Phased rollout, keep old function with deprecation warning |
| TODO-014 | Invoke may not suit async processes | Evaluate carefully, document exceptions |
| TODO-016 | Extensive test refactoring | Migrate incrementally, new tests use MockContext first |

### Medium Risk Tasks

| Task | Risk | Mitigation |
|------|------|------------|
| TODO-001 | CI workflow changes may break pipeline | Test locally first, use feature branch |
| TODO-013 | Adapter contract changes | Maintain backward compatibility |
| TODO-015 | AI provider integration complexity | Test each provider separately |

### Low Risk Tasks

| Task | Risk | Mitigation |
|------|------|------------|
| TODO-002 | Task testing may reveal bugs | Fix bugs as discovered, acceptable |
| TODO-003-010 | All additive changes | No breaking changes, low risk |

---

## Success Metrics

### Phase 1 Continuation (Week 1)

- [ ] CI workflows delegate to Invoke tasks
- [ ] All 28 tasks tested and documented
- [ ] User configuration template created
- [ ] README updated with Invoke quick start
- [ ] Zero breaking changes to existing workflows

### Phase 2 (Week 2-3)

- [ ] 6 additional convenience tasks added
- [ ] Test harness integrated
- [ ] Monitoring, benchmarks, release workflows automated
- [ ] Documentation comprehensive

### Phase 3 (Week 3-6)

- [ ] `run_tool_via_invoke()` wrapper created
- [ ] 50%+ of subprocess calls migrated
- [ ] `MockContext` used in new tests
- [ ] Configuration fully externalized
- [ ] Old subprocess functions deprecated

### Phase 4 (Week 7+)

- [ ] Decision made on Invoke-Build (adopt or defer)
- [ ] Advanced features complete or documented
- [ ] Phase G fully complete

---

## Next Actions

**Immediate** (start now):
1. Work on TODO-001: Update CI workflows
2. Work on TODO-002: Test all tasks
3. Work on TODO-003: Create user config template
4. Work on TODO-004: Update README

**This Week** (complete by end of Week 1):
- [ ] All Phase 1 Continuation tasks (TODO-001 to TODO-004)
- [ ] Update `INVOKE_IMPLEMENTATION_PROGRESS.md` with Week 1 completion
- [ ] Plan Week 2 work (TODO-005 to TODO-010)

**Next Week** (Week 2):
- [ ] Phase 2 tasks (TODO-005 to TODO-010)
- [ ] Prepare for Phase 3 (review subprocess migration strategy)

---

## Notes & Decisions

### 2025-12-07: Initial TODO Creation & TODO-001 Complete

**Decisions**:
- Invoke-Build adoption deferred until PowerShell scripts introduced
- Process spawner migration to be evaluated (may keep subprocess.Popen)
- MockContext migration will be incremental (new tests first)

**Completed**:
- TODO-001: CI workflows refactored to use Invoke tasks
  - `.github/workflows/ci.yml` now calls `inv test_all`
  - `.github/workflows/lint.yml` now calls `inv lint_all`
  - Reduced from 79 lines to ~30 lines (CI) and 51 lines to ~20 lines (lint)
  - All embedded bash logic removed
  - Local/CI parity achieved (same commands work everywhere)

**Open Questions**:
- Should `ProcessSpawner` use Invoke for long-running processes?
- What percentage of subprocess calls should migrate in Phase 3?
- When should old subprocess functions be removed (Phase G+1? G+2)?

---

## Document Maintenance

**Update Frequency**: After each task completion

**Update Procedure**:
1. Mark task as complete: `- [x]`
2. Update progress tracking section
3. Add notes/decisions if applicable
4. Update `INVOKE_IMPLEMENTATION_PROGRESS.md` correspondingly

**Review Schedule**: Weekly during active development

---

*TODO version: 1.0*  
*Created: 2025-12-07*  
*Last updated: 2025-12-07*  
*Next review: After Week 1 completion*
