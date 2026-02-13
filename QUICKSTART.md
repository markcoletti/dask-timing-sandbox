# Quick Start Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/markcoletti/dask-timing-sandbox.git  # Replace with your fork URL if applicable
cd dask-timing-sandbox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 5-Minute Quick Start

### Option 1: Time a Local Cluster (Easiest)

Run this single command to time a local Dask cluster:
```bash
python time_local_cluster.py --workers 4
```

You'll see output like:
```
============================================================
TIMING SUMMARY
============================================================
Cluster initialization:      0.7652 seconds
Client connection:           0.0056 seconds
Wait for workers:            0.0009 seconds
First task execution:        0.0153 seconds
------------------------------------------------------------
Total time to ready:         0.7876 seconds
============================================================
```

### Option 2: Use the Bash Wrapper

Run multiple iterations and get statistics:
```bash
./run_timing_study.sh --type local --workers 4 --runs 3
```

### Option 3: Time Separate Scheduler/Workers

Test a distributed-like deployment:
```bash
python time_scheduler_workers.py --workers 4
```

## Understanding the Output

The tools measure several key phases:

1. **Cluster/Scheduler initialization** - Time to start the scheduler
2. **Worker startup** - Time for all workers to register
3. **Client connection** - Time for client to connect
4. **First task** - End-to-end time to execute a task

The **total time** is what matters most - it's when your cluster is fully ready.

## Saving Results

Add `--output results.json` to save detailed timing data:
```bash
python time_local_cluster.py --workers 4 --output results.json
cat results.json
```

## Analyzing Results

If you have multiple result files:
```bash
python analyze_results.py "timing_results/*.json" --compare
```

## Common Use Cases

### Compare worker counts
```bash
./run_timing_study.sh --workers 2 --output-dir comparison
./run_timing_study.sh --workers 4 --output-dir comparison
./run_timing_study.sh --workers 8 --output-dir comparison
python analyze_results.py "comparison/*.json" --compare
```

### Check for performance regressions
```bash
# Run baseline
python time_local_cluster.py --output baseline.json

# After changes, compare
python time_local_cluster.py --output current.json

# Compare times
python -c "
import json
baseline = json.load(open('baseline.json'))['total_time']
current = json.load(open('current.json'))['total_time']
print(f'Baseline: {baseline:.2f}s')
print(f'Current:  {current:.2f}s')
print(f'Change:   {((current/baseline - 1) * 100):+.1f}%')
"
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [examples.sh](examples.sh) for more usage patterns
- Modify the scripts to add custom metrics or workloads
- Integrate into your CI/CD pipeline for regression testing

## Troubleshooting

**"No module named 'dask'"**
→ Run: `pip install -r requirements.txt`

**Workers not starting**
→ Check available memory and close other Dask clusters

**Results vary a lot**
→ Use `--runs 5` to average multiple iterations

**Want more workers than CPU cores**
→ This is OK for timing tests, but reduce `--threads` per worker
