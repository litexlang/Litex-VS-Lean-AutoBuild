# Litex vs. Lean: AI-Driven Geometry Library Construction

This repository contains two AI-driven systems for automatically constructing geometry libraries using large language models (LLMs):

- **LitexGeo** — geometry library construction using Litex.
- **LeanGeo** — geometry library construction using Lean 4.

Both systems generate definitions and mathematical theorems with AI and use their respective verification systems to check the generated content.

The central experiment evaluates how effectively AI can construct a mathematical library in each language, measuring **verified task completion, development time, and token consumption**.

## Experiment Results

### Theorem Generation

The following results compare the two systems on 165 geometry theorem tasks.

| Metric | Litex | Lean | Comparison |
|---|---:|---:|---|
| Theorem tasks | 165 | 165 | Same task set |
| Successful tasks | 150 | 115 | — |
| Success rate | 90.8% | 70.0% | Litex +20.8 percentage points |
| Total time | 280.8 min | 638.9 min | Litex 2.28× faster |
| Token consumption | 11.5M | 10.5M | Litex uses 9.5% more tokens |

| Key finding | Result |
|---|---|
| Higher theorem success rate | Litex: 90.8% vs. Lean: 70.0% |
| Shorter total execution time | Litex: 280.8 min vs. Lean: 638.9 min |
| Lower token consumption | Lean: 10.5M vs. Litex: 11.5M |

Under this experimental setup, Litex achieved a higher theorem-task success rate and shorter total execution time, while consuming more tokens.

These results are specific to the tested task set, prompts, libraries, models, and execution environments. They do not establish that Litex is universally superior to Lean.

## Experiment Tasks

The experiment contains 204 tasks in total.

| Task type | Description | Number of tasks |
|---|---|---:|
| Definitions | Define geometric functions, objects, and predicates | 39 |
| Theorems | Prove geometric and algebraic properties | 165 |
| **Total** | | **204** |

### Definition tasks

Examples include:

- Vector operations: `vec`, `dot`, and `det`.
- Distance and angle functions.
- Geometric objects: lines, circles, and triangles.
- Geometric predicates: parallelism, perpendicularity, and collinearity.

Both systems reportedly achieved a 100% success rate on the 39 definition tasks. However, Litex took 37.8 minutes and consumed 0.56M tokens, compared with Lean's 10.3 minutes and 0.44M tokens. Since these results do not demonstrate an advantage for Litex, definition-task performance is not included in the headline comparison.

### Theorem tasks

Examples include:

- Vector operation properties, such as commutativity and distributivity.
- Triangle angle sums and the Pythagorean theorem.
- Incidence and positional relationships among points, lines, and circles.

## System Comparison

### Language and proof style

| Feature | Litex | Lean |
|---|---|---|
| Version | 0.9.116-beta | 4.35.0 |
| Language paradigm | Declarative, mathematics-oriented | Functional, dependent type theory |
| Typical proof style | Fact-oriented reasoning and equality chains | Tactics and term-based proofs |
| Verification | Litex compiler/verifier | Lean elaboration and kernel checking |
| Incremental workflow | Supported in the experiment | Supported in the experiment |

### Library setup

| Feature | Litex | Lean |
|---|---|---|
| Initial geometry library | Built from scratch | Built from scratch for this experiment |
| Mathematical infrastructure | Manually defined in the experiment | Lean and Mathlib infrastructure |
| Geometry definitions | Experiment-specific library | Experiment-specific library |
| Environment setup | Download the Litex binary | Install Lean and build the project |

The comparison concerns these particular experiment systems, not the full capabilities of either language or its entire ecosystem.

### Illustrative Litex examples

A squared-distance definition:

```litex
have fn distance_sq(A, B cart(R, R)) R =
    let v = vec(A, B) in dot(v, v)
```

A line represented by its general-form equation:

```litex
have fn line(a, b, c R) set =
    {p cart(R, R) | a * p[1] + b * p[2] + c = 0}
```

A dot-product commutativity theorem:

