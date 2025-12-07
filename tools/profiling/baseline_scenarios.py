"""Baseline profiling scenarios for MINI_PIPE performance testing

Defines standard scenarios for consistent performance measurement and
regression detection.
"""

from pathlib import Path
from typing import Dict, Any

from src.acms.gap_registry import GapRecord, GapRegistry, GapSeverity, GapStatus
from src.acms.execution_planner import ExecutionPlanner


class BaselineScenarios:
    """Standard profiling scenarios for performance testing"""
    
    @staticmethod
    def create_sample_gaps(count: int) -> list[GapRecord]:
        """Create sample gaps for testing
        
        Args:
            count: Number of gaps to create
            
        Returns:
            List of GapRecord instances
        """
        gaps = []
        for i in range(count):
            gap = GapRecord(
                gap_id=f"GAP-{i:05d}",
                title=f"Performance Test Gap {i}",
                category="performance" if i % 3 == 0 else "feature",
                description=f"Test gap for performance profiling scenario {i}",
                severity=GapSeverity.MEDIUM if i % 2 == 0 else GapSeverity.HIGH,
                status=GapStatus.DISCOVERED,
                file_paths=[f"file{j}.py" for j in range(i % 5, (i % 5) + 3)],
                discovered_at="2025-12-07T00:00:00Z"
            )
            gaps.append(gap)
        return gaps
    
    @staticmethod
    def scenario_clustering_small() -> Dict[str, Any]:
        """Small clustering scenario (10 gaps)"""
        registry = GapRegistry()
        planner = ExecutionPlanner(gap_registry=registry)
        gaps = BaselineScenarios.create_sample_gaps(10)
        
        def run():
            return planner._cluster_by_file_proximity(gaps=gaps, max_files=10)
        
        return {
            'name': 'clustering_small_10gaps',
            'function': run,
            'description': 'Cluster 10 gaps with max 10 files',
            'expected_time_ms': 50,
            'workload_size': 10
        }
    
    @staticmethod
    def scenario_clustering_medium() -> Dict[str, Any]:
        """Medium clustering scenario (50 gaps)"""
        registry = GapRegistry()
        planner = ExecutionPlanner(gap_registry=registry)
        gaps = BaselineScenarios.create_sample_gaps(50)
        
        def run():
            return planner._cluster_by_file_proximity(gaps=gaps, max_files=10)
        
        return {
            'name': 'clustering_medium_50gaps',
            'function': run,
            'description': 'Cluster 50 gaps with max 10 files',
            'expected_time_ms': 200,
            'workload_size': 50
        }
    
    @staticmethod
    def scenario_clustering_large() -> Dict[str, Any]:
        """Large clustering scenario (200 gaps)"""
        registry = GapRegistry()
        planner = ExecutionPlanner(gap_registry=registry)
        gaps = BaselineScenarios.create_sample_gaps(200)
        
        def run():
            return planner._cluster_by_file_proximity(gaps=gaps, max_files=10)
        
        return {
            'name': 'clustering_large_200gaps',
            'function': run,
            'description': 'Cluster 200 gaps with max 10 files',
            'expected_time_ms': 1000,
            'workload_size': 200
        }
    
    @staticmethod
    def scenario_gap_registry_operations() -> Dict[str, Any]:
        """Gap registry bulk operations"""
        registry = GapRegistry()
        gaps = BaselineScenarios.create_sample_gaps(100)
        
        def run():
            for gap in gaps:
                registry.add_gap(gap)
            stats = registry.get_stats()
            return stats
        
        return {
            'name': 'gap_registry_100ops',
            'function': run,
            'description': 'Add 100 gaps to registry and get stats',
            'expected_time_ms': 100,
            'workload_size': 100
        }
    
    @staticmethod
    def get_all_scenarios() -> Dict[str, Dict[str, Any]]:
        """Get all baseline scenarios
        
        Returns:
            Dictionary mapping scenario names to scenario configs
        """
        scenarios = {
            'clustering_small': BaselineScenarios.scenario_clustering_small(),
            'clustering_medium': BaselineScenarios.scenario_clustering_medium(),
            'clustering_large': BaselineScenarios.scenario_clustering_large(),
            'gap_registry': BaselineScenarios.scenario_gap_registry_operations(),
        }
        return scenarios


def run_all_baselines():
    """Run all baseline scenarios and save results"""
    from tools.profiling.profile_runner import ProfileRunner
    
    runner = ProfileRunner()
    scenarios = BaselineScenarios.get_all_scenarios()
    
    baseline_dir = Path('.performance/baselines')
    baseline_dir.mkdir(parents=True, exist_ok=True)
    
    print("Running baseline profiling scenarios...")
    print("=" * 60)
    
    for scenario_key, scenario_config in scenarios.items():
        print(f"\n📊 Running: {scenario_config['name']}")
        print(f"   Description: {scenario_config['description']}")
        
        result = runner.profile_function(
            func=scenario_config['function'],
            scenario_name=scenario_config['name'],
            iterations=5
        )
        
        print(f"   ✅ Execution time: {result.execution_time_ms:.2f} ms")
        print(f"   📈 Expected: {scenario_config['expected_time_ms']} ms")
        
        if result.execution_time_ms <= scenario_config['expected_time_ms']:
            print(f"   ✅ PASS - Within expected range")
        else:
            ratio = result.execution_time_ms / scenario_config['expected_time_ms']
            print(f"   ⚠️  SLOWER - {ratio:.1f}x expected time")
        
        # Save to baselines directory
        output_file = baseline_dir / f"{scenario_config['name']}_baseline.json"
        runner.save_results(result, output_file)
    
    print("\n" + "=" * 60)
    print("✅ All baseline scenarios complete!")
    print(f"📁 Results saved to: {baseline_dir}")


if __name__ == "__main__":
    run_all_baselines()
