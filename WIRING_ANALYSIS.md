# MINI_PIPE Wiring Analysis - What Needs to be Connected

**Date:** 2025-12-07  
**Status:** Deep Analysis Complete  
**Purpose:** Identify all components that need wiring/integration

---

## 🎯 Executive Summary

### Current State
- **Phase 1 (Automation Foundation):** ✅ **100% Complete** - All components validated (11/11)
- **Phase 2 (Core Functionality):** ✅ **80% Complete** - UET integration done, execution wiring pending
- **Overall Automation:** **65% coverage** (up from 40%)

### What Needs Wiring (Priority Order)

| Priority | Component | Status | Effort | Impact |
|----------|-----------|--------|--------|--------|
| **🔴 P0** | MINI_PIPE Executor → Task Execution | ⚠️ Simulated | 4h | Critical - No real execution |
| **🔴 P0** | Real AI Adapter Integration | ⚠️ Mock | 3h | Critical - No real gap analysis |
| **🟡 P1** | Dependency Derivation Logic | 📝 TODO | 1h | High - Task ordering |
| **🟡 P1** | Tool Execution → Actual Commands | ⚠️ Stub | 2h | High - No tool invocation |
| **🟢 P2** | Patch Ledger Integration | ❌ Not wired | 1h | Medium - Change tracking |
| **🟢 P2** | Recovery/Resilience Layer | ❌ Not wired | 1h | Medium - Error handling |
| **🔵 P3** | Performance Optimizations | 📋 Planned | 22h | Low - Speed improvements |

---

## 📋 Component-by-Component Analysis

### 1. ACMS Controller → MINI_PIPE Orchestrator (Phase 4 Execution)

**Status:** ⚠️ **Partially Wired - Uses Mock Execution**

#### Current Flow (Working)
```python
# src/acms/controller.py - _phase_4_execution()
workstreams_dir = Path(self.state.get("workstreams_dir"))
adapter = UETWorkstreamAdapter(workspace_ref=self.workspace_ref)
workstreams = adapter.load_workstreams_from_directory(workstreams_dir)

# ✅ Loading workstreams: WORKS
# ✅ Converting to execution requests: WORKS
all_requests = []
for ws in workstreams:
    requests = adapter.workstream_to_execution_requests(ws)
    all_requests.extend(requests)

# ⚠️ Execution: STUBBED
print(f"  ℹ️  Execution via orchestrator integration pending")
```

#### What's Missing
```python
# TODO: Wire MINI_PIPE orchestrator actual execution
# File: src/acms/controller.py, Line 737

# Currently missing:
# 1. Create orchestrator instance
# 2. Pass execution requests to executor
# 3. Monitor execution progress
# 4. Collect results

# Proposed wiring:
from src.minipipe.orchestrator import Orchestrator
from src.minipipe.executor import Executor
from src.minipipe.scheduler import ExecutionScheduler
from src.minipipe.router import TaskRouter

# Initialize components
db = Database(db_path=self.run_dir / "minipipe.db")
orchestrator = Orchestrator(db=db)
scheduler = ExecutionScheduler()
router = TaskRouter(config_path=self.repo_root / "config" / "tool_profiles.json")
executor = Executor(orchestrator, router, scheduler)

# Create MINI_PIPE run
run_id = orchestrator.create_run(
    project_id="acms",
    phase_id=self.run_id,
    metadata={"acms_run": self.run_id}
)

# Convert requests to tasks and execute
for req in all_requests:
    task = Task(
        task_id=req.task_id,
        task_kind=req.task_kind,
        depends_on=req.depends_on,
        metadata=req.metadata
    )
    scheduler.add_task(task)

# Execute all tasks
result = executor.run(run_id)

# Update ACMS state with results
self.state["tasks_completed"] = result.get("tasks_completed", 0)
self.state["tasks_failed"] = result.get("tasks_failed", 0)
```

**Files to Modify:**
- `src/acms/controller.py` (Line 703-745)
- `src/acms/real_minipipe_adapter.py` (Line 205 - remove TODO)

