#!/usr/bin/env python3
"""
Dask Timing Study Script

This script measures various timing aspects of Dask cluster startup:
1. Scheduler startup time
2. Worker connection time
3. Time until workers are ready to accept tasks
4. First task execution time
5. Overall cluster readiness time

Usage:
    python dask_timing_study.py [--workers N] [--runs N] [--output FILE]
"""

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, List

from dask.distributed import Client, LocalCluster


def measure_cluster_startup(n_workers: int = 2) -> Dict[str, float]:
    """
    Measure the time it takes for a Dask cluster to start and become ready.
    
    Args:
        n_workers: Number of workers to start
        
    Returns:
        Dictionary containing timing measurements in seconds
    """
    timings = {}
    
    # Measure total cluster startup time
    cluster_start = time.time()
    
    # Start cluster with specified number of workers
    # Using LocalCluster for testing, but this approach works with other cluster types
    cluster = LocalCluster(
        n_workers=0,  # Start with no workers initially
        threads_per_worker=1,
        processes=True,
        dashboard_address=None  # Disable dashboard for cleaner timing
    )
    
    scheduler_ready = time.time()
    timings['scheduler_startup'] = scheduler_ready - cluster_start
    
    # Connect client to scheduler
    client_start = time.time()
    client = Client(cluster)
    client_connected = time.time()
    timings['client_connection'] = client_connected - client_start
    
    # Scale up workers
    workers_start = time.time()
    cluster.scale(n_workers)
    
    # Wait for all workers to connect
    client.wait_for_workers(n_workers, timeout=60)
    workers_ready = time.time()
    timings['workers_startup'] = workers_ready - workers_start
    
    # Measure time for first task execution (measures worker readiness)
    first_task_start = time.time()
    
    # Simple task to verify workers are ready
    def simple_task(x):
        return x * 2
    
    # Submit a task and wait for result
    future = client.submit(simple_task, 1)
    result = future.result()
    
    first_task_complete = time.time()
    timings['first_task_execution'] = first_task_complete - first_task_start
    
    # Calculate total time from start to first task completion
    timings['total_cluster_ready'] = first_task_complete - cluster_start
    
    # Get additional cluster information
    timings['actual_workers'] = len(client.scheduler_info()['workers'])
    
    # Clean up
    client.close()
    cluster.close()
    
    return timings


def measure_scheduler_info(n_workers: int = 2) -> Dict[str, any]:
    """
    Collect detailed scheduler and worker information.
    
    Args:
        n_workers: Number of workers to start
        
    Returns:
        Dictionary containing detailed timing and system information
    """
    info = {}
    
    start_time = time.time()
    
    # Create cluster and client
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=1,
        processes=True,
        dashboard_address=None
    )
    
    client = Client(cluster)
    client.wait_for_workers(n_workers, timeout=60)
    
    setup_time = time.time() - start_time
    info['setup_time'] = setup_time
    
    # Get scheduler info
    scheduler_info = client.scheduler_info()
    
    info['n_workers'] = len(scheduler_info['workers'])
    info['scheduler_id'] = scheduler_info['id']
    
    # Get worker details with timing information
    workers_info = []
    for worker_id, worker_data in scheduler_info['workers'].items():
        worker_info = {
            'id': worker_id,
            'name': worker_data.get('name', 'unknown'),
            'nthreads': worker_data.get('nthreads', 0),
            'memory_limit': worker_data.get('memory_limit', 0),
        }
        workers_info.append(worker_info)
    
    info['workers'] = workers_info
    
    # Measure task distribution timing
    task_start = time.time()
    
    # Submit multiple tasks to test distribution
    futures = client.map(lambda x: x ** 2, range(100))
    results = client.gather(futures)
    
    task_time = time.time() - task_start
    info['task_execution_time'] = task_time
    info['tasks_per_second'] = len(results) / task_time if task_time > 0 else 0
    
    # Clean up
    client.close()
    cluster.close()
    
    return info


def run_timing_study(n_workers: int = 2, n_runs: int = 1) -> List[Dict[str, float]]:
    """
    Run multiple timing studies and collect results.
    
    Args:
        n_workers: Number of workers per run
        n_runs: Number of runs to perform
        
    Returns:
        List of timing dictionaries, one per run
    """
    results = []
    
    print(f"Running {n_runs} timing study runs with {n_workers} workers each...")
    print()
    
    for run in range(n_runs):
        print(f"Run {run + 1}/{n_runs}...", end=" ", flush=True)
        
        try:
            timings = measure_cluster_startup(n_workers)
            timings['run'] = run + 1
            results.append(timings)
            print("✓")
            
            # Small delay between runs to ensure clean shutdown
            if run < n_runs - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"✗ (Error: {e})")
            results.append({'run': run + 1, 'error': str(e)})
    
    return results


