-- LeanGeo base library

import Mathlib.Data.Real.Basic

-- The point type is defined as a pair of real coordinates
def Point := ℝ × ℝ

-- Vector: from A to B
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- Dot product
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- Determinant
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1


-- ========== Defined concepts ==========

-- vec is already defined in the seed library agent_library_seed.txt; no need to redefine it

-- dot is already defined in the seed library agent_library_seed.txt; no need to redefine it

-- det is already defined in the seed library agent_library_seed.txt; no need to redefine it

def distance_sq (A B : Point) : ℝ := dot (vec A B) (vec A B)

def line (A B : Point) (t : ℝ) : Point :=
  (A.1 + t * (B.1 - A.1), A.2 + t * (B.2 - A.2))

def line_of (A B : Point) : Point → Prop :=
  fun P => ∃ t : ℝ, P = line A B t

def angle_cos_num (A B C : Point) : ℝ :=
  dot (vec B A) (vec B C)

def angle_cos_den (A B C : Point) : ℝ :=
  distance_sq B A * distance_sq B C

def circle (O : Point) (r : ℝ) : Point → Prop :=
  fun P => distance_sq O P = r ^ 2

def is_on_segment (P A B : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ t ≤ 1 ∧ P = line A B t

def is_on_ray (P A B : Point) : Prop :=
  ∃ t : ℝ, 0 ≤ t ∧ P = line A B t

def is_collinear (p q r : Point) : Prop :=
  det (vec p q) (vec p r) = 0

def are_segments_congruent (A B C D : Point) : Prop :=
  distance_sq A B = distance_sq C D

def are_angles_congruent (A B C D E F : Point) : Prop :=
  angle_cos_num A B C * angle_cos_num D E F ≥ 0 ∧
    angle_cos_num A B C ^ 2 * angle_cos_den D E F =
      angle_cos_num D E F ^ 2 * angle_cos_den A B C

def is_right_angle (A B C : Point) : Prop :=
  dot (vec B A) (vec B C) = 0

def is_parallel (A B C D : Point) : Prop :=
  A ≠ B ∧ C ≠ D ∧ det (vec A B) (vec C D) = 0

def is_perpendicular (A B C D : Point) : Prop :=
  dot (vec A B) (vec C D) = 0

def is_line (L : Point → Prop) : Prop :=
  ∃ A B : Point, A ≠ B ∧ L = line_of A B

def is_midpoint (P A B : Point) : Prop :=
  P.1 = (A.1 + B.1) / 2 ∧ P.2 = (A.2 + B.2) / 2

def is_affine_combination (P A B : Point) (t : ℝ) : Prop :=
  P = line A B t

def is_centroid (P A B C : Point) : Prop :=
  P.1 = (A.1 + B.1 + C.1) / 3 ∧
  P.2 = (A.2 + B.2 + C.2) / 3

def is_on_line (P A B : Point) : Prop :=
  ∃ t : ℝ, P = line A B t

def is_on_extension (P A B : Point) : Prop :=
  ∃ t : ℝ, 1 ≤ t ∧ P = line A B t

def is_foot (H P A B : Point) : Prop :=
  is_on_line H A B ∧ is_perpendicular P H A B

def is_angle_bisector (P A B C : Point) : Prop :=
  P ≠ B ∧ are_angles_congruent A B P P B C

def is_triangle (A B C : Point) : Prop :=
  ¬ is_collinear A B C

def is_isosceles (A B C : Point) : Prop :=
  distance_sq A B = distance_sq A C ∨
    distance_sq A B = distance_sq B C ∨
    distance_sq A C = distance_sq B C

def is_equilateral (A B C : Point) : Prop :=
  distance_sq A B = distance_sq B C ∧
  distance_sq B C = distance_sq C A

def are_triangles_congruent (A B C D E F : Point) : Prop :=
  are_segments_congruent A B D E ∧
  are_segments_congruent B C E F ∧
  are_segments_congruent C A F D

def are_triangles_similar (A B C D E F : Point) : Prop :=
  are_angles_congruent A B C D E F ∧
  are_angles_congruent B C A E F D ∧
  are_angles_congruent C A B F D E

def is_parallelogram (A B C D : Point) : Prop :=
  is_parallel A B C D ∧ is_parallel B C D A

def is_rectangle (A B C D : Point) : Prop :=
  is_parallelogram A B C D ∧ is_right_angle A B C

def is_rhombus (A B C D : Point) : Prop :=
  is_parallelogram A B C D ∧ are_segments_congruent A B B C

def is_square (A B C D : Point) : Prop :=
  is_rectangle A B C D ∧ is_rhombus A B C D

def is_on_circle (P O : Point) (r : ℝ) : Prop :=
  circle O r P

def are_concyclic (A B C D : Point) : Prop :=
  ∃ O : Point, ∃ r : ℝ,
    circle O r A ∧ circle O r B ∧ circle O r C ∧ circle O r D

def is_diameter_endpoints (A B O : Point) (r : ℝ) : Prop :=
  circle O r A ∧ circle O r B ∧ is_midpoint O A B

def rotated_90_cw (u v : Point) : Prop :=
  v.1 = u.2 ∧ v.2 = -u.1

def rotated_90_ccw (u v : Point) : Prop :=
  v.1 = -u.2 ∧ v.2 = u.1

-- ========== Proven theorems ==========

theorem addition_cancel : ∀ (a b c : ℝ), a + b = a + c → b = c := by
  intro a b c h
  exact add_left_cancel h

theorem addition_cancel_left : ∀ (a b c : ℝ), a + b = a + c → b = c := by
  intro a b c h
  exact addition_cancel a b c h

theorem subtraction_cancel : ∀ (a b c : ℝ), a - b = a - c → b = c := by
  intro a b c h
  have hneg : -b = -c := by
    apply addition_cancel a (-b) (-c)
    simpa [sub_eq_add_neg] using h
  have hbc := congrArg (fun x : ℝ => -x) hneg
  simpa using hbc

theorem cancel_subtraction_in_sum : ∀ (a b : ℝ), a + b - b = a := by
  intro a b
  exact add_sub_cancel_right a b

theorem multiply_both_sides : ∀ (a b c : ℝ), a = b → a * c = b * c := by
  intro a b c h
  rw [h]

theorem half_cancel : ∀ (a b : ℝ), a / 2 = b / 2 → a = b := by
  intro a b h
  have h' := congrArg (fun x : ℝ => x * 2) h
  norm_num at h'
  exact h'

theorem expand_difference_product : ∀ (a b c d : ℝ),
    (a - b) * (c - d) = a * c - a * d - b * c + b * d := by
  intro a b c d
  simp [sub_eq_add_neg, add_mul, mul_add, add_assoc, add_comm, add_left_comm]

theorem cancel_half_product : ∀ (a b c : ℝ), (a / 2) * c = (b / 2) * c → c ≠ 0 → a = b := by
  intro a b c h hc
  have h' : a / 2 = b / 2 := by
    apply (mul_right_cancel₀ hc)
    exact h
  exact half_cancel a b h'

theorem divide_both_sides : ∀ (a b c : ℝ), a = b → a / c = b / c := by
  intro a b c h
  rw [h]

theorem add_equalities : ∀ (a b c d : ℝ), a = b → c = d → a + c = b + d := by
  intro a b c d h₁ h₂
  rw [h₁, h₂]

theorem subtract_equalities : ∀ (a b c d : ℝ), a = b → c = d → a - c = b - d := by
  intro a b c d h₁ h₂
  rw [h₁, h₂]

theorem distance_sq_coordinate_formula : ∀ (A B : Point),
    distance_sq A B =
      (B.1 - A.1) ^ 2 + (B.2 - A.2) ^ 2 := by
  intro A B
  simp [distance_sq, dot, vec, pow_two]

theorem distance_sq_nonnegative : ∀ (A B : Point), 0 ≤ distance_sq A B := by
  intro A B
  rw [distance_sq_coordinate_formula]
  exact add_nonneg (sq_nonneg _) (sq_nonneg _)

theorem vec_coordinate_formula : ∀ (A B : Point),
    vec A B = (B.1 - A.1, B.2 - A.2) := by
  intro A B
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
  rw [mul_comm u.1 v.1, mul_comm u.2 v.2]

theorem dot_commutative : ∀ (u v : Point), dot u v = dot v u := by
  intro u v
  exact dot_symmetric u v

theorem dot_add_left : ∀ (u v w : Point),
    dot (u.1 + v.1, u.2 + v.2) w = dot u w + dot v w := by
  intro u v w
  unfold dot
  simp only [Prod.fst, Prod.snd, add_mul]
  exact add_add_add_comm _ _ _ _

theorem dot_add_right : ∀ (u v w : Point),
    dot u (v.1 + w.1, v.2 + w.2) = dot u v + dot u w := by
  intro u v w
  unfold dot
  simp only [Prod.fst, Prod.snd, mul_add]
  exact add_add_add_comm _ _ _ _

theorem dot_square_sum : ∀ (u : Point),
    dot u u = u.1 ^ 2 + u.2 ^ 2 := by
  intro u
  simp [dot, pow_two]

theorem det_antisymmetric : ∀ (u v : Point), det u v = -det v u := by
  intro u v
  unfold det
  calc
    u.1 * v.2 - u.2 * v.1 =
        -(u.2 * v.1 - u.1 * v.2) :=
      (neg_sub (u.2 * v.1) (u.1 * v.2)).symm
    _ = -(v.1 * u.2 - v.2 * u.1) := by
      rw [mul_comm u.2 v.1, mul_comm u.1 v.2]

theorem segments_congruent_reflexive : ∀ (A B : Point),
    are_segments_congruent A B A B := by
  intro A B
  rfl

theorem collinear_det_expand : ∀ (p q r : Point),
    is_collinear p q r →
      (q.1 - p.1) * (r.2 - p.2) - (q.2 - p.2) * (r.1 - p.1) = 0 := by
  intro p q r h
  unfold is_collinear det vec at h
  exact h

theorem perpendicular_dot_expand : ∀ (A B C D : Point),
    is_perpendicular A B C D →
      (B.1 - A.1) * (D.1 - C.1) + (B.2 - A.2) * (D.2 - C.2) = 0 := by
  intro A B C D h
  unfold is_perpendicular dot vec at h
  exact h

theorem segments_congruent_symmetric : ∀ (A B C D : Point),
    are_segments_congruent A B C D →
      are_segments_congruent C D A B := by
  intro A B C D h
  unfold are_segments_congruent at *
  exact h.symm

theorem segments_congruent_transitive : ∀ (A B C D E F : Point),
    are_segments_congruent A B C D →
    are_segments_congruent C D E F →
    are_segments_congruent A B E F := by
  intro A B C D E F h₁ h₂
  unfold are_segments_congruent at *
  calc
    distance_sq A B = distance_sq C D := h₁
    _ = distance_sq E F := h₂

theorem collinear_symmetric : ∀ (p q r : Point),
    is_collinear p q r → is_collinear p r q := by
  intro p q r h
  unfold is_collinear at h ⊢
  rw [det_antisymmetric (vec p r) (vec p q), h]
  simp

theorem vec_dot_self_is_distance : ∀ (A B : Point),
    dot (vec A B) (vec A B) = distance_sq A B := by
  intro A B
  rfl

theorem solve_cosine_for_dot : ∀ (dot_value cosine denominator : ℝ),
    denominator ≠ 0 →
    dot_value / denominator = cosine →
    dot_value = cosine * denominator := by
  intro dot_value cosine denominator hdenominator hcosine
  exact (div_eq_iff hdenominator).mp hcosine

theorem vec_neg : ∀ (A B : Point),
    vec A B = (-(vec B A).1, -(vec B A).2) := by
  intro A B
  apply Prod.ext
  · simp [vec]
  · simp [vec]

theorem dot_bilinear_expand : ∀ (u v w z : Point),
    dot (u.1 + v.1, u.2 + v.2) (w.1 + z.1, w.2 + z.2) =
      dot u w + dot u z + dot v w + dot v z := by
  intro u v w z
  rw [dot_add_left]
  rw [dot_add_right]
  rw [dot_add_right]
  simp only [add_assoc]

theorem distance_equality_to_dot : ∀ (A B C D : Point),
    distance_sq A B = distance_sq C D →
    dot (vec A B) (vec A B) = dot (vec C D) (vec C D) := by
  intro A B C D h
  simpa [distance_sq] using h

theorem point_difference_norm_pos :
    ∀ (a b : Point), a ≠ b →
      (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 > 0 := by
  intro a b hab
  by_contra hnot
  have hle :
      (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 ≤ 0 :=
    le_of_not_gt hnot
  have hx_le :
      (b.1 - a.1) ^ 2 ≤
        (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 :=
    le_add_of_nonneg_right (sq_nonneg (b.2 - a.2))
  have hy_le :
      (b.2 - a.2) ^ 2 ≤
        (b.1 - a.1) ^ 2 + (b.2 - a.2) ^ 2 :=
    le_add_of_nonneg_left (sq_nonneg (b.1 - a.1))
  have hx_sq : (b.1 - a.1) ^ 2 = 0 := by
    apply le_antisymm
    · exact le_trans hx_le hle
    · exact sq_nonneg (b.1 - a.1)
  have hy_sq : (b.2 - a.2) ^ 2 = 0 := by
    apply le_antisymm
    · exact le_trans hy_le hle
    · exact sq_nonneg (b.2 - a.2)
  have hx_mul : (b.1 - a.1) * (b.1 - a.1) = 0 := by
    simpa [pow_two] using hx_sq
  have hy_mul : (b.2 - a.2) * (b.2 - a.2) = 0 := by
    simpa [pow_two] using hy_sq
  have hx_zero : b.1 - a.1 = 0 := by
    rcases mul_eq_zero.mp hx_mul with h | h
    · exact h
    · exact h
  have hy_zero : b.2 - a.2 = 0 := by
    rcases mul_eq_zero.mp hy_mul with h | h
    · exact h
    · exact h
  have hx_eq : b.1 = a.1 := sub_eq_zero.mp hx_zero
  have hy_eq : b.2 = a.2 := sub_eq_zero.mp hy_zero
  apply hab
  apply Prod.ext
  · exact hx_eq.symm
  · exact hy_eq.symm

theorem collinear_to_standard_det : ∀ (p q r : Point),
    is_collinear p q r →
      (q.1 - p.1) * (r.2 - p.2) =
        (q.2 - p.2) * (r.1 - p.1) := by
  intro p q r h
  exact sub_eq_zero.mp (collinear_det_expand p q r h)

theorem zero_factor_law : ∀ (a b : ℝ), a * b = 0 → a = 0 ∨ b = 0 := by
  intro a b h
  exact mul_eq_zero.mp h

theorem difference_of_squares : ∀ (a b : ℝ),
    a ^ 2 - b ^ 2 = (a - b) * (a + b) := by
  intro a b
  simp [pow_two, sub_mul, mul_add, sub_eq_add_neg,
    mul_comm, add_assoc, add_comm, add_left_comm]

theorem one_dimensional_midpoint : ∀ (a b : ℝ),
    is_midpoint ((a + b) / 2, 0) (a, 0) (b, 0) := by
  intro a b
  unfold is_midpoint
  constructor <;> simp

theorem distance_sq_translate : ∀ (A B T : Point),
    distance_sq (A.1 + T.1, A.2 + T.2)
      (B.1 + T.1, B.2 + T.2) =
    distance_sq A B := by
  intro A B T
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  simp

theorem parallelogram_sides : ∀ (A B C D : Point),
    is_parallelogram A B C D →
      is_parallel A B C D ∧ is_parallel B C D A := by
  intro A B C D h
  exact h

theorem circumcenter_equidistant : ∀ (O A B C : Point) (r : ℝ),
    circle O r A →
    circle O r B →
    circle O r C →
    distance_sq O A = distance_sq O B ∧
      distance_sq O B = distance_sq O C := by
  intro O A B C r hA hB hC
  unfold circle at hA hB hC
  constructor
  · calc
      distance_sq O A = r ^ 2 := hA
      _ = distance_sq O B := hB.symm
  · calc
      distance_sq O B = r ^ 2 := hB
      _ = distance_sq O C := hC.symm

theorem sss_congruence : ∀ (A B C D E F : Point),
    are_segments_congruent A B D E →
    are_segments_congruent B C E F →
    are_segments_congruent C A F D →
    are_triangles_congruent A B C D E F := by
  intro A B C D E F hAB hBC hCA
  unfold are_triangles_congruent
  exact ⟨hAB, hBC, hCA⟩

theorem distance_sq_positive_of_ne : ∀ (A B : Point), A ≠ B → 0 < distance_sq A B := by
  intro A B hne
  rw [distance_sq_coordinate_formula]
  exact point_difference_norm_pos A B hne

theorem asa_angle_equations_bridge : ∀ (A B C D E F : Point),
    angle_cos_num A B C * angle_cos_num D E F ≥ 0 →
    angle_cos_num A B C ^ 2 * angle_cos_den D E F =
      angle_cos_num D E F ^ 2 * angle_cos_den A B C →
    are_angles_congruent A B C D E F := by
  intro A B C D E F hsign heq
  unfold are_angles_congruent
  exact ⟨hsign, heq⟩

theorem asa_congruence : ∀ (A B C D E F : Point),
    are_angles_congruent A B C D E F →
    are_segments_congruent A B D E →
    are_angles_congruent B A C E D F →
    are_segments_congruent B C E F →
    are_segments_congruent C A F D →
    are_triangles_congruent A B C D E F := by
  intro A B C D E F _ hAB _ hBC hCA
  exact sss_congruence A B C D E F hAB hBC hCA

theorem perpendicular_symmetric : ∀ (A B C D : Point),
    is_perpendicular A B C D → is_perpendicular C D A B := by
  intro A B C D h
  unfold is_perpendicular at h ⊢
  rw [dot_symmetric (vec C D) (vec A B)]
  exact h

theorem parallel_symmetric : ∀ (A B C D : Point),
    is_parallel A B C D → is_parallel C D A B := by
  intro A B C D h
  unfold is_parallel at h ⊢
  rcases h with ⟨hAB, hCD, hdet⟩
  refine ⟨hCD, hAB, ?_⟩
  rw [det_antisymmetric (vec C D) (vec A B), hdet]
  simp

theorem det_bilinear_right : ∀ (u v w : Point),
    det u (v.1 + w.1, v.2 + w.2) = det u v + det u w := by
  intro u v w
  simp [det, mul_add, sub_eq_add_neg, add_assoc, add_comm, add_left_comm]

theorem div_mul_cancel_probe : ∀ (a b : ℝ), b ≠ 0 → a / b * b = a := by
  intro a b hb
  exact div_mul_cancel₀ a hb

theorem zero_sum_rearrange : ∀ (a b : ℝ), a + b = 0 → a = -b := by
  intro a b h
  calc
    a = a + b - b := (add_sub_cancel_right a b).symm
    _ = -b := by rw [h]; simp

namespace LeanGeo

theorem sub_add_cancel : ∀ (a b : ℝ), a - b + b = a := by
  intro a b
  exact _root_.sub_add_cancel a b

end LeanGeo

theorem eq_substitution_in_sum : ∀ (a b c : ℝ),
    a = b → a + c = b + c := by
  intro a b c h
  rw [h]

theorem circle_equation_gives_equal_distance : ∀ (O A B : Point) (r : ℝ),
    circle O r A →
    circle O r B →
    distance_sq O A = distance_sq O B := by
  intro O A B r hA hB
  unfold circle at hA hB
  calc
    distance_sq O A = r ^ 2 := hA
    _ = distance_sq O B := hB.symm

theorem translated_difference_square : ∀ (A B T : Point),
    distance_sq (A.1 + T.1, A.2 + T.2)
      (B.1 + T.1, B.2 + T.2) =
    distance_sq A B := by
  intro A B T
  exact distance_sq_translate A B T

theorem common_center_implies_concyclic :
    ∀ (O A B C D : Point) (r : ℝ),
      circle O r A →
      circle O r B →
      circle O r C →
      circle O r D →
      are_concyclic A B C D := by
  intro O A B C D r hA hB hC hD
  exact ⟨O, r, hA, hB, hC, hD⟩

theorem translated_circle_equation_gives_distance : ∀ (O A T : Point) (r : ℝ),
    circle (O.1 + T.1, O.2 + T.2) r (A.1 + T.1, A.2 + T.2) →
    distance_sq O A = r ^ 2 := by
  intro O A T r h
  unfold circle at h
  rw [distance_sq_translate O A T] at h
  exact h

theorem dot_bilinear_right : ∀ (u v w : Point),
    dot u (v.1 + w.1, v.2 + w.2) = dot u v + dot u w := by
  intro u v w
  exact dot_add_right u v w

theorem dot_scale_right : ∀ (u v : Point) (c : ℝ),
    dot u (c * v.1, c * v.2) = c * dot u v := by
  intro u v c
  unfold dot
  simp only [Prod.fst, Prod.snd]
  calc
    u.1 * (c * v.1) + u.2 * (c * v.2) =
        c * (u.1 * v.1) + c * (u.2 * v.2) := by
      rw [mul_left_comm u.1 c v.1, mul_left_comm u.2 c v.2]
    _ = c * (u.1 * v.1 + u.2 * v.2) := by
      rw [mul_add]

theorem det_scale_right : ∀ (u v : Point) (c : ℝ),
    det u (c * v.1, c * v.2) = c * det u v := by
  intro u v c
  unfold det
  simp only [Prod.fst, Prod.snd]
  calc
    u.1 * (c * v.2) - u.2 * (c * v.1) =
        c * (u.1 * v.2) - c * (u.2 * v.1) := by
      rw [mul_left_comm u.1 c v.2, mul_left_comm u.2 c v.1]
    _ = c * (u.1 * v.2 - u.2 * v.1) := by
      rw [mul_sub]

theorem foot_perp_parametric : ∀ (H P A B : Point),
    is_foot H P A B →
      ∃ t : ℝ,
        H = line A B t ∧
        dot (vec P H) (vec A B) = 0 := by
  intro H P A B h
  unfold is_foot is_on_line is_perpendicular at h
  rcases h with ⟨⟨t, ht⟩, hperp⟩
  exact ⟨t, ht, hperp⟩

theorem affine_combination_distance_sq : ∀ (P A B : Point) (t : ℝ),
    is_affine_combination P A B t →
      distance_sq A P = t ^ 2 * distance_sq A B := by
  intro P A B t h
  unfold is_affine_combination at h
  rw [h]
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  simp [line, mul_pow, mul_add]

theorem similar_triangles_ratio : ∀ (A B C D E F : Point),
    are_triangles_similar A B C D E F →
    angle_cos_num A B C ^ 2 * angle_cos_den D E F =
      angle_cos_num D E F ^ 2 * angle_cos_den A B C := by
  intro A B C D E F h
  unfold are_triangles_similar at h
  rcases h with ⟨hABC, _, _⟩
  unfold are_angles_congruent at hABC
  exact hABC.2

theorem similar_triangles_dot : ∀ (A B C D E F : Point),
    are_triangles_similar A B C D E F →
    dot (vec B A) (vec B C) ^ 2 *
        (distance_sq E D * distance_sq E F) =
      dot (vec E D) (vec E F) ^ 2 *
        (distance_sq B A * distance_sq B C) := by
  intro A B C D E F h
  have hratio := similar_triangles_ratio A B C D E F h
  simpa [angle_cos_num, angle_cos_den] using hratio

theorem angle_equality_cross_ratio : ∀ (A B C D E F : Point),
    are_angles_congruent A B C D E F →
    angle_cos_num A B C ^ 2 * angle_cos_den D E F =
      angle_cos_num D E F ^ 2 * angle_cos_den A B C := by
  intro A B C D E F h
  exact h.2

/-- Approach: Rotation swaps the two coordinates of the vector and changes one sign, leaving the sum of squares unchanged. -/
theorem rotation_preserves_distance : ∀ (A B C D : Point),
    rotated_90_cw (vec A B) (vec C D) →
    distance_sq A B = distance_sq C D := by
  intro A B C D h
  rcases h with ⟨hx, hy⟩
  change D.1 - C.1 = B.2 - A.2 at hx
  change D.2 - C.2 = -(B.1 - A.1) at hy
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula,
    hx, hy]
  simp only [neg_sq]
  exact add_comm _ _

/-- Approach: Rotating both vectors clockwise by 90 degrees swaps the two terms of the dot product, leaving its value unchanged. -/
theorem rotation_preserves_dot : ∀ (u v u' v' : Point),
    rotated_90_cw u u' →
    rotated_90_cw v v' →
    dot u v = dot u' v' := by
  intro u v u' v' hu hv
  rcases hu with ⟨hux, huy⟩
  rcases hv with ⟨hvx, hvy⟩
  unfold dot
  rw [hux, huy, hvx, hvy]
  simp only [neg_mul_neg]
  exact add_comm _ _

/-- Approach: Rotating both vectors clockwise by 90 degrees swaps the two terms of the determinant and flips both signs, leaving its value unchanged. -/
theorem rotation_preserves_det : ∀ (u v u' v' : Point),
    rotated_90_cw u u' →
    rotated_90_cw v v' →
    det u v = det u' v' := by
  intro u v u' v' hu hv
  rcases hu with ⟨hux, huy⟩
  rcases hv with ⟨hvx, hvy⟩
  unfold det
  rw [hux, huy, hvx, hvy]
  simp only [mul_neg, neg_mul, sub_eq_add_neg, neg_neg]
  exact add_comm _ _

/-- Approach: Taking the circle's center as the origin, the coordinates of the two diameter endpoints are negatives of each other;
    The dot product equals the squared distance from the point to the center minus the squared radius. -/
theorem angle_in_semicircle_coordinate :
    ∀ (A B P O : Point) (r : ℝ),
      is_diameter_endpoints A B O r →
      circle O r P →
      is_right_angle A P B := by
  intro A B P O r hdiam hP
  rcases hdiam with ⟨hA, _hB, hx, hy⟩
  have hsumx : A.1 + B.1 = O.1 + O.1 := by
    calc
      A.1 + B.1 = (A.1 + B.1) / 2 + (A.1 + B.1) / 2 :=
        (add_halves _).symm
      _ = O.1 + O.1 := by rw [hx]
  have hsumy : A.2 + B.2 = O.2 + O.2 := by
    calc
      A.2 + B.2 = (A.2 + B.2) / 2 + (A.2 + B.2) / 2 :=
        (add_halves _).symm
      _ = O.2 + O.2 := by rw [hy]
  have hBx : B.1 - O.1 = -(A.1 - O.1) := by
    apply (add_left_cancel (a := A.1))
    calc
      A.1 + (B.1 - O.1) = (A.1 + B.1) - O.1 := by
        simp [sub_eq_add_neg, add_assoc]
      _ = O.1 := by rw [hsumx]; simp
      _ = A.1 + -(A.1 - O.1) := by simp
  have hBy : B.2 - O.2 = -(A.2 - O.2) := by
    apply (add_left_cancel (a := A.2))
    calc
      A.2 + (B.2 - O.2) = (A.2 + B.2) - O.2 := by
        simp [sub_eq_add_neg, add_assoc]
      _ = O.2 := by rw [hsumy]; simp
      _ = A.2 + -(A.2 - O.2) := by simp
  have hid (x y : ℝ) :
      (x - y) * (-x - y) = y ^ 2 - x ^ 2 := by
    simp [sub_eq_add_neg, add_mul, mul_add, pow_two,
      mul_comm, add_comm, add_left_comm, add_assoc]
  have hcoord (a b p o : ℝ) (hb : b - o = -(a - o)) :
      (a - p) * (b - p) = (p - o) ^ 2 - (a - o) ^ 2 := by
    calc
      (a - p) * (b - p) =
          ((a - o) - (p - o)) * ((b - o) - (p - o)) := by
        simp
      _ = (p - o) ^ 2 - (a - o) ^ 2 := by
        rw [hb]
        exact hid _ _
  change distance_sq O P = r ^ 2 at hP
  change distance_sq O A = r ^ 2 at hA
  unfold is_right_angle dot vec
  change (A.1 - P.1) * (B.1 - P.1) +
    (A.2 - P.2) * (B.2 - P.2) = 0
  calc
    (A.1 - P.1) * (B.1 - P.1) +
        (A.2 - P.2) * (B.2 - P.2) =
        distance_sq O P - distance_sq O A := by
      rw [hcoord A.1 B.1 P.1 O.1 hBx,
        hcoord A.2 B.2 P.2 O.2 hBy]
      rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
      simp [sub_eq_add_neg, add_comm, add_left_comm, add_assoc]
    _ = 0 := by rw [hP, hA]; simp

/-- Approach: The midpoint coordinates make the corresponding coordinate differences on both sides equal; substitute into the squared-distance formula. -/
theorem collinear_implies_midpoint_distance :
    ∀ (A B M : Point),
      is_collinear A M B →
      is_midpoint M A B →
      distance_sq A M = distance_sq M B := by
  intro A B M _hcol hmid
  rcases hmid with ⟨hx, hy⟩
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  rw [hx, hy]
  have hdx :
      (A.1 + B.1) / 2 - A.1 =
        B.1 - (A.1 + B.1) / 2 := by
    apply (sub_eq_sub_iff_add_eq_add).2
    calc
      (A.1 + B.1) / 2 + (A.1 + B.1) / 2 =
          A.1 + B.1 := add_halves _
      _ = B.1 + A.1 := add_comm _ _
  have hdy :
      (A.2 + B.2) / 2 - A.2 =
        B.2 - (A.2 + B.2) / 2 := by
    apply (sub_eq_sub_iff_add_eq_add).2
    calc
      (A.2 + B.2) / 2 + (A.2 + B.2) / 2 =
          A.2 + B.2 := add_halves _
      _ = B.2 + A.2 := add_comm _ _
  rw [hdx, hdy]

/-- Approach: The definition of parallelism already includes that the determinant of the corresponding vectors is zero; extract that condition directly. -/
theorem parallel_implies_det_zero : ∀ (A B C D : Point),
    is_parallel A B C D → det (vec A B) (vec C D) = 0 := by
  intro A B C D h
  exact h.2.2

theorem circumcenter_equidistant_triple :
    ∀ (O A B C : Point) (r : ℝ),
      circle O r A →
      circle O r B →
      circle O r C →
      distance_sq O A = distance_sq O B ∧
        distance_sq O B = distance_sq O C := by
  intro O A B C r hA hB hC
  exact circumcenter_equidistant O A B C r hA hB hC

/-- Approach: The coordinate differences from the midpoint to the origin and to the reflected point are negatives of each other, so the squared distances are equal. -/
theorem reflection_equidistant : ∀ (P P' M : Point),
    is_midpoint M P P' →
    distance_sq M P = distance_sq M P' := by
  intro P P' M hmid
  rcases hmid with ⟨hx, hy⟩
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  rw [hx, hy]
  have hdx :
      P.1 - (P.1 + P'.1) / 2 =
        -(P'.1 - (P.1 + P'.1) / 2) := by
    calc
      P.1 - (P.1 + P'.1) / 2 =
          (P.1 + P'.1) / 2 - P'.1 := by
        apply (sub_eq_sub_iff_add_eq_add).2
        exact (add_halves (P.1 + P'.1)).symm
      _ = -(P'.1 - (P.1 + P'.1) / 2) := by
        simp
  have hdy :
      P.2 - (P.2 + P'.2) / 2 =
        -(P'.2 - (P.2 + P'.2) / 2) := by
    calc
      P.2 - (P.2 + P'.2) / 2 =
          (P.2 + P'.2) / 2 - P'.2 := by
        apply (sub_eq_sub_iff_add_eq_add).2
        exact (add_halves (P.2 + P'.2)).symm
      _ = -(P'.2 - (P.2 + P'.2) / 2) := by
        simp
  rw [hdx, hdy]
  simp only [neg_sq]

/-- Approach: All four points satisfy the circle equation with the same center and radius; witness concyclicity directly with that center and radius. -/
theorem concyclic_fourth_point :
    ∀ (O A B C D : Point) (r : ℝ),
      circle O r A →
      circle O r B →
      circle O r C →
      circle O r D →
      are_concyclic A B C D := by
  intro O A B C D r hA hB hC hD
  exact ⟨O, r, hA, hB, hC, hD⟩

theorem perp_dot_zero_coordinate : ∀ (A B C D : Point),
    is_perpendicular A B C D →
      (B.1 - A.1) * (D.1 - C.1) +
        (B.2 - A.2) * (D.2 - C.2) = 0 := by
  intro A B C D h
  exact perpendicular_dot_expand A B C D h

/-- Approach: Decompose the coordinate difference of AC as the sum of the coordinate differences of AB and BC,
    Expand the sum of squares, then use the perpendicularity condition to cancel the two cross terms. -/
theorem perpendicular_implies_distance_sum :
    ∀ (A B C : Point),
      is_perpendicular A B B C →
      distance_sq A B + distance_sq B C = distance_sq A C := by
  intro A B C hperp
  have hdot := perpendicular_dot_expand A B B C hperp
  have hx : C.1 - A.1 = (B.1 - A.1) + (C.1 - B.1) := by
    simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
  have hy : C.2 - A.2 = (B.2 - A.2) + (C.2 - B.2) := by
    simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
  have hexpand (x y u v : ℝ) :
      (x + u) ^ 2 + (y + v) ^ 2 =
        (x ^ 2 + y ^ 2) + (u ^ 2 + v ^ 2) +
          (x * u + y * v) + (x * u + y * v) := by
    simp [pow_two, add_mul, mul_add, mul_comm,
      add_assoc, add_comm, add_left_comm]
  rw [distance_sq_coordinate_formula,
    distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  rw [hx, hy, hexpand, hdot]
  simp

theorem wu_circle_quartic : ∀ (O P : Point) (r : ℝ),
    circle O r P →
      ((P.1 - O.1) ^ 2 + (P.2 - O.2) ^ 2) ^ 2 = r ^ 4 := by
  intro O P r h
  unfold circle at h
  rw [distance_sq_coordinate_formula] at h
  calc
    ((P.1 - O.1) ^ 2 + (P.2 - O.2) ^ 2) ^ 2 =
        (r ^ 2) ^ 2 := congrArg (fun x : ℝ => x ^ 2) h
    _ = r ^ 4 := by
      simpa using (pow_mul r 2 2).symm

theorem midpoint_equidistant_prop : ∀ (A B M : Point),
    is_midpoint M A B →
    distance_sq M A = distance_sq M B := by
  intro A B M hmid
  exact reflection_equidistant A B M hmid

/-- Approach: The right-angle condition gives that the dot product of BA and BC is zero;
    Reverse BA to get AB, then apply the squared-distance-sum theorem under the perpendicularity condition. -/
theorem pythagorean_prop : ∀ (A B C : Point),
    is_right_angle A B C →
    distance_sq A B + distance_sq B C = distance_sq A C := by
  intro A B C hright
  apply perpendicular_implies_distance_sum A B C
  unfold is_right_angle dot vec at hright
  unfold is_perpendicular dot vec
  change (B.1 - A.1) * (C.1 - B.1) +
    (B.2 - A.2) * (C.2 - B.2) = 0
  have hx : B.1 - A.1 = -(A.1 - B.1) :=
    (neg_sub A.1 B.1).symm
  have hy : B.2 - A.2 = -(A.2 - B.2) :=
    (neg_sub A.2 B.2).symm
  rw [hx, hy]
  simp only [neg_mul, ← neg_add, hright, neg_zero]

theorem collinear_symmetric_prop : ∀ (A B C : Point),
    is_collinear A B C → is_collinear A C B := by
  intro A B C h
  exact collinear_symmetric A B C h

/-- Approach: Directly apply the already-proven symmetry theorem for perpendicularity. -/
theorem perpendicular_symmetric_prop : ∀ (A B C D : Point),
    is_perpendicular A B C D → is_perpendicular C D A B := by
  intro A B C D h
  exact perpendicular_symmetric A B C D h

/-- Approach: Directly apply the already-proven symmetry theorem for parallelism. -/
theorem parallel_symmetric_prop : ∀ (A B C D : Point),
    is_parallel A B C D → is_parallel C D A B := by
  intro A B C D h
  exact parallel_symmetric A B C D h

/-- Approach: Directly apply the already-proven symmetry theorem for segment congruence. -/
theorem segments_congruent_symmetric_prop : ∀ (A B C D : Point),
    are_segments_congruent A B C D →
    are_segments_congruent C D A B := by
  intro A B C D h
  exact segments_congruent_symmetric A B C D h

/-- Approach: Directly apply the already-proven transitivity theorem for segment congruence. -/
theorem segments_congruent_transitive_prop : ∀ (A B C D E F : Point),
    are_segments_congruent A B C D →
    are_segments_congruent C D E F →
    are_segments_congruent A B E F := by
  intro A B C D E F h₁ h₂
  exact segments_congruent_transitive A B C D E F h₁ h₂

/-- Approach: Directly apply the already-proven reflexivity theorem for segment congruence. -/
theorem segments_congruent_reflexive_prop : ∀ (A B : Point),
    are_segments_congruent A B A B := by
  intro A B
  exact segments_congruent_reflexive A B

theorem segments_congruent_from_distance_sq : ∀ (A B C D : Point),
    distance_sq A B = distance_sq C D →
    are_segments_congruent A B C D := by
  intro A B C D h
  unfold are_segments_congruent
  exact h

/-- Approach: Swapping the two points negates both coordinate differences, leaving the squares unchanged. -/
theorem distance_sq_symmetric_prop : ∀ (A B : Point),
    distance_sq A B = distance_sq B A := by
  intro A B
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  have hx : B.1 - A.1 = -(A.1 - B.1) :=
    (neg_sub A.1 B.1).symm
  have hy : B.2 - A.2 = -(A.2 - B.2) :=
    (neg_sub A.2 B.2).symm
  rw [hx, hy]
  simp only [neg_sq]

/-- Thales' theorem: the inscribed angle subtended by a diameter is a right angle. -/
theorem thales_theorem_prop : ∀ (A B P O : Point) (r : ℝ),
    is_diameter_endpoints A B O r →
    circle O r P →
    is_right_angle A P B := by
  intro A B P O r hdiam hP
  exact angle_in_semicircle_coordinate A B P O r hdiam hP

/-- Approach: The same point is the midpoint of both segments, so the sums of the two pairs of endpoint coordinates are equal;
    Thus the coordinate differences of the two corresponding sides are negatives of each other, and the squared distances are equal. -/
theorem double_midpoint_equal_sides :
    ∀ (A B C D M : Point),
      is_midpoint M A B →
      is_midpoint M C D →
      are_segments_congruent A C B D := by
  intro A B C D M hAB hCD
  rcases hAB with ⟨hABx, hABy⟩
  rcases hCD with ⟨hCDx, hCDy⟩
  have hsumx : A.1 + B.1 = C.1 + D.1 := by
    apply half_cancel
    exact hABx.symm.trans hCDx
  have hsumy : A.2 + B.2 = C.2 + D.2 := by
    apply half_cancel
    exact hABy.symm.trans hCDy
  have hx : C.1 - A.1 = B.1 - D.1 := by
    apply (sub_eq_sub_iff_add_eq_add).2
    calc
      C.1 + D.1 = A.1 + B.1 := hsumx.symm
      _ = B.1 + A.1 := add_comm _ _
  have hy : C.2 - A.2 = B.2 - D.2 := by
    apply (sub_eq_sub_iff_add_eq_add).2
    calc
      C.2 + D.2 = A.2 + B.2 := hsumy.symm
      _ = B.2 + A.2 := add_comm _ _
  have hxneg : C.1 - A.1 = -(D.1 - B.1) := by
    calc
      C.1 - A.1 = B.1 - D.1 := hx
      _ = -(D.1 - B.1) := (neg_sub D.1 B.1).symm
  have hyneg : C.2 - A.2 = -(D.2 - B.2) := by
    calc
      C.2 - A.2 = B.2 - D.2 := hy
      _ = -(D.2 - B.2) := (neg_sub D.2 B.2).symm
  unfold are_segments_congruent
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
  rw [hxneg, hyneg]
  simp only [neg_sq]

/-- Approach: By definition, the midpoint's two coordinates equal the averages of the corresponding endpoint coordinates. -/
theorem midpoint_coordinate_formula : ∀ (M A B : Point),
    is_midpoint M A B →
      M.1 = (A.1 + B.1) / 2 ∧ M.2 = (A.2 + B.2) / 2 := by
  intro M A B h
  exact h

/-- Approach: Unfold the definition of a point on the circle and the definition of the circle to obtain squared distance equals squared radius. -/
theorem on_circle_distance_prop : ∀ (P O : Point) (r : ℝ),
    is_on_circle P O r →
    distance_sq O P = r ^ 2 := by
  intro P O r h
  unfold is_on_circle circle at h
  exact h

/-- Rotating clockwise by 90 degrees preserves the squared distance of the segment corresponding to the vector. -/
theorem rotation_90_cw_distance_prop : ∀ (A B C D : Point),
    rotated_90_cw (vec A B) (vec C D) →
    distance_sq A B = distance_sq C D := by
  intro A B C D h
  exact rotation_preserves_distance A B C D h

/-- Approach: Substitute the clockwise-rotation coordinate relations and use the commutativity of multiplication to cancel the two terms in the dot product. -/
theorem rotation_90_cw_perpendicular_prop : ∀ (A B C D : Point),
    rotated_90_cw (vec A B) (vec C D) →
    is_perpendicular A B C D := by
  intro A B C D h
  rcases h with ⟨hx, hy⟩
  unfold is_perpendicular dot
  rw [hx, hy]
  rw [mul_neg, mul_comm (vec A B).2 (vec A B).1]
  exact add_neg_cancel _

/-- Approach: If a collinear vector is nonzero, then the other vector is a scalar multiple of it;
    Use the homogeneity of the dot product to prove the squared cross-equality, handling the zero vector separately. -/
theorem vertical_angles_square_core :
    ∀ (A B C D O : Point),
      is_collinear O A C →
      is_collinear O B D →
      angle_cos_num A O B ^ 2 * angle_cos_den C O D =
        angle_cos_num C O D ^ 2 * angle_cos_den A O B := by
  intro A B C D O hAC hBD
  let u : Point := vec O A
  let v : Point := vec O B
  let w : Point := vec O C
  let z : Point := vec O D
  have huw : det u w = 0 := hAC
  have hvz : det v z = 0 := hBD
  change dot u v ^ 2 * (dot w w * dot z z) =
    dot w z ^ 2 * (dot u u * dot v v)

  have parallel_scalar :
      ∀ (x y : Point), det x y = 0 →
        x ≠ (0, 0) →
        ∃ a : ℝ, y = (a * x.1, a * x.2) := by
    intro x y hdet hx
    have hxy : x.1 * y.2 = x.2 * y.1 :=
      sub_eq_zero.mp hdet
    by_cases hx1 : x.1 = 0
    · have hx2 : x.2 ≠ 0 := by
        intro hzero
        apply hx
        apply Prod.ext
        · exact hx1
        · exact hzero
      have hy1 : y.1 = 0 := by
        have hz : x.2 * y.1 = 0 := by
          rw [← hxy, hx1, zero_mul]
        exact (mul_eq_zero.mp hz).resolve_left hx2
      refine ⟨y.2 / x.2, ?_⟩
      apply Prod.ext
      · simp [hx1, hy1]
      · exact (div_mul_cancel₀ y.2 hx2).symm
    · refine ⟨y.1 / x.1, ?_⟩
      apply Prod.ext
      · exact (div_mul_cancel₀ y.1 hx1).symm
      · change y.2 = y.1 / x.1 * x.2
        calc
          y.2 = (x.1 * y.2) / x.1 := by
            simp [hx1]
          _ = (x.2 * y.1) / x.1 := by rw [hxy]
          _ = y.1 / x.1 * x.2 := by
            simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

  have scale_dot (x y : Point) (a b : ℝ) :
      dot (a * x.1, a * x.2) (b * y.1, b * y.2) =
        (a * b) * dot x y := by
    simp [dot, mul_add, mul_assoc, mul_comm, mul_left_comm]

  by_cases hu : u = (0, 0)
  · simp [hu, dot]
  by_cases hv : v = (0, 0)
  · simp [hv, dot]
  obtain ⟨a, ha⟩ := parallel_scalar u w huw hu
  obtain ⟨b, hb⟩ := parallel_scalar v z hvz hv
  rw [ha, hb, scale_dot u u a a, scale_dot v v b b,
    scale_dot u v a b]
  simp only [mul_pow, pow_two, mul_assoc, mul_comm, mul_left_comm]

/-- Approach: The intersection point on the segment makes the two pairs of vectors have nonnegative parameter products respectively;
    The product of the two dot products therefore equals a nonnegative coefficient times the square of the same dot product. -/
theorem vertical_angles_sign_core :
    ∀ (A B C D O : Point),
      is_on_segment O A C →
      is_on_segment O B D →
      angle_cos_num A O B * angle_cos_num C O D ≥ 0 := by
  intro A B C D O hAC hBD
  rcases hAC with ⟨t, ht0, ht1, hOAC⟩
  rcases hBD with ⟨s, hs0, hs1, hOBD⟩

  have endpoint_left (a c t : ℝ) :
      a - (a + t * (c - a)) = (-t) * (c - a) := by
    simp only [sub_add_eq_sub_sub, sub_self, zero_sub, neg_mul]

  have endpoint_right (a c t : ℝ) :
      c - (a + t * (c - a)) = (1 - t) * (c - a) := by
    rw [sub_add_eq_sub_sub, sub_mul, one_mul]

  have hOA : vec O A =
      ((-t) * (vec A C).1, (-t) * (vec A C).2) := by
    apply Prod.ext
    · change A.1 - O.1 = (-t) * (C.1 - A.1)
      rw [hOAC]
      exact endpoint_left A.1 C.1 t
    · change A.2 - O.2 = (-t) * (C.2 - A.2)
      rw [hOAC]
      exact endpoint_left A.2 C.2 t

  have hOC : vec O C =
      ((1 - t) * (vec A C).1, (1 - t) * (vec A C).2) := by
    apply Prod.ext
    · change C.1 - O.1 = (1 - t) * (C.1 - A.1)
      rw [hOAC]
      exact endpoint_right A.1 C.1 t
    · change C.2 - O.2 = (1 - t) * (C.2 - A.2)
      rw [hOAC]
      exact endpoint_right A.2 C.2 t

  have hOB : vec O B =
      ((-s) * (vec B D).1, (-s) * (vec B D).2) := by
    apply Prod.ext
    · change B.1 - O.1 = (-s) * (D.1 - B.1)
      rw [hOBD]
      exact endpoint_left B.1 D.1 s
    · change B.2 - O.2 = (-s) * (D.2 - B.2)
      rw [hOBD]
      exact endpoint_left B.2 D.2 s

  have hOD : vec O D =
      ((1 - s) * (vec B D).1, (1 - s) * (vec B D).2) := by
    apply Prod.ext
    · change D.1 - O.1 = (1 - s) * (D.1 - B.1)
      rw [hOBD]
      exact endpoint_right B.1 D.1 s
    · change D.2 - O.2 = (1 - s) * (D.2 - B.2)
      rw [hOBD]
      exact endpoint_right B.2 D.2 s

  have scale_dot (u v : Point) (a b : ℝ) :
      dot (a * u.1, a * u.2) (b * v.1, b * v.2) =
        (a * b) * dot u v := by
    simp [dot, mul_add, mul_assoc, mul_comm, mul_left_comm]

  unfold angle_cos_num
  rw [hOA, hOB, hOC, hOD, scale_dot, scale_dot]
  simp only [neg_mul_neg]
  have hfactor :
      (t * s * dot (vec A C) (vec B D)) *
          ((1 - t) * (1 - s) * dot (vec A C) (vec B D)) =
        ((t * s) * ((1 - t) * (1 - s))) *
          (dot (vec A C) (vec B D)) ^ 2 := by
    simp only [pow_two, mul_assoc, mul_comm, mul_left_comm]
  rw [hfactor]
  exact mul_nonneg
    (mul_nonneg (mul_nonneg ht0 hs0)
      (mul_nonneg (sub_nonneg.mpr ht1) (sub_nonneg.mpr hs1)))
    (sq_nonneg _)

theorem dot_two_scale : ∀ (u v : Point) (a b : ℝ),
    dot (a * u.1, a * u.2) (b * v.1, b * v.2) =
      (a * b) * dot u v := by
  intro u v a b
  simp [dot, mul_add, mul_assoc, mul_comm, mul_left_comm]

/-- Approach: BP is (1-t) times BA; use the homogeneity of the dot product and the symmetry of squared distance. -/
theorem affine_dot_backward : ∀ (P A B : Point) (t : ℝ),
    is_affine_combination P A B t →
    dot (vec B A) (vec B P) = (1 - t) * distance_sq A B := by
  intro P A B t h
  change P = line A B t at h
  have hcoord (a b : ℝ) :
      a + t * (b - a) - b = (1 - t) * (a - b) := by
    simp [sub_eq_add_neg, mul_add, add_mul,
      add_assoc, add_comm, add_left_comm]
  have hvec : vec B P =
      ((1 - t) * (vec B A).1, (1 - t) * (vec B A).2) := by
    rw [h]
    apply Prod.ext
    · change A.1 + t * (B.1 - A.1) - B.1 =
        (1 - t) * (A.1 - B.1)
      exact hcoord A.1 B.1
    · change A.2 + t * (B.2 - A.2) - B.2 =
        (1 - t) * (A.2 - B.2)
      exact hcoord A.2 B.2
  rw [hvec, dot_scale_right, vec_dot_self_is_distance,
    distance_sq_symmetric_prop B A]

/-- Approach: AP is t times AB; use the homogeneity of the dot product in its second argument. -/
theorem affine_dot_forward : ∀ (P A B : Point) (t : ℝ),
    is_affine_combination P A B t →
    dot (vec A B) (vec A P) = t * distance_sq A B := by
  intro P A B t h
  change P = line A B t at h
  have hvec : vec A P =
      (t * (vec A B).1, t * (vec A B).2) := by
    rw [h]
    apply Prod.ext <;> simp [vec, line]
  rw [hvec, dot_scale_right, vec_dot_self_is_distance]

theorem affine_distance_from_parameter : ∀ (P A B : Point) (t : ℝ),
    is_affine_combination P A B t →
    distance_sq A P = t ^ 2 * distance_sq A B := by
  intro P A B t h
  exact affine_combination_distance_sq P A B t h

/-- Approach: The intersection point on the segment gives a nonnegative product of dot products, and the two collinearity relations give the squared cross-equality. -/
theorem vertical_angles_equal :
    ∀ (A B C D O : Point),
      is_collinear O A C →
      is_collinear O B D →
      is_on_segment O A C →
      is_on_segment O B D →
      are_angles_congruent A O B C O D := by
  intro A B C D O hAC hBD hsegAC hsegBD
  exact asa_angle_equations_bridge A O B C O D
    (vertical_angles_sign_core A B C D O hsegAC hsegBD)
    (vertical_angles_square_core A B C D O hAC hBD)

/-- Approach: Use vector scaling and equal side lengths to cancel the nonzero squared distances,
    Obtain k^2 = 1; then use k >= 0 to rule out k = -1. -/
theorem aas_scalar_first_side :
    ∀ (A B D E : Point) (k : ℝ),
      A ≠ B →
      0 ≤ k →
      vec D E = (k * (vec A B).1, k * (vec A B).2) →
      are_segments_congruent A B D E →
      k = 1 := by
  intro A B D E k hAB hk hscale hcong
  have hdist :
      distance_sq D E = k ^ 2 * distance_sq A B := by
    unfold distance_sq
    rw [hscale, dot_two_scale]
    simp only [pow_two]
  have hpos : 0 < distance_sq A B :=
    distance_sq_positive_of_ne A B hAB
  have hne : distance_sq A B ≠ 0 := ne_of_gt hpos
  have heq :
      k ^ 2 * distance_sq A B = 1 * distance_sq A B := by
    calc
      k ^ 2 * distance_sq A B = distance_sq D E := hdist.symm
      _ = distance_sq A B := hcong.symm
      _ = 1 * distance_sq A B := (one_mul _).symm
  have hsquare : k ^ 2 = 1 := mul_right_cancel₀ hne heq
  have hfactor : (k - 1) * (k + 1) = 0 := by
    rw [← difference_of_squares, hsquare]
    simp
  have hsum_pos : 0 < k + 1 := by
    exact lt_of_lt_of_le (zero_lt_one)
      (le_add_of_nonneg_left hk)
  have hsum_ne : k + 1 ≠ 0 := ne_of_gt hsum_pos
  have hsub : k - 1 = 0 :=
    (mul_eq_zero.mp hfactor).resolve_right hsum_ne
  exact sub_eq_zero.mp hsub

/-- Approach: Substitute the final sides CA and FD respectively into the already-proven first-side scalar cancellation theorem. -/
theorem aas_scalar_last_side :
    ∀ (A C D F : Point) (k : ℝ),
      C ≠ A →
      0 ≤ k →
      vec F D = (k * (vec C A).1, k * (vec C A).2) →
      are_segments_congruent C A F D →
      k = 1 := by
  intro A C D F k hCA hk hscale hcong
  exact aas_scalar_first_side C A F D k hCA hk hscale hcong

theorem cancel_positive_right_factor : ∀ (a b c : ℝ),
    a * c = b * c → 0 < c → a = b := by
  intro a b c h hc
  apply (mul_right_cancel₀ (ne_of_gt hc))
  exact h

/-- The three triangle vertices are not collinear, so the determinant of the corresponding vectors is nonzero. -/
theorem triangle_det_nonzero : ∀ (A B C : Point),
    is_triangle A B C →
    det (vec A B) (vec A C) ≠ 0 := by
  intro A B C h
  unfold is_triangle is_collinear at h
  exact h

/-- The three triangle vertices are not collinear, so the squared determinant of the corresponding vectors is strictly positive. -/
theorem triangle_det_square_positive : ∀ (A B C : Point),
    is_triangle A B C →
    0 < det (vec A B) (vec A C) ^ 2 := by
  intro A B C htri
  exact sq_pos_of_ne_zero (triangle_det_nonzero A B C htri)

theorem square_neg : ∀ (a : ℝ), (-a) ^ 2 = a ^ 2 := by
  intro a
  simp

/-- AAS: two pairs of corresponding angles are equal, and the corresponding-side equality condition yields all three sides equal, hence the triangles are congruent. -/
theorem triangle_congruence_AAS : ∀ (A B C D E F : Point),
    are_angles_congruent A B C D E F →
    are_angles_congruent B A C E D F →
    are_segments_congruent A B D E →
    are_segments_congruent B C E F →
    are_segments_congruent C A F D →
    are_triangles_congruent A B C D E F := by
  intro A B C D E F hangle₁ hangle₂ hAB hBC hCA
  exact asa_congruence A B C D E F
    hangle₁ hAB hangle₂ hBC hCA

/-- Approach: The midpoint makes the sum of the two endpoint coordinates equal twice the midpoint coordinate;
    The difference of the squared distances therefore equals twice the dot product of the perpendicular vectors. -/
theorem perpendicular_bisector_property :
    ∀ (P A B M : Point),
      is_midpoint M A B →
      is_perpendicular P M A B →
      distance_sq P A = distance_sq P B := by
  intro P A B M hmid hperp
  rcases hmid with ⟨hx, hy⟩
  have hsumx : A.1 + B.1 = M.1 + M.1 := by
    rw [hx]
    exact (add_halves _).symm
  have hsumy : A.2 + B.2 = M.2 + M.2 := by
    rw [hy]
    exact (add_halves _).symm
  have hdot :
      (M.1 - P.1) * (B.1 - A.1) +
        (M.2 - P.2) * (B.2 - A.2) = 0 :=
    perpendicular_dot_expand P M A B hperp
  have hcoord (a b m p : ℝ) (hsum : a + b = m + m) :
      (b - p) ^ 2 - (a - p) ^ 2 =
        (m - p) * (b - a) + (m - p) * (b - a) := by
    have hs : (b - p) + (a - p) = (m - p) + (m - p) := by
      calc
        (b - p) + (a - p) = (a + b) + (-p + -p) := by
          simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
        _ = (m - p) + (m - p) := by
          rw [hsum]
          simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
    rw [difference_of_squares, hs]
    have hd : (b - p) - (a - p) = b - a := by simp
    rw [hd, mul_add]
    rw [mul_comm (b - a) (m - p)]
  have hdiff : distance_sq P B - distance_sq P A = 0 := by
    rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula]
    calc
      ((B.1 - P.1) ^ 2 + (B.2 - P.2) ^ 2) -
          ((A.1 - P.1) ^ 2 + (A.2 - P.2) ^ 2) =
          ((B.1 - P.1) ^ 2 - (A.1 - P.1) ^ 2) +
            ((B.2 - P.2) ^ 2 - (A.2 - P.2) ^ 2) := by
        simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
      _ =
          ((M.1 - P.1) * (B.1 - A.1) +
            (M.2 - P.2) * (B.2 - A.2)) +
          ((M.1 - P.1) * (B.1 - A.1) +
            (M.2 - P.2) * (B.2 - A.2)) := by
        rw [hcoord A.1 B.1 M.1 P.1 hsumx,
          hcoord A.2 B.2 M.2 P.2 hsumy]
        exact add_add_add_comm _ _ _ _
      _ = 0 := by rw [hdot]; simp
  exact (sub_eq_zero.mp hdiff).symm

theorem perpendicular_bisector_equidistant_sq :
    ∀ (P A B M : Point),
      is_midpoint M A B →
      is_perpendicular P M A B →
      distance_sq P A = distance_sq P B := by
  intro P A B M hmid hperp
  exact perpendicular_bisector_property P A B M hmid hperp

theorem perpendicular_from_dot_zero : ∀ (A B C D : Point),
    dot (vec A B) (vec C D) = 0 →
    is_perpendicular A B C D := by
  intro A B C D h
  unfold is_perpendicular
  exact h

/-- For a parallelogram, the coordinate differences of the two pairs of opposite sides satisfy the corresponding determinant equalities. -/
theorem parallelogram_coordinate_difference :
    ∀ (A B C D : Point),
      is_parallelogram A B C D →
      ((B.1 - A.1) * (D.2 - C.2) =
          (B.2 - A.2) * (D.1 - C.1)) ∧
      ((C.1 - B.1) * (A.2 - D.2) =
          (C.2 - B.2) * (A.1 - D.1)) := by
  intro A B C D h
  rcases h with ⟨hABCD, hBCDA⟩
  constructor
  · exact sub_eq_zero.mp (parallel_implies_det_zero A B C D hABCD)
  · exact sub_eq_zero.mp (parallel_implies_det_zero B C D A hBCDA)

/-- Approach: Substitute the equal real numbers into the squared expression. -/
theorem square_of_equal : ∀ (a b : ℝ), a = b → a ^ 2 = b ^ 2 := by
  intro a b h
  rw [h]

/-- Approach: Expand the square of the coordinate sum and use the orthogonality condition to cancel the two cross terms. -/
theorem orthogonal_coordinate_sum_square :
    ∀ (x₁ y₁ x₂ y₂ : ℝ),
      x₁ * x₂ + y₁ * y₂ = 0 →
      (x₁ + x₂) ^ 2 + (y₁ + y₂) ^ 2 =
        (x₁ ^ 2 + y₁ ^ 2) + (x₂ ^ 2 + y₂ ^ 2) := by
  intro x₁ y₁ x₂ y₂ horth
  calc
    (x₁ + x₂) ^ 2 + (y₁ + y₂) ^ 2 =
        (x₁ ^ 2 + y₁ ^ 2) + (x₂ ^ 2 + y₂ ^ 2) +
          (x₁ * x₂ + y₁ * y₂) +
          (x₁ * x₂ + y₁ * y₂) := by
      simp [pow_two, add_mul, mul_add, mul_comm,
        add_assoc, add_comm, add_left_comm]
    _ = (x₁ ^ 2 + y₁ ^ 2) + (x₂ ^ 2 + y₂ ^ 2) := by
      rw [horth]
      simp

/-- Rotating clockwise by 90 degrees preserves lengths and produces perpendicularity, so the resulting triangle is an isosceles right triangle. -/
theorem rotated_90_creates_isosceles_right : ∀ (A B C : Point),
    rotated_90_cw (vec A B) (vec A C) →
    is_isosceles A B C ∧ is_right_angle B A C := by
  intro A B C hrot
  constructor
  · unfold is_isosceles
    left
    exact rotation_90_cw_distance_prop A B A C hrot
  · exact rotation_90_cw_perpendicular_prop A B A C hrot

/-- The square of a square's diagonal length equals twice the square of its side length. -/
theorem square_diagonal_length : ∀ (A B C D : Point),
    is_square A B C D →
    distance_sq A C = 2 * distance_sq A B := by
  intro A B C D hsquare
  rcases hsquare with ⟨hrect, hrhomb⟩
  have hright : is_right_angle A B C := hrect.2
  have hsides : distance_sq A B = distance_sq B C := hrhomb.2
  have hpyth :
      distance_sq A B + distance_sq B C = distance_sq A C :=
    pythagorean_prop A B C hright
  calc
    distance_sq A C =
        distance_sq A B + distance_sq B C := hpyth.symm
    _ = distance_sq A B + distance_sq A B := by rw [← hsides]
    _ = 2 * distance_sq A B := (two_mul (distance_sq A B)).symm

/-- In an isosceles right triangle, the square of the hypotenuse length equals twice the square of a leg length. -/
theorem isosceles_right_hypotenuse_length : ∀ (A B C : Point),
    is_right_angle A B C →
    are_segments_congruent A B B C →
    distance_sq A C = 2 * distance_sq A B := by
  intro A B C hright hequal
  have hpyth :
      distance_sq A B + distance_sq B C = distance_sq A C :=
    pythagorean_prop A B C hright
  unfold are_segments_congruent at hequal
  calc
    distance_sq A C =
        distance_sq A B + distance_sq B C := hpyth.symm
    _ = distance_sq A B + distance_sq A B := by rw [← hequal]
    _ = 2 * distance_sq A B := (two_mul (distance_sq A B)).symm

/-- Vertical angles correspond to the squared cross-equality of the dot products. -/
theorem vertical_angles_dot_equal :
    ∀ (A B C D O : Point),
      is_collinear O A C →
      is_collinear O B D →
      dot (vec O A) (vec O B) ^ 2 *
          (distance_sq O C * distance_sq O D) =
        dot (vec O C) (vec O D) ^ 2 *
          (distance_sq O A * distance_sq O B) := by
  intro A B C D O hAC hBD
  simpa [angle_cos_num, angle_cos_den] using
    vertical_angles_square_core A B C D O hAC hBD

theorem perpendicular_bisector_equidistant :
    ∀ (P A B M : Point),
      is_midpoint M A B →
      is_perpendicular P M A B →
      distance_sq P A = distance_sq P B := by
  intro P A B M hmid hperp
  exact perpendicular_bisector_equidistant_sq P A B M hmid hperp

theorem test_point_on_line_with_distance : ∀ (P A B : Point),
    is_on_line P A B →
    ∃ t : ℝ, P = line A B t ∧
      distance_sq A P = t ^ 2 * distance_sq A B := by
  intro P A B h
  rcases h with ⟨t, ht⟩
  refine ⟨t, ht, ?_⟩
  apply affine_combination_distance_sq P A B t
  exact ht

theorem dot_sub_right_coordinate : ∀ (u v w : Point),
    dot u (v.1 - w.1, v.2 - w.2) = dot u v - dot u w := by
  intro u v w
  unfold dot
  simp only [Prod.fst, Prod.snd, mul_sub]
  simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]

theorem collinear_coordinates_imply_affine_parameter :
    ∀ (P A B : Point),
      A ≠ B →
      is_collinear A B P →
      ∃ t : ℝ, is_affine_combination P A B t := by
  intro P A B hAB hcol
  have hdet :
      (B.1 - A.1) * (P.2 - A.2) =
        (B.2 - A.2) * (P.1 - A.1) :=
    collinear_to_standard_det A B P hcol
  by_cases hx : B.1 - A.1 = 0
  · have hy : B.2 - A.2 ≠ 0 := by
      intro hy
      apply hAB
      apply Prod.ext
      · exact (sub_eq_zero.mp hx).symm
      · exact (sub_eq_zero.mp hy).symm
    have hprod :
        (B.2 - A.2) * (P.1 - A.1) = 0 := by
      calc
        (B.2 - A.2) * (P.1 - A.1) =
            (B.1 - A.1) * (P.2 - A.2) := hdet.symm
        _ = 0 := by rw [hx]; simp
    have hpx : P.1 - A.1 = 0 :=
      (mul_eq_zero.mp hprod).resolve_left hy
    let t : ℝ := (P.2 - A.2) / (B.2 - A.2)
    have hty :
        t * (B.2 - A.2) = P.2 - A.2 := by
      dsimp [t]
      exact div_mul_cancel₀ (P.2 - A.2) hy
    refine ⟨t, ?_⟩
    unfold is_affine_combination
    apply Prod.ext
    · change P.1 = A.1 + t * (B.1 - A.1)
      rw [hx]
      simp
      exact sub_eq_zero.mp hpx
    · change P.2 = A.2 + t * (B.2 - A.2)
      calc
        P.2 = A.2 + (P.2 - A.2) := by simp
        _ = A.2 + t * (B.2 - A.2) := by rw [hty]
  · let t : ℝ := (P.1 - A.1) / (B.1 - A.1)
    have htx :
        t * (B.1 - A.1) = P.1 - A.1 := by
      dsimp [t]
      exact div_mul_cancel₀ (P.1 - A.1) hx
    have hsame :
        (B.1 - A.1) * (P.2 - A.2) =
          (B.1 - A.1) * (t * (B.2 - A.2)) := by
      calc
        (B.1 - A.1) * (P.2 - A.2) =
            (B.2 - A.2) * (P.1 - A.1) := hdet
        _ = (B.2 - A.2) * (t * (B.1 - A.1)) := by rw [htx]
        _ = (B.1 - A.1) * (t * (B.2 - A.2)) := by
          simp only [mul_assoc, mul_comm, mul_left_comm]
    have hty :
        t * (B.2 - A.2) = P.2 - A.2 := by
      have hcancel :
          P.2 - A.2 = t * (B.2 - A.2) :=
        (mul_left_cancel₀ hx) hsame
      exact hcancel.symm
    refine ⟨t, ?_⟩
    unfold is_affine_combination
    apply Prod.ext
    · change P.1 = A.1 + t * (B.1 - A.1)
      calc
        P.1 = A.1 + (P.1 - A.1) := by simp
        _ = A.1 + t * (B.1 - A.1) := by rw [htx]
    · change P.2 = A.2 + t * (B.2 - A.2)
      calc
        P.2 = A.2 + (P.2 - A.2) := by simp
        _ = A.2 + t * (B.2 - A.2) := by rw [hty]

/-- Approach: Unfold the definitions of a point on the line and of an affine combination; both have the same parametric representation. -/
theorem on_line_implies_affine_parameter : ∀ (P A B : Point),
    is_on_line P A B →
    ∃ t : ℝ, is_affine_combination P A B t := by
  intro P A B h
  rcases h with ⟨t, ht⟩
  exact ⟨t, ht⟩

/-- The right-angle vertex of a right triangle is not equal to its foot on the line containing the opposite side. -/
theorem right_angle_vertex_distinct_from_foot_on_opposite_line :
    ∀ (A B C H : Point),
      is_triangle A B C →
      is_right_angle A B C →
      is_foot H B A C →
      B ≠ H := by
  intro A B C H htri _ hfoot hBH
  unfold is_triangle at htri
  apply htri
  unfold is_collinear
  rcases hfoot.1 with ⟨t, hH⟩
  have hB : B = line A C t := hBH.trans hH
  unfold det vec
  rw [hB]
  simp [line, mul_assoc, mul_comm, mul_left_comm]

/-- The right-angle vertex of a right triangle does not lie on the line containing the opposite side. -/
theorem right_angle_vertex_not_on_opposite_line :
    ∀ (A B C : Point),
      is_triangle A B C →
      is_right_angle A B C →
      ¬ is_on_line B A C := by
  intro A B C htri _ hline
  unfold is_triangle at htri
  apply htri
  unfold is_collinear
  rcases hline with ⟨t, hB⟩
  unfold det vec
  rw [hB]
  simp [line, mul_assoc, mul_comm, mul_left_comm]

theorem dot_scale_left : ∀ (u v : Point) (c : ℝ),
    dot (c * u.1, c * u.2) v = c * dot u v := by
  intro u v c
  rw [dot_commutative, dot_scale_right, dot_commutative]

theorem dot_linear_left : ∀ (u v w : Point),
    dot (u.1 + v.1, u.2 + v.2) w = dot u w + dot v w := by
  intro u v w
  exact dot_add_left u v w

theorem dot_linear_right : ∀ (u v w : Point),
    dot u (v.1 + w.1, v.2 + w.2) = dot u v + dot u w := by
  intro u v w
  exact dot_add_right u v w

theorem orthogonal_midpoint_scalar_finish : ∀ (t d : ℝ),
    0 < d →
    t * d = (1 - t) * d →
    t = 1 / 2 := by
  intro t d hd heq
  have ht : t = 1 - t :=
    cancel_positive_right_factor t (1 - t) d heq hd
  have hsum : t + t = 1 := by
    calc
      t + t = t + (1 - t) :=
        congrArg (fun x : ℝ => t + x) ht
      _ = 1 := by
        simp [sub_eq_add_neg, add_assoc, add_comm, add_left_comm]
  apply (eq_div_iff (show (2 : ℝ) ≠ 0 by norm_num)).2
  calc
    t * 2 = t + t := mul_two t
    _ = 1 := hsum

/-- Approach: By the symmetry of the dot product, rewrite the orthogonality condition as `dot v u = 0`, then use bilinearity of the dot product. -/
theorem orthogonal_midpoint_vector_core : ∀ (u v : Point),
    dot u v = 0 →
    dot (u.1 + v.1, u.2 + v.2) u = dot u u ∧
      dot v (u.1 + v.1, u.2 + v.2) = dot v v := by
  intro u v horth
  have horth' : dot v u = 0 := by
    rw [dot_commutative]
    exact horth
  constructor
  · rw [dot_linear_left, horth', add_zero]
  · rw [dot_linear_right, horth', zero_add]

/-- Approach: Square both sides of the product equality, then rewrite using the square-of-a-product formula. -/
theorem equal_products_have_equal_squares : ∀ (a b c d : ℝ),
    a * b = c * d →
    a ^ 2 * b ^ 2 = c ^ 2 * d ^ 2 := by
  intro a b c d h
  calc
    a ^ 2 * b ^ 2 = (a * b) ^ 2 := (mul_pow a b 2).symm
    _ = (c * d) ^ 2 := congrArg (fun x : ℝ => x ^ 2) h
    _ = c ^ 2 * d ^ 2 := mul_pow c d 2

theorem cancel_positive_factor_from_nonnegative_product : ∀ (a b : ℝ),
    0 < a →
    0 ≤ a * b →
    0 ≤ b := by
  intro a b ha hab
  exact nonneg_of_mul_nonneg_right hab ha

theorem cross_product_positive_det_product_implies_same_sign :
    ∀ (u v w z : Point),
      det u v * det w z > 0 →
      (det u v > 0 ∧ det w z > 0) ∨
        (det u v < 0 ∧ det w z < 0) := by
  intro u v w z h
  exact (mul_pos_iff.mp h)

/-- A positive determinant product means the two determinants have the same sign. -/
theorem cross_ratio_same_det_sign_implies_angle_congruence :
    ∀ (u v w z : Point),
      det u v * det w z > 0 →
      (det u v > 0 ∧ det w z > 0) ∨
        (det u v < 0 ∧ det w z < 0) := by
  intro u v w z h
  exact cross_product_positive_det_product_implies_same_sign u v w z h

theorem equality_from_three_zero_terms : ∀ (a b c d e f : ℝ),
    a - b = 0 →
    c - d = 0 →
    e - f = 0 →
    a + c + e = b + d + f := by
  intro a b c d e f hab hcd hef
  have hab' : a = b := sub_eq_zero.mp hab
  have hcd' : c = d := sub_eq_zero.mp hcd
  have hef' : e = f := sub_eq_zero.mp hef
  rw [hab', hcd', hef']

theorem product_of_equal_factors : ∀ (a b c d : ℝ),
    a = b → c = d → a * c = b * d := by
  intro a b c d hab hcd
  rw [hab, hcd]

/-- Approach: Expand the two squared distances centered at the same point, and use the equality of one coordinate difference to cancel the corresponding squared term. -/
theorem equal_centered_norms_same_chord_coordinate :
    ∀ (O A B : Point),
      distance_sq O A = distance_sq O B →
      A.1 = B.1 →
      (A.2 - O.2) ^ 2 = (B.2 - O.2) ^ 2 := by
  intro O A B hdist hx
  rw [distance_sq_coordinate_formula, distance_sq_coordinate_formula, hx] at hdist
  exact add_left_cancel hdist

/-- Approach: Two points at the same distance from the center have equal squared distances, and since their x-coordinates are equal, the squares of their y-coordinate differences are equal. -/
theorem common_center_same_chord_cross_ratio :
    ∀ (O A B : Point),
      distance_sq O A = distance_sq O B →
      A.1 = B.1 →
      (A.2 - O.2) ^ 2 = (B.2 - O.2) ^ 2 := by
  intro O A B hdist hx
  exact equal_centered_norms_same_chord_coordinate O A B hdist hx