**Estimated Effort:** 4 hours
- Import wiring: 30 min
- Orchestrator initialization: 1 hour
- Task conversion: 1.5 hours
- Result collection: 1 hour

---

### 2. Real AI Adapter Integration (Phase 1 Gap Discovery)

**Status:** ⚠️ **Mock Adapter Active - No Real AI Calls**

#### Current Flow
```python
# src/acms/controller.py - _phase_1_gap_discovery()
# Line 61: ai_adapter_type defaults to "auto" but falls back to mock
self.ai_adapter = create_ai_adapter(ai_adapter_type)

# src/acms/ai_adapter.py - create_ai_adapter()
# Lines 140-166: Auto selection logic
def create_ai_adapter(adapter_type: str = "auto"):
    if adapter_type == "auto":
        # ✅ Check for API keys
        if os.getenv("OPENAI_API_KEY"):
            return OpenAIAdapter()
        elif os.getenv("ANTHROPIC_API_KEY"):
            return AnthropicAdapter()
        # ⚠️ Falls back to mock if no keys
        return MockAIAdapter()
```

#### What's Missing
```python
# TODO: Set up API keys for real adapters
# Required environment variables:

export OPENAI_API_KEY="sk-..."        # For OpenAI GPT-4
export ANTHROPIC_API_KEY="sk-ant-..."  # For Claude

# Or configure in .env file
# Create .env at repo root:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Update requirements.txt (currently commented):
# openai>=1.0.0
# anthropic>=0.8.0
```

#### Wiring Steps
1. **Install dependencies:**
   ```bash
   pip install openai>=1.0.0 anthropic>=0.8.0
   ```

2. **Set API keys:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # OR
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **Test adapter selection:**
   ```python
   from src.acms.ai_adapter import create_ai_adapter
   adapter = create_ai_adapter("auto")
   print(type(adapter).__name__)  # Should print OpenAIAdapter or AnthropicAdapter
   ```

4. **Update controller default:**
   ```python
   # src/acms/controller.py, Line 61
   # Already set to "auto" - no change needed
   ai_adapter_type: str = "auto",  # ✅ Correct
   ```

**Files to Modify:**
- `requirements.txt` (uncomment lines 20-23)
- `.env` (create if using dotenv)
- Environment setup scripts

**Estimated Effort:** 3 hours
- API key acquisition: 1 hour
- Dependency installation: 30 min
- Testing and validation: 1.5 hours

---

### 3. Dependency Derivation Logic (UET Execution Planner)

**Status:** 📝 **TODO Comments - Logic Not Implemented**

#### Missing Implementation
```python
# src/acms/uet_execution_planner.py

# Line 167: derive_gap_dependencies() - STUB
def derive_gap_dependencies(
    self, gaps: List[Gap]
) -> Dict[str, List[str]]:
    """
    Derive dependencies between gaps based on:
    - File overlap
    - Module boundaries
    - Category precedence
    
    Returns: {gap_id: [dependency_gap_ids]}
    """
    # TODO: Implement smart dependency detection
    # For now, no dependencies
    return {gap.gap_id: [] for gap in gaps}

# Line 196: derive_workstream_dependencies() - STUB
def derive_workstream_dependencies(
    self, workstreams: List[WorkstreamV1]
) -> Dict[str, List[str]]:
    """
    Derive workstream-level dependencies.
    
    Returns: {ws_id: [dependency_ws_ids]}
    """
    # TODO: Implement workstream dependency derivation
    return {ws.ws_id: [] for ws in workstreams}
```

