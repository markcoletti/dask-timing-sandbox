# dask-timing-sandbox

A comprehensive toolkit for conducting timing studies on Dask scheduler and worker startup.

## Overview

This repository provides tools to measure and analyze the startup time of Dask schedulers and workers. It includes:

- **Python timing scripts** that measure different phases of Dask cluster startup
- **Bash wrapper script** for running multiple timing studies with different configurations
- **Analysis utilities** for processing and visualizing timing results

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Tools Included

### 1. `time_local_cluster.py`

Times the startup of a Dask LocalCluster (scheduler + workers in a single process).

**Features:**
- Measures cluster initialization time
- Measures client connection time
- Measures time to wait for all workers to be ready
- Tests cluster with actual task execution
- Outputs detailed timing breakdown and saves results to JSON

**Usage:**
```bash
# Basic usage with default settings (4 workers)
python time_local_cluster.py

# Specify number of workers and threads
python time_local_cluster.py --workers 8 --threads 2

# Save results to JSON file
python time_local_cluster.py --output results.json

# Run without waiting for workers
python time_local_cluster.py --no-wait
```

**Example output:**
```
============================================================
Timing Dask LocalCluster Startup
============================================================
Workers: 4
Threads per worker: 1
Wait for workers: True
============================================================

Starting cluster initialization...
✓ Cluster object created: 2.3456 seconds

Connecting client to cluster...
✓ Client connected: 0.1234 seconds

Waiting for 4 workers to be ready...
✓ All workers ready: 1.2345 seconds

Testing with a simple task...
✓ First task completed: 0.0567 seconds

============================================================
TIMING SUMMARY
============================================================
Cluster initialization:      2.3456 seconds
Client connection:           0.1234 seconds
Wait for workers:            1.2345 seconds
First task execution:        0.0567 seconds
------------------------------------------------------------
Total time to ready:         3.7602 seconds
============================================================
```

### 2. `time_scheduler_workers.py`

Times the startup of Dask scheduler and workers as separate processes (similar to a distributed deployment).

**Features:**
- Starts a separate scheduler process
- Starts multiple worker processes
- Measures individual component startup times
- Tests with single and batch task execution
- Automatically cleans up processes

**Usage:**
```bash
# Basic usage with default settings
python time_scheduler_workers.py

# Specify number of workers and threads
python time_scheduler_workers.py --workers 8 --threads 2

# Save results to JSON file
python time_scheduler_workers.py --output results.json
```

**Example output:**
```
============================================================
Timing Dask Scheduler and Workers (Separate Processes)
============================================================
Workers: 4
Threads per worker: 1
============================================================

Starting Dask scheduler...
✓ Scheduler ready: 1.2345 seconds
  Address: localhost:8786

Starting 4 Dask workers...
✓ All 4 workers ready: 2.3456 seconds
  Worker: worker-0
    Memory: 8.00 GB
    Threads: 1
  ...

Testing task execution...
✓ First task completed: 0.0234 seconds

Testing with batch of tasks...
✓ 100 tasks completed: 0.1234 seconds

============================================================
TIMING SUMMARY
============================================================
Scheduler startup:           1.2345 seconds
Workers startup:             2.3456 seconds
First task execution:        0.0234 seconds
Batch (100 tasks):           0.1234 seconds
------------------------------------------------------------
Total time to ready:         3.6035 seconds
============================================================
```

### 3. `run_timing_study.sh`

Bash script that provides a convenient wrapper for running timing studies with different configurations.

**Features:**
- Run either local or distributed timing studies
- Support for multiple runs with statistical analysis
- Automatic dependency checking
- Organized output directory structure
- Computes mean and standard deviation across runs

**Usage:**
```bash
# Run local cluster timing study
./run_timing_study.sh --type local --workers 4

# Run distributed timing study with 8 workers
./run_timing_study.sh --type distributed --workers 8 --threads 2

# Run multiple times and compute statistics
./run_timing_study.sh --type local --runs 5 --output-dir results_dir

# Get help
./run_timing_study.sh --help
```

**Options:**
- `-t, --type TYPE`: Type of study ('local' or 'distributed')
- `-w, --workers NUM`: Number of workers
- `-T, --threads NUM`: Threads per worker
- `-o, --output-dir DIR`: Output directory for results
- `-r, --runs NUM`: Number of runs to average
- `-h, --help`: Show help message

### 4. `analyze_results.py`

Analyzes timing results from JSON files and provides statistics and visualizations.

**Features:**
- Load and analyze multiple result files
- Compute statistics (mean, standard deviation, median, min, max)
- Compare different configurations
- Generate plots (requires matplotlib)

