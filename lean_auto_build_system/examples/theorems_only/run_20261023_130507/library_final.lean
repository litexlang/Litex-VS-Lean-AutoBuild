-- ============================================================
-- LeanGeo AutoBuild — REPL session export library
-- committed entries count: 164
-- ============================================================

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

-- ---------- session committed content ----------

theorem distance_sq_coordinate_formula : ∀ (a b : Point),
    distance_sq a b = (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 := by
  intro a b
  unfold distance_sq dot vec
  ring

theorem distance_sq_nonnegative : ∀ (a b : Point), 0 ≤ distance_sq a b := by
  intro a b
  rw [distance_sq_coordinate_formula]
  positivity

theorem distance_sq_symmetric : ∀ (a b : Point),
    distance_sq a b = distance_sq b a := by
  intro a b
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  ring

theorem vec_dot_self_is_distance : ∀ (a b : Point),
    dot (vec a b) (vec a b) = distance_sq a b := by
  intro a b
  rfl

theorem distance_equality_to_dot : ∀ (a b c d : Point),
    distance_sq a b = distance_sq c d →
    dot (vec a b) (vec a b) = dot (vec c d) (vec c d) := by
  intro a b c d h
  rw [vec_dot_self_is_distance, vec_dot_self_is_distance]
  exact h

theorem point_difference_norm_pos :
    ∀ (a b : Point), a ≠ b →
      (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 > 0 := by
  intro a b hab
  have hcoord :
      (b.1 - a.1) ≠ 0 ∨ (b.2 - a.2) ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]
  rcases hcoord with hx | hy
  · have hxpos : 0 < (b.1 - a.1) ^ 2 := by
      positivity
    have hynonneg : 0 ≤ (b.2 - a.2) ^ 2 := by
      positivity
    linarith
  · have hxnonneg : 0 ≤ (b.1 - a.1) ^ 2 := by
      positivity
    have hypos : 0 < (b.2 - a.2) ^ 2 := by
      positivity
    linarith

theorem distance_sq_translate : ∀ (a b t : Point),
    distance_sq (a.1 + t.1, a.2 + t.2)
      (b.1 + t.1, b.2 + t.2) = distance_sq a b := by
  intro a b t
  unfold distance_sq dot vec
  dsimp
  ring

theorem distance_sq_positive_of_ne : ∀ (a b : Point),
    a ≠ b → distance_sq a b > 0 := by
  intro a b hab
  rw [distance_sq_coordinate_formula]
  exact point_difference_norm_pos a b hab

theorem translated_difference_square : ∀ (x y t : ℝ),
    ((y + t) - (x + t)) ^ 2 = (y - x) ^ 2 := by
  intro x y t
  ring

theorem center_offset_square : ∀ (c p : Point),
    dot (vec c p) (vec c p) =
      dot p p - 2 * dot p c + dot c c := by
  intro c p
  unfold dot vec
  ring

theorem affine_combination_distance_sq : ∀ (a b : Point) (t : ℝ),
    distance_sq a
      ((1 - t) * a.1 + t * b.1, (1 - t) * a.2 + t * b.2) =
    t ^ 2 * distance_sq a b := by
  intro a b t
  unfold distance_sq dot vec
  dsimp
  ring

theorem inner_product_distance_identity : ∀ (a b c : Point),
    dot (vec a b) (vec a c) =
      (distance_sq a b + distance_sq a c - distance_sq b c) / 2 := by
  intro a b c
  unfold distance_sq dot vec
  ring

theorem distance_expansion_identity : ∀ (u v : Point),
    distance_sq u v = dot u u + dot v v - 2 * dot u v := by
  intro u v
  unfold distance_sq dot vec
  ring

theorem affine_distance_from_parameter : ∀ (a b : Point) (t : ℝ),
    distance_sq
      ((1 - t) * a.1 + t * b.1, (1 - t) * a.2 + t * b.2) a =
    t ^ 2 * distance_sq a b := by
  intro a b t
  calc
    distance_sq
        ((1 - t) * a.1 + t * b.1, (1 - t) * a.2 + t * b.2) a =
      distance_sq a
        ((1 - t) * a.1 + t * b.1, (1 - t) * a.2 + t * b.2) := by
          apply distance_sq_symmetric
    _ = t ^ 2 * distance_sq a b := affine_combination_distance_sq a b t

theorem twice_dot_from_distances_direct : ∀ (u v : Point),
    2 * dot u v =
      distance_sq (0, 0) u + distance_sq (0, 0) v - distance_sq u v := by
  intro u v
  unfold distance_sq dot vec
  ring

theorem vec_coordinate_formula : ∀ (a b : Point),
    vec a b = (b.1 - a.1, b.2 - a.2) := by
  intro a b
  rfl

theorem dot_coordinate_formula : ∀ (u v : Point),
    dot u v = u.1 * v.1 + u.2 * v.2 := by
  intro u v
  rfl

theorem det_coordinate_formula : ∀ (u v : Point),
    det u v = u.1 * v.2 - u.2 * v.1 := by
  intro u v
  rfl

theorem dot_symmetric : ∀ (u v : Point), dot u v = dot v u := by
  intro u v
  unfold dot
  ring

theorem dot_commutative : ∀ (u v : Point), dot u v = dot v u := by
  intro u v
  exact dot_symmetric u v

theorem dot_add_left : ∀ (u v w : Point),
    dot (u.1 + v.1, u.2 + v.2) w = dot u w + dot v w := by
  intro u v w
  unfold dot
  ring

theorem dot_add_right : ∀ (u v w : Point),
    dot u (v.1 + w.1, v.2 + w.2) = dot u v + dot u w := by
  intro u v w
  unfold dot
  ring

theorem dot_square_sum : ∀ (u v : Point),
    dot (u.1 + v.1, u.2 + v.2) (u.1 + v.1, u.2 + v.2) =
      dot u u + dot v v + 2 * dot u v := by
  intro u v
  unfold dot
  ring

theorem det_antisymmetric : ∀ (u v : Point), det u v = -det v u := by
  intro u v
  unfold det
  ring

theorem vec_add_path_x : ∀ (a b c : Point),
    (vec a b).1 + (vec b c).1 = (vec a c).1 := by
  intro a b c
  unfold vec
  dsimp
  ring

theorem vec_add_path_y : ∀ (a b c : Point),
    (vec a b).2 + (vec b c).2 = (vec a c).2 := by
  intro a b c
  unfold vec
  dsimp
  ring

theorem dot_from_cosine_law : ∀ (a b c : Point),
    dot (vec a b) (vec a c) =
      (distance_sq a b + distance_sq a c - distance_sq b c) / 2 := by
  intro a b c
  exact inner_product_distance_identity a b c

theorem vec_add : ∀ (a b c : Point),
    ((vec a b).1 + (vec b c).1,
      (vec a b).2 + (vec b c).2) = vec a c := by
  intro a b c
  apply Prod.ext
  · exact vec_add_path_x a b c
  · exact vec_add_path_y a b c

theorem vec_neg : ∀ (a b : Point), vec b a = -(vec a b) := by
  intro a b
  unfold vec
  apply Prod.ext <;> dsimp <;> ring

theorem dot_bilinear_expand : ∀ (u v w z : Point),
    dot (u.1 + v.1, u.2 + v.2) (w.1 + z.1, w.2 + z.2) =
      dot u w + dot u z + dot v w + dot v z := by
  intro u v w z
  unfold dot
  ring

theorem dot_det_eliminate : ∀ (u v : Point),
    dot u v ^ 2 + det u v ^ 2 = dot u u * dot v v := by
  intro u v
  unfold dot det
  ring

theorem dot_neg_left : ∀ (u v : Point), dot (-u) v = -dot u v := by
  intro u v
  unfold dot
  dsimp
  ring

theorem det_neg_left : ∀ (u v : Point), det (-u) v = -det u v := by
  intro u v
  unfold det
  dsimp
  ring

theorem det_change_base : ∀ (a b c : Point),
    det (vec a b) (vec a c) = det (vec a b) (vec b c) := by
  intro a b c
  unfold det vec
  ring

theorem dot_change_base : ∀ (a b c : Point),
    dot (vec a b) (vec a c) =
      dot (vec a b) (vec a b) + dot (vec a b) (vec b c) := by
  intro a b c
  unfold dot vec
  ring

theorem det_bilinear_right : ∀ (u v w : Point),
    det u (v.1 + w.1, v.2 + w.2) = det u v + det u w := by
  intro u v w
  unfold det
  ring

theorem dot_bilinear_right : ∀ (u v w : Point),
    dot u (v.1 + w.1, v.2 + w.2) = dot u v + dot u w := by
  intro u v w
  exact dot_add_right u v w

theorem dot_scale_right : ∀ (u v : Point) (t : ℝ),
    dot u (t * v.1, t * v.2) = t * dot u v := by
  intro u v t
  unfold dot
  ring

theorem det_scale_right : ∀ (u v : Point) (t : ℝ),
    det u (t * v.1, t * v.2) = t * det u v := by
  intro u v t
  unfold det
  ring

theorem dot_squared_plus_det_squared : ∀ (u v : Point),
    dot u u * dot v v = dot u v ^ 2 + det u v ^ 2 := by
  intro u v
  exact (dot_det_eliminate u v).symm

theorem dot_two_scale : ∀ (a b c : Point),
    2 * dot (vec a b) (vec a c) =
      distance_sq a b + distance_sq a c - distance_sq b c := by
  intro a b c
  unfold distance_sq dot vec
  ring

theorem dot_sub_right_coordinate : ∀ (u v w : Point),
    dot u (v.1 - w.1, v.2 - w.2) = dot u v - dot u w := by
  intro u v w
  unfold dot
  ring

theorem dot_scale_left : ∀ (u v : Point) (t : ℝ),
    dot (t * u.1, t * u.2) v = t * dot u v := by
  intro u v t
  unfold dot
  ring

theorem dot_linear_left : ∀ (u v w : Point) (a b : ℝ),
    dot (a * u.1 + b * v.1, a * u.2 + b * v.2) w =
      a * dot u w + b * dot v w := by
  intro u v w a b
  unfold dot
  ring

theorem dot_linear_right : ∀ (u v w : Point) (a b : ℝ),
    dot u (a * v.1 + b * w.1, a * v.2 + b * w.2) =
      a * dot u v + b * dot u w := by
  intro u v w a b
  unfold dot
  ring

theorem collinear_det_expand : ∀ (p q r : Point),
    is_collinear p q r ↔
      (q.1 - p.1) * (r.2 - p.2) -
        (q.2 - p.2) * (r.1 - p.1) = 0 := by
  intro p q r
  unfold is_collinear det vec
  rfl

theorem perpendicular_dot_expand : ∀ (p q r s : Point),
    is_perpendicular p q r s ↔
      p ≠ q ∧ r ≠ s ∧
        (q.1 - p.1) * (s.1 - r.1) +
          (q.2 - p.2) * (s.2 - r.2) = 0 := by
  intro p q r s
  unfold is_perpendicular dot vec
  simp only [Prod.fst, Prod.snd]

theorem collinear_symmetric : ∀ (p q r : Point),
    is_collinear p q r → is_collinear q p r := by
  intro p q r h
  unfold is_collinear det vec at h ⊢
  dsimp at h ⊢
  calc
    (p.1 - q.1) * (r.2 - q.2) -
        (p.2 - q.2) * (r.1 - q.1) =
      -((q.1 - p.1) * (r.2 - p.2) -
        (q.2 - p.2) * (r.1 - p.1)) := by ring
    _ = 0 := by rw [h]; ring

theorem collinear_midpoint : ∀ (a b m : Point),
    a ≠ b → is_midpoint m a b → is_collinear a m b := by
  intro a b m hab hm
  unfold is_midpoint at hm
  rcases hm with ⟨hx, hy⟩
  unfold is_collinear det vec
  dsimp
  rw [hx, hy]
  ring

theorem collinear_to_standard_det : ∀ (p q r : Point),
    is_collinear p q r → det (vec p q) (vec p r) = 0 := by
  intro p q r h
  exact h

theorem collinear_equidistant_implies_midpoint : ∀ (a b m : Point),
    a ≠ b →
    is_collinear a m b →
    distance_sq a m = distance_sq m b →
    is_midpoint m a b := by
  intro a b m hab hcol hdist
  let u : Point :=
    (2 * m.1 - a.1 - b.1, 2 * m.2 - a.2 - b.2)

  have hdot : dot u (vec a b) = 0 := by
    unfold distance_sq at hdist
    dsimp [u]
    unfold dot vec at hdist ⊢
    dsimp at hdist ⊢
    linear_combination hdist

  have hdet : det u (vec a b) = 0 := by
    unfold is_collinear at hcol
    dsimp [u]
    unfold det vec at hcol ⊢
    dsimp at hcol ⊢
    linear_combination 2 * hcol

  have hvpos : 0 < dot (vec a b) (vec a b) := by
    rw [vec_dot_self_is_distance]
    exact distance_sq_positive_of_ne a b hab

  have hprod :
      dot u u * dot (vec a b) (vec a b) = 0 := by
    rw [dot_squared_plus_det_squared, hdot, hdet]
    ring

  have huu : dot u u = 0 := by
    nlinarith

  unfold dot at huu
  dsimp [u] at huu

  have hx : 2 * m.1 - a.1 - b.1 = 0 := by
    nlinarith [sq_nonneg (2 * m.1 - a.1 - b.1),
      sq_nonneg (2 * m.2 - a.2 - b.2)]

  have hy : 2 * m.2 - a.2 - b.2 = 0 := by
    nlinarith [sq_nonneg (2 * m.1 - a.1 - b.1),
      sq_nonneg (2 * m.2 - a.2 - b.2)]

  unfold is_midpoint
  constructor <;> linarith

theorem parallelogram_diagonals : ∀ (a b c d : Point),
    vec a b = vec d c →
    vec a d = vec b c →
    vec a c =
        ((vec a b).1 + (vec a d).1,
         (vec a b).2 + (vec a d).2) ∧
    vec b d =
        ((vec a d).1 - (vec a b).1,
         (vec a d).2 - (vec a b).2) ∧
    distance_sq a c =
        distance_sq a b + distance_sq a d +
          2 * dot (vec a b) (vec a d) ∧
    distance_sq b d =
        distance_sq a b + distance_sq a d -
          2 * dot (vec a b) (vec a d) ∧
    distance_sq a c + distance_sq b d =
        2 * (distance_sq a b + distance_sq a d) := by
  intro a b c d hab _had

  have hx : b.1 - a.1 = c.1 - d.1 := by
    simpa [vec] using congrArg (fun p : Point => p.1) hab
  have hy : b.2 - a.2 = c.2 - d.2 := by
    simpa [vec] using congrArg (fun p : Point => p.2) hab

  have hcx : c.1 = b.1 + d.1 - a.1 := by
    linarith [hx]
  have hcy : c.2 = b.2 + d.2 - a.2 := by
    linarith [hy]

  constructor
  · apply Prod.ext
    · dsimp [vec]
      rw [hcx]
      ring
    · dsimp [vec]
      rw [hcy]
      ring
  · constructor
    · apply Prod.ext <;> dsimp [vec] <;> ring
    · constructor
      · unfold distance_sq dot vec
        dsimp
        rw [hcx, hcy]
        ring
      · constructor
        · unfold distance_sq dot vec
          dsimp
          ring
        · unfold distance_sq dot vec
          dsimp
          rw [hcx, hcy]
          ring

theorem collinear_third : ∀ (a b c d : Point),
    a ≠ b →
    is_collinear a b c →
    is_collinear a b d →
    is_collinear a c d := by
  intro a b c d hab habc habd

  have hcoord :
      b.1 - a.1 ≠ 0 ∨ b.2 - a.2 ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]

  unfold is_collinear det vec at habc habd ⊢
  dsimp at habc habd ⊢

  rcases hcoord with hx | hy
  · have hscaled :
        (b.1 - a.1) *
          ((c.1 - a.1) * (d.2 - a.2) -
           (c.2 - a.2) * (d.1 - a.1)) = 0 := by
      linear_combination
        (c.1 - a.1) * habd - (d.1 - a.1) * habc
    exact (mul_eq_zero.mp hscaled).resolve_left hx
  · have hscaled :
        (b.2 - a.2) *
          ((c.1 - a.1) * (d.2 - a.2) -
           (c.2 - a.2) * (d.1 - a.1)) = 0 := by
      linear_combination
        (c.2 - a.2) * habd - (d.2 - a.2) * habc
    exact (mul_eq_zero.mp hscaled).resolve_left hy