#### Proposed Implementation
```python
def derive_gap_dependencies(
    self, gaps: List[Gap]
) -> Dict[str, List[str]]:
    """
    Derive dependencies between gaps based on:
    1. File overlap (gaps touching same files)
    2. Module boundaries (core before apps)
    3. Category precedence (tests before features)
    """
    dependencies = {}
    
    # Category precedence rules
    precedence_order = {
        "infrastructure": 0,
        "testing": 1,
        "configuration": 2,
        "documentation": 3,
        "feature": 4,
        "optimization": 5,
    }
    
    for gap in gaps:
        deps = []
        
        # Rule 1: File overlap - gaps touching same files must be ordered
        for other_gap in gaps:
            if gap.gap_id == other_gap.gap_id:
                continue
            
            # Check file overlap
            gap_files = set(gap.file_paths or [])
            other_files = set(other_gap.file_paths or [])
            
            if gap_files & other_files:  # Intersection
                # Lower category runs first
                gap_cat = precedence_order.get(gap.category, 99)
                other_cat = precedence_order.get(other_gap.category, 99)
                
                if other_cat < gap_cat:
                    deps.append(other_gap.gap_id)
        
        # Rule 2: Module boundaries - core modules before app modules
        if gap.category == "feature":
            # Feature gaps depend on infrastructure gaps
            for other_gap in gaps:
                if other_gap.category == "infrastructure":
                    deps.append(other_gap.gap_id)
        
        dependencies[gap.gap_id] = list(set(deps))  # Deduplicate
    
    return dependencies

def derive_workstream_dependencies(
    self, workstreams: List[WorkstreamV1]
) -> Dict[str, List[str]]:
    """
    Derive workstream-level dependencies.
    
    Priority order:
    1. Infrastructure workstreams (no deps)
    2. Testing workstreams (depend on infrastructure)
    3. Feature workstreams (depend on infrastructure + testing)
    """
    dependencies = {}
    
    # Group by category
    infra_ws = [ws for ws in workstreams if ws.category == "infrastructure"]
    test_ws = [ws for ws in workstreams if ws.category == "testing"]
    feature_ws = [ws for ws in workstreams if ws.category == "feature"]
    
    # Infrastructure: no dependencies
    for ws in infra_ws:
        dependencies[ws.ws_id] = []
    
    # Testing: depends on infrastructure
    for ws in test_ws:
        dependencies[ws.ws_id] = [iws.ws_id for iws in infra_ws]
    
    # Features: depends on infrastructure + testing
    for ws in feature_ws:
        deps = [iws.ws_id for iws in infra_ws]
        deps.extend([tws.ws_id for tws in test_ws])
        dependencies[ws.ws_id] = deps
    
    return dependencies
```

**Files to Modify:**
- `src/acms/uet_execution_planner.py` (Lines 167-200)

**Estimated Effort:** 1 hour
- Gap dependency logic: 30 min
- Workstream dependency logic: 20 min
- Testing: 10 min

---

### 4. Tool Execution → Actual Command Invocation

**Status:** ⚠️ **Stub - No Actual Tool Calls**

#### Current State
```python
# src/acms/real_minipipe_adapter.py - _execute_task()
# Line 205: TODO - Replace with actual tool execution

# Simulate execution success
# TODO: Replace with actual tool execution in Phase 3
execution_successful = True

if execution_successful:
    return TaskResult(
        task_id=task.task_id,
        status="completed",
        exit_code=0,
        output=f"Task {task.task_id} completed successfully",
        execution_time_seconds=time.time() - task_start,
    )
```

