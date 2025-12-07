"""Performance benchmarks for Wave 2 algorithmic optimizations

Run with: pytest tests/performance/test_wave2_benchmarks.py --benchmark-only
"""

import pytest
from collections import defaultdict
from src.acms.gap_registry import GapRecord, GapSeverity, GapStatus
from src.acms.execution_planner import ExecutionPlanner


class TestWave2Benchmarks:
    """Benchmarks for Wave 2 algorithmic optimizations"""

    @pytest.fixture
    def sample_gaps_large(self):
        """Create large sample gaps dataset for clustering benchmark"""
        gaps = []
        for i in range(200):
            gap = GapRecord(
                gap_id=f"GAP-{i:03d}",
                title=f"Test Gap {i}",
                category="performance" if i % 3 == 0 else "feature",
                description=f"Test gap {i}",
                severity=GapSeverity.MEDIUM,
                status=GapStatus.DISCOVERED,
                # Create overlapping file dependencies for clustering
                file_paths=[f"file{j}.py" for j in range(i % 5, (i % 5) + 3)],
                discovered_at="2025-12-07T00:00:00Z"
            )
            gaps.append(gap)
        return gaps

    @pytest.fixture
    def planner(self):
        """Create execution planner instance"""
        from src.acms.gap_registry import GapRegistry
        from pathlib import Path
        
        registry = GapRegistry()
        return ExecutionPlanner(gap_registry=registry)

    def test_benchmark_priority_queue_clustering(self, benchmark, planner, sample_gaps_large):
        """Benchmark the optimized priority queue clustering algorithm"""
        
        def cluster_gaps():
            workstreams = planner._cluster_by_file_proximity(
                gaps=sample_gaps_large,
                max_files=10
            )
            return workstreams
        
        result = benchmark(cluster_gaps)
        assert len(result) > 0

    def test_benchmark_file_to_gaps_mapping(self, benchmark, sample_gaps_large):
        """Benchmark defaultdict file mapping (Wave 1 + Wave 2 combined)"""
        
        def build_mapping():
            file_to_gaps = defaultdict(list)
            for gap in sample_gaps_large:
                for file_path in gap.file_paths:
                    file_to_gaps[file_path].append(gap)
            return file_to_gaps
        
        result = benchmark(build_mapping)
        assert len(result) > 0


class TestTopologicalSortBenchmarks:
    """Benchmarks for topological sort optimization"""

    @pytest.fixture
    def scheduler_with_deps(self):
        """Create scheduler with complex dependency graph"""
        from src.minipipe.scheduler import Scheduler
        from src.minipipe.task import Task
        
        scheduler = Scheduler()
        
        # Create 100 tasks with dependencies
        for i in range(100):
            task = Task(
                task_id=f"task-{i:03d}",
                task_kind="test",
                input_data={"value": i},
                dependencies=[f"task-{j:03d}" for j in range(max(0, i-3), i)]
            )
            scheduler.add_task(task)
        
        return scheduler

    def test_benchmark_topological_sort(self, benchmark, scheduler_with_deps):
        """Benchmark optimized topological sort with dependency count caching"""
        
        def sort_tasks():
            return scheduler_with_deps.topological_sort()
        
        result = benchmark(sort_tasks)
        assert len(result) > 0


class TestCycleDetectionBenchmarks:
    """Benchmarks for cycle detection optimization"""

    @pytest.fixture
    def scheduler_no_cycles(self):
        """Create scheduler with acyclic dependency graph"""
        from src.minipipe.scheduler import Scheduler
        from src.minipipe.task import Task
        
        scheduler = Scheduler()
        
        # Create deep dependency chain (worst case for path copying)
        for i in range(50):
            deps = [f"task-{i-1:03d}"] if i > 0 else []
            task = Task(
                task_id=f"task-{i:03d}",
                task_kind="test",
                input_data={"value": i},
                dependencies=deps
            )
            scheduler.add_task(task)
        
        return scheduler

    def test_benchmark_cycle_detection(self, benchmark, scheduler_no_cycles):
        """Benchmark optimized cycle detection without path copying"""
        
        def detect():
            return scheduler_no_cycles.detect_cycles()
        
        result = benchmark(detect)
        assert result is None  # No cycles


if __name__ == "__main__":
    pytest.main([__file__, "--benchmark-only", "-v"])
