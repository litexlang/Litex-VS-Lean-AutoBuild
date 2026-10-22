# Lean 4 Short Guide (for Geometry Library Construction)

This guide covers the syntax, tactics, and battle-tested experience needed for building geometry theorem libraries in Lean 4, aligned with the Litex short guide (for proof style see §12.5, **don't copy Litex's fact-oriented approach directly**).

## ⚠️ Important Rules

### 🚫 Do not include import statements
**The seed library already contains all necessary imports, don't write import statements in your code!**

```lean
-- ❌ Error - Don't write import
import Mathlib.Data.Real.Basic

def distance_sq ...

-- ✅ Correct - Write definitions and theorems directly
def distance_sq (A B : Point) : ℝ := dot (vec A B) (vec A B)
```

**Remember: The seed library already has `import Mathlib.Data.Real.Basic`, you only need to write definitions and theorems!**

## 1. Basic Types and Definitions

### 1.1 Real Number Type
```lean
-- ⚠️ Note: Don't write import statements! The seed library already contains them!

-- ℝ is the real number type (already defined in the seed library)
-- ℝ × ℝ is a pair of real numbers (point type)
-- Point is already defined as ℝ × ℝ
```

### 1.2 Defining Functions
```lean
-- Define functions using def
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- Parameter type annotations
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- Return type must be explicit
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
```

### 1.3 Defining Predicates (Propositions)
```lean
-- Predicates return type Prop
def is_collinear (p q r : Point) : Prop := 
  det (vec p q) (vec p r) = 0

-- Can have multiple conditions
def is_parallel (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ det (vec a b) (vec c d) = 0
```

## 2. Theorem Proofs

### 2.1 Theorem Declaration
```lean
-- Use theorem keyword
theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  -- Proof goes here
```

### 2.2 Universal Quantifier (∀)
```lean
-- ∀ means "for all"
theorem example1 : ∀ (x : ℝ), x + 0 = x := by
  intro x
  ring
```

### 2.3 Existential Quantifier (∃)
```lean
-- ∃ means "there exists"
theorem example2 : ∃ (x : ℝ), x + 1 = 2 := by
  use 1
  ring
```

### 2.4 Logical Connectives
```lean
-- ∧ : and
-- ∨ : or  
-- ¬ : not
-- → : implies
-- ↔ : if and only if (iff)

def example_prop (a b : Point) : Prop :=
  a ≠ b ∧ (a.1 = 0 ∨ a.2 = 0)
```

## 3. Proof Tactics

### 3.1 intro - Introduce Variables
```lean
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h  -- Introduce x, y, and hypothesis h : x = y
  rw [h]       -- Rewrite
  rfl          -- Reflexivity
```

### 3.2 rfl - Reflexivity
```lean
-- Used to prove equations where both sides are identical
theorem example : 5 = 5 := by
  rfl
```

### 3.3 rw - Rewrite
```lean
-- Use an equation to rewrite
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h
  rw [h]  -- Replace x with y on the left side
  rfl
```

### 3.4 simp - Simplify
```lean
-- Automatically simplify expressions using simplification rules
theorem example : ∀ (x : ℝ), x + 0 = x := by
  intro x
  simp
```

### 3.5 ring - Ring Solver
```lean
-- Automatically prove identities in ring theory
theorem example : ∀ (x y : ℝ), (x + y)^2 = x^2 + 2*x*y + y^2 := by
  intro x y
  ring
```

### 3.6 field_simp - Field Simplification
```lean
-- Handle fractions and division
theorem example : ∀ (x : ℝ), x ≠ 0 → x / x = 1 := by
  intro x h
  field_simp
```

### 3.7 unfold - Unfold Definition
```lean
-- Unfold function or predicate definition
theorem example : ∀ (A B : Point), vec A B = (B.1 - A.1, B.2 - A.2) := by
  intro A B
  unfold vec  -- Unfold vec definition
  rfl
```

### 3.8 calc - Calculation-Style Proof
```lean
-- For multi-step equation derivations
theorem example : ∀ (x y : ℝ), x = y → x + 1 = y + 1 := by
  intro x y h
  calc x + 1 = y + 1 := by rw [h]
```

### 3.9 apply - Apply Theorem
```lean
-- Apply a known theorem or hypothesis
theorem example : ∀ (x : ℝ), x = x := by
  intro x
  apply Eq.refl  -- Apply reflexivity theorem
```

### 3.10 have - Add Intermediate Conclusion
```lean
theorem example : ∀ (x : ℝ), x + 0 = x := by
  intro x
  have h : 0 + x = x := by simp
  simp
```

## 4. Structures and Patterns

### 4.1 Accessing Tuple Elements
```lean
-- Point = ℝ × ℝ
-- Use .1 and .2 to access elements
def first_coord (p : Point) : ℝ := p.1
def second_coord (p : Point) : ℝ := p.2
```

### 4.2 Pattern Matching
```lean
-- Can directly destructure tuples
def example (p : Point) : ℝ := 
  let (x, y) := p
  x + y
```

