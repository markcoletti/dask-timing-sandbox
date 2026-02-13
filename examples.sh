#!/bin/bash
# Example usage script demonstrating all the timing tools

echo "================================"
echo "Dask Timing Tools - Examples"
echo "================================"
echo ""

# Example 1: Simple local cluster timing
echo "Example 1: Basic local cluster timing"
echo "--------------------------------------"
echo "Command: python time_local_cluster.py --workers 2"
echo ""
# Uncomment to run:
# python time_local_cluster.py --workers 2
echo ""

# Example 2: Distributed timing with custom configuration
echo "Example 2: Distributed timing (separate scheduler/workers)"
echo "-----------------------------------------------------------"
echo "Command: python time_scheduler_workers.py --workers 4 --threads 2"
echo ""
# Uncomment to run:
# python time_scheduler_workers.py --workers 4 --threads 2
echo ""

# Example 3: Multiple runs for statistics
echo "Example 3: Multiple runs for statistical analysis"
echo "--------------------------------------------------"
echo "Command: ./run_timing_study.sh --type local --workers 4 --runs 5"
echo ""
# Uncomment to run:
# ./run_timing_study.sh --type local --workers 4 --runs 5
echo ""

# Example 4: Comparing different configurations
echo "Example 4: Comparing different worker configurations"
echo "-----------------------------------------------------"
echo "Commands:"
echo "  ./run_timing_study.sh --type local --workers 2 --output-dir comparison"
echo "  ./run_timing_study.sh --type local --workers 4 --output-dir comparison"
echo "  ./run_timing_study.sh --type local --workers 8 --output-dir comparison"
echo "  python analyze_results.py 'comparison/*.json' --compare"
echo ""
# Uncomment to run:
# mkdir -p comparison
# ./run_timing_study.sh --type local --workers 2 --output-dir comparison
# ./run_timing_study.sh --type local --workers 4 --output-dir comparison
# ./run_timing_study.sh --type local --workers 8 --output-dir comparison
# python analyze_results.py 'comparison/*.json' --compare
echo ""

# Example 5: Local vs Distributed comparison
echo "Example 5: Comparing local vs distributed deployment"
echo "-----------------------------------------------------"
echo "Commands:"
echo "  ./run_timing_study.sh --type local --workers 4 --runs 3 --output-dir local_vs_dist"
echo "  ./run_timing_study.sh --type distributed --workers 4 --runs 3 --output-dir local_vs_dist"
echo "  python analyze_results.py 'local_vs_dist/*.json' --compare --plot"
echo ""
# Uncomment to run:
# mkdir -p local_vs_dist
# ./run_timing_study.sh --type local --workers 4 --runs 3 --output-dir local_vs_dist
# ./run_timing_study.sh --type distributed --workers 4 --runs 3 --output-dir local_vs_dist
# python analyze_results.py 'local_vs_dist/*.json' --compare --plot
echo ""

# Example 6: Quick test with JSON output
echo "Example 6: Quick test with JSON output for CI/CD"
echo "-------------------------------------------------"
echo "Command: python time_local_cluster.py --workers 2 --output baseline.json"
echo ""
# Uncomment to run:
# python time_local_cluster.py --workers 2 --output baseline.json
# cat baseline.json
echo ""

echo "================================"
echo "To run any example, uncomment the corresponding commands in this script"
echo "or copy the command and run it directly in your terminal."
echo "================================"
