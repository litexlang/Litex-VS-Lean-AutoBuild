# LitexGeo Directory

This directory is for storing Litex-related files and is not included in the git repository.

## 📁 Should Contain

### 1. Litex Compiler
```
LitexGeo/
└── golitex/
    └── litex_0.9.116-beta_darwin_arm64/
        └── litex
```

**How to Obtain**:
- Get from Litex official repository: https://github.com/litexlang/litex/releases
- Download `litex_0.9.116-beta` version for your platform

**Platform Versions**:
- macOS M1/M2: `darwin_arm64`
- macOS Intel: `darwin_amd64`
- Linux: `linux_*`
- Windows: `windows_*`

### 2. Litex Project Files (Optional)

If you need to manually write Litex code, you can create `.lit` files in this directory.

## 🚀 Setup Steps

```bash
# 1. Download Litex compiler
cd LitexGeo
mkdir -p golitex
# Extract the downloaded compiler to golitex/ directory

# 2. Test compiler
golitex/litex_0.9.116-beta_darwin_arm64/litex --version

# 3. Return to experiment system directory
cd ../litex_auto_build_system

# 4. Run experiments
bash scripts/run_all_experiments.sh --test
```

## 📝 Notes

- ⚠️ Contents of this directory are ignored in `.gitignore`
- ⚠️ Compiler is large (~10-50MB) and not included in git repository
- ✅ Only `.gitkeep` file is committed to git to preserve empty directory structure

## 🔗 Related Documentation

- **Litex Official**: https://github.com/litexlang/litex
- **System README**: `../litex_auto_build_system/README.md`
- **Usage Guide**: `../litex_auto_build_system/USAGE_GUIDE.md`