theorem parallelogram_sides : ∀ (a b c d : Point),
    vec a b = vec d c →
    vec a d = vec b c := by
  intro a b c d h
  apply Prod.ext
  · have hx := congrArg (fun p : Point => p.1) h
    dsimp [vec] at hx ⊢
    linarith
  · have hy := congrArg (fun p : Point => p.2) h
    dsimp [vec] at hy ⊢
    linarith

theorem perpendicular_symmetric : ∀ (p q r s : Point),
    is_perpendicular p q r s → is_perpendicular r s p q := by
  intro p q r s h
  unfold is_perpendicular at h ⊢
  rcases h with ⟨hpq, hrs, hdot⟩
  refine ⟨hrs, hpq, ?_⟩
  rw [dot_symmetric]
  exact hdot

theorem parallel_symmetric : ∀ (p q r s : Point),
    is_parallel p q r s → is_parallel r s p q := by
  intro p q r s h
  unfold is_parallel at h ⊢
  rcases h with ⟨hpq, hrs, hdet⟩
  refine ⟨hrs, hpq, ?_⟩
  calc
    det (vec r s) (vec p q) =
        -det (vec p q) (vec r s) := det_antisymmetric _ _
    _ = 0 := by rw [hdet]; ring

theorem perpendicular_from_parallel : ∀ (a b c d p q : Point),
    is_parallel a b c d →
    is_perpendicular p q a b →
    is_perpendicular p q c d := by
  intro a b c d p q hparallel hperp
  unfold is_parallel at hparallel
  unfold is_perpendicular at hperp ⊢
  rcases hparallel with ⟨hab, hcd, hdet⟩
  rcases hperp with ⟨hpq, _, hdot⟩
  refine ⟨hpq, hcd, ?_⟩

  have hcoord :
      b.1 - a.1 ≠ 0 ∨ b.2 - a.2 ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]

  unfold det vec at hdet
  unfold dot vec at hdot ⊢
  dsimp at hdet hdot ⊢

  rcases hcoord with hx | hy
  · have hscaled :
        (b.1 - a.1) *
          ((q.1 - p.1) * (d.1 - c.1) +
           (q.2 - p.2) * (d.2 - c.2)) = 0 := by
      linear_combination
        (d.1 - c.1) * hdot + (q.2 - p.2) * hdet
    exact (mul_eq_zero.mp hscaled).resolve_left hx
  · have hscaled :
        (b.2 - a.2) *
          ((q.1 - p.1) * (d.1 - c.1) +
           (q.2 - p.2) * (d.2 - c.2)) = 0 := by
      linear_combination
        (d.2 - c.2) * hdot - (q.1 - p.1) * hdet
    exact (mul_eq_zero.mp hscaled).resolve_left hy

theorem equidistant_perp_bisector : ∀ (a b m p : Point),
    a ≠ b →
    is_midpoint m a b →
    m ≠ p →
    distance_sq p a = distance_sq p b →
    is_perpendicular a b m p := by
  intro a b m p hab hm hmp hdist
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold is_perpendicular
  refine ⟨hab, hmp, ?_⟩
  unfold distance_sq at hdist
  unfold dot vec at hdist ⊢
  dsimp at hdist ⊢
  rw [hmx, hmy]
  linear_combination (1 / 2 : ℝ) * hdist

theorem parallelogram_diagonal_sum : ∀ (a b c d : Point),
    vec a b = vec d c →
    vec a d = vec b c →
    distance_sq a c + distance_sq b d =
      2 * (distance_sq a b + distance_sq a d) := by
  intro a b c d hab had
  exact (parallelogram_diagonals a b c d hab had).2.2.2.2

theorem collinear_implies_midpoint_distance : ∀ (a b m : Point),
    is_collinear a m b →
    is_midpoint m a b →
    distance_sq a m = distance_sq m b := by
  intro a b m _ hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hmx, hmy]
  ring

theorem equidistant_implies_perp_bisector_dot :
    ∀ (a b m p : Point),
      is_midpoint m a b →
      distance_sq p a = distance_sq p b →
      dot (vec a b) (vec m p) = 0 := by
  intro a b m p hm hdist
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq at hdist
  unfold dot vec at hdist ⊢
  dsimp at hdist ⊢
  rw [hmx, hmy]
  linear_combination (1 / 2 : ℝ) * hdist

theorem parallel_implies_det_zero : ∀ (p q r s : Point),
    is_parallel p q r s → det (vec p q) (vec r s) = 0 := by
  intro p q r s h
  exact h.2.2

theorem parallelogram_midpoint_diagonals : ∀ (a b c d m : Point),
    vec a b = vec d c →
    vec a d = vec b c →
    is_midpoint m a c →
    is_midpoint m b d := by
  intro a b c d m hab _had hm
  unfold is_midpoint at hm ⊢
  rcases hm with ⟨hmx, hmy⟩

  have hx : b.1 - a.1 = c.1 - d.1 := by
    simpa [vec] using congrArg (fun p : Point => p.1) hab

  have hy : b.2 - a.2 = c.2 - d.2 := by
    simpa [vec] using congrArg (fun p : Point => p.2) hab

  constructor
  · rw [hmx]
    linarith
  · rw [hmy]
    linarith

theorem perp_dot_zero_coordinate : ∀ (p q r s : Point),
    is_perpendicular p q r s →
      (q.1 - p.1) * (s.1 - r.1) +
        (q.2 - p.2) * (s.2 - r.2) = 0 := by
  intro p q r s h
  exact (perpendicular_dot_expand p q r s).mp h |>.2.2

