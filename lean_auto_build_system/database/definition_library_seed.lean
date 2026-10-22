-- LeanGeo basic library

import Mathlib.Data.Real.Basic

-- Point type defined as real coordinate pair
def Point := ℝ × ℝ

-- Vector: from A to B
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- Dot product
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- Determinant
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
