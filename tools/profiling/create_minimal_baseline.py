"""Simplified baseline metrics for initial CI/CD setup

This creates a minimal baseline file that can be used immediately,
even if full integration tests can't run yet.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def create_minimal_baseline():
    """Create minimal baseline with target metrics"""
    
    baseline = {
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "source": "manual_targets",
        "benchmarks": [
            {
                "name": "test_router_io_batching_small",
                "stats": {"mean": 0.005},  # 5ms
                "params": {"updates": 10}
            },
            {
                "name": "test_router_io_batching_medium",
                "stats": {"mean": 0.025},  # 25ms
                "params": {"updates": 100}
            },
            {
                "name": "test_router_io_batching_large",
                "stats": {"mean": 0.100},  # 100ms
                "params": {"updates": 1000}
            },
            {
                "name": "test_clustering_small_workload",
                "stats": {"mean": 0.025},  # 25ms
                "params": {"gaps": 10}
            },
            {
                "name": "test_clustering_medium_workload",
                "stats": {"mean": 0.100},  # 100ms
                "params": {"gaps": 50}
            },
            {
                "name": "test_clustering_large_workload",
                "stats": {"mean": 0.500},  # 500ms
                "params": {"gaps": 200}
            },
            {
                "name": "test_topological_sort_linear",
                "stats": {"mean": 0.025},  # 25ms
                "params": {"tasks": 100, "density": "linear"}
            },
            {
                "name": "test_topological_sort_dense",
                "stats": {"mean": 0.050},  # 50ms
                "params": {"tasks": 100, "density": "dense"}
            },
            {
                "name": "test_cycle_detection_no_cycle",
                "stats": {"mean": 0.025},  # 25ms
                "params": {"tasks": 100}
            },
            {
                "name": "test_full_clustering_pipeline",
                "stats": {"mean": 0.250},  # 250ms
                "params": {"gaps": 50}
            }
        ],
        "notes": "Initial baseline with target metrics. Update with real measurements once environment is configured."
    }
    
    return baseline


def main():
    """Create and save minimal baseline"""
    output_dir = Path('.performance/baselines')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    baseline = create_minimal_baseline()
    
    # Save to main.json
    main_file = output_dir / 'main.json'
    main_file.write_text(json.dumps(baseline, indent=2))
    
    # Also save timestamped version
    timestamp_file = output_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    timestamp_file.write_text(json.dumps(baseline, indent=2))
    
    print("=" * 70)
    print("Minimal Baseline Created")
    print("=" * 70)
    print(f"\nCreated baseline with {len(baseline['benchmarks'])} target metrics")
    print(f"Main baseline: {main_file}")
    print(f"Timestamped: {timestamp_file}")
    print("\n📝 Note: These are target metrics. Run actual benchmarks to update.")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