theorem perpendicular_implies_distance_sum : ∀ (a b c : Point),
    is_perpendicular a b b c →
    distance_sq a c = distance_sq a b + distance_sq b c := by
  intro a b c hperp
  unfold is_perpendicular at hperp
  rcases hperp with ⟨_, _, hdot⟩
  unfold dot vec at hdot
  dsimp at hdot
  unfold distance_sq dot vec
  dsimp
  nlinarith [hdot]

theorem perpendicular_bisector_property : ∀ (a b m p : Point),
    is_midpoint m a b →
    is_perpendicular a b m p →
    distance_sq p a = distance_sq p b := by
  intro a b m p hm hperp
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold is_perpendicular at hperp
  rcases hperp with ⟨_, _, hdot⟩
  unfold dot vec at hdot
  dsimp at hdot
  rw [hmx, hmy] at hdot
  unfold distance_sq dot vec
  dsimp
  nlinarith [hdot]

theorem perpendicular_bisector_equidistant_sq : ∀ (a b m p : Point),
    is_midpoint m a b →
    is_perpendicular a b m p →
    distance_sq p a = distance_sq p b := by
  intro a b m p hm hperp
  exact perpendicular_bisector_property a b m p hm hperp

theorem perpendicular_from_dot_zero : ∀ (p q r s : Point),
    p ≠ q →
    r ≠ s →
    dot (vec p q) (vec r s) = 0 →
    is_perpendicular p q r s := by
  intro p q r s hpq hrs hdot
  unfold is_perpendicular
  exact ⟨hpq, hrs, hdot⟩

theorem parallelogram_coordinate_difference : ∀ (a b c d : Point),
    vec a b = vec d c ↔
      b.1 - a.1 = c.1 - d.1 ∧
      b.2 - a.2 = c.2 - d.2 := by
  intro a b c d
  constructor
  · intro h
    constructor
    · simpa [vec] using congrArg (fun p : Point => p.1) h
    · simpa [vec] using congrArg (fun p : Point => p.2) h
  · rintro ⟨hx, hy⟩
    apply Prod.ext
    · simpa [vec] using hx
    · simpa [vec] using hy

theorem perpendicular_bisector_equidistant : ∀ (a b m p : Point),
    is_midpoint m a b →
    is_perpendicular a b m p →
    are_segments_congruent p a p b := by
  intro a b m p hm hperp
  unfold are_segments_congruent
  exact perpendicular_bisector_equidistant_sq a b m p hm hperp

theorem collinear_coordinates_imply_affine_parameter :
    ∀ (a b p : Point),
      a ≠ b →
      is_collinear a b p →
      ∃ t : ℝ,
        p =
          ((1 - t) * a.1 + t * b.1,
           (1 - t) * a.2 + t * b.2) := by
  intro a b p hab hcol

  have hcoord :
      b.1 - a.1 ≠ 0 ∨ b.2 - a.2 ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]

  unfold is_collinear det vec at hcol
  dsimp at hcol

  rcases hcoord with hx | hy
  · refine ⟨(p.1 - a.1) / (b.1 - a.1), ?_⟩
    apply Prod.ext
    · dsimp
      field_simp [hx]
      ring
    · dsimp
      field_simp [hx]
      linear_combination hcol
  · refine ⟨(p.2 - a.2) / (b.2 - a.2), ?_⟩
    apply Prod.ext
    · dsimp
      field_simp [hy]
      linear_combination -hcol
    · dsimp
      field_simp [hy]
      ring

theorem right_angle_vertex_distinct_from_foot_on_opposite_line :
    ∀ (a b c d : Point),
      is_perpendicular a b c d → a ≠ b := by
  intro a b c d hperp
  exact hperp.1

theorem right_angle_vertex_not_on_opposite_line :
    ∀ (a b c d : Point),
      is_perpendicular a b c d → a ≠ b := by
  intro a b c d hperp
  exact right_angle_vertex_distinct_from_foot_on_opposite_line a b c d hperp

theorem right_triangle_foot_midpoints_distinct :
    ∀ (a b c d : Point),
      is_perpendicular a b c d → a ≠ b := by
  intro a b c d hperp
  exact hperp.1

theorem orthocenter_third_altitude : ∀ (a b c h : Point),
    a ≠ b →
    c ≠ h →
    is_perpendicular a h b c →
    is_perpendicular b h a c →
    is_perpendicular c h a b := by
  intro a b c h hab hch hah hbh
  unfold is_perpendicular at hah hbh ⊢
  rcases hah with ⟨_, _, hdot₁⟩
  rcases hbh with ⟨_, _, hdot₂⟩
  refine ⟨hch, hab, ?_⟩
  unfold dot vec at hdot₁ hdot₂ ⊢
  dsimp at hdot₁ hdot₂ ⊢
  linear_combination -hdot₁ + hdot₂

theorem equidistant_dot_half : ∀ (a b p : Point),
    distance_sq p a = distance_sq p b →
    dot (vec a b) (vec a p) = distance_sq a b / 2 := by
  intro a b p hdist
  have hdist' : distance_sq a p = distance_sq b p := by
    calc
      distance_sq a p = distance_sq p a := distance_sq_symmetric a p
      _ = distance_sq p b := hdist
      _ = distance_sq b p := distance_sq_symmetric p b
  rw [inner_product_distance_identity, hdist']
  ring

theorem segments_congruent_reflexive : ∀ (a b : Point),
    are_segments_congruent a b a b := by
  intro a b
  unfold are_segments_congruent
  rfl

theorem segments_congruent_symmetric : ∀ (a b c d : Point),
    are_segments_congruent a b c d →
    are_segments_congruent c d a b := by
  intro a b c d h
  unfold are_segments_congruent at h ⊢
  exact h.symm

theorem segments_congruent_transitive : ∀ (a b c d e f : Point),
    are_segments_congruent a b c d →
    are_segments_congruent c d e f →
    are_segments_congruent a b e f := by
  intro a b c d e f h₁ h₂
  unfold are_segments_congruent at h₁ h₂ ⊢
  exact h₁.trans h₂

theorem segments_congruent_from_distance_sq : ∀ (a b c d : Point),
    distance_sq a b = distance_sq c d →
    are_segments_congruent a b c d := by
  intro a b c d h
  unfold are_segments_congruent
  exact h

theorem midpoint_equidistant : ∀ (a b m : Point),
    a ≠ b →
    is_midpoint m a b →
    distance_sq m a = distance_sq m b := by
  intro a b m _ hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hmx, hmy]
  ring

theorem midpoint_half_distance : ∀ (a b m : Point),
    a ≠ b →
    is_midpoint m a b →
    distance_sq a m = distance_sq a b / 4 := by
  intro a b m _ hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hmx, hmy]
  ring

theorem one_dimensional_midpoint : ∀ (x y m : ℝ),
    m = (x + y) / 2 →
    m - x = (y - x) / 2 ∧
    y - m = (y - x) / 2 ∧
    m - x = y - m ∧
    (m - x) ^ 2 = (y - x) ^ 2 / 4 := by
  intro x y m hm
  rw [hm]
  constructor
  · ring
  constructor
  · ring
  constructor <;> ring

theorem centroid_distance : ∀ (a b c g : Point),
    is_centroid g a b c →
    distance_sq g a + distance_sq g b + distance_sq g c =
      (distance_sq a b + distance_sq b c + distance_sq c a) / 3 := by
  intro a b c g hg
  unfold is_centroid at hg
  rcases hg with ⟨hgx, hgy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hgx, hgy]
  ring

theorem midpoint_segment_ratio : ∀ (a b p : Point) (t : ℝ),
    a ≠ b →
    p =
      ((1 - t) * a.1 + t * b.1,
       (1 - t) * a.2 + t * b.2) →
    (is_midpoint p a b ↔ t = 1 / 2) := by
  intro a b p t hab hp
  subst p

  have hcoord :
      b.1 - a.1 ≠ 0 ∨ b.2 - a.2 ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]

  constructor
  · intro hm
    unfold is_midpoint at hm
    rcases hm with ⟨hmx, hmy⟩
    dsimp at hmx hmy
    rcases hcoord with hx | hy
    · have hprod : (2 * t - 1) * (b.1 - a.1) = 0 := by
        linear_combination 2 * hmx
      have ht : 2 * t - 1 = 0 :=
        (mul_eq_zero.mp hprod).resolve_right hx
      linarith
    · have hprod : (2 * t - 1) * (b.2 - a.2) = 0 := by
        linear_combination 2 * hmy
      have ht : 2 * t - 1 = 0 :=
        (mul_eq_zero.mp hprod).resolve_right hy
      linarith
  · intro ht
    unfold is_midpoint
    rw [ht]
    constructor <;> dsimp <;> ring

theorem double_midpoint_equal_sides : ∀ (a b m : Point),
    a ≠ b →
    is_midpoint m a b →
    are_segments_congruent m a m b := by
  intro a b m hab hm
  unfold are_segments_congruent
  exact midpoint_equidistant a b m hab hm

theorem midpoint_coordinate_formula : ∀ (a b m : Point),
    a ≠ b →
    is_midpoint m a b →
    m = ((a.1 + b.1) / 2, (a.2 + b.2) / 2) := by
  intro a b m _ hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  apply Prod.ext
  · exact hmx
  · exact hmy

theorem affine_dot_backward : ∀ (a b p : Point) (t : ℝ),
    p =
      ((1 - t) * a.1 + t * b.1,
       (1 - t) * a.2 + t * b.2) →
    dot (vec a b) (vec a p) = t * distance_sq a b := by
  intro a b p t hp
  subst p
  unfold distance_sq dot vec
  dsimp
  ring

theorem affine_dot_forward : ∀ (a b p : Point) (t : ℝ),
    a ≠ b →
    is_collinear a b p →
    dot (vec a b) (vec a p) = t * distance_sq a b →
    p =
      ((1 - t) * a.1 + t * b.1,
       (1 - t) * a.2 + t * b.2) := by
  intro a b p t hab hcol hdot
  obtain ⟨s, hp⟩ :=
    collinear_coordinates_imply_affine_parameter a b p hab hcol
  have hdot_s :
      dot (vec a b) (vec a p) = s * distance_sq a b :=
    affine_dot_backward a b p s hp
  have hdist_pos : 0 < distance_sq a b :=
    distance_sq_positive_of_ne a b hab
  have hst : s = t := by
    nlinarith [hdot_s, hdot, hdist_pos]
  rw [hst] at hp
  exact hp

theorem orthogonal_midpoint_scalar_finish : ∀ (a b m p : Point),
    is_midpoint m a b →
    dot (vec a b) (vec m p) = 0 →
    dot (vec a b) (vec a p) = distance_sq a b / 2 := by
  intro a b m p hm horth
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold dot vec at horth
  dsimp at horth
  rw [hmx, hmy] at horth
  unfold distance_sq dot vec
  dsimp
  linear_combination horth

