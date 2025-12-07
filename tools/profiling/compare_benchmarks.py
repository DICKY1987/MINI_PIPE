#!/usr/bin/env python3
"""Compare benchmark results and fail if regression exceeds threshold

Usage:
    python compare_benchmarks.py baseline.json current.json --max-regression-percent=10
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def compare_benchmarks(
    baseline_file: Path,
    current_file: Path,
    max_regression_percent: float = 10.0
) -> Dict[str, Any]:
    """Compare benchmark results and detect regressions
    
    Args:
        baseline_file: Path to baseline benchmark JSON
        current_file: Path to current benchmark JSON
        max_regression_percent: Maximum allowed regression percentage
        
    Returns:
        Dict with regressions, improvements, and summary
        
    Exits:
        1 if regressions detected, 0 otherwise
    """
    
    # Load benchmark files
    try:
        with open(baseline_file) as f:
            baseline = json.load(f)
        with open(current_file) as f:
            current = json.load(f)
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON - {e}")
        sys.exit(2)
    
    regressions = []
    improvements = []
    unchanged = []
    
    # Compare each benchmark
    for bench in current.get('benchmarks', []):
        name = bench['name']
        current_mean = bench['stats']['mean']
        
        # Find matching baseline
        baseline_bench = next(
            (b for b in baseline.get('benchmarks', []) if b['name'] == name),
            None
        )
        
        if not baseline_bench:
            print(f"⚠️  Warning: No baseline found for '{name}'")
            continue
        
        baseline_mean = baseline_bench['stats']['mean']
        change_percent = ((current_mean - baseline_mean) / baseline_mean) * 100
        
        item = {
            'name': name,
            'baseline_ms': baseline_mean * 1000,
            'current_ms': current_mean * 1000,
            'change_percent': change_percent,
            'change_ms': (current_mean - baseline_mean) * 1000
        }
        
        if change_percent > max_regression_percent:
            regressions.append(item)
        elif change_percent < -5:  # 5% improvement threshold
            improvements.append(item)
        else:
            unchanged.append(item)
    
    # Generate report
    report = {
        'regressions': regressions,
        'improvements': improvements,
        'unchanged': unchanged,
        'summary': generate_summary(regressions, improvements, unchanged),
        'passed': len(regressions) == 0
    }
    
    # Write comparison file
    comparison_file = Path('.performance/comparison.json')
    comparison_file.parent.mkdir(exist_ok=True)
    comparison_file.write_text(json.dumps(report, indent=2))
    
    # Print results
    print_results(regressions, improvements, unchanged, max_regression_percent)
    
    # Exit with appropriate code
    return report


def generate_summary(
    regressions: List[Dict],
    improvements: List[Dict],
    unchanged: List[Dict]
) -> str:
    """Generate markdown summary for PR comments"""
    lines = ["## Performance Test Results\n"]
    
    if regressions:
        lines.append("### ❌ Performance Regressions Detected\n")
        lines.append("| Test | Baseline | Current | Change | Δ |")
        lines.append("|------|----------|---------|--------|---|")
        for reg in regressions:
            lines.append(
                f"| {reg['name']} | "
                f"{reg['baseline_ms']:.1f}ms | "
                f"{reg['current_ms']:.1f}ms | "
                f"{reg['change_percent']:+.1f}% | "
                f"{reg['change_ms']:+.1f}ms |"
            )
        lines.append("")
    
    if improvements:
        lines.append("### ✅ Performance Improvements\n")
        lines.append("| Test | Baseline | Current | Change | Δ |")
        lines.append("|------|----------|---------|--------|---|")
        for imp in improvements:
            lines.append(
                f"| {imp['name']} | "
                f"{imp['baseline_ms']:.1f}ms | "
                f"{imp['current_ms']:.1f}ms | "
                f"{imp['change_percent']:.1f}% | "
                f"{imp['change_ms']:.1f}ms |"
            )
        lines.append("")
    
    if unchanged:
        lines.append(f"### ⚪ Unchanged ({len(unchanged)} tests)\n")
        lines.append("Performance within acceptable variance.\n")
    
    return '\n'.join(lines)


def print_results(
    regressions: List[Dict],
    improvements: List[Dict],
    unchanged: List[Dict],
    threshold: float
):
    """Print colored console output"""
    print("\n" + "=" * 70)
    print("Performance Comparison Results")
    print("=" * 70 + "\n")
    
    if regressions:
        print("❌ PERFORMANCE REGRESSIONS DETECTED:\n")
        for reg in regressions:
            print(f"  {reg['name']}")
            print(f"    Baseline:  {reg['baseline_ms']:>8.1f}ms")
            print(f"    Current:   {reg['current_ms']:>8.1f}ms")
            print(f"    Change:    {reg['change_percent']:>+7.1f}% ({reg['change_ms']:+.1f}ms)")
            print()
        print(f"  Threshold: {threshold}% maximum allowed regression\n")
    
    if improvements:
        print("✅ PERFORMANCE IMPROVEMENTS:\n")
        for imp in improvements:
            print(f"  {imp['name']}")
            print(f"    Baseline:  {imp['baseline_ms']:>8.1f}ms")
            print(f"    Current:   {imp['current_ms']:>8.1f}ms")
            print(f"    Change:    {imp['change_percent']:>+7.1f}% ({imp['change_ms']:+.1f}ms)")
            print()
    
    if unchanged:
        print(f"⚪ UNCHANGED: {len(unchanged)} tests within variance\n")
    
    print("=" * 70)
    
    if regressions:
        print("❌ BUILD FAILED: Performance regressions exceed threshold")
        sys.exit(1)
    else:
        print("✅ BUILD PASSED: No performance regressions detected")
        sys.exit(0)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compare performance benchmarks and detect regressions'
    )
    parser.add_argument(
        'baseline',
        type=Path,
        help='Path to baseline benchmark JSON file'
    )
    parser.add_argument(
        'current',
        type=Path,
        help='Path to current benchmark JSON file'
    )
    parser.add_argument(
        '--max-regression-percent',
        type=float,
        default=10.0,
        help='Maximum allowed regression percentage (default: 10%%)'
    )
    
    args = parser.parse_args()
    
    compare_benchmarks(
        args.baseline,
        args.current,
        args.max_regression_percent
    )


if __name__ == '__main__':
    main()
