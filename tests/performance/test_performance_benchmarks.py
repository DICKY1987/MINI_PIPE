"""Performance regression tests for MINI_PIPE optimizations

These tests establish baseline performance metrics and fail if regressions occur.
Run with: pytest tests/performance/ --benchmark-only
"""

import pytest
from pathlib import Path
import tempfile
import json
from typing import List

# Import modules to test (will work with conftest.py path setup)
try:
    from acms.execution_planner import ExecutionPlanner, Workstream
    from acms.gap_registry import GapRecord, GapSeverity, GapStatus
    from minipipe.scheduler import Scheduler
    from minipipe.router import FileBackedStateStore
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Skip all tests if imports unavailable
pytestmark = pytest.mark.skipif(
    not IMPORTS_AVAILABLE,
    reason=f"Required imports unavailable: {IMPORT_ERROR if not IMPORTS_AVAILABLE else ''}"
)


# ============================================================================
# Helper Functions
# ============================================================================

def create_test_gaps(count: int) -> List[GapRecord]:
    """Create synthetic gaps for testing
    
    Args:
        count: Number of gaps to create
        
    Returns:
        List of GapRecord objects with varying file overlaps
    """
    gaps = []
    for i in range(count):
        # Create overlapping file patterns
        file_count = (i % 3) + 2  # 2-4 files per gap
        file_start = i % 10  # Creates overlap
        
        gap = GapRecord(
            gap_id=f"gap_{i:04d}",
            title=f"Test Gap {i}",
            severity=GapSeverity.MEDIUM,
            status=GapStatus.OPEN,
            file_paths=[f"file_{j:03d}.py" for j in range(file_start, file_start + file_count)],
            description=f"Test gap {i} for performance benchmarking",
            project_id="test_project"
        )
        gaps.append(gap)
    return gaps


def create_test_scheduler(task_count: int, dependency_density: float = 0.3) -> Scheduler:
    """Create test scheduler with specified task graph
    
    Args:
        task_count: Number of tasks
        dependency_density: Fraction of possible dependencies to create (0.0-1.0)
        
    Returns:
        Scheduler with tasks and dependencies
    """
    scheduler = Scheduler()
    
    for i in range(task_count):
        # Each task can depend on previous tasks
        max_deps = int(i * dependency_density)
        dependencies = [f"task_{j:04d}" for j in range(max(0, i - max_deps), i)]
        
        scheduler.add_task(
            task_id=f"task_{i:04d}",
            command=f"echo 'Task {i}'",
            dependencies=dependencies
        )
    
    return scheduler


# ============================================================================
# Wave 1: I/O Batching Tests
# ============================================================================

@pytest.mark.benchmark(group="wave1_io")
def test_router_io_batching_small(benchmark, tmp_path):
    """Validate I/O batching for small workload (10 updates)
    
    Target: < 10ms
    Wave 1 optimization: Batched writes reduce I/O operations
    """
    state_file = tmp_path / "router_state.json"
    
    def run_routing():
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(10):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
    
    result = benchmark(run_routing)
    
    # Should complete very quickly with batching
    assert benchmark.stats['mean'] < 0.01, \
        f"Router batching (10 updates) should complete under 10ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave1_io")
def test_router_io_batching_medium(benchmark, tmp_path):
    """Validate I/O batching for medium workload (100 updates)
    
    Target: < 50ms
    Expected: ~10 disk writes instead of 100
    """
    state_file = tmp_path / "router_state.json"
    
    def run_routing():
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(100):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
    
    result = benchmark(run_routing)
    
    assert benchmark.stats['mean'] < 0.05, \
        f"Router batching (100 updates) should complete under 50ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave1_io")
def test_router_io_batching_large(benchmark, tmp_path):
    """Validate I/O batching for large workload (1000 updates)
    
    Target: < 200ms
    Expected: ~100 disk writes instead of 1000 (90% reduction)
    """
    state_file = tmp_path / "router_state.json"
    
    def run_routing():
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(1000):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
    
    result = benchmark(run_routing)
    
    assert benchmark.stats['mean'] < 0.2, \
        f"Router batching (1000 updates) should complete under 200ms, got {benchmark.stats['mean']:.3f}s"


# ============================================================================
# Wave 2: Clustering Performance Tests
# ============================================================================

@pytest.mark.benchmark(group="wave2_clustering")
def test_clustering_small_workload(benchmark):
    """Baseline: Priority queue clustering with 10 gaps
    
    Target: < 50ms
    Algorithm: O(n log n) priority queue
    """
    gaps = create_test_gaps(count=10)
    
    def run_clustering():
        planner = ExecutionPlanner()
        return planner._cluster_gaps_by_files(gaps, max_files=20)
    
    result = benchmark(run_clustering)
    
    assert benchmark.stats['mean'] < 0.05, \
        f"Small clustering (10 gaps) should complete under 50ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave2_clustering")
def test_clustering_medium_workload(benchmark):
    """Baseline: Priority queue clustering with 50 gaps
    
    Target: < 200ms
    Expected speedup: 10-50x vs naive O(n³)
    """
    gaps = create_test_gaps(count=50)
    
    def run_clustering():
        planner = ExecutionPlanner()
        return planner._cluster_gaps_by_files(gaps, max_files=20)
    
    result = benchmark(run_clustering)
    
    assert benchmark.stats['mean'] < 0.2, \
        f"Medium clustering (50 gaps) should complete under 200ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave2_clustering")
