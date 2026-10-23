# Litex & Lean Auto-Build Experiment Systems

This repository contains two AI-driven geometry library auto-build experiment systems: **LitexGeo** and **LeanGeo**.

## 📊 Experiment Overview

Both systems aim to automatically generate geometry library definitions and theorems through AI, with real-time verification by their respective compilers.

### Experiment Tasks

| Type           | Task Description                                | Count |
| -------------- | ----------------------------------------------- | ----- |
| **Definition** | Define geometric basic functions and predicates | 39    |
| **Theorem**    | Prove geometric theorems                        | 165   |

**Definition Task Examples**:

- Define vector operations (vec, dot, det)
- Define distance and angle functions
- Define geometric objects (line, circle, triangle)
- Define geometric predicates (parallel, perpendicular, collinear, etc.)

**Theorem Task Examples**:

- Vector operation properties (commutativity, distributivity)
- Geometric relation theorems (triangle angle sum, Pythagorean theorem)
- Point, line, circle position relationship theorems

## 🎯 Experiment Results

### Performance Comparison Tables

#### Definition Experiment (39 tasks)

| System    | Success Rate     | Total Time  | Total Tokens | Avg Time/Task | Avg Tokens/Task |
| --------- | ---------------- | ----------- | ------------ | ------------- | --------------- |
| **Litex** | **100%** (39/39) | **1.0 min** | 542,375      | 1.5s          | 13,907          |
| **Lean**  | **100%** (39/39) | 8.2 min     | 210,129      | 12.6s         | 5,388           |

**Key Findings**:

- ✅ Both systems achieved 100% success rate
- ⚡ **Litex is 8.2× faster** than Lean
- 🔢 Litex consumed 2.6× more tokens than Lean
- 📊 Lean is more token-efficient per task

#### Theorem Experiment (165 tasks)

| System    | Success Rate        | Total Time   | Total Tokens | Avg Time/Task | Avg Tokens/Task |
| --------- | ------------------- | ------------ | ------------ | ------------- | --------------- |
| **Litex** | **100%** (165/165)  | **14.3 min** | 18,546,452   | 5.2s          | 112,403         |
| **Lean**  | **99.4%** (164/165) | 177.5 min    | 3,150,308    | 64.5s         | 19,093          |

**Key Findings**:

- ✅ Litex achieved 100% success vs Lean's 99.4%
- ⚡ **Litex is 12.4× faster** than Lean
- 🔢 Litex consumed 5.9× more tokens than Lean
- 📊 Lean is significantly more token-efficient
- 🚀 Litex shows better scalability on complex theorem proving

### Overall Summary

| Metric               | Litex Advantage                    | Lean Advantage           |
| -------------------- | ---------------------------------- | ------------------------ |
| **Success Rate**     | Higher (100% vs 99.4% on theorems) | -                        |
| **Speed**            | **8-12× faster**                   | -                        |
| **Token Efficiency** | -                                  | **3-6× more efficient**  |
| **Reliability**      | No failed tasks                    | 1 failed task (theorems) |

### Litex System

#### Definition Experiment

**Litex Code Example**:

```litex
# Define squared distance between two points
have fn distance_sq(A, B cart(R, R)) R = 
  let v = vec(A, B) in dot(v, v)

# Define line (general form equation)
have fn line(a, b, c R) set = 
  {p cart(R, R) | a * p[1] + b * p[2] + c = 0}
```

#### Theorem Experiment

**Litex Proof Example**:

```litex
# Vector dot product commutativity
thm dot_comm(u, v cart(R, R)) : dot(u, v) = dot(v, u)
proof:
  calc:
    dot(u, v)
    = u[1] * v[1] + u[2] * v[2]   by def dot
    = v[1] * u[1] + v[2] * u[2]   by comm_mul
    = dot(v, u)                    by def dot
qed
```

## ⚖️ System Feature Comparison

### Compiler and Language

| Feature           | Litex                               | Lean                        |
| ----------------- | ----------------------------------- | --------------------------- |
| Compiler          | Litex 0.9.116-beta                  | Lean 4.35.0                 |
| Language Paradigm | Declarative, natural language style | Functional, dependent types |
| Proof Style       | calc chain reasoning                | tactic proofs               |

**Litex Advantages**:

- ✅ **Natural Language Style**: Syntax close to math textbooks, easy to understand
- ✅ **Concise Proofs**: calc style is intuitive, suitable for geometric reasoning
- ✅ **Rapid Prototyping**: No complex type annotations needed, quick verification

### Verification Method

| Feature                 | Litex            | Lean                                       |
| ----------------------- | ---------------- | ------------------------------------------ |
| Verification Mode       | Session protocol | REPL (via lake env)                        |
| Incremental Compilation | ✅ Supported      | ✅ Supported                                |
| Compilation Speed       | Fast             | Slow (first time requires loading Mathlib) |

### Standard Library

| Feature                | Litex                     | Lean                   |
| ---------------------- | ------------------------- | ---------------------- |
| Standard Library       | None (build from scratch) | Mathlib (~300MB)       |
| Real Number Operations | Manually defined          | Ready-made (Real type) |
| Geometry Library       | Completely self-built     | Partially available    |

### Development Experience

| Feature      | Litex                   | Lean                                    |
| ------------ | ----------------------- | --------------------------------------- |
| Installation | Download binary and use | Need to install elan + download Mathlib |

### Performance Comparison

#### Definition Experiment (39 tasks)