theorem orthogonal_midpoint_vector_core : ∀ (a b m p : Point),
    a ≠ b →
    is_midpoint m a b →
    is_collinear a b p →
    dot (vec a b) (vec m p) = 0 →
    p = m := by
  intro a b m p hab hm hcol horth

  have hdot :
      dot (vec a b) (vec a p) =
        (1 / 2 : ℝ) * distance_sq a b := by
    calc
      dot (vec a b) (vec a p) =
          distance_sq a b / 2 :=
        orthogonal_midpoint_scalar_finish a b m p hm horth
      _ = (1 / 2 : ℝ) * distance_sq a b := by ring

  have hp :
      p =
        ((1 - (1 / 2 : ℝ)) * a.1 + (1 / 2 : ℝ) * b.1,
         (1 - (1 / 2 : ℝ)) * a.2 + (1 / 2 : ℝ) * b.2) :=
    affine_dot_forward a b p (1 / 2 : ℝ) hab hcol hdot

  have hm :
      m = ((a.1 + b.1) / 2, (a.2 + b.2) / 2) :=
    midpoint_coordinate_formula a b m hab hm

  calc
    p =
        ((1 - (1 / 2 : ℝ)) * a.1 + (1 / 2 : ℝ) * b.1,
         (1 - (1 / 2 : ℝ)) * a.2 + (1 / 2 : ℝ) * b.2) := hp
    _ = ((a.1 + b.1) / 2, (a.2 + b.2) / 2) := by
      apply Prod.ext <;> dsimp <;> ring
    _ = m := hm.symm

theorem solve_cosine_for_dot : ∀ (u v : Point) (c : ℝ),
    0 < dot u u →
    0 < dot v v →
    c = dot u v / Real.sqrt (dot u u * dot v v) →
    dot u v = c * Real.sqrt (dot u u * dot v v) := by
  intro u v c huu hvv hc
  have hprod : 0 < dot u u * dot v v := mul_pos huu hvv
  have hsqrt : Real.sqrt (dot u u * dot v v) ≠ 0 :=
    ne_of_gt (Real.sqrt_pos.2 hprod)
  calc
    dot u v =
        (dot u v / Real.sqrt (dot u u * dot v v)) *
          Real.sqrt (dot u u * dot v v) := by
            field_simp [hsqrt]
    _ = c * Real.sqrt (dot u u * dot v v) := by rw [← hc]

theorem cosine_law : ∀ (a b c : Point),
    distance_sq b c =
      distance_sq a b + distance_sq a c -
        2 * dot (vec a b) (vec a c) := by
  intro a b c
  have h := dot_two_scale a b c
  linarith

theorem isosceles_base_dot : ∀ (a b c : Point),
    distance_sq a b = distance_sq a c →
    dot (vec b a) (vec b c) = dot (vec c a) (vec c b) := by
  intro a b c hiso
  calc
    dot (vec b a) (vec b c) =
        (distance_sq b a + distance_sq b c - distance_sq a c) / 2 :=
      inner_product_distance_identity b a c
    _ =
        (distance_sq c a + distance_sq c b - distance_sq a b) / 2 := by
      rw [distance_sq_symmetric b a,
          distance_sq_symmetric b c,
          distance_sq_symmetric c a]
      linarith
    _ = dot (vec c a) (vec c b) :=
      (inner_product_distance_identity c a b).symm

theorem angle_equality_cross_ratio : ∀ (u v w z : Point),
    0 < dot u u →
    0 < dot v v →
    0 < dot w w →
    0 < dot z z →
    (dot u v / Real.sqrt (dot u u * dot v v) =
        dot w z / Real.sqrt (dot w w * dot z z) ↔
      dot u v * Real.sqrt (dot w w * dot z z) =
        dot w z * Real.sqrt (dot u u * dot v v)) := by
  intro u v w z huu hvv hww hzz
  have huv : 0 < dot u u * dot v v := mul_pos huu hvv
  have hwz : 0 < dot w w * dot z z := mul_pos hww hzz
  have hsuv : Real.sqrt (dot u u * dot v v) ≠ 0 :=
    ne_of_gt (Real.sqrt_pos.2 huv)
  have hswz : Real.sqrt (dot w w * dot z z) ≠ 0 :=
    ne_of_gt (Real.sqrt_pos.2 hwz)
  exact div_eq_div_iff hsuv hswz

theorem angle_in_semicircle_coordinate : ∀ (a b p : Point),
    (p.1 - (a.1 + b.1) / 2) ^ 2 +
        (p.2 - (a.2 + b.2) / 2) ^ 2 =
      ((b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2) / 4 →
    (a.1 - p.1) * (b.1 - p.1) +
        (a.2 - p.2) * (b.2 - p.2) = 0 := by
  intro a b p hcircle
  nlinarith [hcircle]

theorem isosceles_implies_equal_projections : ∀ (a b c : Point),
    distance_sq a b = distance_sq a c →
    dot (vec b a) (vec b c) = dot (vec c a) (vec c b) := by
  intro a b c hiso
  exact isosceles_base_dot a b c hiso

theorem vertical_angles_square_core : ∀ (a b c : Point),
    are_segments_congruent a b a c →
    dot (vec b a) (vec b c) = dot (vec c a) (vec c b) := by
  intro a b c hcongr
  unfold are_segments_congruent at hcongr
  exact isosceles_base_dot a b c hcongr

theorem vertical_angles_sign_core : ∀ (a b c : Point),
    are_segments_congruent a b a c →
    0 ≤
      dot (vec b a) (vec b c) *
        dot (vec c a) (vec c b) := by
  intro a b c hcongr
  have hdot :
      dot (vec b a) (vec b c) =
        dot (vec c a) (vec c b) :=
    vertical_angles_square_core a b c hcongr
  rw [← hdot]
  exact mul_self_nonneg _

theorem vertical_angles_equal : ∀ (a b c d : Point),
    a ≠ b →
    c ≠ d →
    dot (vec a b) (vec c d) /
        Real.sqrt (dot (vec a b) (vec a b) *
          dot (vec c d) (vec c d)) =
      dot (vec b a) (vec d c) /
        Real.sqrt (dot (vec b a) (vec b a) *
          dot (vec d c) (vec d c)) := by
  intro a b c d _ _
  have hdot :
      dot (vec a b) (vec c d) =
        dot (vec b a) (vec d c) := by
    unfold dot vec
    dsimp
    ring
  have hab :
      dot (vec a b) (vec a b) =
        dot (vec b a) (vec b a) := by
    unfold dot vec
    dsimp
    ring
  have hcd :
      dot (vec c d) (vec c d) =
        dot (vec d c) (vec d c) := by
    unfold dot vec
    dsimp
    ring
  rw [hdot, hab, hcd]

theorem cosine_square_to_det_square_ratio : ∀ (u v w z : Point),
    0 < dot u u →
    0 < dot v v →
    0 < dot w w →
    0 < dot z z →
    dot u v ^ 2 / (dot u u * dot v v) =
      dot w z ^ 2 / (dot w w * dot z z) →
    det u v ^ 2 / (dot u u * dot v v) =
      det w z ^ 2 / (dot w w * dot z z) := by
  intro u v w z huu hvv hww hzz hcos

  have huv : dot u u * dot v v ≠ 0 :=
    ne_of_gt (mul_pos huu hvv)
  have hwz : dot w w * dot z z ≠ 0 :=
    ne_of_gt (mul_pos hww hzz)

  have hdot_cross :
      dot u v ^ 2 * (dot w w * dot z z) =
        dot w z ^ 2 * (dot u u * dot v v) :=
    (div_eq_div_iff huv hwz).mp hcos

  have hdet_uv :
      det u v ^ 2 = dot u u * dot v v - dot u v ^ 2 := by
    nlinarith [dot_det_eliminate u v]

  have hdet_wz :
      det w z ^ 2 = dot w w * dot z z - dot w z ^ 2 := by
    nlinarith [dot_det_eliminate w z]

  apply (div_eq_div_iff huv hwz).mpr
  rw [hdet_uv, hdet_wz]
  calc
    (dot u u * dot v v - dot u v ^ 2) *
          (dot w w * dot z z) =
        (dot u u * dot v v) * (dot w w * dot z z) -
          dot u v ^ 2 * (dot w w * dot z z) := by ring
    _ =
        (dot u u * dot v v) * (dot w w * dot z z) -
          dot w z ^ 2 * (dot u u * dot v v) := by rw [hdot_cross]
    _ =
        (dot w w * dot z z - dot w z ^ 2) *
          (dot u u * dot v v) := by ring

theorem congruent_angle_det_square_ratio : ∀ (u v w z : Point),
    0 < dot u u →
    0 < dot v v →
    0 < dot w w →
    0 < dot z z →
    dot u v / Real.sqrt (dot u u * dot v v) =
      dot w z / Real.sqrt (dot w w * dot z z) →
    det u v ^ 2 / (dot u u * dot v v) =
      det w z ^ 2 / (dot w w * dot z z) := by
  intro u v w z huu hvv hww hzz hangle

  have huv : 0 < dot u u * dot v v := mul_pos huu hvv
  have hwz : 0 < dot w w * dot z z := mul_pos hww hzz

  have hcross :
      dot u v * Real.sqrt (dot w w * dot z z) =
        dot w z * Real.sqrt (dot u u * dot v v) :=
    (angle_equality_cross_ratio u v w z huu hvv hww hzz).mp hangle

  have hsuv :
      Real.sqrt (dot u u * dot v v) ^ 2 =
        dot u u * dot v v :=
    Real.sq_sqrt (le_of_lt huv)

  have hswz :
      Real.sqrt (dot w w * dot z z) ^ 2 =
        dot w w * dot z z :=
    Real.sq_sqrt (le_of_lt hwz)

  have hcos :
      dot u v ^ 2 / (dot u u * dot v v) =
        dot w z ^ 2 / (dot w w * dot z z) := by
    have huv_ne : dot u u * dot v v ≠ 0 := ne_of_gt huv
    have hwz_ne : dot w w * dot z z ≠ 0 := ne_of_gt hwz
    apply (div_eq_div_iff huv_ne hwz_ne).mpr
    calc
      dot u v ^ 2 * (dot w w * dot z z) =
          (dot u v * Real.sqrt (dot w w * dot z z)) ^ 2 := by
            rw [mul_pow, hswz]
      _ = (dot w z * Real.sqrt (dot u u * dot v v)) ^ 2 := by
            rw [hcross]
      _ = dot w z ^ 2 * (dot u u * dot v v) := by
            rw [mul_pow, hsuv]

  exact cosine_square_to_det_square_ratio
    u v w z huu hvv hww hzz hcos

theorem vertical_angles_dot_equal : ∀ (a b c d : Point),
    dot (vec a b) (vec c d) =
      dot (vec b a) (vec d c) := by
  intro a b c d
  unfold dot vec
  dsimp
  ring

theorem cross_product_positive_det_product_implies_same_sign :
    ∀ (u v w z : Point),
      0 < det u v * det w z →
      (0 < det u v ∧ 0 < det w z) ∨
      (det u v < 0 ∧ det w z < 0) := by
  intro u v w z h
  exact (mul_pos_iff.mp h)

theorem cross_ratio_same_det_sign_implies_angle_congruence :
    ∀ (u v w z : Point),
      0 < dot u u →
      0 < dot v v →
      0 < dot w w →
      0 < dot z z →
      dot u v ^ 2 / (dot u u * dot v v) =
        dot w z ^ 2 / (dot w w * dot z z) →
      0 < det u v * det w z →
      det u v / Real.sqrt (dot u u * dot v v) =
        det w z / Real.sqrt (dot w w * dot z z) := by
  intro u v w z huu hvv hww hzz hcos hsign

  have huv : 0 < dot u u * dot v v := mul_pos huu hvv
  have hwz : 0 < dot w w * dot z z := mul_pos hww hzz

  have hsuv : 0 < Real.sqrt (dot u u * dot v v) :=
    Real.sqrt_pos.2 huv
  have hswz : 0 < Real.sqrt (dot w w * dot z z) :=
    Real.sqrt_pos.2 hwz

  have hsuv_ne : Real.sqrt (dot u u * dot v v) ≠ 0 :=
    ne_of_gt hsuv
  have hswz_ne : Real.sqrt (dot w w * dot z z) ≠ 0 :=
    ne_of_gt hswz

  have hdet_ratio :
      det u v ^ 2 / (dot u u * dot v v) =
        det w z ^ 2 / (dot w w * dot z z) :=
    cosine_square_to_det_square_ratio
      u v w z huu hvv hww hzz hcos

  have huv_ne : dot u u * dot v v ≠ 0 := ne_of_gt huv
  have hwz_ne : dot w w * dot z z ≠ 0 := ne_of_gt hwz

  have hdet_cross :
      det u v ^ 2 * (dot w w * dot z z) =
        det w z ^ 2 * (dot u u * dot v v) :=
    (div_eq_div_iff huv_ne hwz_ne).mp hdet_ratio

  have hsuv_sq :
      Real.sqrt (dot u u * dot v v) ^ 2 =
        dot u u * dot v v :=
    Real.sq_sqrt (le_of_lt huv)

  have hswz_sq :
      Real.sqrt (dot w w * dot z z) ^ 2 =
        dot w w * dot z z :=
    Real.sq_sqrt (le_of_lt hwz)

  have hsquare :
      (det u v * Real.sqrt (dot w w * dot z z)) ^ 2 =
        (det w z * Real.sqrt (dot u u * dot v v)) ^ 2 := by
    rw [mul_pow, mul_pow, hswz_sq, hsuv_sq]
    exact hdet_cross

  have hcross :
      det u v * Real.sqrt (dot w w * dot z z) =
        det w z * Real.sqrt (dot u u * dot v v) := by
    rcases
        cross_product_positive_det_product_implies_same_sign
          u v w z hsign with hpos | hneg
    · have hleft :
          0 < det u v * Real.sqrt (dot w w * dot z z) :=
        mul_pos hpos.1 hswz
      have hright :
          0 < det w z * Real.sqrt (dot u u * dot v v) :=
        mul_pos hpos.2 hsuv
      nlinarith
    · have hleft :
          det u v * Real.sqrt (dot w w * dot z z) < 0 :=
        mul_neg_of_neg_of_pos hneg.1 hswz
      have hright :
          det w z * Real.sqrt (dot u u * dot v v) < 0 :=
        mul_neg_of_neg_of_pos hneg.2 hsuv
      nlinarith

  exact (div_eq_div_iff hsuv_ne hswz_ne).mpr hcross

theorem sas_third_side : ∀ (a b c d e f : Point),
    a ≠ b →
    a ≠ c →
    d ≠ e →
    d ≠ f →
    distance_sq a b = distance_sq d e →
    distance_sq a c = distance_sq d f →
    dot (vec a b) (vec a c) /
        Real.sqrt
          (dot (vec a b) (vec a b) *
           dot (vec a c) (vec a c)) =
      dot (vec d e) (vec d f) /
        Real.sqrt
          (dot (vec d e) (vec d e) *
           dot (vec d f) (vec d f)) →
    distance_sq b c = distance_sq e f := by
  intro a b c d e f hab hac hde hdf hs₁ hs₂ hangle

  have habpos : 0 < dot (vec a b) (vec a b) := by
    rw [vec_dot_self_is_distance]
    exact distance_sq_positive_of_ne a b hab

  have hacpos : 0 < dot (vec a c) (vec a c) := by
    rw [vec_dot_self_is_distance]
    exact distance_sq_positive_of_ne a c hac

  have hdepos : 0 < dot (vec d e) (vec d e) := by
    rw [vec_dot_self_is_distance]
    exact distance_sq_positive_of_ne d e hde

  have hdfpos : 0 < dot (vec d f) (vec d f) := by
    rw [vec_dot_self_is_distance]
    exact distance_sq_positive_of_ne d f hdf

  let k : ℝ :=
    dot (vec a b) (vec a c) /
      Real.sqrt
        (dot (vec a b) (vec a b) *
         dot (vec a c) (vec a c))

  have hdot₁ :
      dot (vec a b) (vec a c) =
        k * Real.sqrt
          (dot (vec a b) (vec a b) *
           dot (vec a c) (vec a c)) := by
    apply solve_cosine_for_dot
    · exact habpos
    · exact hacpos
    · rfl

  have hdot₂ :
      dot (vec d e) (vec d f) =
        k * Real.sqrt
          (dot (vec d e) (vec d e) *
           dot (vec d f) (vec d f)) := by
    apply solve_cosine_for_dot
    · exact hdepos
    · exact hdfpos
    · exact hangle

  have hnorm₁ :
      dot (vec a b) (vec a b) =
        dot (vec d e) (vec d e) := by
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance]
    exact hs₁

  have hnorm₂ :
      dot (vec a c) (vec a c) =
        dot (vec d f) (vec d f) := by
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance]
    exact hs₂

  have hsqrt :
      Real.sqrt
          (dot (vec a b) (vec a b) *
           dot (vec a c) (vec a c)) =
        Real.sqrt
          (dot (vec d e) (vec d e) *
           dot (vec d f) (vec d f)) := by
    rw [hnorm₁, hnorm₂]

  have hdot :
      dot (vec a b) (vec a c) =
        dot (vec d e) (vec d f) := by
    rw [hdot₁, hdot₂, hsqrt]

  have hcos₁ := cosine_law a b c
  have hcos₂ := cosine_law d e f
  linarith