```litex
thm dot_comm(u, v cart(R, R)) : dot(u, v) = dot(v, u)
proof:
  calc:
    dot(u, v)
    = u[1] * v[1] + u[2] * v[2]   by def dot
    = v[1] * u[1] + v[2] * u[2]   by comm_mul
    = dot(v, u)                    by def dot
qed
```

These snippets illustrate the intended mathematical presentation style. They are examples of the language, not independent evidence for the measured performance differences.

## Quick Start

### Litex system

```bash
# 1. Download the compiler from:
# https://github.com/litexlang/litex/releases
# Use version litex_0.9.116-beta.

# 2. Configure the API
cd litex_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json

# 3. Run a small test
bash scripts/run_all_experiments.sh --test

# 4. Run all tasks
bash scripts/run_all_experiments.sh
```

### Lean system

```bash
# 1. Install Lean using elan
curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh

# 2. Build the Lean project and its dependencies
cd LeanGeo
lake build

# 3. Configure the API
cd ../lean_auto_build_system
cp config/api_config.example.json config/api_config.json
vim config/api_config.json

# 4. Run a small test
bash scripts/run_all_experiments.sh --test

# 5. Run all tasks
bash scripts/run_all_experiments.sh
```

Configure the API key, base URL, and model in the corresponding `config/api_config.json` file before running either experiment.

Example configuration:

```json
{
  "api_key": "your-actual-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4"
}
```

Use your actual provider-supported model identifier.

## Repository Structure

```text
auto-build/
├── README.md
├── litex_auto_build_system/
│   ├── scripts/
│   ├── config/
│   ├── database/
│   ├── README.md
│   └── USAGE_GUIDE.md
├── lean_auto_build_system/
│   ├── scripts/
│   ├── config/
│   ├── prompts/
│   ├── README.md
│   └── USAGE_GUIDE.md
├── LitexGeo/
│   └── README.md
└── LeanGeo/
    └── README.md
```

The Litex compiler binary is obtained separately. The Lean project and its dependencies are built separately.

## Experiment Output

Each experiment generates a timestamped output directory containing records such as:

```text
*_auto_validated_250tasks/
├── definitions_only/
│   └── run_YYYYMMDD_HHMMSS/
│       ├── experiment.log
│       ├── library_final.*
│       ├── attempts.json
│       └── state.json
└── theorems_only/
    └── run_YYYYMMDD_HHMMSS/
        ├── experiment.log
        ├── library_final.*
        ├── attempts.json
        ├── axioms_debt.md
        └── state.json
```

The output files record experiment execution, generated libraries, task attempts, experiment state, and (for theorem runs) the axiom-debt report.

## Run Options

Test mode:

```bash
bash scripts/run_all_experiments.sh --test
```

Runs the first three tasks for a quick environment check.

Full mode:

```bash
bash scripts/run_all_experiments.sh
```

Runs the full set of 39 definition tasks and 165 theorem tasks.

Individual experiments:

```bash
python3 scripts/run_*_definitions.py --max-tasks 10
python3 scripts/run_*_theorems.py --max-tasks 10
```

## Documentation

- `litex_auto_build_system/README.md` — Litex experiment details.
- `litex_auto_build_system/USAGE_GUIDE.md` — Litex usage guide.
- `lean_auto_build_system/README.md` — Lean experiment details.
- `lean_auto_build_system/USAGE_GUIDE.md` — Lean usage guide.

## Related Links

- [Litex](https://github.com/litexlang/litex)
- [Lean](https://leanprover.github.io/)
- [Mathlib documentation](https://leanprover-community.github.io/mathlib4_docs/)

## Reproducibility and Interpretation

The reported results describe the observed performance of two AI-driven systems under a particular experimental configuration. A rigorous comparison should also document the model and version, prompts, retry limits, task ordering, library state, timeout policy, hardware, and the exact criterion for task success.

In particular, successful compilation should not automatically be interpreted as mathematical correctness unless the verification process and its trusted assumptions are also specified.

**Last updated:** 2026-10-22

**Experiment versions:** Litex 0.9.116-beta; Lean 4.35.0