| Metric            | Litex    | Lean     |
| ----------------- | -------- | -------- |
| Total Time        | 37.8 min | 10.3 min |
| Token Consumption | 0.56M    | 0.44M    |
| Success Rate      | 100%     | 100%     |

#### Theorem Experiment (165 tasks)

| Metric            | Litex     | Lean      |
| ----------------- | --------- | --------- |
| Total Time        | 280.8 min | 638.9 min |
| Token Consumption | 11.5M     | 10.5M     |
| Success Rate      | 90.8%     | 70%       |

### Overall Rating

| Dimension             | Litex | Lean  |
| --------------------- | ----- | ----- |
| **Ease of Use**       | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |
| **Rigor**             | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Learning Curve**    | ⭐⭐⭐⭐⭐ | ⭐⭐    |
| **Compilation Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |
| **Expressiveness**    | ⭐⭐⭐⭐⭐ | ⭐⭐⭐   |

---

## 🚀 Quick Start

### Litex System

```bash
# 1. Get the compiler
# Download litex_0.9.116-beta from https://github.com/litexlang/litex/releases
# Extract to LitexGeo/golitex/ directory

# 2. Configure API
cd litex_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # Fill in API key

# 3. Run experiment (test mode: first 3 tasks)
bash scripts/run_all_experiments.sh --test

# 4. Full run (all 204 tasks)
bash scripts/run_all_experiments.sh
```

### Lean System

```bash
# 1. Install Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
source ~/.zshrc

# 2. Build project (download Mathlib, first time takes 5-10 minutes)
cd LeanGeo
lake build

# 3. Configure API
cd ../lean_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json  # Fill in API key

# 4. Run experiment (test mode: first 3 tasks)
bash scripts/run_all_experiments.sh --test

# 5. Full run (all 204 tasks)
bash scripts/run_all_experiments.sh
```

## 📁 Directory Structure

```
auto-build/
│
├── README.md                          # This file
│
├── litex_auto_build_system/          # Litex experiment system
│   ├── scripts/                      # Experiment scripts
│   ├── config/                       # API configuration
│   ├── database/                     # Seed library
│   ├── README.md                     # Detailed documentation
│   └── USAGE_GUIDE.md               # Usage guide
│
├── lean_auto_build_system/           # Lean experiment system
│   ├── scripts/                      # Experiment scripts
│   ├── config/                       # API configuration
│   ├── prompts/                      # Syntax guide
│   ├── README.md                     # Detailed documentation
│   └── USAGE_GUIDE.md               # Usage guide
│
├── LitexGeo/                         # Litex compiler directory (obtain separately)
│   └── README.md                     # Acquisition instructions
│
└── LeanGeo/                          # Lean project directory (build separately)
    └── README.md                     # Build instructions
```

## ⚠️ After First Clone

### 1. Get Litex Compiler (not included in repository)

- Download from https://github.com/litexlang/litex/releases
- Version: `litex_0.9.116-beta`
- Place at: `LitexGeo/golitex/litex_0.9.116-beta_<platform>/litex`

### 2. Install Lean Environment (not included in repository)

```bash
# Install Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Build project (download Mathlib)
cd LeanGeo && lake build
```

### 3. Configure API Keys

Both systems require:

```bash
# Enter corresponding system directory
cd litex_auto_build_system  # or lean_auto_build_system

# Copy configuration template
cp config/api_config.example.json config/api_config.json

# Edit configuration, fill in API key
vim config/api_config.json
```

Configuration format:

```json
{
  "api_key": "your-actual-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

## 📊 Experiment Output

After running, the following will be generated in each system's output directory:

```
*_auto_validated_250tasks/
├── definitions_only/
│   └── run_YYYYMMDD_HHMMSS/
│       ├── experiment.log           # Complete run log
│       ├── library_final.*          # Generated complete library
│       ├── attempts.json            # All attempt records
│       └── state.json               # Experiment state
│
└── theorems_only/
    └── run_YYYYMMDD_HHMMSS/
        ├── experiment.log
        ├── library_final.*
        ├── attempts.json
        ├── axioms_debt.md           # Axiom debt list
        └── state.json
```

## 🎯 Run Options

### Test Mode

```bash
bash scripts/run_all_experiments.sh --test
# Each experiment runs only the first 3 tasks, quick environment verification
```

### Full Mode

```bash
bash scripts/run_all_experiments.sh
# Run all tasks (Definition: 39 + Theorem: 165)
```

### Individual Run

```bash
# Run only Definition experiment
python3 scripts/run_*_definitions.py --max-tasks 10

# Run only Theorem experiment  
python3 scripts/run_*_theorems.py --max-tasks 10
```

## 📖 Documentation Index

- **[litex_auto_build_system/README.md](litex_auto_build_system/README.md)** - Litex system detailed documentation
- **[litex_auto_build_system/USAGE_GUIDE.md](litex_auto_build_system/USAGE_GUIDE.md)** - Litex usage guide
- **[lean_auto_build_system/README.md](lean_auto_build_system/README.md)** - Lean system detailed documentation
- **[lean_auto_build_system/USAGE_GUIDE.md](lean_auto_build_system/USAGE_GUIDE.md)** - Lean usage guide

## 🔗 Related Links

- **Litex**: https://github.com/litexlang/litex
- **Lean**: https://leanprover.github.io/
- **Mathlib**: https://leanprover-community.github.io/mathlib4_docs/

## 📝 License

Please comply with the license requirements of the respective compilers and libraries.

---

**Last Updated**: 2026-10-22  
**System Versions**: Litex 0.9.116-beta, Lean 4.35.0