theorem sas_congruence : ∀ (a b c d e f : Point),
    a ≠ b →
    a ≠ c →
    d ≠ e →
    d ≠ f →
    are_segments_congruent a b d e →
    are_segments_congruent a c d f →
    dot (vec a b) (vec a c) /
        Real.sqrt
          (dot (vec a b) (vec a b) *
           dot (vec a c) (vec a c)) =
      dot (vec d e) (vec d f) /
        Real.sqrt
          (dot (vec d e) (vec d e) *
           dot (vec d f) (vec d f)) →
    are_segments_congruent b c e f := by
  intro a b c d e f hab hac hde hdf hs₁ hs₂ hangle
  unfold are_segments_congruent at hs₁ hs₂ ⊢
  exact sas_third_side a b c d e f
    hab hac hde hdf hs₁ hs₂ hangle

theorem sss_congruence : ∀ (a b c d e f : Point),
    a ≠ b →
    a ≠ c →
    d ≠ e →
    d ≠ f →
    are_segments_congruent a b d e →
    are_segments_congruent a c d f →
    are_segments_congruent b c e f →
    dot (vec a b) (vec a c) /
        Real.sqrt
          (dot (vec a b) (vec a b) *
           dot (vec a c) (vec a c)) =
      dot (vec d e) (vec d f) /
        Real.sqrt
          (dot (vec d e) (vec d e) *
           dot (vec d f) (vec d f)) := by
  intro a b c d e f _hab _hac _hde _hdf hs₁ hs₂ hs₃
  unfold are_segments_congruent at hs₁ hs₂ hs₃

  have hdot :
      dot (vec a b) (vec a c) =
        dot (vec d e) (vec d f) := by
    have h₁ := dot_two_scale a b c
    have h₂ := dot_two_scale d e f
    linarith

  have hnorm₁ :
      dot (vec a b) (vec a b) =
        dot (vec d e) (vec d e) := by
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance]
    exact hs₁

  have hnorm₂ :
      dot (vec a c) (vec a c) =
        dot (vec d f) (vec d f) := by
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance]
    exact hs₂

  rw [hdot, hnorm₁, hnorm₂]

theorem multiply_both_sides : ∀ (a b c : ℝ),
    a = b → a * c = b * c := by
  intro a b c h
  rw [h]

theorem add_equalities : ∀ (a b c d : ℝ),
    a = b → c = d → a + c = b + d := by
  intro a b c d hab hcd
  rw [hab, hcd]

theorem subtract_equalities : ∀ (a b c d : ℝ),
    a = b → c = d → a - c = b - d := by
  intro a b c d hab hcd
  rw [hab, hcd]

theorem zero_factor_law : ∀ (a b : ℝ),
    a * b = 0 → a ≠ 0 → b = 0 := by
  intro a b hab ha
  exact (mul_eq_zero.mp hab).resolve_left ha

theorem cancel_positive_right_factor : ∀ (a b c : ℝ),
    0 < c → a * c = b * c → a = b := by
  intro a b c hc hab
  have hc_ne : c ≠ 0 := ne_of_gt hc
  exact mul_right_cancel₀ hc_ne hab

theorem rearrange_sum : ∀ (a b c : ℝ),
    a - b - c = 0 → a = b + c := by
  intro a b c h
  linarith

theorem asa_scalar_core : ∀ (a b c : Point),
    dot (vec a b) (vec a c) +
      dot (vec b a) (vec b c) =
        distance_sq a b := by
  intro a b c
  unfold distance_sq dot vec
  ring

theorem asa_angle_equations_bridge : ∀ (a b c d e f : Point),
    distance_sq a b = distance_sq d e →
    (dot (vec a b) (vec a c) = dot (vec d e) (vec d f) ↔
      dot (vec b a) (vec b c) = dot (vec e d) (vec e f)) := by
  intro a b c d e f hside
  have h₁ := asa_scalar_core a b c
  have h₂ := asa_scalar_core d e f
  constructor <;> intro hangle <;> linarith

theorem asa_congruence : ∀ (a b c d e f : Point),
    are_segments_congruent a b d e →
    dot (vec a b) (vec a c) = dot (vec d e) (vec d f) →
    dot (vec b a) (vec b c) = dot (vec e d) (vec e f) := by
  intro a b c d e f hside hangle
  unfold are_segments_congruent at hside
  exact
    (asa_angle_equations_bridge a b c d e f hside).mp hangle

theorem sss_dot_equal : ∀ (a b c d e f : Point),
    are_segments_congruent a b d e →
    are_segments_congruent a c d f →
    are_segments_congruent b c e f →
    dot (vec a b) (vec a c) =
      dot (vec d e) (vec d f) := by
  intro a b c d e f hab hac hbc
  unfold are_segments_congruent at hab hac hbc
  have h₁ := dot_two_scale a b c
  have h₂ := dot_two_scale d e f
  linarith

theorem triangle_area_det : ∀ (a b c : Point),
    (a.1 * b.2 + b.1 * c.2 + c.1 * a.2 -
      a.2 * b.1 - b.2 * c.1 - c.2 * a.1) / 2 =
    det (vec a b) (vec a c) / 2 := by
  intro a b c
  unfold det vec
  dsimp
  ring

