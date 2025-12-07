"""Performance regression tests for MINI_PIPE optimizations

These tests ensure that performance improvements are maintained and
detect any regressions in critical code paths.

Run with: pytest tests/performance/test_regression.py -v
"""

import pytest
from tools.profiling.baseline_scenarios import BaselineScenarios
from tools.profiling.profile_runner import ProfileRunner


@pytest.mark.performance
@pytest.mark.regression
class TestClusteringRegression:
    """Performance regression tests for clustering algorithms"""
    
    def test_clustering_small_no_regression(self, profile_runner, assert_no_regression):
        """Ensure small clustering hasn't regressed"""
        scenario = BaselineScenarios.scenario_clustering_small()
        
        result = profile_runner.profile_function(
            func=scenario['function'],
            scenario_name=scenario['name'],
            iterations=5
        )
        
        assert_no_regression(scenario['name'], result)
    
    def test_clustering_medium_no_regression(self, profile_runner, assert_no_regression):
        """Ensure medium clustering hasn't regressed"""
        scenario = BaselineScenarios.scenario_clustering_medium()
        
        result = profile_runner.profile_function(
            func=scenario['function'],
            scenario_name=scenario['name'],
            iterations=5
        )
        
        assert_no_regression(scenario['name'], result)
    
    def test_clustering_large_no_regression(self, profile_runner, assert_no_regression):
        """Ensure large clustering hasn't regressed"""
        scenario = BaselineScenarios.scenario_clustering_large()
        
        result = profile_runner.profile_function(
            func=scenario['function'],
            scenario_name=scenario['name'],
            iterations=5
        )
        
        assert_no_regression(scenario['name'], result)
    
    def test_clustering_large_absolute_threshold(self, profile_runner, get_threshold):
        """Ensure clustering meets absolute performance threshold"""
        scenario = BaselineScenarios.scenario_clustering_large()
        
        result = profile_runner.profile_function(
            func=scenario['function'],
            scenario_name=scenario['name'],
            iterations=5
        )
        
        threshold = get_threshold(scenario['name'], 'max_time_ms')
        if threshold:
            assert result.execution_time_ms < threshold, \
                f"Clustering took {result.execution_time_ms:.2f}ms, expected < {threshold}ms"


@pytest.mark.performance
@pytest.mark.regression
class TestGapRegistryRegression:
    """Performance regression tests for gap registry operations"""
    
    def test_gap_registry_no_regression(self, profile_runner, assert_no_regression):
        """Ensure gap registry operations haven't regressed"""
        scenario = BaselineScenarios.scenario_gap_registry_operations()
        
        result = profile_runner.profile_function(
            func=scenario['function'],
            scenario_name=scenario['name'],
            iterations=5
        )
        
        assert_no_regression(scenario['name'], result)


@pytest.mark.performance
@pytest.mark.baseline
class TestEstablishBaselines:
    """Tests to establish performance baselines (run once)"""
    
    @pytest.mark.skip(reason="Run manually to establish baselines")
    def test_establish_all_baselines(self, profile_runner):
        """Establish baselines for all scenarios"""
        from pathlib import Path
        from tools.profiling.baseline_scenarios import run_all_baselines
        
        # This will create baseline files
        run_all_baselines()
        
        # Verify baselines were created
        baseline_dir = Path('.performance/baselines')
        assert baseline_dir.exists()
        
        baseline_files = list(baseline_dir.glob('*_baseline.json'))
        assert len(baseline_files) >= 4, "Expected at least 4 baseline files"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "regression"])