### 4.3 Conditional Statements
```lean
-- Use if-then-else
def abs (x : ℝ) : ℝ :=
  if x ≥ 0 then x else -x
```

## 5. Common Proof Patterns

### 5.1 Proving Symmetry
```lean
theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq
  unfold dot
  unfold vec
  ring  -- Algebraic simplification
```

### 5.2 Proving Transitivity
```lean
theorem example_trans : ∀ (a b c d e f : Point),
  are_segments_congruent a b c d →
  are_segments_congruent c d e f →
  are_segments_congruent a b e f := by
  intro a b c d e f h1 h2
  unfold are_segments_congruent at *
  calc distance_sq a b = distance_sq c d := h1
    _ = distance_sq e f := h2
```

### 5.3 Unfold Definitions and Simplify
```lean
theorem example : ∀ (p q r : Point),
  is_collinear p q r → det (vec p q) (vec p r) = 0 := by
  intro p q r h
  unfold is_collinear at h
  exact h  -- h is already the conclusion we need
```

## 6. Types and Proofs

### 6.1 Propositions as Types
```lean
-- Prop is the type of propositions
-- A proof is an element of that proposition type
def example_prop : Prop := 1 + 1 = 2
def example_proof : example_prop := by rfl
```

### 6.2 Dependent Types
```lean
-- Types can depend on values
def example (n : ℕ) : n + 0 = n := by simp
```

## 7. Common Errors and Solutions

### 7.1 Type Mismatch
```
error: type mismatch
  ℝ
has type
  Type
but is expected to have type
  Prop
```
**Solution**: Check the return type of the definition. Predicates should return `Prop`, functions should return concrete types (like `ℝ`).

### 7.2 Tactic Failure
```
error: tactic 'rfl' failed, the left-hand side
  x + 1
is not definitionally equal to the right-hand side
  x + 2
```
**Solution**: `rfl` can only prove definitionally equal expressions. Use `ring` or other tactics for equations that require computation.

### 7.3 Unsolved Goals
```
error: unsolved goals
x : ℝ
⊢ x + 0 = x
```
**Solution**: The proof is incomplete. Add tactics to complete the proof (such as `simp` or `ring`).

### 7.4 Unknown Identifier
```
error: unknown identifier 'distance_sq'
```
**Solution**: Ensure the function is already defined, or you need to define it first.

## 8. Best Practices

### 8.1 Naming Conventions
- Type names: Start with uppercase (`Point`, `Line`)
- Function names: Lowercase with underscores (`distance_sq`, `vec`)
- Theorem names: Lowercase with underscores (`distance_sq_symm`, `collinear_symm`)
- Predicate names: Start with `is_` or `are_` (`is_collinear`, `are_congruent`)

### 8.2 Proof Structure
```lean
theorem theorem_name : statement := by
  intro ...           -- Introduce variables
  unfold ...          -- Unfold definitions
  have ... := ...     -- Intermediate steps
  calc ...            -- Calculation chain (if needed)
  ring / simp / ...   -- Final simplification
```

### 8.3 Comments
```lean
-- Single-line comments use --

/- 
  Multi-line comments
  use /- ... -/
-/

/-- 
  Documentation comments (shown in hover)
  use /-- ... -/
-/
def documented_function : ℝ := 42
```

## 9. Common Tactic Combinations

### 9.1 Unfold and Simplify
```lean
by
  intro x y
  unfold distance_sq dot vec
  ring
```

### 9.2 Rewrite Using Hypotheses
```lean
by
  intro x y h
  rw [h]
  rfl
```

### 9.3 Decompose AND Conditions
```lean
by
  intro h
  obtain ⟨h1, h2⟩ := h  -- Decompose h : A ∧ B into h1 : A and h2 : B
  ...
```

## 10. Mathematical Symbols

| Symbol | Input | Meaning |
|------|------|------|
| `ℝ` | `\R` or `\real` | Real numbers |
| `×` | `\times` | Cartesian product |
| `∀` | `\forall` | Universal quantifier |
| `∃` | `\exists` | Existential quantifier |
| `∧` | `\and` | Logical and |
| `∨` | `\or` | Logical or |
| `¬` | `\not` | Logical not |
| `→` | `\to` | Implies |
| `↔` | `\iff` | If and only if |
| `≠` | `\ne` | Not equal |
| `≤` | `\le` | Less than or equal |
| `≥` | `\ge` | Greater than or equal |

## 11. Example: Complete Proof

```lean
-- ⚠️ Don't write import! The seed library already contains it!

-- Seed library already has:
-- def Point := ℝ × ℝ
-- def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)
-- def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- You only need to write new definitions and theorems:
def distance_sq (A B : Point) : ℝ := dot (vec A B) (vec A B)

theorem distance_sq_symm : ∀ (A B : Point), 
  distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq
  unfold dot
  unfold vec
  ring
```

This example shows the correct code structure: **Write definitions and theorems directly, don't include import statements!**

## 12. Common Techniques (Battle-Tested Experience)

Aligned with Litex short guide's library construction habits; **don't copy proof style from Litex** (see 12.5).