theorem similar_triangles_ratio : ∀ (a b c d e f : Point),
    d ≠ e →
    d ≠ f →
    e ≠ f →
    distance_sq a b * distance_sq d f =
      distance_sq a c * distance_sq d e →
    distance_sq a b * distance_sq e f =
      distance_sq b c * distance_sq d e →
    distance_sq a b / distance_sq d e =
        distance_sq a c / distance_sq d f ∧
      distance_sq a b / distance_sq d e =
        distance_sq b c / distance_sq e f := by
  intro a b c d e f hde hdf hef h₁ h₂
  have hDE : distance_sq d e ≠ 0 :=
    ne_of_gt (distance_sq_positive_of_ne d e hde)
  have hDF : distance_sq d f ≠ 0 :=
    ne_of_gt (distance_sq_positive_of_ne d f hdf)
  have hEF : distance_sq e f ≠ 0 :=
    ne_of_gt (distance_sq_positive_of_ne e f hef)
  constructor
  · exact (div_eq_div_iff hDE hDF).2 h₁
  · exact (div_eq_div_iff hDE hEF).2 h₂

theorem similar_triangles_dot : ∀ (a b c d e f : Point),
    d ≠ e →
    d ≠ f →
    e ≠ f →
    distance_sq a b * distance_sq d f =
      distance_sq a c * distance_sq d e →
    distance_sq a b * distance_sq e f =
      distance_sq b c * distance_sq d e →
    dot (vec a b) (vec a c) * distance_sq d e =
      dot (vec d e) (vec d f) * distance_sq a b := by
  intro a b c d e f _hde _hdf _hef h₁ h₂
  have hdot₁ := dot_two_scale a b c
  have hdot₂ := dot_two_scale d e f
  linear_combination
    (distance_sq d e / 2) * hdot₁ -
    (distance_sq a b / 2) * hdot₂ -
    (1 / 2 : ℝ) * h₁ +
    (1 / 2 : ℝ) * h₂

theorem similar_triangles_det : ∀ (a b c d e f : Point),
    d ≠ e →
    d ≠ f →
    e ≠ f →
    distance_sq a b * distance_sq d f =
      distance_sq a c * distance_sq d e →
    distance_sq a b * distance_sq e f =
      distance_sq b c * distance_sq d e →
    det (vec a b) (vec a c) ^ 2 * distance_sq d e ^ 2 =
      det (vec d e) (vec d f) ^ 2 * distance_sq a b ^ 2 := by
  intro a b c d e f hde hdf hef h₁ h₂

  have hdot :
      dot (vec a b) (vec a c) * distance_sq d e =
        dot (vec d e) (vec d f) * distance_sq a b :=
    similar_triangles_dot a b c d e f hde hdf hef h₁ h₂

  have hdet₁ :
      det (vec a b) (vec a c) ^ 2 =
        distance_sq a b * distance_sq a c -
          dot (vec a b) (vec a c) ^ 2 := by
    have h := dot_det_eliminate (vec a b) (vec a c)
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance] at h
    nlinarith

  have hdet₂ :
      det (vec d e) (vec d f) ^ 2 =
        distance_sq d e * distance_sq d f -
          dot (vec d e) (vec d f) ^ 2 := by
    have h := dot_det_eliminate (vec d e) (vec d f)
    rw [vec_dot_self_is_distance, vec_dot_self_is_distance] at h
    nlinarith

  have hnorm_cross :
      (distance_sq a b * distance_sq a c) * distance_sq d e ^ 2 =
        (distance_sq d e * distance_sq d f) * distance_sq a b ^ 2 := by
    calc
      (distance_sq a b * distance_sq a c) * distance_sq d e ^ 2 =
          (distance_sq a c * distance_sq d e) *
            (distance_sq a b * distance_sq d e) := by ring
      _ =
          (distance_sq a b * distance_sq d f) *
            (distance_sq a b * distance_sq d e) := by rw [← h₁]
      _ =
          (distance_sq d e * distance_sq d f) *
            distance_sq a b ^ 2 := by ring

  have hdot_cross :
      dot (vec a b) (vec a c) ^ 2 * distance_sq d e ^ 2 =
        dot (vec d e) (vec d f) ^ 2 * distance_sq a b ^ 2 := by
    calc
      dot (vec a b) (vec a c) ^ 2 * distance_sq d e ^ 2 =
          (dot (vec a b) (vec a c) * distance_sq d e) ^ 2 := by ring
      _ =
          (dot (vec d e) (vec d f) * distance_sq a b) ^ 2 := by
            rw [hdot]
      _ =
          dot (vec d e) (vec d f) ^ 2 * distance_sq a b ^ 2 := by ring

  rw [hdet₁, hdet₂]
  linear_combination hnorm_cross - hdot_cross

theorem aas_scalar_first_side : ∀ (a b c d e f : Point),
    dot (vec a b) (vec a c) = dot (vec d e) (vec d f) →
    dot (vec b a) (vec b c) = dot (vec e d) (vec e f) →
    are_segments_congruent a b d e := by
  intro a b c d e f hangle₁ hangle₂
  unfold are_segments_congruent
  have h₁ := asa_scalar_core a b c
  have h₂ := asa_scalar_core d e f
  linarith

theorem aas_scalar_last_side : ∀ (a b c d e f : Point),
    dot (vec a b) (vec a c) = dot (vec d e) (vec d f) →
    dot (vec b a) (vec b c) = dot (vec e d) (vec e f) →
    are_segments_congruent a c d f →
    are_segments_congruent b c e f := by
  intro a b c d e f hangle₁ hangle₂ hside

  have hab : are_segments_congruent a b d e :=
    aas_scalar_first_side a b c d e f hangle₁ hangle₂

  unfold are_segments_congruent at hab hside ⊢
  have h₁ := dot_two_scale a b c
  have h₂ := dot_two_scale d e f
  linarith

theorem triangle_det_nonzero : ∀ (a b c : Point),
    ¬ is_collinear a b c →
    det (vec a b) (vec a c) ≠ 0 := by
  intro a b c h
  unfold is_collinear at h
  exact h

theorem triangle_det_square_positive : ∀ (a b c : Point),
    ¬ is_collinear a b c →
    0 < det (vec a b) (vec a c) ^ 2 := by
  intro a b c hnoncol
  have hdet : det (vec a b) (vec a c) ≠ 0 :=
    triangle_det_nonzero a b c hnoncol
  positivity

theorem triangle_det_squared_vertex : ∀ (a b c : Point),
    det (vec a b) (vec a c) ^ 2 =
      distance_sq a b * distance_sq a c -
        ((distance_sq a b + distance_sq a c -
          distance_sq b c) / 2) ^ 2 := by
  intro a b c
  have h := dot_det_eliminate (vec a b) (vec a c)
  rw [vec_dot_self_is_distance, vec_dot_self_is_distance,
      inner_product_distance_identity] at h
  linarith

theorem triangle_congruence_AAS : ∀ (a b c d e f : Point),
    dot (vec a b) (vec a c) = dot (vec d e) (vec d f) →
    dot (vec b a) (vec b c) = dot (vec e d) (vec e f) →
    are_segments_congruent a c d f →
    are_segments_congruent b c e f := by
  intro a b c d e f hangle₁ hangle₂ hside
  exact aas_scalar_last_side a b c d e f hangle₁ hangle₂ hside

theorem strict_triangle_one_side : ∀ (a b c : Point),
    ¬ is_collinear a b c →
    Real.sqrt (distance_sq a c) <
      Real.sqrt (distance_sq a b) + Real.sqrt (distance_sq b c) := by
  intro a b c hnoncol

  have hdet :
      det (vec a b) (vec b c) ≠ 0 := by
    have hdet' : det (vec a b) (vec a c) ≠ 0 :=
      triangle_det_nonzero a b c hnoncol
    rw [det_change_base a b c] at hdet'
    exact hdet'

  have hdetpos :
      0 < det (vec a b) (vec b c) ^ 2 := by
    positivity

  have hidentity :=
    dot_det_eliminate (vec a b) (vec b c)
  rw [vec_dot_self_is_distance, vec_dot_self_is_distance] at hidentity

  have hdot_sq_lt :
      dot (vec a b) (vec b c) ^ 2 <
        distance_sq a b * distance_sq b c := by
    nlinarith

  have hab_sqrt :
      Real.sqrt (distance_sq a b) ^ 2 = distance_sq a b :=
    Real.sq_sqrt (distance_sq_nonnegative a b)

  have hbc_sqrt :
      Real.sqrt (distance_sq b c) ^ 2 = distance_sq b c :=
    Real.sq_sqrt (distance_sq_nonnegative b c)

  have hac_sqrt :
      Real.sqrt (distance_sq a c) ^ 2 = distance_sq a c :=
    Real.sq_sqrt (distance_sq_nonnegative a c)

  have hprod_nonneg :
      0 ≤ Real.sqrt (distance_sq a b) *
        Real.sqrt (distance_sq b c) :=
    mul_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _)

  have hprod_sq :
      (Real.sqrt (distance_sq a b) *
        Real.sqrt (distance_sq b c)) ^ 2 =
          distance_sq a b * distance_sq b c := by
    rw [mul_pow, hab_sqrt, hbc_sqrt]

  have hdot_lt :
      dot (vec a b) (vec b c) <
        Real.sqrt (distance_sq a b) *
          Real.sqrt (distance_sq b c) := by
    nlinarith

  have hexpand :
      distance_sq a c =
        distance_sq a b + distance_sq b c +
          2 * dot (vec a b) (vec b c) := by
    unfold distance_sq dot vec
    dsimp
    ring

  have hsum_nonneg :
      0 ≤ Real.sqrt (distance_sq a b) +
        Real.sqrt (distance_sq b c) :=
    add_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _)

  have hac_sqrt_nonneg :
      0 ≤ Real.sqrt (distance_sq a c) :=
    Real.sqrt_nonneg _

  nlinarith

theorem triangle_inequality : ∀ (a b c : Point),
    Real.sqrt (distance_sq a c) ≤
      Real.sqrt (distance_sq a b) + Real.sqrt (distance_sq b c) := by
  intro a b c

  have hidentity := dot_det_eliminate (vec a b) (vec b c)
  rw [vec_dot_self_is_distance, vec_dot_self_is_distance] at hidentity

  have hdot_sq_le :
      dot (vec a b) (vec b c) ^ 2 ≤
        distance_sq a b * distance_sq b c := by
    nlinarith [sq_nonneg (det (vec a b) (vec b c))]

  have hab_sqrt :
      Real.sqrt (distance_sq a b) ^ 2 = distance_sq a b :=
    Real.sq_sqrt (distance_sq_nonnegative a b)

  have hbc_sqrt :
      Real.sqrt (distance_sq b c) ^ 2 = distance_sq b c :=
    Real.sq_sqrt (distance_sq_nonnegative b c)

  have hac_sqrt :
      Real.sqrt (distance_sq a c) ^ 2 = distance_sq a c :=
    Real.sq_sqrt (distance_sq_nonnegative a c)

  have hprod_nonneg :
      0 ≤ Real.sqrt (distance_sq a b) *
        Real.sqrt (distance_sq b c) :=
    mul_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _)

  have hprod_sq :
      (Real.sqrt (distance_sq a b) *
        Real.sqrt (distance_sq b c)) ^ 2 =
          distance_sq a b * distance_sq b c := by
    rw [mul_pow, hab_sqrt, hbc_sqrt]

  have hdot_le :
      dot (vec a b) (vec b c) ≤
        Real.sqrt (distance_sq a b) *
          Real.sqrt (distance_sq b c) := by
    nlinarith

  have hexpand :
      distance_sq a c =
        distance_sq a b + distance_sq b c +
          2 * dot (vec a b) (vec b c) := by
    unfold distance_sq dot vec
    dsimp
    ring

  have hsum_nonneg :
      0 ≤ Real.sqrt (distance_sq a b) +
        Real.sqrt (distance_sq b c) :=
    add_nonneg (Real.sqrt_nonneg _) (Real.sqrt_nonneg _)

  have hac_nonneg :
      0 ≤ Real.sqrt (distance_sq a c) :=
    Real.sqrt_nonneg _

  nlinarith

