# Experiment Output Directory

This directory is for storing your own experiment run outputs.

## 📁 Directory Structure

```
litex_auto_validated_250tasks/
├── definitions_only/
│   └── run_YYYYMMDD_HHMMSS/    # Your Definition experiment output
└── theorems_only/
    └── run_YYYYMMDD_HHMMSS/    # Your Theorem experiment output
```

## ✅ Features

- **Auto-created**: Automatically creates timestamped directories when running experiments
- **No Overwriting**: Each run creates a new directory, old run results are preserved
- **Complete Records**: Contains logs, states, attempt records, and all other information

## 📊 Output File Description

Each run directory contains:

| File | Description |
|------|-------------|
| `experiment.log` | Complete console log |
| `experiment_log.md` | Markdown format log |
| `state.json` | Experiment state (completed tasks, etc.) |
| `library_final.lit` | Final generated complete library |
| `attempts.json` | Detailed record of all attempts |
| `axioms_debt.md` | Axiom debt list (Theorem only) |

## 🎯 Viewing Results

```bash
# List all runs
ls -lt litex_auto_validated_250tasks/*/

# View latest Definition run
ls -lt litex_auto_validated_250tasks/definitions_only/run_*/

# View latest Theorem run
ls -lt litex_auto_validated_250tasks/theorems_only/run_*/
```

## 🔄 Difference from Examples

- **`examples/`**: Pre-provided example outputs for reference and learning
- **`litex_auto_validated_250tasks/`**: Your own actual run outputs

## 🧹 Cleanup

If you need to clean up old run results:

```bash
# Delete all Definition runs (except the latest)
cd litex_auto_validated_250tasks/definitions_only
ls -t | tail -n +2 | xargs rm -rf

# Delete all Theorem runs (except the latest)
cd ../theorems_only
ls -t | tail -n +2 | xargs rm -rf
```

**Note**: Make sure you don't need this data before deleting!
