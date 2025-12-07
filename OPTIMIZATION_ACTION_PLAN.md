# MINI_PIPE Codebase Optimization Action Plan

**Generated:** 2025-12-07  
**Based on:**
1. Comprehensive Gap-Finding Framework
2. Codebase Efficiency and Performance Optimization Opportunities
3. Python & PowerShell Performance Optimization Guide

---

## Executive Summary

This action plan provides a systematic, data-driven approach to optimizing the MINI_PIPE codebase. Following industry best practices, all optimization efforts **must begin with measurement** before implementing changes.

**Key Finding:** 11 O(n) list membership checks detected across the codebase, along with 14 large files (>300 lines) that may benefit from modular refactoring.

---

## Phase 1: Measurement & Baseline (Week 1)

### Objective
Establish performance baselines and identify actual bottlenecks using profiling tools.

### Actions

#### 1.1 Install Profiling Tools
```bash
pip install py-spy line_profiler cProfile-prettytable
```

#### 1.2 Production-Safe Profiling with py-spy
```bash
# For long-running processes
py-spy record -o profile.svg --pid <PID>

# For script execution
py-spy record -o profile.svg -- python src/cli/demo_acms_pipeline.py
```

**Deliverable:** Flame graph visualization showing CPU time distribution
- **Wide blocks** = High CPU consumption (optimization targets)
- **Deep stacks** = Call chain complexity

#### 1.3 Deterministic Profiling with cProfile
```bash
python -m cProfile -o profile.stats src/cli/demo_acms_pipeline.py
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)  # Top 20 by cumulative time
p.sort_stats('time').print_stats(20)        # Top 20 by internal time
"
```

**Deliverable:** Ranked list of functions by execution time

#### 1.4 Line-Level Analysis (for identified hot functions)
```bash
kernprof -l -v hot_function_file.py
```

**Deliverable:** Line-by-line execution time breakdown

### Success Criteria
- [ ] Flame graph generated
- [ ] Top 10 CPU-consuming functions identified
- [ ] Hot paths documented with % CPU time
- [ ] Baseline metrics recorded (total execution time, memory usage)

---

## Phase 2: Algorithmic Optimization (Week 2-3)

### 2.1 O(n) → O(1) List Lookup Conversion

**Priority:** HIGH  
**Impact:** Non-linear performance improvement for large datasets  
**Guide Reference:** Section 2.2.1 - The O(n) Look-up Code Smell

#### Identified Instances

| File | Line | Current Code | Optimized Code |
|------|------|--------------|----------------|
| `src/acms/ai_adapter.py` | 355 | `if adapter_type in ["openai", "anthropic"]:` | `VALID_ADAPTERS = {"openai", "anthropic"}` <br> `if adapter_type in VALID_ADAPTERS:` |
| `src/acms/controller.py` | 280 | `if mode in ["full", "analyze_only", "plan_only"]:` | `VALID_MODES = {"full", "analyze_only", "plan_only"}` <br> `if mode in VALID_MODES:` |
| `src/acms/controller.py` | 292 | `if mode in ["full", "plan_only", "execute_only"]:` | Use set-based lookup |
| `src/acms/controller.py` | 314 | `if mode in ["full", "execute_only"]:` | Use set-based lookup |
| `src/acms/controller.py` | 380 | `if g.status.value in ["resolved", "verified"]):` | `TERMINAL_STATUSES = {"resolved", "verified"}` |

**Implementation Pattern:**
```python
# BEFORE (O(n) lookup)
if status in ["pending", "active", "completed", "failed"]:
    process_status(status)

# AFTER (O(1) lookup)
VALID_STATUSES = {"pending", "active", "completed", "failed"}  # Define once at module level
if status in VALID_STATUSES:
    process_status(status)
```

**Testing:**
- Unit tests should pass without modification
- Benchmark before/after for collections with >100 items

### 2.2 Efficient Collection Building

**Priority:** MEDIUM  
**Impact:** Reduces O(n²) complexity in loop-based list building

```python
# BEFORE (inefficient for large collections)
results = []
for item in large_dataset:
    results.append(process(item))

# AFTER (optimal)
results = [process(item) for item in large_dataset]  # List comprehension

# OR for complex logic
from collections import deque
results = deque()  # O(1) append on both ends
for item in large_dataset:
    results.append(process(item))
results = list(results)
```

