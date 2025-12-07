"""Pytest configuration for performance regression tests

Provides fixtures and utilities for performance testing with pytest-benchmark.
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from tools.profiling.profile_runner import ProfileRunner, ProfileResult


@pytest.fixture(scope='session')
def profile_runner():
    """Provide ProfileRunner instance for tests"""
    return ProfileRunner(output_dir=Path('.performance/test_profiles'))


@pytest.fixture(scope='session')
def baseline_dir():
    """Path to baseline profiling data"""
    return Path('.performance/baselines')


@pytest.fixture
def performance_threshold():
    """Default performance regression threshold (%)"""
    return 15.0  # Allow 15% slower before flagging as regression


def pytest_configure(config):
    """Register custom markers for performance tests"""
    config.addinivalue_line(
        "markers", 
        "performance: mark test as performance test (slow)"
    )
    config.addinivalue_line(
        "markers",
        "regression: mark test as performance regression test"
    )
    config.addinivalue_line(
        "markers",
        "baseline: mark test to establish performance baseline"
    )


def pytest_benchmark_group_stats(config, benchmarks, group_by):
    """Custom grouping for benchmark results"""
    return group_by


@pytest.fixture
def assert_no_regression(profile_runner, baseline_dir, performance_threshold):
    """Helper to assert no performance regression
    
    Usage:
        def test_clustering(assert_no_regression):
            result = run_clustering()
            assert_no_regression('clustering_large', result)
    """
    def _assert(scenario_name: str, current_result: ProfileResult):
        baseline = profile_runner.load_baseline(scenario_name, baseline_dir)
        
        if baseline is None:
            pytest.skip(f"No baseline found for {scenario_name}")
        
        comparison = profile_runner.compare_results(
            current_result,
            baseline,
            threshold_percent=performance_threshold
        )
        
        if comparison['is_regression']:
            report = profile_runner.generate_report(comparison)
            pytest.fail(
                f"Performance regression detected!\n{report}"
            )
        
        # Log success
        print(f"\n✅ No regression: {scenario_name}")
        print(f"   Current: {comparison['current_time_ms']:.2f} ms")
        print(f"   Baseline: {comparison['baseline_time_ms']:.2f} ms")
        print(f"   Change: {comparison['difference_percent']:+.1f}%")
    
    return _assert


@pytest.fixture
def benchmark_metadata():
    """Add metadata to benchmark results"""
    import sys
    import platform
    
    return {
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'platform': platform.platform(),
        'processor': platform.processor(),
        'commit_sha': _get_git_commit()
    }


def _get_git_commit() -> str:
    """Get current git commit SHA"""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return 'unknown'


# Benchmark comparison parameters
BENCHMARK_THRESHOLDS = {
    'clustering_small': {
        'max_time_ms': 100,
        'max_memory_mb': 50
    },
    'clustering_medium': {
        'max_time_ms': 400,
        'max_memory_mb': 100
    },
    'clustering_large': {
        'max_time_ms': 1500,
        'max_memory_mb': 200
    }
}


@pytest.fixture
def get_threshold():
    """Get performance threshold for a scenario"""
    def _get(scenario_name: str, metric: str = 'max_time_ms'):
        scenario_key = scenario_name.replace('_' + scenario_name.split('_')[-1], '')
        thresholds = BENCHMARK_THRESHOLDS.get(scenario_key, {})
        return thresholds.get(metric)
    
    return _get
