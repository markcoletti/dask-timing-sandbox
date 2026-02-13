#!/usr/bin/env python3
"""
Example: Using Dask Timing Functions Programmatically

This example demonstrates how to import and use the timing functions
from dask_timing_study.py in your own scripts.
"""

from dask_timing_study import (
    measure_cluster_startup,
    measure_scheduler_info,
    calculate_statistics,
    print_results
)


def main():
    print("Example 1: Single Timing Measurement")
    print("=" * 70)
    
    # Measure timing for a single cluster startup
    timings = measure_cluster_startup(n_workers=2)
    
    print(f"Scheduler startup time:    {timings['scheduler_startup']:.4f}s")
    print(f"Client connection time:    {timings['client_connection']:.4f}s")
    print(f"Workers startup time:      {timings['workers_startup']:.4f}s")
    print(f"First task execution:      {timings['first_task_execution']:.4f}s")
    print(f"Total cluster ready time:  {timings['total_cluster_ready']:.4f}s")
    print()
    
    print("\nExample 2: Multiple Runs with Statistics")
    print("=" * 70)
    
    # Run multiple times and calculate statistics
    results = []
    for i in range(3):
        print(f"Running measurement {i + 1}/3...", end=" ", flush=True)
        result = measure_cluster_startup(n_workers=2)
        result['run'] = i + 1
        results.append(result)
        print("✓")
    
    # Calculate and display statistics
    statistics = calculate_statistics(results)
    print_results(results, statistics)
    
    print("\nExample 3: Detailed Cluster Information")
    print("=" * 70)
    
    # Get detailed information about the cluster
    detailed_info = measure_scheduler_info(n_workers=2)
    
    print(f"Setup time:           {detailed_info['setup_time']:.4f}s")
    print(f"Number of workers:    {detailed_info['n_workers']}")
    print(f"Task execution time:  {detailed_info['task_execution_time']:.4f}s")
    print(f"Tasks per second:     {detailed_info['tasks_per_second']:.2f}")
    print()
    print("Worker details:")
    for worker in detailed_info['workers']:
        print(f"  - {worker['name']}: {worker['nthreads']} threads, "
              f"{worker['memory_limit'] / (1024**3):.2f} GB memory limit")
    
    print("\n" + "=" * 70)
    print("Examples completed successfully!")


if __name__ == '__main__':
    main()
