#!/usr/bin/env python3
"""
Analyze timing results from Dask timing studies.

This script reads JSON result files and provides analysis including:
- Summary statistics
- Comparisons across different configurations
- Visualization (if matplotlib is available)
"""

import json
import argparse
import glob
import os
from collections import defaultdict
from statistics import mean, stdev, median


def load_results(pattern):
    """Load all JSON result files matching the pattern."""
    files = glob.glob(pattern)
    results = []
    
    for filepath in files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['_filename'] = os.path.basename(filepath)
                results.append(data)
        except Exception as e:
            print(f"Warning: Could not load {filepath}: {e}")
    
    return results


def analyze_results(results):
    """Analyze a collection of timing results."""
    if not results:
        print("No results to analyze")
        return
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS OF {len(results)} TIMING RESULT(S)")
    print(f"{'='*70}\n")
    
    # Group by configuration
    by_config = defaultdict(list)
    for result in results:
        key = (result.get('n_workers'), result.get('threads_per_worker'))
        by_config[key].append(result)
    
    # Analyze each configuration
    for (n_workers, threads_per_worker), config_results in sorted(by_config.items()):
        print(f"Configuration: {n_workers} workers, {threads_per_worker} thread(s) per worker")
        print(f"Number of runs: {len(config_results)}")
        print(f"{'-'*70}")
        
        # Collect metrics
        metrics = defaultdict(list)
        for result in config_results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and not key.startswith('_'):
                    metrics[key].append(value)
        
        # Print statistics for each metric
        for metric_name, values in sorted(metrics.items()):
            if len(values) > 1:
                avg = mean(values)
                std = stdev(values)
                med = median(values)
                min_val = min(values)
                max_val = max(values)
                print(f"  {metric_name:30s}:")
                print(f"    Mean:   {avg:>10.4f} seconds")
                print(f"    StdDev: {std:>10.4f} seconds")
                print(f"    Median: {med:>10.4f} seconds")
                print(f"    Min:    {min_val:>10.4f} seconds")
                print(f"    Max:    {max_val:>10.4f} seconds")
            else:
                print(f"  {metric_name:30s}: {values[0]:>10.4f} seconds")
        
        print()
    
    # Overall summary
    print(f"{'='*70}")
    print("OVERALL SUMMARY")
    print(f"{'='*70}")
    
    all_total_times = [r['total_time'] for r in results if 'total_time' in r]
    if all_total_times:
        print(f"Total time to ready (all runs):")
        print(f"  Mean:   {mean(all_total_times):>10.4f} seconds")
        if len(all_total_times) > 1:
            print(f"  StdDev: {stdev(all_total_times):>10.4f} seconds")
        print(f"  Min:    {min(all_total_times):>10.4f} seconds")
        print(f"  Max:    {max(all_total_times):>10.4f} seconds")
    
    print(f"{'='*70}\n")


def compare_configs(results):
    """Compare different configurations."""
    by_config = defaultdict(list)
    for result in results:
        key = (result.get('n_workers'), result.get('threads_per_worker'))
        by_config[key].append(result)
    
    if len(by_config) < 2:
        return
    
    print(f"\n{'='*70}")
    print("CONFIGURATION COMPARISON")
    print(f"{'='*70}\n")
    
    configs = []
    for (n_workers, threads_per_worker), config_results in sorted(by_config.items()):
        total_times = [r['total_time'] for r in config_results if 'total_time' in r]
        if total_times:
            configs.append({
                'n_workers': n_workers,
                'threads_per_worker': threads_per_worker,
                'avg_time': mean(total_times),
                'runs': len(total_times)
            })
    
    # Sort by average time
    configs.sort(key=lambda x: x['avg_time'])
    
    print(f"{'Workers':<10} {'Threads':<10} {'Avg Time':<15} {'Runs':<10}")
    print(f"{'-'*70}")
    for config in configs:
        print(f"{config['n_workers']:<10} {config['threads_per_worker']:<10} "
              f"{config['avg_time']:<15.4f} {config['runs']:<10}")
    
    print(f"{'='*70}\n")


def plot_results(results):
    """Plot timing results if matplotlib is available."""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Matplotlib not available for plotting")
        return
    
    # Group by configuration
    by_config = defaultdict(list)
    for result in results:
        key = f"{result.get('n_workers')}w-{result.get('threads_per_worker')}t"
        by_config[key].append(result)
    
    # Prepare data for plotting
    configs = []
    total_times = []
    
    for config_name, config_results in sorted(by_config.items()):
        times = [r['total_time'] for r in config_results if 'total_time' in r]
        if times:
            configs.append(config_name)
            total_times.append(times)
    
    if not configs:
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Box plot
    ax.boxplot(total_times, labels=configs)
    ax.set_xlabel('Configuration (workers-threads)')
    ax.set_ylabel('Total Time (seconds)')
    ax.set_title('Dask Startup Time by Configuration')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    output_file = 'timing_analysis.png'
    plt.savefig(output_file, dpi=150)
    print(f"✓ Plot saved to: {output_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Dask timing study results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all results in timing_results directory
  python analyze_results.py "timing_results/*.json"
  
  # Analyze specific configuration
  python analyze_results.py "timing_results/*_w4_*.json"
  
  # Create plots (requires matplotlib)
  python analyze_results.py "timing_results/*.json" --plot
        """
    )
    parser.add_argument(
        'pattern',
        nargs='?',
        default='timing_results/*.json',
        help='Glob pattern for JSON result files (default: timing_results/*.json)'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate plots (requires matplotlib)'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare different configurations'
    )
    
    args = parser.parse_args()
    
    # Load results
    print(f"Loading results from: {args.pattern}")
    results = load_results(args.pattern)
    
    if not results:
        print(f"No results found matching pattern: {args.pattern}")
        return
    
    print(f"Loaded {len(results)} result file(s)")
    
    # Analyze results
    analyze_results(results)
    
    # Compare configurations if requested
    if args.compare:
        compare_configs(results)
    
    # Plot results if requested
    if args.plot:
        plot_results(results)


if __name__ == '__main__':
    main()
