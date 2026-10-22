# LeanGeo Automated Build Experiment System - User Guide

## 📋 Table of Contents

1. [Environment Preparation](#environment-preparation)
2. [Initial Configuration](#initial-configuration)
3. [Running Experiments](#running-experiments)
4. [Viewing Results](#viewing-results)
5. [FAQ](#faq)

---

## Environment Preparation

### 1. Install Lean 4 and Lake

**Important**: The Lean 4 compiler and the Lake build tool are not included in the git repository and must be installed first.

#### macOS/Linux Installation

```bash
# Install elan (Lean version manager)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Restart the terminal or refresh the environment
source ~/.zshrc  # if using zsh
# or
source ~/.bashrc  # if using bash

# Verify the installation
elan --version    # should display the version number
lean --version    # should display Lean (version 4.x.x, ...)
lake --version    # should display the version number
```

#### Windows Installation

1. Download and install: https://github.com/leanprover/elan/releases
2. Or refer to the official documentation: https://leanprover-community.github.io/install/windows.html

#### Installation Locations

- **Lean compiler**: `~/.elan/toolchains/leanprover--lean4---v4.35.0/`
- **Mathlib library**: the project's `LeanGeo/.lake/packages/` directory
- **Global tools**: All Lean projects share the same compiler

### 2. Build the Lean Project (download Mathlib)

```bash
# Enter the LeanGeo directory
cd /path/to/auto-build/LeanGeo

# Build the project (the first run downloads Mathlib, about 300MB)
lake build
```

**Notes**:
- The first run takes 5-10 minutes to download Mathlib
- A stable network connection is required
- After the download completes, it compiles automatically, taking a total of about 10-15 minutes

---

## Initial Configuration

### 1. Configure the API Key

**Must be completed before the first run!**

```bash
# Enter the project directory
cd /path/to/auto-build/lean_auto_build_system

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
python3 scripts/run_lean_definitions.py 5

# Theorem experiment (5 tasks)
python3 scripts/run_lean_theorems.py 5
```

#### Full run
```bash
# Definition experiment (all 39 tasks)
python3 scripts/run_lean_definitions.py

# Theorem experiment (all 165 tasks)
python3 scripts/run_lean_theorems.py
```

### Method 3: Parallel execution

The Definition and Theorem experiments use independent seed libraries and can be run in parallel to save time:

```bash
# Run tests in parallel (5 tasks)
python3 scripts/run_lean_definitions.py 5 & python3 scripts/run_lean_theorems.py 5 & wait

# Run full experiments in parallel
python3 scripts/run_lean_definitions.py & python3 scripts/run_lean_theorems.py & wait
```

**Advantages**:
- ✅ Saves time by running both experiments simultaneously
- ✅ Independent seed libraries, no mutual interference
- ✅ Automatically waits for both experiments to complete

**Note**: When running in parallel, console logs will be interleaved. To view separate logs, check the `experiment.log` file in the output directory.

---

## Viewing Results

### Output Directory Structure

```
lean_auto_validated_250tasks/
├── definitions_only/
│   └── run_20261021_230000/    # Timestamped directory
│       ├── experiment.log      # Complete log
│       ├── library_final.lean  # Final generated library
│       ├── state.json          # Experiment state
│       └── attempts.json       # All attempt records
└── theorems_only/
    └── run_20261021_230000/
        ├── experiment.log
        ├── library_final.lean
        ├── state.json
        ├── attempts.json
        └── axioms_debt.md      # Axiom debt list
```

### Viewing Commands

```bash
# List all runs
ls -lt lean_auto_validated_250tasks/definitions_only/
ls -lt lean_auto_validated_250tasks/theorems_only/

# View the latest Definition experiment log
tail -f lean_auto_validated_250tasks/definitions_only/run_*/experiment.log

# View the latest Theorem experiment log
tail -f lean_auto_validated_250tasks/theorems_only/run_*/experiment.log

# View the generated library
cat lean_auto_validated_250tasks/definitions_only/run_*/library_final.lean
cat lean_auto_validated_250tasks/theorems_only/run_*/library_final.lean
```

### Output File Descriptions

| File | Description |
|------|-------------|
| `experiment.log` | Complete console log |
| `experiment_log.md` | Markdown-format log |
| `state.json` | Experiment state (completed tasks, etc.) |
| `library_final.lean` | Final complete generated library |
| `attempts.json` | Detailed records of all attempts (including token statistics) |
| `axioms_debt.md` | Axiom debt list (Theorem experiment only) |

---

## FAQ

### Q1: "lean: command not found"

**Cause**: Lean is not installed or the environment variable is not configured

**Solution**:
```bash
# Install elan and Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Refresh the environment
source ~/.zshrc  # or source ~/.bashrc

# Verify the installation
lean --version
```

### Q2: "API config file does not exist"

**Cause**: `config/api_config.json` was not created

**Solution**:
```bash
cp config/api_config.example.json config/api_config.json
# Then edit the file and fill in the API key
```

### Q3: "Please configure the API key"

**Cause**: The `api_key` in `api_config.json` is still `"your-api-key-here"`

**Solution**: Edit `config/api_config.json` and fill in the real API key

### Q4: "Unknown identifier `dot`"

**Cause**: The seed library was not loaded correctly

**Check**:
```bash
# Confirm the seed library exists
ls -la ../LeanGeo/LeanGeoCore/theorem_library_seed.lean

# Confirm the seed library content is correct (should include vec, dot, det definitions)
head -20 ../LeanGeo/LeanGeoCore/theorem_library_seed.lean
```

### Q5: Mathlib download failed or timed out

**Cause**: Network issues or unstable GitHub connection

**Solution**:
```bash
cd ../LeanGeo

# Clear the cache and retry
rm -rf .lake
lake build

# Or use a domestic mirror (if available)
# For specific configuration, refer to the Lean community documentation
```

### Q6: How to switch to the OpenAI API

**Solution**: Edit `config/api_config.json`:
```json
{
  "api_key": "sk-your-OpenAI-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

### Q7: What if the experiment run is interrupted?

**Note**: Each run creates a new timestamped directory, so you can simply re-run without overwriting previous results.

The experiment automatically skips definitions already in the seed library and continues processing subsequent tasks.

**Suggestions**:
- If interrupted due to network issues, simply re-run
- If due to a code error, check the log file to understand the cause of failure
- The complete log of each run is saved in `experiment.log`

### Q8: How to view token usage statistics?

**Solution**: View the `attempts.json` file:
```bash
# Requires the jq tool to be installed
cat lean_auto_validated_250tasks/definitions_only/run_*/attempts.json | jq '.[] | {task_id, total_tokens}'
```

### Q9: What if Lean compilation is very slow?

**Note**: The first build of Mathlib does take 10-15 minutes, which is normal.

**Optimization**:
```bash
# Use multi-core compilation (e.g., 8 cores)
cd ../LeanGeo
lake build -j8
```

### Q10: How to clean up old run results

**Solution**:
```bash
# Keep only the latest Definition run
cd lean_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# Keep only the latest Theorem run
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**Warning**: Please confirm you do not need this data before deleting!

---

## 🔧 How the System Works

1. **Task Assignment**: Process tasks one by one from a predefined task list
2. **Syntax Guidance**: Each task includes the complete Lean 4 syntax guide
3. **Code Generation**: The AI generates code based on the task description and syntax guide
4. **Real-time Verification**: The Lean REPL verifies the generated code
5. **Error Feedback**: Compilation errors are automatically fed back to the AI (up to 5 retries)
6. **Incremental Accumulation**: Verified code is committed to the session for use by subsequent tasks
7. **Complete Records**: All attempts, errors, and token usage information are recorded

This closed-loop system can automatically correct errors and continuously improve code quality.

---

## 🎯 Quick Reference

```bash
# Full workflow (first run)
# 1. Install Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.zshrc

# 2. Build the project
cd /path/to/auto-build/LeanGeo
lake build

# 3. Configure the API
cd ../lean_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # Fill in the API key

# 4. Test run
bash scripts/run_all_experiments.sh --test

# Full workflow (already configured)
bash scripts/run_all_experiments.sh
```

---

## 📚 More Documentation

- **System Architecture**: [README.md](README.md) - System overview and directory structure
- **API Configuration**: [config/README.md](config/README.md) - Detailed configuration options
- **Lean Syntax**: [prompts/lean_short_guide.md](prompts/lean_short_guide.md) - Complete syntax guide
- **Example Output**: [examples/README.md](examples/README.md) - Example run results
- **Lean Official Documentation**: https://leanprover.github.io/
- **Mathlib Documentation**: https://leanprover-community.github.io/mathlib4_docs/