def calculate_statistics(results: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate mean, min, max, and std dev for timing results.
    
    Args:
        results: List of timing dictionaries
        
    Returns:
        Dictionary with statistics for each timing metric
    """
    # Filter out failed runs
    valid_results = [r for r in results if 'error' not in r]
    
    if not valid_results:
        return {}
    
    # Get all timing keys (excluding 'run' and 'actual_workers')
    timing_keys = [k for k in valid_results[0].keys() 
                   if k not in ['run', 'actual_workers', 'error']]
    
    statistics = {}
    
    for key in timing_keys:
        values = [r[key] for r in valid_results if key in r]
        
        if values:
            stats = {
                'mean': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
            
            # Calculate standard deviation
            if len(values) > 1:
                mean = stats['mean']
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                stats['std_dev'] = variance ** 0.5
            else:
                stats['std_dev'] = 0.0
            
            statistics[key] = stats
    
    return statistics


def print_results(results: List[Dict[str, float]], statistics: Dict[str, Dict[str, float]]):
    """
    Print timing results in a formatted manner.
    
    Args:
        results: List of timing dictionaries
        statistics: Dictionary with statistics for each timing metric
    """
    print("\n" + "=" * 70)
    print("DASK TIMING STUDY RESULTS")
    print("=" * 70)
    
    if not results:
        print("No results to display.")
        return
    
    # Print individual run results
    print("\nIndividual Runs:")
    print("-" * 70)
    
    for result in results:
        if 'error' in result:
            print(f"Run {result['run']}: ERROR - {result['error']}")
        else:
            print(f"\nRun {result['run']}:")
            print(f"  Scheduler startup:       {result['scheduler_startup']:.4f}s")
            print(f"  Client connection:       {result['client_connection']:.4f}s")
            print(f"  Workers startup:         {result['workers_startup']:.4f}s")
            print(f"  First task execution:    {result['first_task_execution']:.4f}s")
            print(f"  Total cluster ready:     {result['total_cluster_ready']:.4f}s")
            print(f"  Workers connected:       {result.get('actual_workers', 'N/A')}")
    
    # Print statistics if multiple runs
    if statistics and len(results) > 1:
        print("\n" + "-" * 70)
        print("Statistics (across all successful runs):")
        print("-" * 70)
        
        # Define order and labels for metrics
        metrics = [
            ('scheduler_startup', 'Scheduler Startup'),
            ('client_connection', 'Client Connection'),
            ('workers_startup', 'Workers Startup'),
            ('first_task_execution', 'First Task Execution'),
            ('total_cluster_ready', 'Total Cluster Ready')
        ]
        
        print(f"\n{'Metric':<25} {'Mean':>10} {'Min':>10} {'Max':>10} {'Std Dev':>10}")
        print("-" * 70)
        
        for key, label in metrics:
            if key in statistics:
                stats = statistics[key]
                print(f"{label:<25} "
                      f"{stats['mean']:>9.4f}s "
                      f"{stats['min']:>9.4f}s "
                      f"{stats['max']:>9.4f}s "
                      f"{stats['std_dev']:>9.4f}s")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point for the timing study script."""
    parser = argparse.ArgumentParser(
        description='Measure Dask cluster startup and readiness timing'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of workers to start (default: 2)'
    )
    parser.add_argument(
        '--runs',
        type=int,
        default=1,
        help='Number of timing runs to perform (default: 1)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file for results (optional)'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Include detailed scheduler and worker information'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.workers < 1:
        print("Error: Number of workers must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    if args.runs < 1:
        print("Error: Number of runs must be at least 1", file=sys.stderr)
        sys.exit(1)
    
    # Run timing studies
    results = run_timing_study(n_workers=args.workers, n_runs=args.runs)
    
    # Calculate statistics if multiple runs
    statistics = calculate_statistics(results) if args.runs > 1 else {}
    
    # Print results to console
    print_results(results, statistics)
    
    # Optionally get detailed information
    if args.detailed:
        print("\nCollecting detailed cluster information...")
        try:
            detailed_info = measure_scheduler_info(n_workers=args.workers)
            print("\nDetailed Information:")
            print("-" * 70)
            print(f"Setup time:              {detailed_info['setup_time']:.4f}s")
            print(f"Number of workers:       {detailed_info['n_workers']}")
            print(f"Task execution time:     {detailed_info['task_execution_time']:.4f}s")
            print(f"Tasks per second:        {detailed_info['tasks_per_second']:.2f}")
            print(f"\nWorker Details:")
            for worker in detailed_info['workers']:
                print(f"  - {worker['name']}: {worker['nthreads']} threads")
        except Exception as e:
            print(f"Error collecting detailed information: {e}", file=sys.stderr)
    
    # Save to JSON if requested
    if args.output:
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'parameters': {
                'workers': args.workers,
                'runs': args.runs
            },
            'results': results,
            'statistics': statistics
        }
        
        try:
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\nResults saved to: {args.output}")
        except Exception as e:
            print(f"Error saving results: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Return success if at least one run completed
    valid_runs = len([r for r in results if 'error' not in r])
    if valid_runs == 0:
        print("\nAll runs failed!", file=sys.stderr)
        sys.exit(1)
    
    print("\nTiming study completed successfully!")


if __name__ == '__main__':
    main()
