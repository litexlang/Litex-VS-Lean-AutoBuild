-- LeanGeo 基础库

import Mathlib.Data.Real.Basic

-- 点类型定义为实数坐标对
def Point := ℝ × ℝ

-- 向量：从A到B
def vec (A B : Point) : Point := (B.1 - A.1, B.2 - A.2)

-- 点积
def dot (u v : Point) : ℝ := u.1 * v.1 + u.2 * v.2

-- 行列式
def det (u v : Point) : ℝ := u.1 * v.2 - u.2 * v.1
