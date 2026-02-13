# dask-timing-sandbox

Doing various timing studies related to Dask schedulers and workers. This repository provides tools to measure how long it takes for Dask schedulers and workers to start up and become ready to accept and execute tasks.

## Overview

This repository contains scripts to perform comprehensive timing studies on Dask clusters, measuring:

- **Scheduler startup time**: Time for the scheduler to initialize
- **Client connection time**: Time to establish client connection to scheduler
- **Worker startup time**: Time for workers to connect and become available
- **First task execution time**: Time from cluster ready to first task completion
- **Total cluster readiness**: End-to-end time until cluster can process tasks

## Installation

1. Clone this repository:
```bash
git clone https://github.com/markcoletti/dask-timing-sandbox.git
cd dask-timing-sandbox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start with Bash Script

The easiest way to run timing studies is using the bash wrapper script:

```bash
# Quick test (1 run, 2 workers)
./run_timing_study.sh quick

# Standard test (5 runs, 2 workers, saves JSON results)
./run_timing_study.sh standard

# Scalability test (tests with 1, 2, 4, and 8 workers)
./run_timing_study.sh scalability

# Detailed test (includes extra cluster information)
./run_timing_study.sh detailed

# Custom test with specific parameters
./run_timing_study.sh custom --workers 4 --runs 10 --output my_results.json
```

### Using the Python Script Directly

For more control, you can run the Python script directly:

```bash
# Basic usage with 2 workers
python dask_timing_study.py

# Run with 4 workers
python dask_timing_study.py --workers 4

# Run 10 times for statistical analysis
python dask_timing_study.py --workers 4 --runs 10

# Save results to JSON file
python dask_timing_study.py --workers 2 --runs 5 --output results.json

# Include detailed cluster information
python dask_timing_study.py --workers 2 --detailed

# Combine options
python dask_timing_study.py --workers 4 --runs 10 --detailed --output detailed_results.json
```

### Command Line Options

**Python Script Options:**
- `--workers N`: Number of workers to start (default: 2)
- `--runs N`: Number of timing runs to perform (default: 1)
- `--output FILE`: Save results to JSON file (optional)
- `--detailed`: Include detailed scheduler and worker information (optional)

**Bash Script Commands:**
- `quick`: Run a quick test (1 run, 2 workers)
- `standard`: Run standard test (5 runs, 2 workers, saves JSON)
- `scalability`: Run scalability test (1-8 workers, 3 runs each)
- `detailed`: Run detailed test with extra cluster info
- `custom`: Run with custom parameters (pass options after custom)
- `help`: Show help message

## Output Examples

### Console Output

```
Running 5 timing study runs with 2 workers each...

Run 1/5... ✓
Run 2/5... ✓
Run 3/5... ✓
Run 4/5... ✓
Run 5/5... ✓

======================================================================
DASK TIMING STUDY RESULTS
======================================================================

Individual Runs:
----------------------------------------------------------------------

Run 1:
  Scheduler startup:       1.2345s
  Client connection:       0.1234s
  Workers startup:         2.3456s
  First task execution:    0.0567s
  Total cluster ready:     3.7602s
  Workers connected:       2

...

----------------------------------------------------------------------
Statistics (across all successful runs):
----------------------------------------------------------------------

Metric                        Mean        Min        Max    Std Dev
----------------------------------------------------------------------
Scheduler Startup           1.2500s    1.2000s    1.3000s    0.0400s
Client Connection           0.1250s    0.1200s    0.1300s    0.0040s
Workers Startup             2.3500s    2.3000s    2.4000s    0.0400s
First Task Execution        0.0570s    0.0560s    0.0580s    0.0008s
Total Cluster Ready         3.7820s    3.7000s    3.8500s    0.0600s

======================================================================
```

### JSON Output Format

When using `--output`, results are saved in JSON format:

```json
{
  "timestamp": "2026-02-13T19:42:00.000000",
  "parameters": {
    "workers": 2,
    "runs": 5
  },
  "results": [
    {
      "run": 1,
      "scheduler_startup": 1.2345,
      "client_connection": 0.1234,
      "workers_startup": 2.3456,
      "first_task_execution": 0.0567,
      "total_cluster_ready": 3.7602,
      "actual_workers": 2
    }
  ],
  "statistics": {
    "scheduler_startup": {
      "mean": 1.2500,
      "min": 1.2000,
      "max": 1.3000,
      "std_dev": 0.0400,
      "count": 5
    }
  }
}
```

## Understanding the Metrics

- **Scheduler Startup**: Time from cluster initialization to scheduler being ready. This includes setting up the scheduler process and its internal state.

- **Client Connection**: Time to establish a connection between the client and scheduler. This is typically very fast.

- **Workers Startup**: Time for all workers to start, connect to the scheduler, and register themselves as available. This is usually the longest phase.

- **First Task Execution**: Time from submitting the first task to receiving its result. This verifies that workers are fully operational and can execute code.

- **Total Cluster Ready**: The complete end-to-end time from starting the cluster to being able to execute tasks. This is the most important metric for understanding overall readiness.

## Use Cases

### Performance Benchmarking
Run multiple iterations to understand typical startup times:
```bash
./run_timing_study.sh standard
```

### Scalability Analysis
Test how startup time scales with worker count:
```bash
./run_timing_study.sh scalability
```

### CI/CD Integration
Integrate timing checks into your CI/CD pipeline:
```bash
python dask_timing_study.py --workers 2 --runs 3 --output ci_results.json
```

### Debugging Slow Startups
Use detailed mode to identify bottlenecks:
```bash
python dask_timing_study.py --workers 4 --detailed
```

## Dask Built-in Instrumentation

The scripts leverage Dask's built-in features:

- **`Client.wait_for_workers()`**: Ensures workers are connected before timing
- **`Client.scheduler_info()`**: Provides detailed cluster state information
- **`LocalCluster`**: Used for testing, but the timing approach works with any cluster type (e.g., `KubeCluster`, `SLURMCluster`)

## Customization

You can modify `dask_timing_study.py` to:

- Test different cluster types (e.g., Kubernetes, SLURM)
- Measure different task types or workloads
- Add custom metrics specific to your use case
- Integrate with monitoring systems

## Requirements

- Python 3.7+
- dask[distributed] >= 2024.1.0

See `requirements.txt` for specific versions.

## Contributing

Feel free to open issues or submit pull requests to enhance the timing studies or add new features.

## License

This project is open source and available for use in timing studies and performance analysis.
