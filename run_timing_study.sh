#!/bin/bash

# Bash script for running Dask timing studies
# This script provides a convenient wrapper for running timing studies
# with different configurations and collecting results.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
STUDY_TYPE="local"
WORKERS=4
THREADS=1
OUTPUT_DIR="timing_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Function to print usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run Dask timing studies for scheduler and worker startup.

OPTIONS:
    -t, --type TYPE         Type of study: 'local' or 'distributed' (default: local)
    -w, --workers NUM       Number of workers (default: 4)
    -T, --threads NUM       Threads per worker (default: 1)
    -o, --output-dir DIR    Output directory for results (default: timing_results)
    -r, --runs NUM          Number of runs to average (default: 1)
    -h, --help              Show this help message

EXAMPLES:
    # Run local cluster timing study
    $0 --type local --workers 4

    # Run distributed timing study with 8 workers
    $0 --type distributed --workers 8 --threads 2

    # Run multiple times and average results
    $0 --type local --runs 5 --output-dir results_dir

EOF
    exit 1
}

# Function to check if required Python packages are installed
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"
    python3 -c "import dask" 2>/dev/null || {
        echo -e "${RED}Error: dask package not found${NC}"
        echo "Install with: pip install -r requirements.txt"
        exit 1
    }
    python3 -c "import distributed" 2>/dev/null || {
        echo -e "${RED}Error: distributed package not found${NC}"
        echo "Install with: pip install -r requirements.txt"
        exit 1
    }
    echo -e "${GREEN}✓ Dependencies OK${NC}"
}

# Function to run a single timing study
run_study() {
    local study_type=$1
    local workers=$2
    local threads=$3
    local output_file=$4
    
    echo -e "${YELLOW}Running ${study_type} study...${NC}"
    echo "  Workers: ${workers}"
    echo "  Threads per worker: ${threads}"
    echo "  Output: ${output_file}"
    echo ""
    
    # Record start time
    start_time=$(date +%s)
    
    if [ "$study_type" == "local" ]; then
        python3 time_local_cluster.py \
            --workers "$workers" \
            --threads "$threads" \
            --output "$output_file"
    elif [ "$study_type" == "distributed" ]; then
        python3 time_scheduler_workers.py \
            --workers "$workers" \
            --threads "$threads" \
            --output "$output_file"
    else
        echo -e "${RED}Error: Unknown study type: ${study_type}${NC}"
        exit 1
    fi
    
    # Record end time
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo -e "${GREEN}✓ Study completed in ${duration} seconds${NC}"
    echo ""
}

# Function to run multiple studies and compute statistics
run_multiple_studies() {
    local study_type=$1
    local workers=$2
    local threads=$3
    local runs=$4
    local output_dir=$5
    
    echo -e "${YELLOW}Running ${runs} iterations...${NC}"
    echo ""
    
    # Create array to store output files
    output_files=()
    
    for i in $(seq 1 "$runs"); do
        echo -e "${YELLOW}=== Run $i of $runs ===${NC}"
        output_file="${output_dir}/${study_type}_w${workers}_t${threads}_run${i}_${TIMESTAMP}.json"
        output_files+=("$output_file")
        run_study "$study_type" "$workers" "$threads" "$output_file"
        
        # Small delay between runs
        if [ "$i" -lt "$runs" ]; then
            echo "Waiting 2 seconds before next run..."
            sleep 2
        fi
    done
    
    # Compute statistics if Python is available with numpy
    if python3 -c "import numpy" 2>/dev/null; then
        echo ""
        echo -e "${YELLOW}Computing statistics...${NC}"
        python3 - "${output_files[@]}" << 'PYEOF'
import json
import sys
from statistics import mean, stdev

files = sys.argv[1:]
metrics = {}

for filepath in files:
    with open(filepath) as f:
        data = json.load(f)
    
    for key, value in data.items():
        if isinstance(value, (int, float)):
            if key not in metrics:
                metrics[key] = []
            metrics[key].append(value)

print("\n" + "="*60)
print("STATISTICS ACROSS RUNS")
print("="*60)

for key, values in metrics.items():
    if len(values) > 1:
        avg = mean(values)
        std = stdev(values)
        print(f"{key:30s}: {avg:>10.4f} ± {std:.4f} seconds")
    else:
        print(f"{key:30s}: {values[0]:>10.4f} seconds")

print("="*60)
PYEOF
    fi
    
    echo ""
    echo -e "${GREEN}✓ All runs completed. Results in: ${output_dir}${NC}"
}

# Parse command line arguments
RUNS=1

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            STUDY_TYPE="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -T|--threads)
            THREADS="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -r|--runs)
            RUNS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Main execution
echo ""
echo "================================================================"
echo "Dask Timing Study Runner"
echo "================================================================"
echo "Study type: ${STUDY_TYPE}"
echo "Workers: ${WORKERS}"
echo "Threads per worker: ${THREADS}"
echo "Number of runs: ${RUNS}"
echo "Output directory: ${OUTPUT_DIR}"
echo "================================================================"
echo ""

# Check dependencies
check_dependencies

# Create output directory
mkdir -p "$OUTPUT_DIR"
echo -e "${GREEN}✓ Output directory created: ${OUTPUT_DIR}${NC}"
echo ""

# Run the study/studies
if [ "$RUNS" -eq 1 ]; then
    output_file="${OUTPUT_DIR}/${STUDY_TYPE}_w${WORKERS}_t${THREADS}_${TIMESTAMP}.json"
    run_study "$STUDY_TYPE" "$WORKERS" "$THREADS" "$output_file"
else
    run_multiple_studies "$STUDY_TYPE" "$WORKERS" "$THREADS" "$RUNS" "$OUTPUT_DIR"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
