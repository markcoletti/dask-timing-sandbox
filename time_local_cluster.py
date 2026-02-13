#!/usr/bin/env python3
"""
Timing study for Dask LocalCluster startup.

This script measures the time it takes for a Dask LocalCluster (scheduler + workers)
to start up and be ready to accept tasks.
"""

import time
import json
from datetime import datetime
from dask.distributed import LocalCluster, Client
import argparse


def time_local_cluster(n_workers=4, threads_per_worker=1, wait_for_workers=True, output_json=None):
    """
    Time the startup of a Dask LocalCluster.
    
    Parameters
    ----------
    n_workers : int
        Number of workers to start
    threads_per_worker : int
        Number of threads per worker
    wait_for_workers : bool
        Whether to wait for all workers to be ready
    output_json : str, optional
        Path to save timing results as JSON
        
    Returns
    -------
    dict
        Dictionary containing timing measurements
    """
    results = {
        'timestamp': datetime.now().isoformat(),
        'n_workers': n_workers,
        'threads_per_worker': threads_per_worker,
    }
    
    print(f"\n{'='*60}")
    print(f"Timing Dask LocalCluster Startup")
    print(f"{'='*60}")
    print(f"Workers: {n_workers}")
    print(f"Threads per worker: {threads_per_worker}")
    print(f"Wait for workers: {wait_for_workers}")
    print(f"{'='*60}\n")
    
    # Measure cluster initialization
    print("Starting cluster initialization...")
    start_cluster = time.time()
    cluster = LocalCluster(
        n_workers=n_workers,
        threads_per_worker=threads_per_worker,
        processes=True,
        silence_logs=False
    )
    end_cluster = time.time()
    cluster_init_time = end_cluster - start_cluster
    
    results['cluster_init_time'] = cluster_init_time
    print(f"✓ Cluster object created: {cluster_init_time:.4f} seconds")
    
    # Measure client connection
    print("\nConnecting client to cluster...")
    start_client = time.time()
    client = Client(cluster)
    end_client = time.time()
    client_connect_time = end_client - start_client
    
    results['client_connect_time'] = client_connect_time
    print(f"✓ Client connected: {client_connect_time:.4f} seconds")
    
    # Wait for all workers to be ready
    if wait_for_workers:
        print(f"\nWaiting for {n_workers} workers to be ready...")
        start_wait = time.time()
        client.wait_for_workers(n_workers=n_workers, timeout=60)
        end_wait = time.time()
        wait_time = end_wait - start_wait
        
        results['wait_for_workers_time'] = wait_time
        print(f"✓ All workers ready: {wait_time:.4f} seconds")
    
    # Get scheduler and worker info
    scheduler_info = client.scheduler_info()
    results['scheduler_address'] = scheduler_info['address']
    results['actual_workers'] = len(scheduler_info['workers'])
    
    # Test with a simple task to measure end-to-end readiness
    print("\nTesting with a simple task...")
    start_task = time.time()
    future = client.submit(lambda x: x + 1, 1)
    result = future.result()
    end_task = time.time()
    first_task_time = end_task - start_task
    
    results['first_task_time'] = first_task_time
    print(f"✓ First task completed: {first_task_time:.4f} seconds")
    
    # Calculate total time
    total_time = end_task - start_cluster
    results['total_time'] = total_time
    
    # Display summary
    print(f"\n{'='*60}")
    print("TIMING SUMMARY")
    print(f"{'='*60}")
    print(f"Cluster initialization:  {cluster_init_time:>10.4f} seconds")
    print(f"Client connection:       {client_connect_time:>10.4f} seconds")
    if wait_for_workers:
        print(f"Wait for workers:        {wait_time:>10.4f} seconds")
    print(f"First task execution:    {first_task_time:>10.4f} seconds")
    print(f"{'-'*60}")
    print(f"Total time to ready:     {total_time:>10.4f} seconds")
    print(f"{'='*60}\n")
    
    # Get additional metrics from scheduler
    print("Additional Metrics:")
    print(f"  Scheduler address: {results['scheduler_address']}")
    print(f"  Active workers: {results['actual_workers']}")
    
    # Get worker details
    for worker_addr, worker_info in scheduler_info['workers'].items():
        print(f"\n  Worker: {worker_addr}")
        print(f"    Memory: {worker_info.get('memory_limit', 0) / 1e9:.2f} GB")
        print(f"    Threads: {worker_info.get('nthreads', 0)}")
    
    # Save results to JSON if requested
    if output_json:
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {output_json}")
    
    # Cleanup
    print("\nShutting down cluster...")
    client.close()
    cluster.close()
    print("✓ Cluster closed")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Time Dask LocalCluster startup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Time startup with default settings (4 workers)
  python time_local_cluster.py
  
  # Time startup with 8 workers, 2 threads each
  python time_local_cluster.py --workers 8 --threads 2
  
  # Save results to JSON file
  python time_local_cluster.py --output results.json
  
  # Run without waiting for workers
  python time_local_cluster.py --no-wait
        """
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Number of workers (default: 4)'
    )
    parser.add_argument(
        '--threads', '-t',
        type=int,
        default=1,
        help='Threads per worker (default: 1)'
    )
    parser.add_argument(
        '--no-wait',
        action='store_false',
        dest='wait',
        help='Do not wait for all workers to be ready'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output JSON file for results'
    )
    
    args = parser.parse_args()
    
    time_local_cluster(
        n_workers=args.workers,
        threads_per_worker=args.threads,
        wait_for_workers=args.wait,
        output_json=args.output
    )


if __name__ == '__main__':
    main()