### Success Criteria
- [ ] All 11 list membership checks converted to set/dict
- [ ] No performance regressions (verified by profiling)
- [ ] Unit tests pass
- [ ] Before/after benchmark documented

---

## Phase 3: Structural Improvements (Week 4-5)

### 3.1 God Object Refactoring

**Priority:** MEDIUM (long-term maintainability)  
**Impact:** Improved testability, clearer profiling results

#### Large Files Identified (>300 lines)

| File | Lines | Size | Recommendation |
|------|-------|------|----------------|
| `src/acms/controller.py` | 769 | 31KB | Split into: `controller_core.py`, `controller_phases.py`, `controller_state.py` |
| `src/minipipe/orchestrator.py` | 695 | 22KB | Extract: `orchestrator_tasks.py`, `orchestrator_execution.py` |
| `src/minipipe/router.py` | 675 | 24KB | Extract: `router_rules.py`, `router_dispatch.py` |
| `src/minipipe/patch_ledger.py` | 642 | 19KB | Extract: `ledger_storage.py`, `ledger_queries.py` |
| `src/minipipe/executor.py` | 621 | 23KB | Extract: `executor_runtime.py`, `executor_monitoring.py` |

**Refactoring Strategy:**
1. Identify cohesive responsibility groups within each file
2. Extract into separate modules with clear interfaces
3. Use composition over inheritance
4. Maintain backward compatibility via facade pattern

**Example for `controller.py`:**
```python
# controller_core.py - Core orchestration logic
# controller_phases.py - Phase execution (GAP, PLAN, EXEC)
# controller_state.py - State management and persistence

# controller.py (facade)
from .controller_core import ACMSController
from .controller_phases import PhaseExecutor
from .controller_state import StateManager

class ACMSController:
    def __init__(self, ...):
        self._executor = PhaseExecutor(...)
        self._state = StateManager(...)
        self._core = ControllerCore(self._executor, self._state)
```

### Success Criteria
- [ ] No single file exceeds 400 lines
- [ ] Each module has single, clear responsibility
- [ ] Profiling shows clearer function attribution
- [ ] All tests pass without modification

---

## Phase 4: Performance Enhancement (Week 6)

### 4.1 Caching Implementation

**Priority:** HIGH (if profiling identifies repeated computation)  
**Guide Reference:** Section 4.4 - Strategic Caching

```python
from functools import lru_cache

# For pure functions with deterministic output
@lru_cache(maxsize=128)
def expensive_computation(input_data):
    # ... heavy calculation
    return result

# For methods (use cache per instance)
from cachetools import cached, TTLCache

class DataProcessor:
    def __init__(self):
        self._cache = TTLCache(maxsize=100, ttl=300)  # 5 min TTL
    
    @cached(cache=lambda self: self._cache)
    def process_data(self, key):
        # ... expensive operation
        return result
```

**Monitoring:**
```python
# Add cache metrics
print(f"Cache info: {expensive_computation.cache_info()}")
# CacheInfo(hits=45, misses=10, maxsize=128, currsize=10)
```

### 4.2 Logging Optimization

**Priority:** MEDIUM  
**Guide Reference:** Section 4.2.1 - Unoptimized Logging

```python
import logging

logger = logging.getLogger(__name__)

# BEFORE (always formats, even if not logged)
logger.debug(f"Processing {len(items)} items: {expensive_format(items)}")

# AFTER (guarded logging)
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Processing {len(items)} items: {expensive_format(items)}")

# BEST (lazy evaluation)
logger.debug("Processing %d items: %s", len(items), lambda: expensive_format(items))
```

### 4.3 I/O Optimization

**For frequent file operations:**
```python
# BEFORE
for item in large_list:
    with open(f"output_{item}.txt", "w") as f:
        f.write(process(item))

# AFTER (buffered, batch writes)
from io import StringIO

buffer = StringIO()
for item in large_list:
    buffer.write(process(item) + "\n")

with open("output_batch.txt", "w") as f:
    f.write(buffer.getvalue())
```

### Success Criteria
- [ ] Cache hit rate >80% for cached functions
- [ ] Logging overhead <5% of execution time
- [ ] File I/O reduced by batching operations
- [ ] Overall execution time reduced by 20%+

---

## Phase 5: Database & External I/O (Week 7)

### 5.1 N+1 Query Detection

**Priority:** HIGH (if database operations detected in profiling)  
**Guide Reference:** Section 4.1 - N+1 Query Problem

