#!/bin/bash
# LitexGeo Auto-build Experiments - One-click Run Script
#
# Usage:
#   ./run_all_experiments.sh              # Run all tasks
#   ./run_all_experiments.sh --test       # Test mode (only run 3 tasks per experiment)
#   ./run_all_experiments.sh --def-only   # Only run definition experiment
#   ./run_all_experiments.sh --thm-only   # Only run theorem experiment

set -e  # Exit immediately on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Switch to project root directory (parent of scripts)
cd "$SCRIPT_DIR/.."

# Parse arguments
TEST_MODE=false
DEF_ONLY=false
THM_ONLY=false
TASK_LIMIT=""

for arg in "$@"; do
    case $arg in
        --test)
            TEST_MODE=true
            TASK_LIMIT="3"
            shift
            ;;
        --def-only)
            DEF_ONLY=true
            shift
            ;;
        --thm-only)
            THM_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown parameter: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}LitexGeo Auto-build Experiments${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

if [ "$TEST_MODE" = true ]; then
    echo -e "${YELLOW}⚠️  Test mode: Only run first 3 tasks per experiment${NC}"
    echo ""
fi

# Check Python environment
echo -e "${GREEN}[1/5] Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not installed${NC}"
    exit 1
fi
echo -e "   ✅ Python version: $(python3 --version)"

# Check dependencies
echo -e "${GREEN}[2/5] Checking dependencies...${NC}"
if ! python3 -c "import openai" 2>/dev/null; then
    echo -e "${RED}❌ openai library not installed${NC}"
    echo -e "${YELLOW}Please run: pip3 install openai${NC}"
    exit 1
fi
echo -e "   ✅ openai library installed"

# Check Litex compiler
echo -e "${GREEN}[3/5] Checking Litex compiler...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LITEX_BIN="$PROJECT_ROOT/../LitexGeo/golitex/litex_0.9.116-beta_darwin_arm64/litex"
if [ ! -f "$LITEX_BIN" ]; then
    echo -e "${RED}❌ Litex compiler not found: $LITEX_BIN${NC}"
    exit 1
fi
echo -e "   ✅ Litex compiler found"

# Set environment variables
export LITEX_BIN="$LITEX_BIN"

# Check seed files
echo -e "${GREEN}[4/5] Checking seed files...${NC}"

# Definition seed
DEF_SEED="database/definition_library_seed.lit"
if [ ! -f "$DEF_SEED" ]; then
    echo -e "${RED}❌ Definition seed file does not exist: $DEF_SEED${NC}"
    exit 1
fi
echo -e "   ✅ Definition seed: database/definition_library_seed.lit"

# Theorem seed
THM_SEED="database/theorem_library_seed.lit"
if [ ! -f "$THM_SEED" ]; then
    echo -e "${RED}❌ Theorem seed file does not exist: $THM_SEED${NC}"
    exit 1
fi
echo -e "   ✅ Theorem seed: database/theorem_library_seed.lit"

echo ""
echo -e "${GREEN}[5/5] Starting experiments...${NC}"
echo ""

# Run Definition experiment
if [ "$THM_ONLY" = false ]; then
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}Running Definition experiment${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "Seed library: database/definition_library_seed.lit"
    echo -e "Task count: 39 definition tasks"
    if [ "$TEST_MODE" = true ]; then
        echo -e "Test mode: Only run first 3 tasks"
    fi
    echo ""

    START_TIME=$(date +%s)

    if [ "$TEST_MODE" = true ]; then
        python3 scripts/run_litex_definitions.py 3
    else
        python3 scripts/run_litex_definitions.py
    fi

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Definition experiment completed (Duration: ${DURATION}sec)${NC}"
    echo ""
fi

# Run Theorem experiment
if [ "$DEF_ONLY" = false ]; then

    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}Running Theorem experiment${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo -e "Seed library: database/theorem_library_seed.lit"
    echo -e "Task count: 165 theorem tasks"
    if [ "$TEST_MODE" = true ]; then
        echo -e "Test mode: Only run first 3 tasks"
    fi
    echo ""

    START_TIME=$(date +%s)

    if [ "$TEST_MODE" = true ]; then
        python3 scripts/run_litex_theorems.py 3
    else
        python3 scripts/run_litex_theorems.py
    fi

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Theorem experiment completed (Duration: ${DURATION}sec)${NC}"
    echo ""
fi

echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ All experiments completed!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "Output directory:"
echo -e "  - Definition: litex_auto_validated_250tasks/run_*/"
echo -e "  - Theorem: litex_auto_validated_250tasks/theorems_only/run_*/"
echo ""
echo -e "View results:"
echo -e "  ls -lht litex_auto_validated_250tasks/*/run_*/"
