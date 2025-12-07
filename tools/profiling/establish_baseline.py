"""Baseline performance measurement script

This script establishes baseline performance metrics for the MINI_PIPE codebase.
Run this to create initial benchmarks before any changes.

Usage:
    python tools/profiling/establish_baseline.py [--output-dir .performance/baselines]
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def measure_router_performance() -> Dict[str, Any]:
    """Measure router I/O batching performance"""
    from minipipe.router import FileBackedStateStore
    import tempfile
    
    results = {}
    
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "router_state.json"
        
        # Test small workload (10 updates)
        start = time.perf_counter()
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(10):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
        elapsed_small = time.perf_counter() - start
        
        # Test medium workload (100 updates)
        state_file.unlink(missing_ok=True)
        start = time.perf_counter()
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(100):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
        elapsed_medium = time.perf_counter() - start
        
        # Test large workload (1000 updates)
        state_file.unlink(missing_ok=True)
        start = time.perf_counter()
        store = FileBackedStateStore(str(state_file), auto_save_interval=10)
        for i in range(1000):
            store.set_round_robin_index(f"rule_{i}", i)
        store.flush()
        elapsed_large = time.perf_counter() - start
    
    results = {
        "router_batching_small": {
            "time_ms": elapsed_small * 1000,
            "updates": 10,
            "target_ms": 10,
            "pass": elapsed_small * 1000 < 10
        },
        "router_batching_medium": {
            "time_ms": elapsed_medium * 1000,
            "updates": 100,
            "target_ms": 50,
            "pass": elapsed_medium * 1000 < 50
        },
        "router_batching_large": {
            "time_ms": elapsed_large * 1000,
            "updates": 1000,
            "target_ms": 200,
            "pass": elapsed_large * 1000 < 200
        }
    }
    
    return results


def measure_clustering_performance() -> Dict[str, Any]:
    """Measure clustering algorithm performance"""
    from acms.execution_planner import ExecutionPlanner
    from acms.gap_registry import GapRecord, GapSeverity, GapStatus
    
    def create_test_gaps(count: int) -> List:
        gaps = []
        for i in range(count):
            file_count = (i % 3) + 2
            file_start = i % 10
            gap = GapRecord(
                gap_id=f"gap_{i:04d}",
                title=f"Test Gap {i}",
                severity=GapSeverity.MEDIUM,
                status=GapStatus.OPEN,
                file_paths=[f"file_{j:03d}.py" for j in range(file_start, file_start + file_count)],
                description=f"Test gap {i}",
                project_id="test_project"
            )
            gaps.append(gap)
        return gaps
    
    results = {}
    planner = ExecutionPlanner()
    
    # Test small workload (10 gaps)
    gaps = create_test_gaps(10)
    start = time.perf_counter()
    workstreams = planner._cluster_gaps_by_files(gaps, max_files=20)
    elapsed_small = time.perf_counter() - start
    
    # Test medium workload (50 gaps)
    gaps = create_test_gaps(50)
    start = time.perf_counter()
    workstreams = planner._cluster_gaps_by_files(gaps, max_files=20)
    elapsed_medium = time.perf_counter() - start
    
    # Test large workload (200 gaps)
    gaps = create_test_gaps(200)
    start = time.perf_counter()
    workstreams = planner._cluster_gaps_by_files(gaps, max_files=20)
    elapsed_large = time.perf_counter() - start
    
    results = {
        "clustering_small": {
            "time_ms": elapsed_small * 1000,
            "gaps": 10,
            "target_ms": 50,
            "pass": elapsed_small * 1000 < 50
        },
        "clustering_medium": {
            "time_ms": elapsed_medium * 1000,
            "gaps": 50,
            "target_ms": 200,
            "pass": elapsed_medium * 1000 < 200
        },
        "clustering_large": {
            "time_ms": elapsed_large * 1000,
            "gaps": 200,
            "target_ms": 1000,
            "pass": elapsed_large * 1000 < 1000
        }
    }
    
    return results


def measure_scheduler_performance() -> Dict[str, Any]:
    """Measure scheduler performance"""
    from minipipe.scheduler import Scheduler
    
    def create_test_scheduler(task_count: int, density: float = 0.3):
        scheduler = Scheduler()
        for i in range(task_count):
            max_deps = int(i * density)
            dependencies = [f"task_{j:04d}" for j in range(max(0, i - max_deps), i)]
            scheduler.add_task(
                task_id=f"task_{i:04d}",
                command=f"echo 'Task {i}'",
                dependencies=dependencies
            )
        return scheduler
    
    results = {}
    
    # Test linear dependencies
    scheduler = create_test_scheduler(100, density=0.01)
    start = time.perf_counter()
    order = scheduler.get_execution_order()
    elapsed_linear = time.perf_counter() - start
    
    # Test dense dependencies
    scheduler = create_test_scheduler(100, density=0.3)
    start = time.perf_counter()
    order = scheduler.get_execution_order()
    elapsed_dense = time.perf_counter() - start
    
    # Test cycle detection
    scheduler = create_test_scheduler(100, density=0.2)
    start = time.perf_counter()
    cycle = scheduler.detect_cycles()
    elapsed_cycle = time.perf_counter() - start
    
    results = {
        "topological_sort_linear": {
            "time_ms": elapsed_linear * 1000,
            "tasks": 100,
            "target_ms": 50,
            "pass": elapsed_linear * 1000 < 50
        },
        "topological_sort_dense": {
            "time_ms": elapsed_dense * 1000,
            "tasks": 100,
            "target_ms": 100,
            "pass": elapsed_dense * 1000 < 100
        },
        "cycle_detection": {
            "time_ms": elapsed_cycle * 1000,
            "tasks": 100,
            "target_ms": 50,
            "pass": elapsed_cycle * 1000 < 50
        }
    }
    
    return results


def main():
    """Run all baseline measurements"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Establish performance baselines')
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('.performance/baselines'),
        help='Directory to save baseline metrics'
    )
    
    args = parser.parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Establishing Performance Baselines")
    print("=" * 70)
    
    all_results = {}
    
    # Router performance
    print("\n📊 Measuring Router I/O Performance...")
    try:
        router_results = measure_router_performance()
        all_results.update(router_results)
        for name, data in router_results.items():
            status = "✅ PASS" if data['pass'] else "❌ FAIL"
            print(f"  {name}: {data['time_ms']:.2f}ms (target: {data['target_ms']}ms) {status}")
    except Exception as e:
        print(f"  ⚠️ Router tests skipped: {e}")
    
    # Clustering performance
    print("\n📊 Measuring Clustering Performance...")
    try:
        clustering_results = measure_clustering_performance()
        all_results.update(clustering_results)
        for name, data in clustering_results.items():
            status = "✅ PASS" if data['pass'] else "❌ FAIL"
            print(f"  {name}: {data['time_ms']:.2f}ms (target: {data['target_ms']}ms) {status}")
    except Exception as e:
        print(f"  ⚠️ Clustering tests skipped: {e}")
    
    # Scheduler performance
    print("\n📊 Measuring Scheduler Performance...")
    try:
        scheduler_results = measure_scheduler_performance()
        all_results.update(scheduler_results)
        for name, data in scheduler_results.items():
            status = "✅ PASS" if data['pass'] else "❌ FAIL"
            print(f"  {name}: {data['time_ms']:.2f}ms (target: {data['target_ms']}ms) {status}")
    except Exception as e:
        print(f"  ⚠️ Scheduler tests skipped: {e}")
    
    # Save results
    baseline_file = output_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    main_baseline = output_dir / "main.json"
    
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "metrics": all_results
    }
    
    baseline_file.write_text(json.dumps(metadata, indent=2))
    main_baseline.write_text(json.dumps(metadata, indent=2))
    
    # Summary
    print("\n" + "=" * 70)
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results.values() if r.get('pass', False))
    
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    print(f"Baseline saved to: {baseline_file}")
    print(f"Main baseline: {main_baseline}")
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("\n✅ All performance targets met!")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests exceeded target time")
        return 1


if __name__ == '__main__':
    sys.exit(main())
