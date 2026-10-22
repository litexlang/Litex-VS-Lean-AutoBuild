#!/bin/bash

# LeanGeo Auto-build Experiments - One-click Run Script
# Supports running both Definition and Theorem experiments

set -e  # Exit immediately on error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print usage instructions
print_usage() {
    cat << EOF
Usage: $0 [options]

Options:
    --test         Test mode (only run 3 tasks per experiment)
    --def-only     Only run Definition experiment
    --thm-only     Only run Theorem experiment
    --help         Show this help message

Examples:
    $0                    # Full run (all tasks)
    $0 --test            # Test mode
    $0 --def-only        # Only run Definition
    $0 --thm-only        # Only run Theorem
EOF
}

# Parse command line arguments
TEST_MODE=0
DEF_ONLY=0
THM_ONLY=0

for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE=1
            shift
            ;;
        --def-only)
            DEF_ONLY=1
            shift
            ;;
        --thm-only)
            THM_ONLY=1
            shift
            ;;
        --help)
            print_usage
            exit 0
            ;;
        *)
            print_error "Unknown parameter: $arg"
            print_usage
            exit 1
            ;;
    esac
done

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not installed"
    exit 1
fi

# Check Lean
if ! command -v lean &> /dev/null; then
    print_error "Lean not installed, please run: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh"
    exit 1
fi

# Check API configuration
API_CONFIG="$PROJECT_ROOT/config/api_config.json"
if [ ! -f "$API_CONFIG" ]; then
    print_error "API configuration file does not exist: $API_CONFIG"
    print_info "Please run: cp config/api_config.example.json config/api_config.json"
    exit 1
fi

# Check seed library
SEED_FILE="$PROJECT_ROOT/../LeanGeo/LeanGeoCore/theorem_library_seed.lean"
if [ ! -f "$SEED_FILE" ]; then
    print_error "Seed library file does not exist: $SEED_FILE"
    exit 1
fi

# Print configuration information
print_info "========================================="
print_info "LeanGeo Auto-build Experiment System"
print_info "========================================="
print_info "Project directory: $PROJECT_ROOT"
print_info "Python version: $(python3 --version)"
print_info "Lean version: $(lean --version | head -1)"

if [ $TEST_MODE -eq 1 ]; then
    print_warning "Test mode: Only run 3 tasks per experiment"
    TASK_LIMIT=3
else
    print_info "Full mode: Run all tasks"
    TASK_LIMIT=""
fi

# Record start time
START_TIME=$(date +%s)

# Run Definition experiment
if [ $THM_ONLY -eq 0 ]; then
    print_info ""
    print_info "========================================="
    print_info "1. Running Definition experiment"
    print_info "========================================="

    if [ $TEST_MODE -eq 1 ]; then
        python3 "$SCRIPT_DIR/run_lean_definitions.py" $TASK_LIMIT
    else
        python3 "$SCRIPT_DIR/run_lean_definitions.py"
    fi

    if [ $? -eq 0 ]; then
        print_success "Definition experiment completed"
    else
        print_error "Definition experiment failed"
        exit 1
    fi
fi

# Run Theorem experiment
if [ $DEF_ONLY -eq 0 ]; then
    print_info ""
    print_info "========================================="
    print_info "2. Running Theorem experiment"
    print_info "========================================="

    if [ $TEST_MODE -eq 1 ]; then
        python3 "$SCRIPT_DIR/run_lean_theorems.py" $TASK_LIMIT
    else
        python3 "$SCRIPT_DIR/run_lean_theorems.py"
    fi

    if [ $? -eq 0 ]; then
        print_success "Theorem experiment completed"
    else
        print_error "Theorem experiment failed"
        exit 1
    fi
fi

# Calculate total duration
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
ELAPSED_MIN=$((ELAPSED / 60))
ELAPSED_SEC=$((ELAPSED % 60))

# Print summary
print_info ""
print_info "========================================="
print_success "All experiments completed!"
print_info "========================================="
print_info "Total duration: ${ELAPSED_MIN}min ${ELAPSED_SEC}sec"
print_info ""
print_info "Output directory:"
if [ $THM_ONLY -eq 0 ]; then
    LATEST_DEF=$(ls -t "$PROJECT_ROOT/lean_auto_validated_250tasks/definitions_only" 2>/dev/null | head -1)
    if [ -n "$LATEST_DEF" ]; then
        print_info "  Definition: lean_auto_validated_250tasks/definitions_only/$LATEST_DEF"
    fi
fi
if [ $DEF_ONLY -eq 0 ]; then
    LATEST_THM=$(ls -t "$PROJECT_ROOT/lean_auto_validated_250tasks/theorems_only" 2>/dev/null | head -1)
    if [ -n "$LATEST_THM" ]; then
        print_info "  Theorem: lean_auto_validated_250tasks/theorems_only/$LATEST_THM"
    fi
fi