#### What's Missing - Real Tool Execution
```python
# src/acms/real_minipipe_adapter.py - _execute_task()
# Replace stub with actual execution

def _execute_task(self, task, orchestrator, router, run_id: str) -> TaskResult:
    """Execute a single task using actual tools"""
    task_start = time.time()
    
    try:
        # Route task to appropriate tool
        tool_config = router.route_task(task)
        
        if not tool_config:
            return TaskResult(
                task_id=task.task_id,
                status="skipped",
                exit_code=0,
                output="No tool configured for task type",
                execution_time_seconds=time.time() - task_start,
            )
        
        # ✅ REAL EXECUTION: Use SubprocessAdapter
        from core.adapters.subprocess_adapter import SubprocessAdapter
        from core.adapters.base import ToolConfig
        
        # Build tool configuration
        config = ToolConfig(
            tool_id=tool_config.get("tool_id"),
            kind=tool_config.get("kind", "tool"),
            command=tool_config.get("command"),
            capabilities=tool_config.get("capabilities", {}),
            limits=tool_config.get("limits", {}),
            safety_tier=tool_config.get("safety_tier", "medium"),
        )
        
        # Create adapter
        adapter = SubprocessAdapter(config)
        
        # Build execution request
        from core.engine.execution_request_builder import ExecutionRequestBuilder
        builder = (
            ExecutionRequestBuilder()
            .with_task(task.task_kind, task.metadata.get("description", ""))
            .with_tool(config.tool_id, config.command)
        )
        
        if constraints := task.metadata.get("constraints"):
            builder.with_constraints(constraints)
        
        request = builder.build()
        
        # ✅ EXECUTE TOOL
        result = adapter.execute(request, timeout=config.get_timeout())
        
        # Return result
        return TaskResult(
            task_id=task.task_id,
            status="completed" if result.exit_code == 0 else "failed",
            exit_code=result.exit_code,
            output=result.stdout,
            error=result.stderr if result.exit_code != 0 else None,
            execution_time_seconds=time.time() - task_start,
        )
        
    except Exception as e:
        return TaskResult(
            task_id=task.task_id,
            status="failed",
            exit_code=1,
            error=str(e),
            execution_time_seconds=time.time() - task_start,
        )
```

**Files to Modify:**
- `src/acms/real_minipipe_adapter.py` (Lines 179-232)

**Estimated Effort:** 2 hours
- SubprocessAdapter integration: 1 hour
- Error handling: 30 min
- Testing: 30 min

---

### 5. Patch Ledger Integration (Optional - REC_006)

**Status:** ❌ **Not Wired - Available But Unused**

#### Available Components (Not Connected)
```python
# src/minipipe/patch_converter.py - EXISTS
# src/minipipe/patch_ledger.py - EXISTS

# Usage pattern (not currently wired):
from src.minipipe.patch_converter import PatchConverter
from src.minipipe.patch_ledger import PatchLedger

# Initialize
converter = PatchConverter()
ledger = PatchLedger(ledger_path=self.run_dir / "patches.jsonl")

# After task execution:
patch = converter.convert_tool_output(task_result)
ledger.add_patch(patch)
ledger.mark_applied(patch.patch_id)
```

#### Wiring Location
```python
# src/minipipe/executor.py - _run_with_adapter()
# After Line 620 (inside execute_task method)

# Add after task execution:
if self.patch_ledger_enabled:
    # Convert tool output to patch
    patch = self.patch_converter.convert_output(result)
    
    # Add to ledger
    self.patch_ledger.add_patch(patch)
    
    # Track in task metadata
    task.result_metadata["patch_id"] = patch.patch_id
```

**Files to Modify:**
- `src/minipipe/executor.py` (add patch ledger support)
- `src/acms/controller.py` (add enable_patch_ledger flag)

**Estimated Effort:** 1 hour

---

### 6. Recovery/Resilience Layer (Optional - REC_006)

**Status:** ❌ **Not Wired - Components Exist But Unused**

#### Available Components
```python
# src/minipipe/circuit_breaker.py - EXISTS
# src/minipipe/circuit_breakers.py - EXISTS
# src/minipipe/retry.py - EXISTS
# src/minipipe/resilient_executor.py - EXISTS
# src/minipipe/recovery.py - EXISTS
```

#### Wiring Pattern
```python
# src/minipipe/executor.py - __init__()
# Add resilience layer option

def __init__(
    self,
    orchestrator: Orchestrator,
    router: TaskRouter,
    scheduler: ExecutionScheduler,
    enable_resilience: bool = False,  # ← NEW FLAG
    ...
):
    self.resilience_enabled = enable_resilience
    
    if self.resilience_enabled:
        from src.minipipe.resilient_executor import ResilientExecutor
        from src.minipipe.circuit_breakers import CircuitBreakerRegistry
        
        self.circuit_breakers = CircuitBreakerRegistry()
        self.resilient_executor = ResilientExecutor(
            circuit_breakers=self.circuit_breakers
        )

# Then in execute_task():
if self.resilience_enabled:
    result = self.resilient_executor.execute(
        tool_id=tool_id,
        func=lambda: self.adapter_runner(task, tool_id, run),
    )
else:
    result = self.adapter_runner(task, tool_id, run)
```

