"""Profiling Infrastructure for MINI_PIPE Performance Monitoring

Provides automated profiling capabilities for performance regression detection
and optimization validation.

Usage:
    from tools.profiling.profile_runner import ProfileRunner
    
    runner = ProfileRunner()
    results = runner.profile_scenario('clustering_200_gaps')
    runner.save_results(results, '.performance/baselines/')
"""

import cProfile
import json
import pstats
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ProfileResult:
    """Results from a profiling run"""
    scenario_name: str
    execution_time_ms: float
    total_calls: int
    peak_memory_mb: float
    timestamp: str
    top_functions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'scenario_name': self.scenario_name,
            'execution_time_ms': self.execution_time_ms,
            'total_calls': self.total_calls,
            'peak_memory_mb': self.peak_memory_mb,
            'timestamp': self.timestamp,
            'top_functions': self.top_functions,
            'metadata': self.metadata
        }


class ProfileRunner:
    """Automated profiling harness for performance testing"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path('.performance/profiles')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def profile_function(
        self, 
        func: Callable,
        scenario_name: str,
        iterations: int = 1,
        **kwargs
    ) -> ProfileResult:
        """Profile a function with cProfile
        
        Args:
            func: Function to profile
            scenario_name: Name of the profiling scenario
            iterations: Number of times to run the function
            **kwargs: Arguments to pass to the function
            
        Returns:
            ProfileResult with profiling data
        """
        profiler = cProfile.Profile()
        
        # Warm-up run
        func(**kwargs)
        
        # Profile execution
        start_time = time.perf_counter()
        profiler.enable()
        
        for _ in range(iterations):
            func(**kwargs)
        
        profiler.disable()
        end_time = time.perf_counter()
        
        # Extract statistics
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Get top functions
        top_functions = self._extract_top_functions(stats, limit=20)
        
        # Calculate metrics
        execution_time_ms = (end_time - start_time) * 1000 / iterations
        total_calls = sum(stat[0] for stat in stats.stats.values())
        
        # Estimate memory (simplified - would need memory_profiler for accurate)
        peak_memory_mb = 0.0  # Placeholder
        
        return ProfileResult(
            scenario_name=scenario_name,
            execution_time_ms=execution_time_ms,
            total_calls=total_calls,
            peak_memory_mb=peak_memory_mb,
            timestamp=datetime.now(UTC).isoformat(),
            top_functions=top_functions,
            metadata={
                'iterations': iterations,
                'python_version': self._get_python_version()
            }
        )
    
    def _extract_top_functions(self, stats: pstats.Stats, limit: int = 20) -> List[Dict[str, Any]]:
        """Extract top N functions from stats"""
        top_functions = []
        
        for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:limit]:
            filename, line, func_name = func
            top_functions.append({
                'function': func_name,
                'filename': str(filename),
                'line': line,
                'call_count': nc,
                'total_time': tt,
                'cumulative_time': ct
            })
        
        return top_functions
    
    def _get_python_version(self) -> str:
        """Get Python version string"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def save_results(self, result: ProfileResult, output_path: Optional[Path] = None):
        """Save profiling results to JSON file
        
        Args:
            result: ProfileResult to save
            output_path: Optional custom output path
        """
        if output_path is None:
            timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
            filename = f"{result.scenario_name}_{timestamp}.json"
            output_path = self.output_dir / filename
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        print(f"✅ Saved profiling results to: {output_path}")
    
    def load_baseline(self, scenario_name: str, baseline_dir: Path = None) -> Optional[ProfileResult]:
        """Load baseline profiling results for comparison
        
        Args:
            scenario_name: Name of the scenario to load
            baseline_dir: Directory containing baseline files
            
        Returns:
            ProfileResult if found, None otherwise
        """
        baseline_dir = baseline_dir or (self.output_dir / 'baselines')
        
        if not baseline_dir.exists():
            return None
        
        # Find most recent baseline for this scenario
        baseline_files = list(baseline_dir.glob(f"{scenario_name}_*.json"))
        if not baseline_files:
            return None
        
        latest_file = max(baseline_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        return ProfileResult(
            scenario_name=data['scenario_name'],
            execution_time_ms=data['execution_time_ms'],
            total_calls=data['total_calls'],
            peak_memory_mb=data['peak_memory_mb'],
            timestamp=data['timestamp'],
            top_functions=data.get('top_functions', []),
            metadata=data.get('metadata', {})
        )
    
    def compare_results(
        self, 
        current: ProfileResult, 
        baseline: ProfileResult,
        threshold_percent: float = 10.0
    ) -> Dict[str, Any]:
        """Compare current results against baseline
        
        Args:
            current: Current profiling results
            baseline: Baseline profiling results
            threshold_percent: Regression threshold percentage
            
        Returns:
            Comparison report with regression detection
        """
        time_diff_ms = current.execution_time_ms - baseline.execution_time_ms
        time_diff_percent = (time_diff_ms / baseline.execution_time_ms) * 100
        
        is_regression = time_diff_percent > threshold_percent
        
        return {
            'scenario': current.scenario_name,
            'current_time_ms': current.execution_time_ms,
            'baseline_time_ms': baseline.execution_time_ms,
            'difference_ms': time_diff_ms,
            'difference_percent': time_diff_percent,
            'is_regression': is_regression,
            'threshold_percent': threshold_percent,
            'status': '❌ REGRESSION' if is_regression else '✅ PASS',
            'current_calls': current.total_calls,
            'baseline_calls': baseline.total_calls,
            'timestamp': current.timestamp
        }
    
    def generate_report(self, comparison: Dict[str, Any]) -> str:
        """Generate human-readable comparison report
        
        Args:
            comparison: Comparison dictionary from compare_results
            
        Returns:
            Formatted report string
        """
        report = f"""
Performance Comparison Report
{'=' * 50}

Scenario: {comparison['scenario']}
Status:   {comparison['status']}

Execution Time:
  Current:   {comparison['current_time_ms']:.2f} ms
  Baseline:  {comparison['baseline_time_ms']:.2f} ms
  Difference: {comparison['difference_ms']:+.2f} ms ({comparison['difference_percent']:+.1f}%)
  Threshold: {comparison['threshold_percent']}%

Function Calls:
  Current:  {comparison['current_calls']:,}
  Baseline: {comparison['baseline_calls']:,}

Timestamp: {comparison['timestamp']}
"""
        return report


if __name__ == "__main__":
    # Example usage
    runner = ProfileRunner()
    
    def example_workload():
        """Example workload for testing"""
        import time
        data = [i**2 for i in range(1000)]
        time.sleep(0.001)
        return sum(data)
    
    result = runner.profile_function(
        example_workload,
        scenario_name='example_test',
        iterations=10
    )
    
    print(f"Execution time: {result.execution_time_ms:.2f} ms")
    print(f"Total calls: {result.total_calls:,}")
    
    runner.save_results(result)
