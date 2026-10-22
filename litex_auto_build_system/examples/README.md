# Example Output

This directory contains complete experiment run examples for reference and learning purposes.

## 📁 Directory Structure

```
examples/
├── definitions_only/
│   └── run_20260920_145809/    # Definition experiment example
│       ├── experiment.log       # Complete log
│       ├── library_final.lit    # Final generated definition library
│       ├── state.json           # Experiment state
│       └── attempts.json        # All attempt records
└── theorems_only/
    └── run_20260928_153815/    # Theorem experiment example
        ├── experiment.log       # Complete log
        ├── library_final.lit    # Final generated theorem library
        ├── state.json           # Experiment state
        ├── attempts.json        # All attempt records
        └── axioms_debt.md       # Axiom debt list
```

## 📊 Example Statistics

### Definition Experiment Example (run_20260920_145809)
- **Completed Tasks**: 36 definitions
- **Success Rate**: High
- **Output**: Complete geometry definition library

### Theorem Experiment Example (run_20260928_153815)
- **Completed Tasks**: Multiple theorem proofs
- **Success Rate**: High
- **Output**: Complete library with theorem proofs

## 🎯 Purpose

1. **Reference Examples**: View format and content of experiment output
2. **Learning Material**: Learn how to write Litex code
3. **Comparison Verification**: Check if your run results are normal

## ⚠️ Notes

- ✅ These are **example outputs** and will not be overwritten by new experiments
- ✅ Actual run output is saved to `../litex_auto_validated_250tasks/`
- ✅ Safe to reference and learn from these examples

## 🔍 Viewing Examples

```bash
# View Definition example log
cat examples/definitions_only/run_20260920_145809/experiment.log

# View Theorem example log
cat examples/theorems_only/run_20260928_153815/experiment.log

# View generated libraries
cat examples/definitions_only/run_20260920_145809/library_final.lit
cat examples/theorems_only/run_20260928_153815/library_final.lit
```
