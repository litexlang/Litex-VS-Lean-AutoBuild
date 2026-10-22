# LitexGeo Automated Build Experiment System - User Guide

## 📋 Table of Contents

1. [Environment Preparation](#environment-preparation)
2. [Initial Configuration](#initial-configuration)
3. [Verifying the Environment](#verifying-the-environment)
4. [Running Experiments](#running-experiments)
5. [Viewing Results](#viewing-results)
6. [FAQ](#faq)

---

## Environment Preparation

### Obtaining the Litex Compiler

**Important**: This project uses the Litex 1.1.2-beta compiler. Because the compiler is large, it is not included in the git repository and must be obtained separately.

#### How to Obtain

**Method 1: From the Litex official repository**
```bash
# Visit the Litex official repository to get the latest version
# https://github.com/litexlang/litex/releases
```

**Method 2: Verify the in-project version (if already downloaded)**
```bash
# Check whether the compiler exists
ls -lh /path/to/auto-build/LitexGeo/golitex/target/release/litex

# Test the compiler
/path/to/auto-build/LitexGeo/golitex/target/release/litex --version
# Should display: Litex 1.1.2-beta
```

**Compiler location**:
- Used by this project: `../LitexGeo/golitex/target/release/litex`
- This is a universal build (no platform-specific versions)

---

## Initial Configuration

### 1. Configure the API Key

**Must be completed before the first run!**

```bash
# Enter the project directory
cd cd litex_auto_build_system

# Copy the configuration template
cp config/api_config.example.json config/api_config.json

# Edit the configuration file
vim config/api_config.json
# Or use another editor: code config/api_config.json
```

Configuration file contents:
```json
{
  "api_key": "sk-your-actual-key",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

**Security notes**:
- ✅ `api_config.json` is ignored by `.gitignore`
- ✅ It will not be committed to the git repository
- ⚠️ Do not share this file with others

Detailed configuration instructions: [config/README.md](config/README.md)

---

## Verifying the Environment

Run the verification script to confirm that all configurations are correct:

```bash
python3 scripts/final_verification.py
```

**Checks performed**:
- ✅ Python environment and version
- ✅ Whether the openai library is installed
- ✅ Whether the Litex compiler exists and supports session mode
- ✅ Whether the seed library files are complete
- ✅ Whether the experiment scripts can be imported
- ✅ Whether the validator works correctly
- ✅ Whether the Litex syntax guide exists

If all checks show ✅, the environment is configured correctly and you can start running experiments.

---

## Running Experiments

### Method 1: One-click run script (recommended)

#### Test mode (recommended for first run)
```bash
bash scripts/run_all_experiments.sh --test
```
- Each experiment runs only 3 tasks
- Estimated time: 20-30 minutes
- Suitable for verifying that the system works correctly

#### Full run
```bash
bash scripts/run_all_experiments.sh
```
- Definition experiment: 39 tasks
- Theorem experiment: 165 tasks
- Estimated time: 6-10 hours

#### Run separately
```bash
# Run only the Definition experiment
bash scripts/run_all_experiments.sh --def-only

# Run only the Theorem experiment
bash scripts/run_all_experiments.sh --thm-only
```

### Method 2: Run the Python scripts directly

#### Test mode
```bash
# Definition experiment (5 tasks)
# Note: Disable proxy if using DeepSeek API
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py 5

# Theorem experiment (5 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py 5
```

#### Full run
```bash
# Definition experiment (all 39 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py

# Theorem experiment (all 165 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py
```

### Method 3: Parallel execution

The Definition and Theorem experiments use independent seed libraries and can be run in parallel to save time:

```bash
# Run tests in parallel (5 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py 5 & \
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py 5 & \
wait

# Run full experiments in parallel
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py & \
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py & \
wait
```

**Advantages**:
- ✅ Saves time by running both experiments simultaneously
- ✅ Independent seed libraries, no mutual interference
- ✅ Automatically waits for both experiments to complete

**Note**: 
- When running in parallel, console logs will be interleaved. To view separate logs, check the `experiment.log` file in the output directory.
- If using DeepSeek API, always use `env -u http_proxy -u https_proxy -u all_proxy` to disable proxy

---

## Viewing Results

### Output Directory Structure

```
litex_auto_validated_250tasks/
├── definitions_only/
│   └── run_20261021_210000/    # Timestamped directory
│       ├── experiment.log      # Complete log
│       ├── library_final.lit   # Final generated library
│       ├── state.json          # Experiment state
│       └── attempts.json       # All attempt records
└── theorems_only/
    └── run_20261021_210000/
        ├── experiment.log
        ├── library_final.lit
        ├── state.json
        ├── attempts.json
        └── axioms_debt.md      # Axiom debt list
```

### Viewing Commands

```bash
# List all runs
ls -lt litex_auto_validated_250tasks/definitions_only/
ls -lt litex_auto_validated_250tasks/theorems_only/

# View the latest Definition experiment log
tail -f litex_auto_validated_250tasks/definitions_only/run_*/experiment.log

# View the latest Theorem experiment log
tail -f litex_auto_validated_250tasks/theorems_only/run_*/experiment.log

# View the generated library
cat litex_auto_validated_250tasks/definitions_only/run_*/library_final.lit
cat litex_auto_validated_250tasks/theorems_only/run_*/library_final.lit
```

### Output File Descriptions

| File | Description |
|------|-------------|
| `experiment.log` | Complete console log |
| `experiment_log.md` | Markdown-format log |
| `state.json` | Experiment state (completed tasks, etc.) |
| `library_final.lit` | Final complete generated library |
| `attempts.json` | Detailed records of all attempts (including token statistics) |
| `axioms_debt.md` | Axiom debt list (Theorem experiment only) |

---

## FAQ

### Q1: "API config file does not exist"

**Cause**: `config/api_config.json` was not created

**Solution**:
```bash
cp config/api_config.example.json config/api_config.json
# Then edit the file and fill in the API key
```

### Q2: "Please configure the API key"

**Cause**: The `api_key` in `api_config.json` is still `"your-api-key-here"`

**Solution**: Edit `config/api_config.json` and fill in the real API key

### Q3: "Litex compiler not found" or "litex: command not found"

**Cause**: The Litex compiler does not exist or the path is incorrect

**Solution**:
```bash
# 1. Check whether the compiler file exists
ls -lh ../LitexGeo/golitex/target/release/litex

# 2. If it does not exist, obtain it from the Litex official repository
# https://github.com/litexlang/litex/releases
# Download the litex_1.1.2-beta version

# 3. Set the environment variable to point to the correct path
export LITEX_BIN="/path/to/LitexGeo/golitex/target/release/litex"

# 4. Test the compiler
$LITEX_BIN --version  # Should display Litex 1.1.2-beta
```

### Q4: How to switch to the OpenAI API

**Solution**: Edit `config/api_config.json`:
```json
{
  "api_key": "sk-your-OpenAI-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### Q5: What if the experiment run is interrupted?

**Note**: Each run creates a new timestamped directory, so you can simply re-run without overwriting previous results.

The experiment automatically skips definitions already in the seed library and continues processing subsequent tasks.

**Suggestions**:
- If interrupted due to network issues, simply re-run
- If due to a code error, check the log file to understand the cause of failure
- The complete log of each run is saved in `experiment.log`

### Q6: How to view token usage statistics?

**Solution**: View the `attempts.json` file:
```bash
cat litex_auto_validated_250tasks/definitions_only/run_*/attempts.json | jq '.[] | {task_id, total_tokens}'
```

### Q7: How to clean up old run results

**Solution**:
```bash
# Keep only the latest Definition run
cd litex_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# Keep only the latest Theorem run
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**Warning**: Please confirm you do not need this data before deleting!

### Q8: SOCKS proxy error when calling DeepSeek API

**Cause**: Environment proxy settings interfere with DeepSeek API calls

**Solution**: Disable proxy when running experiments
```bash
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py 5
```

### Q9: Syntax errors with coordinate access

**Cause**: Litex 1.1.2-beta uses new syntax for coordinate access

**Solution**: Use `(1)`, `(2)` instead of `[1]`, `[2]`
```litex
# Correct (Litex 1.1.2-beta)
have fn vec(A, B cart(R, R)) cart(R, R) = (B(1) - A(1), B(2) - A(2))

# Wrong (old syntax)
have fn vec(A, B cart(R, R)) cart(R, R) = (B[1] - A[1], B[2] - A[2])
```

---

## 📚 More Documentation

- **System Architecture**: [README.md](README.md) - System overview and directory structure
- **API Configuration**: [config/README.md](config/README.md) - Detailed configuration options
- **Script Explanation**: [SCRIPTS_EXPLANATION.md](SCRIPTS_EXPLANATION.md) - Description of each script's functionality
- **Litex Syntax**: [prompts/litex_short_guide.md](prompts/litex_short_guide.md) - Complete 25KB syntax guide
- **Example Output**: [examples/README.md](examples/README.md) - Example run results

---

## 🔧 How the System Works

1. **Task Assignment**: Process tasks one by one from a predefined task list
2. **Syntax Guidance**: Each task includes the complete Litex syntax guide (25KB)
3. **Code Generation**: The AI generates code based on the task description and syntax guide
4. **Real-time Verification**: The Litex compiler verifies the generated code in session mode
5. **Error Feedback**: Compilation errors are automatically formatted and fed back to the AI (up to 5 retries)
6. **Incremental Accumulation**: Verified code is committed to the session for use by subsequent tasks
7. **Complete Records**: All attempts, errors, and token usage information are recorded

This closed-loop system can automatically correct errors and continuously improve code quality.

---

## 🎯 Quick Reference

```bash
# Full workflow (first run)
# 1. Obtain the Litex compiler (if you don't have it yet)
# Download litex_1.1.2-beta from https://github.com/litexlang/litex/releases

# 2. Verify the compiler
ls -lh ../LitexGeo/golitex/target/release/litex

# 3. Configure the API
cp config/api_config.example.json config/api_config.json
vim config/api_config.json                    # Fill in the API key

# 4. Verify the environment
python3 scripts/final_verification.py

# 5. Test run (disable proxy if using DeepSeek)
env -u http_proxy -u https_proxy -u all_proxy bash scripts/run_all_experiments.sh --test

# Full workflow (already configured)
python3 scripts/final_verification.py         # Verify the environment
env -u http_proxy -u https_proxy -u all_proxy bash scripts/run_all_experiments.sh           # Full run
```
