#!/usr/bin/env python3
"""
Timing study for Dask Scheduler and Worker startup (separate processes).

This script measures the time it takes to start a Dask scheduler and workers
as separate processes, similar to how they would run in a distributed environment.
"""

import time
import subprocess
import sys
import json
import argparse
from datetime import datetime
from dask.distributed import Client
import signal
import os


class SchedulerWorkerTimer:
    """Class to manage timing of separate scheduler and worker processes."""
    
    def __init__(self, n_workers=4, threads_per_worker=1, output_json=None):
        self.n_workers = n_workers
        self.threads_per_worker = threads_per_worker
        self.output_json = output_json
        self.scheduler_proc = None
        self.worker_procs = []
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'n_workers': n_workers,
            'threads_per_worker': threads_per_worker,
        }
    
    def start_scheduler(self):
        """Start the Dask scheduler process."""
        print("Starting Dask scheduler...")
        start_time = time.time()
        
        # Start scheduler on port 8786 (default)
        self.scheduler_proc = subprocess.Popen(
            ['dask-scheduler', '--port', '8786'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for scheduler to be ready
        client = None
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                time.sleep(0.5)
                client = Client('localhost:8786', timeout='2s')
                # If we can connect, scheduler is ready
                break
            except Exception:
                if attempt == max_attempts - 1:
                    raise RuntimeError("Scheduler failed to start within timeout")
                continue
        
        end_time = time.time()
        scheduler_start_time = end_time - start_time
        self.results['scheduler_start_time'] = scheduler_start_time
        
        print(f"✓ Scheduler ready: {scheduler_start_time:.4f} seconds")
        print(f"  Address: localhost:8786")
        
        if client:
            client.close()
        
        return scheduler_start_time
    
    def start_workers(self):
        """Start the Dask worker processes."""
        print(f"\nStarting {self.n_workers} Dask workers...")
        start_time = time.time()
        
        for i in range(self.n_workers):
            worker_proc = subprocess.Popen(
                [
                    'dask-worker',
                    'localhost:8786',
                    '--nthreads', str(self.threads_per_worker),
                    '--name', f'worker-{i}'
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.worker_procs.append(worker_proc)
        
        # Wait for all workers to connect to scheduler
        client = Client('localhost:8786', timeout='5s')
        client.wait_for_workers(n_workers=self.n_workers, timeout=60)
        
        end_time = time.time()
        workers_start_time = end_time - start_time
        self.results['workers_start_time'] = workers_start_time
        
        print(f"✓ All {self.n_workers} workers ready: {workers_start_time:.4f} seconds")
        
        # Get worker info
        scheduler_info = client.scheduler_info()
        for worker_addr, worker_info in scheduler_info['workers'].items():
            print(f"  Worker: {worker_info.get('name', worker_addr)}")
            print(f"    Memory: {worker_info.get('memory_limit', 0) / 1e9:.2f} GB")
            print(f"    Threads: {worker_info.get('nthreads', 0)}")
        
        client.close()
        return workers_start_time
    
    def test_task_execution(self):
        """Test cluster readiness with a simple task."""
        print("\nTesting task execution...")
        start_time = time.time()
        
        client = Client('localhost:8786', timeout='5s')
        
        # Submit a simple task
        future = client.submit(lambda x: x + 1, 1)
        result = future.result()
        
        end_time = time.time()
        first_task_time = end_time - start_time
        self.results['first_task_time'] = first_task_time
        
        print(f"✓ First task completed: {first_task_time:.4f} seconds")
        
        # Test with multiple tasks
        print("\nTesting with batch of tasks...")
        start_batch = time.time()
        futures = [client.submit(lambda x: x * 2, i) for i in range(100)]
        results = client.gather(futures)
        end_batch = time.time()
        batch_time = end_batch - start_batch
        self.results['batch_100_tasks_time'] = batch_time
        
        print(f"✓ 100 tasks completed: {batch_time:.4f} seconds")
        
        client.close()
        return first_task_time, batch_time
    
    def cleanup(self):
        """Stop all scheduler and worker processes."""
        print("\nShutting down cluster...")
        
        # Stop workers
        for worker_proc in self.worker_procs:
            try:
                worker_proc.send_signal(signal.SIGTERM)
                worker_proc.wait(timeout=5)
            except Exception:
                worker_proc.kill()
        
        # Stop scheduler
        if self.scheduler_proc:
            try:
                self.scheduler_proc.send_signal(signal.SIGTERM)
                self.scheduler_proc.wait(timeout=5)
            except Exception:
                self.scheduler_proc.kill()
        
        print("✓ Cluster shut down")
    
    def run(self):
        """Run the complete timing study."""
        print(f"\n{'='*60}")
        print(f"Timing Dask Scheduler and Workers (Separate Processes)")
        print(f"{'='*60}")
        print(f"Workers: {self.n_workers}")
        print(f"Threads per worker: {self.threads_per_worker}")
        print(f"{'='*60}\n")
        
        try:
            # Time each phase
            overall_start = time.time()
            
            scheduler_time = self.start_scheduler()
            workers_time = self.start_workers()
            first_task_time, batch_time = self.test_task_execution()
            
            overall_end = time.time()
            total_time = overall_end - overall_start
            self.results['total_time'] = total_time
            
            # Display summary
            print(f"\n{'='*60}")
            print("TIMING SUMMARY")
            print(f"{'='*60}")
            print(f"Scheduler startup:       {scheduler_time:>10.4f} seconds")
            print(f"Workers startup:         {workers_time:>10.4f} seconds")
            print(f"First task execution:    {first_task_time:>10.4f} seconds")
            print(f"Batch (100 tasks):       {batch_time:>10.4f} seconds")
            print(f"{'-'*60}")
            print(f"Total time to ready:     {total_time:>10.4f} seconds")
            print(f"{'='*60}\n")
            
            # Save results to JSON if requested
            if self.output_json:
                with open(self.output_json, 'w') as f:
                    json.dump(self.results, f, indent=2)
                print(f"✓ Results saved to: {self.output_json}")
            
        finally:
            self.cleanup()
        
        return self.results


def main():
    parser = argparse.ArgumentParser(
        description='Time Dask Scheduler and Worker startup (separate processes)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Time startup with default settings (4 workers)
  python time_scheduler_workers.py
  
  # Time startup with 8 workers, 2 threads each
  python time_scheduler_workers.py --workers 8 --threads 2
  
  # Save results to JSON file
  python time_scheduler_workers.py --output results.json
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
        '--output', '-o',
        type=str,
        help='Output JSON file for results'
    )
    
    args = parser.parse_args()
    
    timer = SchedulerWorkerTimer(
        n_workers=args.workers,
        threads_per_worker=args.threads,
        output_json=args.output
    )
    timer.run()


if __name__ == '__main__':
    main()