### 12.1 Break Down in Natural Language First, Then Write Lean

Before solving a problem, write out your approach in natural language, then map it to code. It's recommended to put **brief natural language process** at the beginning of the proof as comments:

```lean
/-- Approach: unfold distance_sq / dot / vec, coordinate-level ring -/
theorem distance_sq_symm : ∀ (A B : Point),
    distance_sq A B = distance_sq B A := by
  intro A B
  unfold distance_sq dot vec
  ring
```

Outline: Given / Goal / Initial approach (unfold? calc? which lemma to use?).

### 12.2 Definitions Aim for Convenience, First Instinct Isn't Always Best

For the same geometric concept, choose **the definition that's easiest to prove later**.

```lean
-- ❌ Heavy: collinearity + equidistance
def is_midpoint (p a b : Point) : Prop :=
  is_collinear a p b ∧ distance_sq a p = distance_sq p b

-- ✅ Convenient: coordinate average (subsequent proofs are mostly algebraic)
def is_midpoint (p a b : Point) : Prop :=
  p.1 = (a.1 + b.1) / 2 ∧ p.2 = (a.2 + b.2) / 2
```

Principle: Definitions should serve subsequent reasoning, not just "sound geometrically right".

### 12.3 Fix Where You're Stuck; If Stuck, Change Approach

- When errors occur: Only fix **the first** failing goal, don't rewrite the whole section.
- Still stuck: Change approach — change definition shape, switch `calc`/`ring`/`linarith`, break down `have` intermediate lemmas.

### 12.4 Build Framework First, Use `sorry` / `axiom` When Stuck, Then Fill In Gradually

For library construction: **First establish interface and dependency skeleton, then fill in proof details**.

If a theorem repeatedly fails to prove but will be used later, you can first:

```lean
axiom point_difference_norm_pos :
  ∀ (a b : Point), a ≠ b →
    (b.1 - a.1)^2 + (b.2 - a.2)^2 > 0
```

Or temporarily use `sorry` (debt list same as above). axiom/`sorry` must be statements you believe are true; each records a debt, to be filled in later.

### 12.5 Lean is Tactic-Oriented (Different from Litex)

**Don't copy Litex's "fewer `by thm`, only write facts" approach directly to Lean.**

| | Litex | Lean |
|--|-------|------|
| Orientation | **fact-oriented**: main text writes what to prove | **tactic-oriented**: `by` block writes how to prove |
| Unfold definitions | Directly write equation facts | `unfold` / `rw` / `simp` / `dsimp` |
| Reuse conclusions | Use small lemmas `by thm` sparingly; only reference large theorems | `apply` / `exact` / `have :=` using library theorems is normal |
| Computation | Very long equation chains | `calc` + `ring` / `field_simp` / `linarith` |

Encouraged in Lean:

- Small `have` steps to pin down subgoals
- For coordinate geometry, prefer `unfold` followed by `ring`
- Use Mathlib lemmas when appropriate, don't refuse `apply` just to "be like Litex"

Motto: **Lean writes clear tactic paths; Litex writes clear facts. Don't mix the two styles.**

### 12.6 For Every Step, First Ask: Are the Premises Sufficient?

Before each tactic, think clearly: what is the current goal, what hypotheses are needed, has the previous step already provided them. `unknown identifier` / `failed to synthesize` / tactic failures are often because premises or types weren't set up properly.

## 13. Building LitexGeo (Lean) from Scratch: Three Minimal Concepts

Library construction order is the same: **Base functions → Relational predicates → Geometric predicates**.

### 13.1 Base: vec and dot

```lean
-- Seed library usually already has Point / vec / dot; shown for illustration:
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
```

### 13.2 Relations: is_collinear

```lean
def is_collinear (p q r : Point) : Prop :=
  det (vec p q) (vec p r) = 0
```

### 13.3 Geometric predicates: is_midpoint

```lean
def is_midpoint (p a b : Point) : Prop :=
  p.1 = (a.1 + b.1) / 2 ∧ p.2 = (a.2 + b.2) / 2
```

### 13.4 Summary

| Concept | Form | Dependencies | Unlocks |
|------|------|------|------|
| `vec` / `dot` (+`det`) | `def` | Coordinates | Length, perpendicularity, collinearity computations |
| `is_collinear` | `Prop` | `vec`,`det` | Positional relationships |
| `is_midpoint` | `Prop` | Coordinates | Midpoint-related theorems |

## 14. Common Tactic / Solver Shapes (Quick Reference)

Not Litex Builtin, but Lean-side "what shapes are easier to prove":

| Goal Shape | Common Approach |
|----------|----------|
| Polynomial / coordinate identities | `unfold` + `ring` |
| Field fractions | `field_simp` then `ring` |
| Linear inequalities | `linarith` / `nlinarith` |
| Definition expansion | `unfold` / `dsimp` / `rw [def]` |
| Equation chains | `calc` |
| Apply existing theorems | `apply` / `exact` / `have :=` |

Motto: First transform the goal into a shape that solvers can handle, then apply `ring`/`linarith`; if big steps don't work, break them down with `have`.