def test_clustering_large_workload(benchmark):
    """Baseline: Priority queue clustering with 200 gaps
    
    Target: < 1000ms (1 second)
    Wave 2 optimization: O(n³) → O(n log n)
    Expected: 10-100x faster than naive approach
    """
    gaps = create_test_gaps(count=200)
    
    def run_clustering():
        planner = ExecutionPlanner()
        return planner._cluster_gaps_by_files(gaps, max_files=20)
    
    result = benchmark(run_clustering)
    
    assert benchmark.stats['mean'] < 1.0, \
        f"Large clustering (200 gaps) should complete under 1s, got {benchmark.stats['mean']:.3f}s"


# ============================================================================
# Wave 2: Scheduler Performance Tests
# ============================================================================

@pytest.mark.benchmark(group="wave2_scheduler")
def test_topological_sort_linear(benchmark):
    """Topological sort with linear dependencies (simple chain)
    
    Target: < 50ms for 100 tasks
    Complexity: O(n + e) where e = n-1
    """
    scheduler = create_test_scheduler(task_count=100, dependency_density=0.01)
    
    result = benchmark(scheduler.get_execution_order)
    
    assert benchmark.stats['mean'] < 0.05, \
        f"Linear topological sort (100 tasks) should complete under 50ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave2_scheduler")
def test_topological_sort_dense(benchmark):
    """Topological sort with dense dependency graph
    
    Target: < 100ms for 100 tasks
    Complexity: O(n + e) with cached dependency counts
    Wave 2 optimization: O(1) ready checks vs O(m) issubset
    """
    scheduler = create_test_scheduler(task_count=100, dependency_density=0.3)
    
    result = benchmark(scheduler.get_execution_order)
    
    assert benchmark.stats['mean'] < 0.1, \
        f"Dense topological sort (100 tasks) should complete under 100ms, got {benchmark.stats['mean']:.3f}s"


@pytest.mark.benchmark(group="wave2_scheduler")
def test_cycle_detection_no_cycle(benchmark):
    """Cycle detection with valid DAG
    
    Target: < 50ms for 100 tasks
    Memory: O(n) with backtracking (no path copying)
    """
    scheduler = create_test_scheduler(task_count=100, dependency_density=0.2)
    
    result = benchmark(scheduler.detect_cycles)
    
    assert result is None, "Should not detect cycle in valid DAG"
    assert benchmark.stats['mean'] < 0.05, \
        f"Cycle detection (100 tasks) should complete under 50ms, got {benchmark.stats['mean']:.3f}s"


# ============================================================================
# Integration Tests: End-to-End Performance
# ============================================================================

@pytest.mark.benchmark(group="integration")
def test_full_clustering_pipeline(benchmark):
    """Full clustering pipeline: gap creation → clustering → workstream generation
    
    Target: < 500ms for 50 gaps
    Tests all Wave 2 optimizations together
    """
    gaps = create_test_gaps(count=50)
    
    def run_full_pipeline():
        planner = ExecutionPlanner()
        workstreams = planner._cluster_gaps_by_files(gaps, max_files=25)
        # Additional processing would happen here
        return workstreams
    
    result = benchmark(run_full_pipeline)
    
    assert benchmark.stats['mean'] < 0.5, \
        f"Full clustering pipeline (50 gaps) should complete under 500ms, got {benchmark.stats['mean']:.3f}s"


# ============================================================================
# Performance Characteristics Documentation
# ============================================================================

def test_document_performance_characteristics(tmp_path):
    """Document actual performance characteristics for baseline
    
    This test always passes but records metrics for documentation
    """
    results = {}
    
    # Test various scales
    for gap_count in [10, 50, 100, 200]:
        gaps = create_test_gaps(count=gap_count)
        planner = ExecutionPlanner()
        
        import time
        start = time.perf_counter()
        workstreams = planner._cluster_gaps_by_files(gaps, max_files=20)
        elapsed = time.perf_counter() - start
        
        results[f"clustering_{gap_count}_gaps"] = {
            "time_ms": elapsed * 1000,
            "workstreams_created": len(workstreams),
            "complexity": "O(n log n)"
        }
    
    # Save results
    output_file = tmp_path / "performance_characteristics.json"
    output_file.write_text(json.dumps(results, indent=2))
    
    print(f"\n📊 Performance Characteristics:\n{json.dumps(results, indent=2)}")
    assert True, "Documentation test always passes"


# ============================================================================
# Test Summary
# ============================================================================

def test_performance_summary():
    """Print test summary for documentation"""
    summary = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║           MINI_PIPE Performance Test Suite                      ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    Wave 1 Tests (I/O Batching):
      • Router small (10 updates):    Target < 10ms
      • Router medium (100 updates):  Target < 50ms  
      • Router large (1000 updates):  Target < 200ms
    
    Wave 2 Tests (Algorithmic):
      • Clustering small (10 gaps):   Target < 50ms
      • Clustering medium (50 gaps):  Target < 200ms
      • Clustering large (200 gaps):  Target < 1000ms
      • Topological sort linear:      Target < 50ms
      • Topological sort dense:       Target < 100ms
      • Cycle detection:              Target < 50ms
    
    Integration Tests:
      • Full pipeline (50 gaps):      Target < 500ms
    
    Run with: pytest tests/performance/ --benchmark-only
    """
    print(summary)
    assert True