**Files to Modify:**
- `src/minipipe/executor.py` (add resilience support)
- `src/acms/controller.py` (add enable_resilience flag)

**Estimated Effort:** 1 hour

---

## 🔌 Integration Map

### Current Data Flow (What Works)

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 0: Run Configuration                                      │
│ ✅ WORKING - Controller initializes, generates run_id          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: Gap Discovery                                          │
│ ⚠️ MOCK - Uses MockAIAdapter (not real gap analysis)           │
│                                                                  │
│ controller._phase_1_gap_discovery()                            │
│   ├─► ai_adapter.analyze_gaps()  [MOCK DATA]                  │
│   └─► gap_registry.load_from_report()  [✅ WORKS]             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: Gap Consolidation & Clustering                         │
│ ✅ WORKING - UET workstreams generated correctly               │
│                                                                  │
│ controller._phase_2_gap_consolidation()                        │
│   ├─► uet_planner.cluster_gaps_to_workstreams()  [✅ WORKS]   │
│   └─► uet_planner.save_workstreams()  [✅ WORKS]              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: Plan Generation                                        │
│ ✅ WORKING - UET plans generated, backward compatible          │
│                                                                  │
│ controller._phase_3_plan_generation()                          │
│   ├─► Collects tasks from workstreams  [✅ WORKS]             │
│   └─► Generates mini_pipe_execution_plan.json  [✅ WORKS]     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 4: Execution                                              │
│ ⚠️ STUB - Loads workstreams but doesn't execute               │
│                                                                  │
│ controller._phase_4_execution()                                │
│   ├─► adapter.load_workstreams()  [✅ WORKS]                  │
│   ├─► adapter.workstream_to_execution_requests()  [✅ WORKS]  │
│   └─► orchestrator.execute() [❌ NOT WIRED - PRINT ONLY]      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Phase 5: Summary                                                │
│ ✅ WORKING - Generates reports and status                      │
│                                                                  │
│ controller._phase_5_summary()                                  │
│   └─► _generate_summary()  [✅ WORKS]                         │
└─────────────────────────────────────────────────────────────────┘
```

---

### Target Data Flow (Fully Wired)

```
┌──────────────────┐
│ ACMS Controller  │
└────────┬─────────┘
         │
         ├─► AI Adapter ──────► [OpenAI/Anthropic API]  ← P0: Wire real AI
         │                      (gap discovery)
         │
         ├─► Gap Registry ─────► [SQLite/JSON]  ✅ WORKING
         │                      (gap tracking)
         │
         ├─► UET Planner ──────► [Workstreams]  ✅ WORKING
         │                      (task clustering)
         │
         └─► MINI_PIPE Adapter
                   │
                   └─► MINI_PIPE Orchestrator  ← P0: Wire execution
                             │
                             ├─► Scheduler ─────► [Task DAG]  ✅ WORKING
                             │
                             ├─► Router ────────► [Tool Selection]  ✅ WORKING
                             │
                             └─► Executor
                                      │
                                      ├─► SubprocessAdapter ─► [Real Tools]  ← P1: Wire tools
                                      │                        (gh copilot, pytest, etc.)
                                      │
                                      ├─► Patch Converter ───► [Patch Ledger]  ← P2: Optional
                                      │                        (change tracking)
                                      │
                                      └─► Circuit Breakers ──► [Resilience]  ← P2: Optional
                                                               (retry, recovery)