**Detection:**
```python
# Enable query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Look for patterns like:
# SELECT * FROM users
# SELECT * FROM posts WHERE user_id=1
# SELECT * FROM posts WHERE user_id=2
# ... (N queries for N users)
```

**Fix (for SQLAlchemy):**
```python
# BEFORE (lazy loading - N+1 queries)
users = session.query(User).all()
for user in users:
    print(user.posts)  # Triggers separate query per user

# AFTER (eager loading - single join query)
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded
```

### Success Criteria
- [ ] No N+1 query patterns detected
- [ ] Database queries reduced by >50%
- [ ] API response time improved by >30%

---

## Phase 6: Concurrency Strategy (Week 8) - If Needed

**Prerequisite:** Profiling shows CPU-bound bottlenecks  
**Guide Reference:** Section 2.1 - Managing the GIL

### 6.1 Workload Classification

| Workload Type | Characteristics | Solution |
|--------------|-----------------|----------|
| **CPU-Bound** | Heavy computation, minimal I/O | `multiprocessing.Pool` |
| **I/O-Bound (slow)** | Network calls, DB queries | `asyncio` |
| **I/O-Bound (fast)** | File I/O, simple APIs | `threading.ThreadPoolExecutor` |

### 6.2 Implementation Example (CPU-Bound)

```python
from multiprocessing import Pool

def expensive_calculation(data):
    # Pure function, no shared state
    return complex_computation(data)

# BEFORE (sequential)
results = [expensive_calculation(item) for item in large_dataset]

# AFTER (parallel)
with Pool(processes=4) as pool:
    results = pool.map(expensive_calculation, large_dataset)
```

### 6.3 Implementation Example (I/O-Bound)

```python
import asyncio
import aiohttp

async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# BEFORE (sequential)
results = [fetch_data(url) for url in urls]

# AFTER (concurrent)
async def fetch_all():
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)

results = asyncio.run(fetch_all())
```

### Success Criteria
- [ ] CPU-bound tasks show linear speedup with cores
- [ ] I/O-bound tasks show >5x improvement
- [ ] No race conditions or deadlocks
- [ ] Memory usage remains within acceptable bounds

---

## Measurement & Validation

### Before Each Phase
1. Run profiling suite
2. Document baseline metrics
3. Identify specific optimization targets

### After Each Change
1. Re-run profiling
2. Compare before/after metrics
3. Run full test suite
4. Document improvements

### Key Metrics to Track

| Metric | Tool | Target |
|--------|------|--------|
| Total execution time | `time` command | -20% minimum |
| Function call count | `cProfile` | Reduce top offenders |
| Memory usage | `memory_profiler` | No regression |
| Cache hit rate | Custom logging | >80% |
| Test coverage | `pytest-cov` | >85% maintained |

---

## Risk Mitigation

### Safety Measures
1. **Version Control:** All optimizations in feature branches
2. **Testing:** Full test suite passes before merge
3. **Rollback Plan:** Keep original implementation for 1 sprint
4. **Performance Tests:** Automated benchmarks in CI/CD

### Red Flags
- Performance regression in any metric
- Test failures
- Increased memory usage >20%
- Code complexity increase (cyclomatic complexity)

---

## Tools & Resources

### Required Tools
```bash
pip install py-spy line_profiler memory_profiler pytest-benchmark cachetools
```

### Recommended Reading
1. "High Performance Python" by Micha Gorelick
2. Python's official profiling documentation
3. Guide documents provided (already reviewed)

### Useful Commands
```bash
# Quick profile
python -m cProfile -s cumulative script.py | head -20

# Memory profiling
python -m memory_profiler script.py

# Benchmark comparison
pytest tests/ --benchmark-only --benchmark-compare
```

---

## Conclusion

This action plan prioritizes **measurement-driven optimization** following industry best practices:

1. **Measure First:** Use py-spy and cProfile to identify actual bottlenecks
2. **Fix Algorithms:** Convert O(n) to O(1) operations (11 instances)
3. **Refactor Structure:** Break down large files for maintainability
4. **Add Caching:** Reduce redundant computation
5. **Optimize I/O:** Batch operations, guard logging
6. **Parallelize (if needed):** Only after profiling confirms benefit

**Expected Overall Impact:**
- Execution time: -20% to -40%
- Code maintainability: Improved (smaller modules)
- Test coverage: Maintained at >85%
- Memory usage: No regression

**Timeline:** 8 weeks for full implementation
**Effort:** ~40 hours of focused optimization work
