-- LeanGeo basics: definitions for theorem proving

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

-- Part 1: Basic definitions

-- Points are real coordinate pairs
abbrev Point := ℝ × ℝ

-- Vector from A to B
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- Dot product
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- 2D determinant (signed parallelogram area / cross product z-component)
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1

-- Squared Euclidean distance |ab|^2 (avoids square roots)
def distance_sq (a b : Point) : ℝ := dot (vec a b) (vec a b)

-- General form: the line ax + by + c = 0 (a, b not both zero)
def line (a b c : ℝ) (h : a ≠ 0 ∨ b ≠ 0) : Set Point := {p : Point | a * p.1 + b * p.2 + c = 0}

-- Two-point form: the unique line through distinct points a and b
def line_through_points (a b : Point) (h : a ≠ b) : Set Point := {p : Point | det (vec a p) (vec a b) = 0}

-- Cosine of angle pqr at q, without square roots
def angle_cos_num (p q r : Point) : ℝ := dot (vec q p) (vec q r)

def angle_cos_den (p q r : Point) : ℝ := distance_sq q p * distance_sq q r

-- Circle with center o and radius r
def circle (o : Point) (r : ℝ) : Set Point := {p : Point | distance_sq o p = r * r}

-- p lies on the closed segment between a and b
def is_on_segment (p a b : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ t ≤ 1 ∧ p.1 = (1 - t) * a.1 + t * b.1 ∧ p.2 = (1 - t) * a.2 + t * b.2

-- p lies on the ray from a through b (t >= 0)
def is_on_ray (p a b : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ p.1 = a.1 + t * (b.1 - a.1) ∧ p.2 = a.2 + t * (b.2 - a.2)

-- Points p, q, r are collinear
def is_collinear (p q r : Point) : Prop := det (vec p q) (vec p r) = 0

-- Segments ab and cd have equal length
def are_segments_congruent (a b c d : Point) : Prop := distance_sq a b = distance_sq c d

-- Angles pqr and uvw are congruent (same |cos|, same sign)
def are_angles_congruent (p q r u v w : Point) : Prop :=
  angle_cos_den p q r > 0 ∧
  angle_cos_den u v w > 0 ∧
  (angle_cos_num p q r)^2 * angle_cos_den u v w = (angle_cos_num u v w)^2 * angle_cos_den p q r ∧
  angle_cos_num p q r * angle_cos_num u v w ≥ 0

-- Angle pqr at q is a right angle
def is_right_angle (p q r : Point) : Prop :=
  p ≠ q ∧ r ≠ q ∧ dot (vec q p) (vec q r) = 0

-- Directed segments ab and cd are parallel
def is_parallel (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ det (vec a b) (vec c d) = 0

-- Directed segments ab and cd are perpendicular
def is_perpendicular (a b c d : Point) : Prop :=
  a ≠ b ∧ c ≠ d ∧ dot (vec a b) (vec c d) = 0

-- Set l is a line in the plane
def is_line (l : Set Point) : Prop :=
  ∃ a b c : ℝ, (a ≠ 0 ∨ b ≠ 0) ∧ ∃ h : a ≠ 0 ∨ b ≠ 0, l = line a b c h

-- m is the midpoint of segment ab
def is_midpoint (m a b : Point) : Prop :=
  m.1 = (a.1 + b.1) / 2 ∧ m.2 = (a.2 + b.2) / 2

-- p lies on the affine line through a and b
def is_affine_combination (p a b : Point) : Prop :=
  ∃ t : ℝ, p.1 = (1 - t) * a.1 + t * b.1 ∧ p.2 = (1 - t) * a.2 + t * b.2

-- g is the centroid of triangle abc
def is_centroid (g a b c : Point) : Prop :=
  g.1 = (a.1 + b.1 + c.1) / 3 ∧ g.2 = (a.2 + b.2 + c.2) / 3

-- p lies on the line through distinct points a and b
def is_on_line (p a b : Point) (h : a ≠ b) : Prop :=
  p ∈ line_through_points a b h

-- p lies on the extension of segment ab beyond b (t > 1)
def is_on_extension (p a b : Point) : Prop :=
  ∃ t : ℝ, t > 1 ∧ p.1 = (1 - t) * a.1 + t * b.1 ∧ p.2 = (1 - t) * a.2 + t * b.2

-- f is the foot of the perpendicular from p to line ab
def is_foot (f p a b : Point) (h : a ≠ b) : Prop :=
  is_on_line f a b h ∧ dot (vec p f) (vec a b) = 0

-- Ray bd bisects angle abc
def is_angle_bisector (a b c d : Point) : Prop :=
  are_angles_congruent a b d d b c

-- a, b, c form a non-degenerate triangle
def is_triangle (a b c : Point) : Prop := det (vec a b) (vec a c) ≠ 0

-- Triangle abc is isosceles with ab = ac
def is_isosceles (a b c : Point) : Prop :=
  is_triangle a b c ∧ are_segments_congruent a b a c

-- Triangle abc is equilateral
def is_equilateral (a b c : Point) : Prop :=
  is_triangle a b c ∧
  are_segments_congruent a b b c ∧
  are_segments_congruent b c c a

-- Triangles pqr and uvw are congruent by SSS
def are_triangles_congruent (p q r u v w : Point) : Prop :=
  is_triangle p q r ∧
  is_triangle u v w ∧
  are_segments_congruent p q u v ∧
  are_segments_congruent q r v w ∧
  are_segments_congruent r p w u

-- Triangles pqr and uvw are similar by AAA
def are_triangles_similar (p q r u v w : Point) : Prop :=
  is_triangle p q r ∧
  is_triangle u v w ∧
  are_angles_congruent q p r v u w ∧
  are_angles_congruent p q r u v w ∧
  are_angles_congruent p r q u w v

-- Quadrilateral abcd is a parallelogram
def is_parallelogram (a b c d : Point) : Prop :=
  is_parallel a b d c ∧ is_parallel a d b c

-- Quadrilateral abcd is a rectangle
def is_rectangle (a b c d : Point) : Prop :=
  is_parallelogram a b c d ∧ is_right_angle d a b

-- Quadrilateral abcd is a rhombus
def is_rhombus (a b c d : Point) : Prop :=
  is_parallelogram a b c d ∧ are_segments_congruent a b b c

-- Quadrilateral abcd is a square
def is_square (a b c d : Point) : Prop :=
  is_rectangle a b c d ∧ are_segments_congruent a b b c

-- p lies on the circle with center o and radius r
def is_on_circle (p o : Point) (r : ℝ) : Prop := distance_sq o p = r * r

-- Points a, b, c, d lie on a common circle
def are_concyclic (a b c d : Point) : Prop :=
  ∃ o : Point, distance_sq o a = distance_sq o b ∧
               distance_sq o b = distance_sq o c ∧
               distance_sq o c = distance_sq o d

-- a and b are endpoints of a diameter with center o
def is_diameter_endpoints (a b o : Point) : Prop := is_midpoint o a b

-- q is p rotated 90 degrees clockwise about c
def rotated_90_cw (q p c : Point) : Prop :=
  q.1 = c.1 + p.2 - c.2 ∧ q.2 = c.2 - p.1 + c.1

-- q is p rotated 90 degrees counterclockwise about c
def rotated_90_ccw (q p c : Point) : Prop :=
  q.1 = c.1 - p.2 + c.2 ∧ q.2 = c.2 + p.1 - c.1
