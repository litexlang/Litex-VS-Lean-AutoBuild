-- ============================================================
-- LeanGeo AutoBuild — REPL session export library
-- Number of committed entries: 36
-- ============================================================

-- LeanGeo base library: Definition seed library
-- Corresponds to Litex's definition_library_seed.lit

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- A point is a pair of real coordinates
def Point := ℝ × ℝ

-- Vector: from A to B
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- Dot product
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- Determinant (the z-component of the 2D cross product)
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1

-- ---------- Content committed in this session ----------

def distance_sq (A B : Point) : ℝ :=
  dot (vec A B) (vec A B)

def line (a b c : ℝ) (_ : a ≠ 0 ∨ b ≠ 0) : Set Point :=
  {p | a * p.1 + b * p.2 + c = 0}

def line_of (a b : Point) (_ : a ≠ b) : Set Point :=
  {p | det (vec a b) (vec a p) = 0}

def angle_cos_num (p q r : Point) : ℝ :=
  dot (vec q p) (vec q r)

def angle_cos_den (p q r : Point) : ℝ :=
  distance_sq q p * distance_sq q r

def circle (o : Point) (r : ℝ) : Set Point :=
  {p | distance_sq o p = r ^ 2}

def is_on_segment (p a b : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ t ≤ 1 ∧
    p.1 = (1 - t) * a.1 + t * b.1 ∧
    p.2 = (1 - t) * a.2 + t * b.2

def is_on_ray (p a b : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧
    p.1 = a.1 + t * (b.1 - a.1) ∧
    p.2 = a.2 + t * (b.2 - a.2)

def is_collinear (p q r : Point) : Prop :=
  det (vec p q) (vec p r) = 0

def are_segments_congruent (a b c d : Point) : Prop :=
  distance_sq a b = distance_sq c d

def are_angles_congruent (p q r u v w : Point) : Prop :=
  0 < angle_cos_den p q r ∧
  0 < angle_cos_den u v w ∧
  angle_cos_num p q r ^ 2 * angle_cos_den u v w =
    angle_cos_num u v w ^ 2 * angle_cos_den p q r ∧
  0 ≤ angle_cos_num p q r * angle_cos_num u v w

def is_right_angle (p q r : Point) : Prop :=
  dot (vec q p) (vec q r) = 0

def is_parallel (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ det (vec a b) (vec c d) = 0

def is_perpendicular (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ dot (vec a b) (vec c d) = 0

def is_line (L : Set Point) : Prop :=
  ∃ a b c : ℝ,
    (a ≠ 0 ∨ b ≠ 0) ∧
    L = {p : Point | a * p.1 + b * p.2 + c = 0}

def is_midpoint (m a b : Point) : Prop :=
  m.1 = (a.1 + b.1) / 2 ∧
  m.2 = (a.2 + b.2) / 2

def is_affine_combination (p a b : Point) : Prop :=
  ∃ t : ℝ,
    p.1 = (1 - t) * a.1 + t * b.1 ∧
    p.2 = (1 - t) * a.2 + t * b.2

def is_centroid (g a b c : Point) : Prop :=
  g.1 = (a.1 + b.1 + c.1) / 3 ∧
  g.2 = (a.2 + b.2 + c.2) / 3

def is_on_line (p a b : Point) (h : a ≠ b) : Prop :=
  p ∈ line_of a b h

def is_on_extension (p a b : Point) : Prop :=
  ∃ t : ℝ, 1 < t ∧
    p.1 = (1 - t) * a.1 + t * b.1 ∧
    p.2 = (1 - t) * a.2 + t * b.2

def is_foot (f p a b : Point) : Prop :=
  a ≠ b ∧
  is_collinear a b f ∧
  dot (vec p f) (vec a b) = 0

def is_angle_bisector (a b c d : Point) : Prop :=
  is_on_ray d b d ∧
  are_angles_congruent a b d d b c

def is_triangle (a b c : Point) : Prop :=
  ¬ is_collinear a b c

def is_isosceles (a b c : Point) : Prop :=
  are_segments_congruent a b a c

def is_equilateral (a b c : Point) : Prop :=
  are_segments_congruent a b b c ∧
  are_segments_congruent b c c a

def are_triangles_congruent (p q r u v w : Point) : Prop :=
  are_segments_congruent p q u v ∧
  are_segments_congruent q r v w ∧
  are_segments_congruent r p w u

def are_triangles_similar (p q r u v w : Point) : Prop :=
  are_angles_congruent q p r v u w ∧
  are_angles_congruent p q r u v w ∧
  are_angles_congruent p r q u w v

def is_parallelogram (a b c d : Point) : Prop :=
  is_parallel a b d c ∧ is_parallel a d b c

def is_rectangle (a b c d : Point) : Prop :=
  is_parallelogram a b c d ∧ is_right_angle d a b

def is_rhombus (a b c d : Point) : Prop :=
  is_parallelogram a b c d ∧ are_segments_congruent a b b c

def is_square (a b c d : Point) : Prop :=
  is_rectangle a b c d ∧ are_segments_congruent a b b c

def is_on_circle (p o : Point) (r : ℝ) : Prop :=
  distance_sq o p = r ^ 2

def are_concyclic (a b c d : Point) : Prop :=
  ∃ o : Point,
    distance_sq o a = distance_sq o b ∧
    distance_sq o b = distance_sq o c ∧
    distance_sq o c = distance_sq o d

def is_diameter_endpoints (a b o : Point) : Prop :=
  is_midpoint o a b

def rotated_90_cw (p c q : Point) : Prop :=
  q.1 = c.1 + (p.2 - c.2) ∧
  q.2 = c.2 - (p.1 - c.1)

def rotated_90_ccw (p c q : Point) : Prop :=
  q.1 = c.1 - (p.2 - c.2) ∧
  q.2 = c.2 + (p.1 - c.1)