```

---

## 📊 Priority Matrix

### P0 (Critical - Blocking Core Functionality)

#### 1. Wire MINI_PIPE Orchestrator Execution (4 hours)
**Why Critical:** Without this, no actual code changes occur
- **Current:** Loads workstreams, prints "execution pending"
- **Target:** Actually executes tasks via orchestrator
- **Impact:** Enables end-to-end automation
- **Blocker for:** Real gap fixes, automated PRs, full pipeline

#### 2. Wire Real AI Adapter (3 hours)
**Why Critical:** Without this, gap discovery is fake
- **Current:** Returns mock gap data
- **Target:** Real GPT-4/Claude gap analysis
- **Impact:** Finds real issues in codebase
- **Blocker for:** Actual gap resolution, meaningful runs

**Total P0 Effort:** 7 hours

---

### P1 (High - Needed for Production)

#### 3. Implement Dependency Derivation (1 hour)
**Why High:** Task ordering prevents conflicts
- **Current:** All tasks independent (no dependencies)
- **Target:** Smart dependency graph
- **Impact:** Prevents file conflicts, correct execution order
- **Blocker for:** Complex multi-module changes

#### 4. Wire Tool Execution (2 hours)
**Why High:** Tools need to actually run
- **Current:** Simulates tool success
- **Target:** Invokes gh copilot, pytest, linters
- **Impact:** Real code fixes
- **Blocker for:** Automated code generation

**Total P1 Effort:** 3 hours

---

### P2 (Medium - Quality/Robustness)

#### 5. Wire Patch Ledger (1 hour)
**Why Medium:** Adds granular change tracking
- **Current:** Changes not tracked individually
- **Target:** Per-file patch ledger with rollback
- **Impact:** Better debugging, selective rollback
- **Blocker for:** Advanced change management

#### 6. Wire Resilience Layer (1 hour)
**Why Medium:** Improves reliability
- **Current:** No retry/circuit breaking
- **Target:** Automatic retry, failure isolation
- **Impact:** More robust execution
- **Blocker for:** Production reliability

**Total P2 Effort:** 2 hours

---

### P3 (Low - Optimization)

#### 7. Performance Optimizations (22 hours)
**Why Low:** System works, just slower
- See: `OPTIMIZATION_ACTION_PLAN.md`
- 11 O(n) → O(1) conversions
- Large file refactoring
- Profiling infrastructure

**Total P3 Effort:** 22 hours

---

## 🎯 Recommended Execution Plan

### Sprint 1: Core Wiring (1 Week - 10 Hours)
**Goal:** Get end-to-end execution working with real AI

**Day 1-2 (7 hours):**
1. ✅ Wire MINI_PIPE orchestrator execution (4h)
2. ✅ Wire real AI adapter (3h)

**Day 3 (3 hours):**
3. ✅ Implement dependency derivation (1h)
4. ✅ Wire tool execution (2h)

**Outcome:** Fully functional automated gap-fix pipeline

---

### Sprint 2: Robustness (3 Days - 4 Hours)
**Goal:** Add tracking and resilience

**Day 1 (2 hours):**
1. Wire patch ledger (1h)
2. Wire resilience layer (1h)

**Day 2-3 (2 hours):**
3. Integration testing
4. Documentation updates

**Outcome:** Production-ready pipeline with recovery

---

### Sprint 3: Optimization (2 Weeks - 22 Hours)
**Goal:** Performance improvements
- Follow `OPTIMIZATION_ACTION_PLAN.md`
- Measure before/after
- Continuous profiling

**Outcome:** 2-3x faster execution

---

## 🔍 Validation Checklist

### After P0 Wiring (Critical)
- [ ] Real AI adapter returns actual gaps (not mock data)
- [ ] MINI_PIPE orchestrator creates run record
- [ ] Tasks execute via executor
- [ ] Tools are invoked (gh copilot, pytest, etc.)
- [ ] Results persisted to database
- [ ] E2E test creates real code changes

### After P1 Wiring (High Priority)
- [ ] Dependencies prevent file conflicts
- [ ] Tasks execute in correct order
- [ ] SubprocessAdapter invokes tools
- [ ] Tool output captured correctly

### After P2 Wiring (Medium Priority)
- [ ] Patches tracked in ledger
- [ ] Circuit breakers prevent cascading failures
- [ ] Retries occur on transient failures
- [ ] Recovery patterns triggered

---

## 📁 Files Requiring Changes

### Critical Changes (P0)
1. **src/acms/controller.py**
   - Line 737: Wire orchestrator execution
   - Line 61: Already using "auto" adapter ✅

2. **src/acms/ai_adapter.py**
   - Already has "auto" selection ✅
   - Just needs API keys in environment

3. **requirements.txt**
   - Uncomment lines 20-23 (openai, anthropic)

### High Priority Changes (P1)
4. **src/acms/uet_execution_planner.py**
   - Line 167: Implement derive_gap_dependencies()
   - Line 196: Implement derive_workstream_dependencies()

5. **src/acms/real_minipipe_adapter.py**
   - Line 205: Replace execution stub with SubprocessAdapter

### Medium Priority Changes (P2)
6. **src/minipipe/executor.py**
   - Add patch_ledger_enabled flag
   - Add resilience_enabled flag
   - Wire converters and circuit breakers

---

## 💡 Quick Wins (< 1 Hour Each)

### 1. Enable Real AI (30 min)
```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-key"

