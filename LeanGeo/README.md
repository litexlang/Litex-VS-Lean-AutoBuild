# LeanGeo Directory

This directory is for storing Lean project files and is not included in the git repository.

## 📁 Should Contain

### 1. Lake Project Configuration Files
```
LeanGeo/
├── lakefile.toml         # Lake build configuration
├── lean-toolchain        # Lean version specification
└── LeanGeoCore/
    └── theorem_library_seed.lean  # Seed library
```

### 2. Lean Project Structure
```
LeanGeo/
├── lakefile.toml
├── lean-toolchain
├── LeanGeoCore/
│   └── theorem_library_seed.lean
├── LeanGeoCore.lean
├── Main.lean
├── lake-manifest.json    # Lake dependency manifest
└── .lake/                # Mathlib and build cache (~300MB)
```

## 🚀 Setup Steps

### First Time Use

```bash
# 1. Install Lean (globally, only once)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.zshrc

# 2. Verify installation
lean --version
lake --version

# 3. Clone or create Lean project
cd LeanGeo
# If project files don't exist, you need to manually create lakefile.toml and other configs

# 4. Build project (download Mathlib, first time takes 5-10 minutes)
lake build

# 5. Return to experiment system directory
cd ../lean_auto_build_system

# 6. Run experiments
bash scripts/run_all_experiments.sh --test
```

## 📝 Notes

- ⚠️ Contents of this directory are ignored in `.gitignore`
- ⚠️ `.lake/` directory is ~300MB (Mathlib) and not included in git repository
- ⚠️ `lake-manifest.json` is auto-generated, no need to create manually
- ✅ Only `.gitkeep` file is committed to git to preserve empty directory structure

## 🔗 Lean Project Configuration Examples

### lakefile.toml
```toml
name = "LeanGeo"
version = "0.1.0"

[[lean_lib]]
name = "LeanGeoCore"
```

### lean-toolchain
```
leanprover/lean4:v4.35.0
```

### Seed Library Location
- **Definition seed**: `LeanGeoCore/theorem_library_seed.lean` (minimal version, 4 basic definitions)
- **Full backup**: `LeanGeoCore/theorem_library_seed_full.lean.bak` (182 lines)

## 🔗 Related Documentation

- **Lean Official**: https://leanprover.github.io/
- **Lean Installation**: https://leanprover-community.github.io/install/
- **System README**: `../lean_auto_build_system/README.md`
- **Usage Guide**: `../lean_auto_build_system/USAGE_GUIDE.md`