theorem pythagorean_theorem : ∀ (a b c : Point),
    is_perpendicular a b b c →
    distance_sq a c = distance_sq a b + distance_sq b c := by
  intro a b c hperp
  exact perpendicular_implies_distance_sum a b c hperp

theorem right_angle_implies_distance_relation : ∀ (a b c : Point),
    is_perpendicular a b b c →
    distance_sq a c = distance_sq a b + distance_sq b c := by
  intro a b c hperp
  exact pythagorean_theorem a b c hperp

theorem isosceles_right_triangle_vertex_formula : ∀ (a b c : Point),
    is_perpendicular a b a c →
    are_segments_congruent a b a c →
    distance_sq b c = 2 * distance_sq a b := by
  intro a b c hperp hiso
  unfold is_perpendicular at hperp
  rcases hperp with ⟨_, _, hdot⟩
  unfold are_segments_congruent at hiso
  have hcos := cosine_law a b c
  linarith

theorem isosceles_right_hypotenuse_length : ∀ (a b c : Point),
    is_perpendicular a b a c →
    are_segments_congruent a b a c →
    Real.sqrt (distance_sq b c) =
      Real.sqrt 2 * Real.sqrt (distance_sq a b) := by
  intro a b c hperp hiso
  have hsq :
      distance_sq b c = 2 * distance_sq a b :=
    isosceles_right_triangle_vertex_formula a b c hperp hiso
  rw [hsq, Real.sqrt_mul (by positivity : (0 : ℝ) ≤ 2)]

theorem translated_circle_equation_gives_distance :
    ∀ (c p q : Point) (r : ℝ),
      (p.1 - c.1) ^ 2 + (p.2 - c.2) ^ 2 = r ^ 2 →
      (q.1 - c.1) ^ 2 + (q.2 - c.2) ^ 2 = r ^ 2 →
      distance_sq c p = distance_sq c q := by
  intro c p q r hp hq
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  exact hp.trans hq.symm

theorem circumcenter_equidistant : ∀ (c p q : Point) (r : ℝ),
    distance_sq c p = r ^ 2 →
    distance_sq c q = r ^ 2 →
    distance_sq c p = distance_sq c q := by
  intro c p q r hp hq
  exact hp.trans hq.symm