# Test
python -c "
from src.acms.ai_adapter import create_ai_adapter
adapter = create_ai_adapter('auto')
print(f'Using: {type(adapter).__name__}')
"
```

### 2. Dependency Derivation (1 hour)
- Copy proposed implementation above
- Paste into `uet_execution_planner.py`
- Run e2e tests to validate

### 3. Notifications Already Wired ✅ (0 min)
- Just set environment variables:
```bash
export ACMS_SLACK_WEBHOOK="https://hooks.slack.com/..."
export ACMS_GITHUB_REPO="owner/repo"
```

---

## 🚨 Critical Gaps Summary

| Gap | Impact | Effort | Status |
|-----|--------|--------|--------|
| **No Real Execution** | No code changes | 4h | ⚠️ P0 |
| **Mock AI Only** | No real gap finding | 3h | ⚠️ P0 |
| **No Dependencies** | File conflicts | 1h | 📝 P1 |
| **Simulated Tools** | No actual fixes | 2h | 📝 P1 |
| **No Patch Tracking** | Can't rollback | 1h | ❌ P2 |
| **No Resilience** | Brittle execution | 1h | ❌ P2 |

---

## 📈 Expected Outcomes After Wiring

### After P0 (7 hours)
- ✅ Real AI gap analysis
- ✅ Actual task execution
- ✅ Code changes committed
- ✅ End-to-end automation: 40% → 85%

### After P1 (10 hours total)
- ✅ Smart dependency ordering
- ✅ Real tool invocation
- ✅ Production-ready pipeline
- ✅ Automation coverage: 85% → 90%

### After P2 (12 hours total)
- ✅ Granular change tracking
- ✅ Automatic recovery
- ✅ Enterprise-grade reliability
- ✅ Automation coverage: 90% → 95%

---

## 🎓 Key Insights

### What's Already Built (Good News)
1. ✅ **Infrastructure complete** - Orchestrator, scheduler, router all work
2. ✅ **Monitoring & notifications** - Already wired and validated
3. ✅ **UET integration** - Workstream generation fully functional
4. ✅ **E2E tests** - All passing, just need real execution
5. ✅ **Auto adapter** - Smart selection based on API keys

### What's Missing (Wiring Needed)
1. ⚠️ **Execution glue** - Connect controller → orchestrator → executor
2. ⚠️ **API keys** - Set OPENAI_API_KEY or ANTHROPIC_API_KEY
3. 📝 **Dependency logic** - Implement smart ordering
4. 📝 **Tool invocation** - Call actual gh copilot, pytest, etc.
5. ❌ **Optional features** - Patch ledger, resilience (nice-to-have)

### Best Path Forward
**Start with P0 (7 hours)** - This unblocks everything else:
1. Set API key (5 min)
2. Wire orchestrator execution (4h)
3. Test end-to-end (30 min)
4. Celebrate first real automated gap fix! 🎉

---

**Analysis Complete**  
**Total Critical Wiring:** 7 hours (P0)  
**Total High Priority:** 3 hours (P1)  
**Total Production-Ready:** 10 hours (P0+P1)

**Next Step:** Start with P0 wiring (see Sprint 1 plan above)
