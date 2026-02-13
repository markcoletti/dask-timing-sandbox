#!/bin/bash
# Dask Timing Study Bash Wrapper
#
# This script provides a convenient way to run Dask timing studies
# with common configurations.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/dask_timing_study.py"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
check_dependencies() {
    info "Checking dependencies..."
    python3 -c "import dask, distributed" 2>/dev/null
    if [ $? -ne 0 ]; then
        warn "Dask dependencies not found. Installing from requirements.txt..."
        if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
            pip install -r "$SCRIPT_DIR/requirements.txt"
        else
            error "requirements.txt not found"
            exit 1
        fi
    fi
    info "Dependencies OK"
}

# Function to run a quick test (single run, 2 workers)
quick_test() {
    info "Running quick test (1 run, 2 workers)..."
    python3 "$PYTHON_SCRIPT" --workers 2 --runs 1
}

# Function to run a standard test (5 runs, 2 workers)
standard_test() {
    info "Running standard test (5 runs, 2 workers)..."
    python3 "$PYTHON_SCRIPT" --workers 2 --runs 5 --output "dask_timing_results_$(date +%Y%m%d_%H%M%S).json"
}

# Function to run a scalability test (varying worker counts)
scalability_test() {
    info "Running scalability test (1-8 workers)..."
    
    for workers in 1 2 4 8; do
        info "Testing with $workers workers..."
        python3 "$PYTHON_SCRIPT" --workers "$workers" --runs 3 --output "dask_timing_${workers}workers_$(date +%Y%m%d_%H%M%S).json"
        echo ""
    done
}

# Function to run detailed test
detailed_test() {
    info "Running detailed test with cluster information..."
    python3 "$PYTHON_SCRIPT" --workers 2 --runs 3 --detailed --output "dask_timing_detailed_$(date +%Y%m%d_%H%M%S).json"
}

# Print usage information
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
    quick           Run a quick test (1 run, 2 workers)
    standard        Run standard test (5 runs, 2 workers, saves JSON)
    scalability     Run scalability test (1-8 workers, 3 runs each)
    detailed        Run detailed test with extra cluster info
    custom          Run with custom parameters (requires options)
    help            Show this help message

Custom Options (for 'custom' command):
    -w, --workers N     Number of workers (default: 2)
    -r, --runs N        Number of runs (default: 1)
    -o, --output FILE   Output JSON file
    -d, --detailed      Include detailed information

Examples:
    $0 quick
    $0 standard
    $0 custom --workers 4 --runs 10
    $0 custom -w 3 -r 5 -o results.json -d

EOF
}

# Main script logic
main() {
    # Check dependencies first
    check_dependencies
    
    # Parse command
    COMMAND="${1:-help}"
    shift || true
    
    case "$COMMAND" in
        quick)
            quick_test
            ;;
        standard)
            standard_test
            ;;
        scalability)
            scalability_test
            ;;
        detailed)
            detailed_test
            ;;
        custom)
            python3 "$PYTHON_SCRIPT" "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: $COMMAND"
            usage
            exit 1
            ;;
    esac
}

main "$@"