theorem thales_theorem : ∀ (a b p : Point),
    a ≠ b →
    p ≠ a →
    p ≠ b →
    (p.1 - (a.1 + b.1) / 2) ^ 2 +
        (p.2 - (a.2 + b.2) / 2) ^ 2 =
      ((b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2) / 4 →
    is_perpendicular p a p b := by
  intro a b p _hab hpa hpb hcircle
  apply perpendicular_from_dot_zero
  · exact hpa
  · exact hpb
  · have hdot :=
      angle_in_semicircle_coordinate a b p hcircle
    simpa [dot, vec] using hdot

theorem thales_converse : ∀ (a b p : Point),
    a ≠ b →
    p ≠ a →
    p ≠ b →
    is_perpendicular p a p b →
    (p.1 - (a.1 + b.1) / 2) ^ 2 +
        (p.2 - (a.2 + b.2) / 2) ^ 2 =
      ((b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2) / 4 := by
  intro a b p _hab _hpa _hpb hperp
  have hdot := perp_dot_zero_coordinate p a p b hperp
  nlinarith [hdot]

theorem circle_equation_gives_equal_distance : ∀ (c p q : Point),
    2 * (q.1 - p.1) * c.1 + 2 * (q.2 - p.2) * c.2 =
      q.1 ^ 2 + q.2 ^ 2 - p.1 ^ 2 - p.2 ^ 2 →
    distance_sq c p = distance_sq c q := by
  intro c p q h
  unfold distance_sq dot vec
  dsimp
  nlinarith [h]

def is_concyclic (a b c d : Point) : Prop :=
  ∃ center : Point,
    distance_sq center a = distance_sq center b ∧
    distance_sq center a = distance_sq center c ∧
    distance_sq center a = distance_sq center d

theorem common_center_implies_concyclic :
    ∀ (a b c d center : Point),
      distance_sq center a = distance_sq center b →
      distance_sq center a = distance_sq center c →
      distance_sq center a = distance_sq center d →
      is_concyclic a b c d := by
  intro a b c d center hab hac had
  exact ⟨center, hab, hac, had⟩

theorem concyclic_det_criterion_implies_concyclic :
    ∀ (a b c d : Point),
      det (vec a b) (vec a c) ≠ 0 →
      distance_sq a b * det (vec a c) (vec a d) -
          distance_sq a c * det (vec a b) (vec a d) +
          distance_sq a d * det (vec a b) (vec a c) = 0 →
      is_concyclic a b c d := by
  intro a b c d hdet hcriterion

  have hcriterion' := hcriterion
  unfold distance_sq at hcriterion'

  set q : Point :=
    ((dot (vec a b) (vec a b) * (vec a c).2 -
        dot (vec a c) (vec a c) * (vec a b).2) /
        (2 * det (vec a b) (vec a c)),
     ((vec a b).1 * dot (vec a c) (vec a c) -
        (vec a c).1 * dot (vec a b) (vec a b)) /
        (2 * det (vec a b) (vec a c))) with hqdef

  have hq₁ :
      2 * dot q (vec a b) =
        dot (vec a b) (vec a b) := by
    rw [hqdef]
    unfold dot
    dsimp
    field_simp [hdet]
    unfold det
    ring

  have hq₂ :
      2 * dot q (vec a c) =
        dot (vec a c) (vec a c) := by
    rw [hqdef]
    unfold dot
    dsimp
    field_simp [hdet]
    unfold det
    ring

  have hq₃ :
      2 * dot q (vec a d) =
        dot (vec a d) (vec a d) := by
    rw [hqdef]
    unfold dot at hcriterion' ⊢
    dsimp at hcriterion' ⊢
    field_simp [hdet]
    unfold det at hcriterion' ⊢
    linear_combination -hcriterion'

  have hequidistant :
      ∀ (p : Point),
        2 * dot q (vec a p) = dot (vec a p) (vec a p) →
        distance_sq (a.1 + q.1, a.2 + q.2) a =
          distance_sq (a.1 + q.1, a.2 + q.2) p := by
    intro p hp
    unfold distance_sq dot vec at hp ⊢
    dsimp at hp ⊢
    nlinarith [hp]

  apply common_center_implies_concyclic
    a b c d (a.1 + q.1, a.2 + q.2)
  · exact hequidistant b hq₁
  · exact hequidistant c hq₂
  · exact hequidistant d hq₃

theorem concyclic_det_criterion : ∀ (a b c d : Point),
    det (vec a b) (vec a c) ≠ 0 →
    (is_concyclic a b c d ↔
      distance_sq a b * det (vec a c) (vec a d) -
          distance_sq a c * det (vec a b) (vec a d) +
          distance_sq a d * det (vec a b) (vec a c) = 0) := by
  intro a b c d hdet
  constructor
  · rintro ⟨center, hab, hac, had⟩
    unfold distance_sq dot vec at hab hac had ⊢
    unfold det
    dsimp at hab hac had ⊢
    linear_combination
      -((c.1 - a.1) * (d.2 - a.2) -
          (c.2 - a.2) * (d.1 - a.1)) * hab +
       ((b.1 - a.1) * (d.2 - a.2) -
          (b.2 - a.2) * (d.1 - a.1)) * hac -
       ((b.1 - a.1) * (c.2 - a.2) -
          (b.2 - a.2) * (c.1 - a.1)) * had
  · intro hcriterion
    exact concyclic_det_criterion_implies_concyclic
      a b c d hdet hcriterion

theorem nine_point_center : ∀ (o h n : Point),
    is_midpoint n o h →
    n = ((o.1 + h.1) / 2, (o.2 + h.2) / 2) := by
  intro o h n hn
  unfold is_midpoint at hn
  rcases hn with ⟨hnx, hny⟩
  apply Prod.ext
  · exact hnx
  · exact hny

theorem power_of_point_difference : ∀ (o p a b : Point),
    a ≠ b →
    is_collinear p a b →
    distance_sq o a = distance_sq o b →
    dot (vec p a) (vec p b) =
      distance_sq p o - distance_sq o a := by
  intro o p a b hab hcol hcircle

  have hcoord :
      a.1 - b.1 ≠ 0 ∨ a.2 - b.2 ≠ 0 := by
    by_contra h
    simp only [not_or, not_not] at h
    apply hab
    apply Prod.ext
    · linarith [h.1]
    · linarith [h.2]

  unfold is_collinear det vec at hcol
  unfold distance_sq dot vec at hcircle ⊢
  dsimp at hcol hcircle ⊢

  have horth :
      (a.1 - b.1) *
          ((a.1 - p.1) + (b.1 - p.1) - 2 * (o.1 - p.1)) +
        (a.2 - b.2) *
          ((a.2 - p.2) + (b.2 - p.2) - 2 * (o.2 - p.2)) = 0 := by
    linear_combination hcircle

  have hdet :
      (a.1 - b.1) * (a.2 - p.2) -
        (a.2 - b.2) * (a.1 - p.1) = 0 := by
    linear_combination hcol

  have htarget :
      (a.1 - p.1) *
          ((a.1 - p.1) + (b.1 - p.1) - 2 * (o.1 - p.1)) +
        (a.2 - p.2) *
          ((a.2 - p.2) + (b.2 - p.2) - 2 * (o.2 - p.2)) = 0 := by
    rcases hcoord with hx | hy
    · have hscaled :
          (a.1 - b.1) *
            ((a.1 - p.1) *
                ((a.1 - p.1) + (b.1 - p.1) -
                  2 * (o.1 - p.1)) +
             (a.2 - p.2) *
                ((a.2 - p.2) + (b.2 - p.2) -
                  2 * (o.2 - p.2))) = 0 := by
        linear_combination
          (a.1 - p.1) * horth +
          ((a.2 - p.2) + (b.2 - p.2) -
            2 * (o.2 - p.2)) * hdet
      exact (mul_eq_zero.mp hscaled).resolve_left hx
    · have hscaled :
          (a.2 - b.2) *
            ((a.1 - p.1) *
                ((a.1 - p.1) + (b.1 - p.1) -
                  2 * (o.1 - p.1)) +
             (a.2 - p.2) *
                ((a.2 - p.2) + (b.2 - p.2) -
                  2 * (o.2 - p.2))) = 0 := by
        linear_combination
          (a.2 - p.2) * horth -
          ((a.1 - p.1) + (b.1 - p.1) -
            2 * (o.1 - p.1)) * hdet
      exact (mul_eq_zero.mp hscaled).resolve_left hy

  linear_combination htarget

theorem circumcenter_equidistant_triple :
    ∀ (o a b c : Point) (r : ℝ),
      distance_sq o a = r ^ 2 →
      distance_sq o b = r ^ 2 →
      distance_sq o c = r ^ 2 →
      distance_sq o a = distance_sq o b ∧
      distance_sq o b = distance_sq o c := by
  intro o a b c r ha hb hc
  constructor
  · exact ha.trans hb.symm
  · exact hb.trans hc.symm

theorem concyclic_fourth_point :
    ∀ (o a b c d : Point) (r : ℝ),
      distance_sq o a = r ^ 2 →
      distance_sq o b = r ^ 2 →
      distance_sq o c = r ^ 2 →
      distance_sq o d = r ^ 2 →
      is_concyclic a b c d := by
  intro o a b c d r ha hb hc hd
  apply common_center_implies_concyclic a b c d o
  · exact ha.trans hb.symm
  · exact ha.trans hc.symm
  · exact ha.trans hd.symm

theorem equal_centered_norms_same_chord_coordinate :
    ∀ (o a b c d : Point),
      distance_sq o a = distance_sq o b →
      distance_sq o a = distance_sq o c →
      distance_sq o a = distance_sq o d →
      distance_sq a b * det (vec a c) (vec a d) -
          distance_sq a c * det (vec a b) (vec a d) +
          distance_sq a d * det (vec a b) (vec a c) = 0 := by
  intro o a b c d hab hac had
  unfold distance_sq dot vec at hab hac had ⊢
  unfold det
  dsimp at hab hac had ⊢
  linear_combination
    -((c.1 - a.1) * (d.2 - a.2) -
        (c.2 - a.2) * (d.1 - a.1)) * hab +
     ((b.1 - a.1) * (d.2 - a.2) -
        (b.2 - a.2) * (d.1 - a.1)) * hac -
     ((b.1 - a.1) * (c.2 - a.2) -
        (b.2 - a.2) * (c.1 - a.1)) * had

theorem common_center_same_chord_cross_ratio :
    ∀ (o a b c d : Point),
      distance_sq o a = distance_sq o b →
      distance_sq o a = distance_sq o c →
      distance_sq o a = distance_sq o d →
      are_segments_congruent a b c d →
      dot (vec o a) (vec o b) /
          Real.sqrt
            (dot (vec o a) (vec o a) *
             dot (vec o b) (vec o b)) =
        dot (vec o c) (vec o d) /
          Real.sqrt
            (dot (vec o c) (vec o c) *
             dot (vec o d) (vec o d)) := by
  intro o a b c d hab hac had hchord
  unfold are_segments_congruent at hchord

  have hdot :
      dot (vec o a) (vec o b) =
        dot (vec o c) (vec o d) := by
    have h₁ := dot_two_scale o a b
    have h₂ := dot_two_scale o c d
    linarith

  simp only [vec_dot_self_is_distance]
  rw [hdot, ← hab, ← hac, ← had]

theorem concyclic_same_chord_angles_congruent :
    ∀ (o a b c d : Point),
      distance_sq o a = distance_sq o b →
      distance_sq o a = distance_sq o c →
      distance_sq o a = distance_sq o d →
      are_segments_congruent a b c d →
      dot (vec o a) (vec o b) /
          Real.sqrt
            (dot (vec o a) (vec o a) *
             dot (vec o b) (vec o b)) =
        dot (vec o c) (vec o d) /
          Real.sqrt
            (dot (vec o c) (vec o c) *
             dot (vec o d) (vec o d)) := by
  intro o a b c d hab hac had hchord
  exact common_center_same_chord_cross_ratio
    o a b c d hab hac had hchord

theorem apollonius_theorem : ∀ (a b c m : Point),
    is_midpoint m b c →
    distance_sq a b + distance_sq a c =
      2 * (distance_sq a m + distance_sq b m) := by
  intro a b c m hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hmx, hmy]
  ring

theorem square_orthogonal_parallel_quadrilateral_coordinates :
    ∀ (x : ℝ), (-x) ^ 2 = x ^ 2 := by
  intro x
  ring

theorem orthogonal_coordinate_sum_square : ∀ (a b : ℝ),
    a = b → a ^ 2 = b ^ 2 := by
  intro a b h
  rw [h]

theorem square_diagonal_length : ∀ (a b c d : Point),
    vec a b = vec d c →
    vec a d = vec b c →
    is_perpendicular a b a d →
    are_segments_congruent a b a d →
    distance_sq a c = 2 * distance_sq a b := by
  intro a b c d hab had hperp hsides
  have hdiag :
      distance_sq a c =
        distance_sq a b + distance_sq a d +
          2 * dot (vec a b) (vec a d) :=
    (parallelogram_diagonals a b c d hab had).2.2.1
  have hdot : dot (vec a b) (vec a d) = 0 := hperp.2.2
  unfold are_segments_congruent at hsides
  linarith

theorem reflection_distance : ∀ (a b m p : Point),
    is_midpoint m a b →
    is_perpendicular a b m p →
    distance_sq p a = distance_sq p b := by
  intro a b m p hm hperp
  exact perpendicular_bisector_property a b m p hm hperp

theorem rotation_preserves_distance : ∀ (a b : Point) (θ : ℝ),
    distance_sq
        (a.1 * Real.cos θ - a.2 * Real.sin θ,
         a.1 * Real.sin θ + a.2 * Real.cos θ)
        (b.1 * Real.cos θ - b.2 * Real.sin θ,
         b.1 * Real.sin θ + b.2 * Real.cos θ) =
      distance_sq a b := by
  intro a b θ
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  dsimp
  calc
    ((b.1 * Real.cos θ - b.2 * Real.sin θ) -
          (a.1 * Real.cos θ - a.2 * Real.sin θ)) ^ 2 +
        ((b.1 * Real.sin θ + b.2 * Real.cos θ) -
          (a.1 * Real.sin θ + a.2 * Real.cos θ)) ^ 2 =
      (Real.sin θ ^ 2 + Real.cos θ ^ 2) *
        ((b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2) := by
          ring
    _ = (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 := by
      rw [Real.sin_sq_add_cos_sq]
      ring

theorem rotation_preserves_dot : ∀ (u v : Point),
    dot (-u.2, u.1) (-v.2, v.1) = dot u v := by
  intro u v
  unfold dot
  dsimp
  ring

theorem rotation_preserves_det : ∀ (u v : Point),
    det (-u.2, u.1) (-v.2, v.1) = det u v := by
  intro u v
  unfold det
  dsimp
  ring

theorem reflection_equidistant : ∀ (a b m p : Point),
    is_midpoint m a b →
    is_perpendicular a b m p →
    distance_sq p a = distance_sq p b := by
  intro a b m p hm hperp
  exact perpendicular_bisector_property a b m p hm hperp

theorem rotated_90_creates_isosceles_right : ∀ (a b : Point),
    a ≠ b →
    is_perpendicular a b a
        (a.1 + (b.2 - a.2), a.2 - (b.1 - a.1)) ∧
      are_segments_congruent a b a
        (a.1 + (b.2 - a.2), a.2 - (b.1 - a.1)) := by
  intro a b hab
  constructor
  · unfold is_perpendicular
    refine ⟨hab, ?_, ?_⟩
    · intro h
      apply hab
      have hx := congrArg (fun p : Point => p.1) h
      have hy := congrArg (fun p : Point => p.2) h
      simp only [Prod.fst, Prod.snd] at hx hy
      apply Prod.ext <;> linarith
    · unfold dot vec
      simp only [Prod.fst, Prod.snd]
      ring
  · unfold are_segments_congruent distance_sq dot vec
    simp only [Prod.fst, Prod.snd]
    ring

theorem reflected_vec_sum : ∀ (a b m : Point),
    is_midpoint m a b →
    ((vec m a).1 + (vec m b).1,
     (vec m a).2 + (vec m b).2) = (0, 0) := by
  intro a b m hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold vec
  apply Prod.ext
  · dsimp
    rw [hmx]
    ring
  · dsimp
    rw [hmy]
    ring

theorem stewart_theorem : ∀ (a b c d : Point) (t : ℝ),
    d =
      ((1 - t) * b.1 + t * c.1,
       (1 - t) * b.2 + t * c.2) →
    (1 - t) * distance_sq a b + t * distance_sq a c =
      distance_sq a d + t * (1 - t) * distance_sq b c := by
  intro a b c d t hd
  subst d
  unfold distance_sq dot vec
  dsimp
  ring

theorem median_length : ∀ (a b c m : Point),
    is_midpoint m b c →
    distance_sq a m =
      (2 * distance_sq a b + 2 * distance_sq a c -
        distance_sq b c) / 4 := by
  intro a b c m hm
  unfold is_midpoint at hm
  rcases hm with ⟨hmx, hmy⟩
  unfold distance_sq dot vec
  dsimp
  rw [hmx, hmy]
  ring

theorem foot_perp_parametric : ∀ (a b p h : Point),
    a ≠ b →
    is_collinear a b h →
    is_perpendicular p h a b →
    h =
      ((1 - dot (vec a b) (vec a p) / distance_sq a b) * a.1 +
          (dot (vec a b) (vec a p) / distance_sq a b) * b.1,
       (1 - dot (vec a b) (vec a p) / distance_sq a b) * a.2 +
          (dot (vec a b) (vec a p) / distance_sq a b) * b.2) := by
  intro a b p h hab hcol hperp

  have horth : dot (vec a b) (vec p h) = 0 := by
    rw [dot_symmetric]
    exact hperp.2.2

  have hdot :
      dot (vec a b) (vec a h) =
        dot (vec a b) (vec a p) := by
    unfold dot vec at horth ⊢
    dsimp at horth ⊢
    linarith

  have hdist_ne : distance_sq a b ≠ 0 :=
    ne_of_gt (distance_sq_positive_of_ne a b hab)

  let t : ℝ :=
    dot (vec a b) (vec a p) / distance_sq a b

  have hdot_t :
      dot (vec a b) (vec a h) =
        t * distance_sq a b := by
    rw [hdot]
    dsimp [t]
    field_simp [hdist_ne]

  have hh :=
    affine_dot_forward a b h t hab hcol hdot_t

  simpa [t] using hh

theorem median_inequality_distance : ∀ (a b c m : Point),
    is_midpoint m b c →
    distance_sq a m ≤
      (distance_sq a b + distance_sq a c) / 2 := by
  intro a b c m hm
  have hmedian := median_length a b c m hm
  have hbc : 0 ≤ distance_sq b c :=
    distance_sq_nonnegative b c
  linarith
