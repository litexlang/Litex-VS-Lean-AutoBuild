# LitexGeo Auto-Build Experiment System

This is a complete LitexGeo geometry library auto-build experiment system that uses AI agents to automatically generate definitions and theorems, with real-time verification by the Litex compiler.

## 📁 Directory Structure

```
litex_auto_build_system/
├── scripts/                          # Core scripts
│   ├── run_litex_definitions.py     # Definition experiment script
│   ├── run_litex_theorems.py        # Theorem experiment script
│   ├── litex_session.py             # Litex verifier
│   ├── final_verification.py        # Environment verification script
│   └── run_all_experiments.sh       # One-click run script
├── prompts/                          # Prompt documents
│   └── litex_short_guide.md         # Litex syntax guide
├── config/                           # Configuration files
│   ├── api_config.json              # API configuration (create yourself)
│   ├── api_config.example.json      # API configuration example
│   └── README.md                    # Configuration instructions
├── database/                         # Seed library
│   ├── definition_library_seed.lit  # Definition seed library
│   └── theorem_library_seed.lit     # Theorem seed library
├── litex_auto_validated_250tasks/   # Experiment output
│   ├── definitions_only/            # Definition experiment output
│   └── theorems_only/               # Theorem experiment output
├── examples/                         # Example output
│   ├── definitions_only/            # Definition examples
│   └── theorems_only/               # Theorem examples
└── README.md                         # This file
```

## 🚀 Quick Start

### 0. Get Litex Compiler (Required for First Use)

**Important**: This project uses Litex 1.1.2-beta compiler. Due to its large size, it is not included in the git repository and needs to be obtained separately.

#### Litex Compiler Location

The compiler used by this project is located at:
```
../LitexGeo/golitex/target/release/litex
```

#### How to Obtain

**Method 1: Get from Litex Official Repository**
```bash
# Visit Litex official repository for the latest version
# https://github.com/litexlang/litex/releases
```

**Method 2: Use Existing Version in Project (if already downloaded)**
```bash
# Verify compiler exists
ls -lh /path/to/auto-build/LitexGeo/golitex/target/release/litex

# Test compiler
/path/to/auto-build/LitexGeo/golitex/target/release/litex --version
```

**Installation Location Notes**:
- Litex compiler: in project at `../LitexGeo/golitex/target/release/litex`
- Compiler is a standalone binary, no dependencies required

### 1. Configure API Key (Required for First Run)

```bash
cd litex_auto_build_system

# Copy API configuration template
cp config/api_config.example.json config/api_config.json

# Edit configuration file, fill in your API key
# vim config/api_config.json or use other editor
```

Configuration file format:
```json
{
  "api_key": "your-actual-api-key-here",
  "base_url": "https://api.deepseek.com",
  "model": "deepseek-chat"
}
```

For detailed configuration instructions, see: `config/README.md`

### 2. Verify Environment

```bash
cd litex_auto_build_system
python3 scripts/final_verification.py
```

### 3. Run Experiments

#### One-Click Run (Recommended)

```bash
# Run complete experiments
bash scripts/run_all_experiments.sh

# Test mode (run only 3 tasks per experiment)
bash scripts/run_all_experiments.sh --test

# Run only Definition experiment
bash scripts/run_all_experiments.sh --def-only

# Run only Theorem experiment
bash scripts/run_all_experiments.sh --thm-only
```

#### Run Separately

```bash
# Definition experiment (test with 5 tasks)
# Note: Disable proxy if using DeepSeek API
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py 5

# Theorem experiment (test with 5 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py 5

# Full run
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py
```

#### Parallel Run

```bash
# Parallel run (test with 5 tasks)
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py 5 & \
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py 5 & \
wait

# Parallel full run
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py & \
env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_theorems.py & \
wait
```

**Note**: If you encounter SOCKS proxy errors, use the `env -u` commands above to disable proxy settings.

## 📊 Experiment Description

### Definition Experiment
- **Seed Library**: `database/definition_library_seed.lit` (309 bytes)
- **Task Count**: 39 definition tasks
- **Output Directory**: `litex_auto_validated_250tasks/definitions_only/run_YYYYMMDD_HHMMSS/`

### Theorem Experiment
- **Seed Library**: `database/theorem_library_seed.lit` (6.3KB)
- **Task Count**: 165 theorem tasks
- **Output Directory**: `litex_auto_validated_250tasks/theorems_only/run_YYYYMMDD_HHMMSS/`