**Usage:**
```bash
# Analyze all results in timing_results directory
python analyze_results.py "timing_results/*.json"

# Analyze specific configuration
python analyze_results.py "timing_results/*_w4_*.json"

# Generate plots and comparisons
python analyze_results.py "timing_results/*.json" --plot --compare
```

**Example output:**
```
======================================================================
ANALYSIS OF 5 TIMING RESULT(S)
======================================================================

Configuration: 4 workers, 1 thread(s) per worker
Number of runs: 5
----------------------------------------------------------------------
  total_time                    :
    Mean:       3.7602 seconds
    StdDev:     0.1234 seconds
    Median:     3.7500 seconds
    Min:        3.6123 seconds
    Max:        3.9234 seconds
  ...

======================================================================
OVERALL SUMMARY
======================================================================
Total time to ready (all runs):
  Mean:       3.7602 seconds
  StdDev:     0.1234 seconds
  Min:        3.6123 seconds
  Max:        3.9234 seconds
======================================================================
```

## Timing Phases Explained

The timing scripts measure several distinct phases:

1. **Cluster/Scheduler Initialization**: Time to create the cluster/scheduler object and get it running
2. **Client Connection**: Time for the client to connect to the scheduler
3. **Worker Startup**: Time for all workers to start and register with the scheduler
4. **First Task**: Time to execute the first task (tests end-to-end readiness)
5. **Batch Tasks**: Time to execute a batch of tasks (tests throughput)

## Use Cases

### Basic Timing Study

Run a simple timing study to see how long your cluster takes to start:

```bash
python time_local_cluster.py --workers 4
```

### Compare Different Configurations

Compare startup times with different worker counts:

```bash
./run_timing_study.sh --type local --workers 2 --output-dir comparison
./run_timing_study.sh --type local --workers 4 --output-dir comparison
./run_timing_study.sh --type local --workers 8 --output-dir comparison
python analyze_results.py "comparison/*.json" --compare --plot
```

### Statistical Analysis

Run multiple iterations to get reliable statistics:

```bash
./run_timing_study.sh --type local --workers 4 --runs 10 --output-dir stats
```

### Local vs Distributed Comparison

Compare local cluster vs separate scheduler/workers:

```bash
./run_timing_study.sh --type local --workers 4 --runs 5 --output-dir comparison
./run_timing_study.sh --type distributed --workers 4 --runs 5 --output-dir comparison
python analyze_results.py "comparison/*.json" --compare
```

## Understanding the Results

### What affects startup time?

1. **Number of workers**: More workers typically means longer startup time
2. **Threads per worker**: Generally minimal impact on startup time
3. **System resources**: Available CPU, memory, and I/O affect startup speed
4. **Process creation overhead**: Separate processes (distributed) may have more overhead
5. **Network latency**: In distributed setups, network communication adds latency

### Interpreting metrics

- **Total time to ready**: Most important metric - time until cluster can execute tasks
- **First task time**: Measures true end-to-end readiness
- **Batch task time**: Tests cluster throughput capability

## Advanced Usage

### Custom Configuration

You can modify the Python scripts to:
- Add custom workloads for testing
- Measure additional Dask instrumentation metrics
- Test different cluster configurations
- Add custom logging or monitoring

### Integration with CI/CD

Use the JSON output to track startup time regressions:

```bash
python time_local_cluster.py --output baseline.json

# Compare against baseline in CI
python - << EOF
import json
with open('baseline.json') as f:
    baseline = json.load(f)['total_time']
with open('current.json') as f:
    current = json.load(f)['total_time']

if current > baseline * 1.2:  # 20% regression threshold
    print(f"Performance regression: {current:.2f}s vs {baseline:.2f}s")
    exit(1)
EOF
```

## Dask Built-in Instrumentation

The scripts leverage Dask's built-in capabilities:

- `scheduler_info()`: Get detailed scheduler and worker information
- `wait_for_workers()`: Wait for specific number of workers to be ready
- Worker metrics: Memory limits, thread counts, etc.

For more advanced instrumentation, consider:
- Dask's performance report: `client.performance_report('report.html')`
- Dask dashboard: Monitor real-time cluster activity
- Custom plugins: Add instrumentation at scheduler/worker level

## Troubleshooting

### Workers not starting

If workers fail to start, check:
- Available system memory
- Port availability (8786 for scheduler)
- Firewall settings (for distributed mode)

### Timing inconsistencies

For consistent results:
- Run multiple iterations (`--runs` option)
- Ensure system is not under heavy load
- Close other Dask clusters
- Consider warm-up runs

## Contributing

Feel free to extend these tools with:
- Additional timing metrics
- Support for other cluster types (e.g., SLURM, Kubernetes)
- Enhanced visualization
- Performance regression testing

## License

This is a sandbox repository for timing studies. Use freely for research and development.