## 🔧 System Requirements

- **Python**: 3.8+
- **Python Dependencies**: `pip3 install openai`
- **Litex Compiler**: 1.1.2-beta (obtain separately, see "Get Litex Compiler" section)
- **API Key**: DeepSeek or other OpenAI API compatible service

**Important Notes**:
- **Syntax Change**: Litex 1.1.2-beta uses `(1)`, `(2)` for coordinate access (not `[1]`, `[2]`)
- **Proxy Settings**: If using DeepSeek API, disable proxy with `env -u http_proxy -u https_proxy -u all_proxy`
- **Session Mode**: This version uses Litex session mode with unified JSON return format

## 🔐 API Configuration

This system uses external configuration files to manage API keys and **does not** hardcode keys into the code.

Configuration steps:
1. Copy `config/api_config.example.json` to `config/api_config.json`
2. Edit `config/api_config.json`, fill in your API key
3. `api_config.json` is ignored by `.gitignore` and will not be committed to git

Detailed instructions: `config/README.md`

## 📝 Output Files

Each run creates a timestamped subdirectory in the corresponding directory, containing:

| File | Description |
|------|-------------|
| `experiment.log` | Complete console log |
| `experiment_log.md` | Markdown format log |
| `state.json` | Experiment state (completed tasks, etc.) |
| `library_final.lit` | Final generated complete library |
| `attempts.json` | Detailed record of all attempts |
| `axioms_debt.md` | Axiom debt list (Theorem only) |

## 🎯 Key Features

- ✅ **Automatic Verification**: Real-time verification of generated code using Litex compiler session mode
- ✅ **Smart Error Feedback**: Compilation errors automatically formatted and fed back to AI for correction (max 5 retries)
- ✅ **Complete Syntax Guidance**: Each task includes 25KB Litex syntax guide
- ✅ **Incremental Build**: Build complete library progressively from minimal seed library
- ✅ **Independent Experiments**: Definition and Theorem use separate seed libraries, can run in parallel
- ✅ **Timestamped Output**: Each run creates new directory, won't overwrite old results
- ✅ **Complete Records**: Save all attempts, token usage, time consumption, etc.
- ✅ **External API Configuration**: Keys stored in configuration file, not hardcoded

## 📖 Related Documentation

- **System Comparison**: See `../LITEX_VS_LEAN_COMPARISON.md` for detailed comparison between Litex and Lean systems
- **Usage Guide**: See `USAGE_GUIDE.md` for detailed usage instructions
- **API Configuration**: See `config/README.md` for configuration options
- **Environment Verification**: Run `python3 scripts/final_verification.py`
- **Script Explanation**: See `SCRIPTS_EXPLANATION.md`
- **Litex Syntax**: See `prompts/litex_short_guide.md` (25KB complete guide)
- **Example Output**: See `examples/` directory

## 🔄 Version Control

- **`.gitignore`**: Configured to ignore user run output
- **Example Retention**: Examples in `examples/` directory are kept in git
- **User Output**: `litex_auto_validated_250tasks/*/run_*/` will be ignored

## 📞 Troubleshooting

If you encounter problems, please check:

1. **Litex Compiler**: Confirm compiler exists and is executable
   ```bash
   # Check compiler file
   ls -lh ../LitexGeo/golitex/target/release/litex
   
   # Test compiler
   ../LitexGeo/golitex/target/release/litex --version
   
   # Or set environment variable
   export LITEX_BIN="/path/to/LitexGeo/golitex/target/release/litex"
   ```

2. **API Configuration**: Confirm `config/api_config.json` exists and key is valid

3. **Python Dependencies**: Confirm `openai` library is installed
   ```bash
   pip3 install openai
   ```

4. **Seed Library Files**: Confirm both seed library files in `database/` directory are complete
   ```bash
   ls -lh database/definition_library_seed.lit
   ls -lh database/theorem_library_seed.lit
   ```

5. **Proxy Issues**: If encountering SOCKS proxy errors with DeepSeek API
   ```bash
   # Disable proxy when running experiments
   env -u http_proxy -u https_proxy -u all_proxy python3 scripts/run_litex_definitions.py
   ```

6. **Run Verification**: Execute `python3 scripts/final_verification.py` for comprehensive check

7. **Syntax Errors**: Litex 1.1.2-beta uses `(1)`, `(2)` for coordinates, not `[1]`, `[2]`
