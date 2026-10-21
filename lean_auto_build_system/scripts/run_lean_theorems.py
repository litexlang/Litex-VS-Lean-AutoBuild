#!/usr/bin/env python3
"""
Lean Theorem 自动证明系统
基于完整的definition库证明theorems
"""

import os
import json
import sys
import argparse
from openai import OpenAI
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import time

# 导入 Lean 验证器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lean_session import SessionBackedValidator

# ========================================
# 数据结构
# ========================================

@dataclass
class Task:
    """单个任务"""
    id: str
    stage: int
    name: str
    description: str
    task_type: str
    hints: List[str]

@dataclass
class TaskAttempt:
    """单次尝试记录"""
    task_id: str
    attempt_number: int
    agent_output: str
    success: bool
    error_type: Optional[str]
    compiler_output: Optional[str]
    timestamp: str
    time_elapsed: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

# ========================================
# Lean Theorem 任务定义（从litex保持一致）
# ========================================

LEAN_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="证明distance_sq_coordinate_formula定理",
        description="Expand distance_sq(a, b) into (Δx)^2 + (Δy)^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="证明distance_sq_nonnegative定理",
        description="Squared distance is always nonnegative.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="证明distance_sq_symmetric定理",
        description="distance_sq(a, b) = distance_sq(b, a).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.4",
        stage=1,
        name="证明vec_dot_self_is_distance定理",
        description="dot(vec(a, b), vec(a, b)) equals distance_sq(a, b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.5",
        stage=1,
        name="证明distance_equality_to_dot定理",
        description="Equal distances imply a related dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.6",
        stage=1,
        name="证明point_difference_norm_pos定理",
        description="Distinct points give strictly positive squared difference.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.7",
        stage=1,
        name="证明distance_sq_translate定理",
        description="Translating both endpoints preserves distance_sq.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.8",
        stage=1,
        name="证明distance_sq_positive_of_ne定理",
        description="a != b implies distance_sq(a, b) > 0.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.9",
        stage=1,
        name="证明translated_difference_square定理",
        description="Expand a translated coordinate difference squared.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.10",
        stage=1,
        name="证明center_offset_square定理",
        description="Squared offset from a center expands by bilinearity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.1",
        stage=2,
        name="证明affine_combination_distance_sq定理",
        description="Squared distance along an affine combination (p = (1-t)a + t b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.2",
        stage=2,
        name="证明inner_product_distance_identity定理",
        description="Relate a dot product to a combination of distance_sq terms.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.3",
        stage=2,
        name="证明distance_expansion_identity定理",
        description="Expand |u-v|^2 via |u|^2 + |v|^2 - 2 u·v style identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.4",
        stage=2,
        name="证明affine_distance_from_parameter定理",
        description="Predicate form: distance_sq symmetry.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.5",
        stage=2,
        name="证明twice_dot_from_distances_direct定理",
        description="Solve for 2 u·v from three distance_sq values.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.6",
        stage=2,
        name="证明vec_coordinate_formula定理",
        description="Unfold vec(a, b) to coordinate differences.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.7",
        stage=2,
        name="证明dot_coordinate_formula定理",
        description="Unfold dot(u, v) to the coordinate formula.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.8",
        stage=2,
        name="证明det_coordinate_formula定理",
        description="Unfold det(u, v) to the coordinate formula.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.9",
        stage=2,
        name="证明dot_symmetric定理",
        description="Dot product is symmetric: u·v = v·u.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.10",
        stage=2,
        name="证明dot_commutative定理",
        description="Dot product is commutative (same as symmetry).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.1",
        stage=3,
        name="证明dot_add_left定理",
        description="Dot is additive in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.2",
        stage=3,
        name="证明dot_add_right定理",
        description="Dot is additive in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.3",
        stage=3,
        name="证明dot_square_sum定理",
        description="Expand |u+v|^2 = |u|^2 + |v|^2 + 2 u·v.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.4",
        stage=3,
        name="证明det_antisymmetric定理",
        description="det(u, v) = -det(v, u).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.5",
        stage=3,
        name="证明vec_add_path_x定理",
        description="x-component of chained vectors adds.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.6",
        stage=3,
        name="证明vec_add_path_y定理",
        description="y-component of chained vectors adds.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.7",
        stage=3,
        name="证明dot_from_cosine_law定理",
        description="Recover a dot product from the law of cosines.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.8",
        stage=3,
        name="证明vec_add定理",
        description="Vector addition along a path: vec(a,b) + vec(b,c) = vec(a,c).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.9",
        stage=3,
        name="证明vec_neg定理",
        description="vec(b, a) = -vec(a, b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.10",
        stage=3,
        name="证明dot_bilinear_expand定理",
        description="Expand a bilinear combination of dots.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.1",
        stage=4,
        name="证明dot_det_eliminate定理",
        description="Eliminate mixed dot/det terms in a polynomial identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.2",
        stage=4,
        name="证明dot_neg_left定理",
        description="dot(-u, v) = -dot(u, v).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.3",
        stage=4,
        name="证明det_neg_left定理",
        description="det(-u, v) = -det(u, v).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.4",
        stage=4,
        name="证明det_change_base定理",
        description="Change-of-base formula for det.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.5",
        stage=4,
        name="证明dot_change_base定理",
        description="Change-of-base formula for dot.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.6",
        stage=4,
        name="证明det_bilinear_right定理",
        description="Det is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.7",
        stage=4,
        name="证明dot_bilinear_right定理",
        description="Dot is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.8",
        stage=4,
        name="证明dot_scale_right定理",
        description="Dot scales in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.9",
        stage=4,
        name="证明det_scale_right定理",
        description="Det scales in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.10",
        stage=4,
        name="证明dot_squared_plus_det_squared定理",
        description="|u|^2|v|^2 = (u·v)^2 + det(u,v)^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.1",
        stage=5,
        name="证明dot_two_scale定理",
        description="Predicate form of recovering dot from the cosine law.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.2",
        stage=5,
        name="证明dot_sub_right_coordinate定理",
        description="Coordinate form of dot(u, v-w).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.3",
        stage=5,
        name="证明dot_scale_left定理",
        description="Dot scales in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.4",
        stage=5,
        name="证明dot_linear_left定理",
        description="Dot is linear in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.5",
        stage=5,
        name="证明dot_linear_right定理",
        description="Dot is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.6",
        stage=5,
        name="证明collinear_det_expand定理",
        description="Expand the collinearity det condition in coordinates.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.7",
        stage=5,
        name="证明perpendicular_dot_expand定理",
        description="Expand the perpendicularity dot condition in coordinates.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.8",
        stage=5,
        name="证明collinear_symmetric定理",
        description="Collinearity is symmetric in the three points (reorderings).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.9",
        stage=5,
        name="证明collinear_midpoint定理",
        description="The midpoint lies on the line through distinct endpoints (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.10",
        stage=5,
        name="证明collinear_to_standard_det定理",
        description="Normalize a collinearity statement to a standard det form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.1",
        stage=6,
        name="证明collinear_equidistant_implies_midpoint定理",
        description="Collinear and equidistant implies midpoint.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.2",
        stage=6,
        name="证明parallelogram_diagonals定理",
        description="Parallelogram diagonal vector/length identities.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.3",
        stage=6,
        name="证明collinear_third定理",
        description="Two collinear pairs sharing a side imply a third collinearity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.4",
        stage=6,
        name="证明parallelogram_sides定理",
        description="Opposite sides of a parallelogram are equal (vector form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.5",
        stage=6,
        name="证明perpendicular_symmetric定理",
        description="Perpendicularity of segments is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.6",
        stage=6,
        name="证明parallel_symmetric定理",
        description="Parallelism of segments is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.7",
        stage=6,
        name="证明perpendicular_from_parallel定理",
        description="A line perpendicular to one of two parallels is perpendicular to the other.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.8",
        stage=6,
        name="证明equidistant_perp_bisector定理",
        description="Equidistant points lie on the perpendicular bisector.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.9",
        stage=6,
        name="证明parallelogram_diagonal_sum定理",
        description="Sum of squared diagonals equals sum of squared sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.10",
        stage=6,
        name="证明collinear_implies_midpoint_distance定理",
        description="Collinearity implies a midpoint distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.1",
        stage=7,
        name="证明equidistant_implies_perp_bisector_dot定理",
        description="Equidistance implies the perp-bisector dot condition.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.2",
        stage=7,
        name="证明parallel_implies_det_zero定理",
        description="Parallel segments have det of direction vectors zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.3",
        stage=7,
        name="证明parallelogram_midpoint_diagonals定理",
        description="Diagonals of a parallelogram bisect each other.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.4",
        stage=7,
        name="证明perp_dot_zero_coordinate定理",
        description="Coordinate form of perpendicular => dot zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.5",
        stage=7,
        name="证明perpendicular_implies_distance_sum定理",
        description="Right angle gives the Pythagorean distance sum identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.6",
        stage=7,
        name="证明perpendicular_bisector_property定理",
        description="Predicate form of collinearity symmetry.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.7",
        stage=7,
        name="证明perpendicular_bisector_equidistant_sq定理",
        description="Points on the perp bisector are equidistant (squared).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.8",
        stage=7,
        name="证明perpendicular_from_dot_zero定理",
        description="dot = 0 of direction vectors implies perpendicular segments.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.9",
        stage=7,
        name="证明parallelogram_coordinate_difference定理",
        description="Coordinate difference form of a parallelogram.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.10",
        stage=7,
        name="证明perpendicular_bisector_equidistant定理",
        description="Perp bisector points are equidistant (predicate style).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.1",
        stage=8,
        name="证明collinear_coordinates_imply_affine_parameter定理",
        description="Place a test point on a line at a prescribed distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.2",
        stage=8,
        name="证明on_line_implies_affine_parameter定理",
        description="Membership on line_through_points gives an affine parameter (a != b, matching is_on_line).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.3",
        stage=8,
        name="证明right_angle_vertex_distinct_from_foot_on_opposite_line定理",
        description="In a right triangle, the right vertex is not the foot on the opposite side (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.4",
        stage=8,
        name="证明right_angle_vertex_not_on_opposite_line定理",
        description="The right-angle vertex does not lie on the opposite side line (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.5",
        stage=8,
        name="证明right_triangle_foot_midpoints_distinct定理",
        description="Feet/midpoints arising in a right triangle are distinct as needed (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.6",
        stage=8,
        name="证明orthocenter_third_altitude定理",
        description="Two altitudes determine the third: their intersection lies on the remaining altitude.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.7",
        stage=8,
        name="证明equidistant_dot_half定理",
        description="Equidistance implies a half-dot projection identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.8",
        stage=8,
        name="证明segments_congruent_reflexive定理",
        description="Segment congruence is reflexive.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.9",
        stage=8,
        name="证明segments_congruent_symmetric定理",
        description="Segment congruence is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.10",
        stage=8,
        name="证明segments_congruent_transitive定理",
        description="Segment congruence is transitive.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.1",
        stage=9,
        name="证明segments_congruent_from_distance_sq定理",
        description="Predicate form of symmetric segment congruence.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.2",
        stage=9,
        name="证明midpoint_equidistant定理",
        description="A midpoint of a nondegenerate segment is equidistant from the endpoints (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.3",
        stage=9,
        name="证明midpoint_half_distance定理",
        description="Distance from endpoint to midpoint is half the segment (squared: factor 1/4; a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.4",
        stage=9,
        name="证明one_dimensional_midpoint定理",
        description="1D midpoint formula and consequences.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.5",
        stage=9,
        name="证明centroid_distance定理",
        description="Distance identities involving the centroid.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.6",
        stage=9,
        name="证明midpoint_segment_ratio定理",
        description="Midpoint vs affine parameter on a nondegenerate segment (a != b; p = (1-t)a + tb).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.7",
        stage=9,
        name="证明double_midpoint_equal_sides定理",
        description="Predicate form of midpoint equidistance.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.8",
        stage=9,
        name="证明midpoint_coordinate_formula定理",
        description="Coordinate formula for the midpoint of a nondegenerate segment (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.9",
        stage=9,
        name="证明affine_dot_backward定理",
        description="Backward direction of an affine-parameter dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.10",
        stage=9,
        name="证明affine_dot_forward定理",
        description="Forward direction of an affine-parameter dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.1",
        stage=10,
        name="证明orthogonal_midpoint_scalar_finish定理",
        description="Finish an orthogonal-midpoint computation with a scalar identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.2",
        stage=10,
        name="证明orthogonal_midpoint_vector_core定理",
        description="Core vector identity for midpoints of orthogonal segments.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.3",
        stage=10,
        name="证明solve_cosine_for_dot定理",
        description="Solve the cosine ratio for the underlying dot product.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.4",
        stage=10,
        name="证明cosine_law定理",
        description="Law of cosines: relate side distance_sq values to a dot product.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.5",
        stage=10,
        name="证明isosceles_base_dot定理",
        description="In an isosceles triangle, base angles give equal projection dots.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.6",
        stage=10,
        name="证明angle_equality_cross_ratio定理",
        description="Equal undirected angles via a cross-multiplied cosine ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.7",
        stage=10,
        name="证明angle_in_semicircle_coordinate定理",
        description="Angle in a semicircle, coordinate form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.8",
        stage=10,
        name="证明isosceles_implies_equal_projections定理",
        description="Isosceles triangle implies equal projections onto the base.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.9",
        stage=10,
        name="证明vertical_angles_square_core定理",
        description="Predicate form of the isosceles base-dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.10",
        stage=10,
        name="证明vertical_angles_sign_core定理",
        description="Same-sign cosine condition for vertical angles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.1",
        stage=11,
        name="证明vertical_angles_equal定理",
        description="Vertical angles are congruent (crossing segments ab, cd with a != b, c != d).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.2",
        stage=11,
        name="证明cosine_square_to_det_square_ratio定理",
        description="Pass between cos^2 ratios and det^2 ratios.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.3",
        stage=11,
        name="证明congruent_angle_det_square_ratio定理",
        description="Congruent angles imply matching det^2 cross ratios (nonzero arms).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.4",
        stage=11,
        name="证明vertical_angles_dot_equal定理",
        description="Vertical angles give equal dots of the forming vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.5",
        stage=11,
        name="证明cross_product_positive_det_product_implies_same_sign定理",
        description="Positive det products force matching orientation signs.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.6",
        stage=11,
        name="证明cross_ratio_same_det_sign_implies_angle_congruence定理",
        description="Matching cos^2 ratio and det sign imply angle congruence.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.7",
        stage=11,
        name="证明sas_third_side定理",
        description="SAS: the third side is determined (distance_sq identity).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.8",
        stage=11,
        name="证明sas_congruence定理",
        description="SAS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.9",
        stage=11,
        name="证明sss_congruence定理",
        description="SSS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.10",
        stage=11,
        name="证明multiply_both_sides定理",
        description="Algebraic helpers used by the ASA scalar elimination.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.1",
        stage=12,
        name="证明add_equalities定理",
        description="证明add_equalities定理。",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.2",
        stage=12,
        name="证明subtract_equalities定理",
        description="证明subtract_equalities定理。",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.3",
        stage=12,
        name="证明zero_factor_law定理",
        description="If a product is zero and one factor is nonzero, the other factor is zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.4",
        stage=12,
        name="证明cancel_positive_right_factor定理",
        description="Cancel a common strictly positive scalar factor.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.5",
        stage=12,
        name="证明rearrange_sum定理",
        description="Rearrange a - b - c = 0 into a = b + c.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.6",
        stage=12,
        name="证明asa_scalar_core定理",
        description="ASA scalar core identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.7",
        stage=12,
        name="证明asa_angle_equations_bridge定理",
        description="Bridge ASA angle equations to side relations.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.8",
        stage=12,
        name="证明asa_congruence定理",
        description="ASA congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.9",
        stage=12,
        name="证明sss_dot_equal定理",
        description="SSS implies corresponding vertex dots are equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.10",
        stage=12,
        name="证明triangle_area_det定理",
        description="Signed area of a triangle via det of two sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.1",
        stage=13,
        name="证明similar_triangles_ratio定理",
        description="Similar triangles have proportional corresponding sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.2",
        stage=13,
        name="证明similar_triangles_dot定理",
        description="Similar triangles: corresponding dots scale by the square of the ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.3",
        stage=13,
        name="证明similar_triangles_det定理",
        description="Similar triangles: corresponding dets scale by the square of the ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.4",
        stage=13,
        name="证明aas_scalar_first_side定理",
        description="Predicate form of sss_dot_equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.5",
        stage=13,
        name="证明aas_scalar_last_side定理",
        description="AAS: recover the last unknown side scalar.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.6",
        stage=13,
        name="证明triangle_det_nonzero定理",
        description="A nondegenerate triangle has nonzero side-det.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.7",
        stage=13,
        name="证明triangle_det_square_positive定理",
        description="Nondegenerate triangle => det^2 > 0.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.8",
        stage=13,
        name="证明triangle_det_squared_vertex定理",
        description="Det^2 expressed from a chosen vertex.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.9",
        stage=13,
        name="证明triangle_congruence_AAS定理",
        description="AAS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.10",
        stage=13,
        name="证明strict_triangle_one_side定理",
        description="Strict triangle inequality helper on one side.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.1",
        stage=14,
        name="证明triangle_inequality定理",
        description="Triangle inequality for Euclidean distances.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.2",
        stage=14,
        name="证明pythagorean_theorem定理",
        description="Pythagorean theorem in squared-distance form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.3",
        stage=14,
        name="证明right_angle_implies_distance_relation定理",
        description="A right angle implies the Pythagorean distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.4",
        stage=14,
        name="证明isosceles_right_triangle_vertex_formula定理",
        description="Predicate form of the Pythagorean theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.5",
        stage=14,
        name="证明isosceles_right_hypotenuse_length定理",
        description="Hypotenuse length of an isosceles right triangle.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.6",
        stage=14,
        name="证明translated_circle_equation_gives_distance定理",
        description="A translated circle equation yields equal distances to the center.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.7",
        stage=14,
        name="证明circumcenter_equidistant定理",
        description="Predicate: on-circle iff distance_sq equals r^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.8",
        stage=14,
        name="证明thales_theorem定理",
        description="Thales' theorem: angle in a semicircle is right.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.9",
        stage=14,
        name="证明thales_converse定理",
        description="Converse of Thales' theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.10",
        stage=14,
        name="证明circle_equation_gives_equal_distance定理",
        description="First Cramer equation for a circle through points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.1",
        stage=15,
        name="证明common_center_implies_concyclic定理",
        description="A shared center with equal radii implies concyclic points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.2",
        stage=15,
        name="证明concyclic_det_criterion_implies_concyclic定理",
        description="Det criterion implies four points are concyclic.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.3",
        stage=15,
        name="证明concyclic_det_criterion定理",
        description="Determinant criterion for four concyclic points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.4",
        stage=15,
        name="证明nine_point_center定理",
        description="Nine-point center coordinate identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.5",
        stage=15,
        name="证明power_of_point_difference定理",
        description="Power of a point as a difference of products of lengths.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.6",
        stage=15,
        name="证明circumcenter_equidistant_triple定理",
        description="Equidistance of the circumcenter from three vertices.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.7",
        stage=15,
        name="证明concyclic_fourth_point定理",
        description="Construct/verify a fourth concyclic point.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.8",
        stage=15,
        name="证明equal_centered_norms_same_chord_coordinate定理",
        description="Wu-method style quartic identity for a circle configuration.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.9",
        stage=15,
        name="证明common_center_same_chord_cross_ratio定理",
        description="Same center and chord length control an angle cross ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.10",
        stage=15,
        name="证明concyclic_same_chord_angles_congruent定理",
        description="Concyclic points with the same chord have congruent inscribed angles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.1",
        stage=16,
        name="证明apollonius_theorem定理",
        description="Apollonius' theorem for medians (squared form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.2",
        stage=16,
        name="证明square_orthogonal_parallel_quadrilateral_coordinates定理",
        description="(-x)^2 = x^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.3",
        stage=16,
        name="证明orthogonal_coordinate_sum_square定理",
        description="Square of equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.4",
        stage=16,
        name="证明square_diagonal_length定理",
        description="Square diagonal length.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.5",
        stage=16,
        name="证明reflection_distance定理",
        description="Reflection preserves distance to the mirror line setup.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.6",
        stage=16,
        name="证明rotation_preserves_distance定理",
        description="Rotation preserves distance.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.7",
        stage=16,
        name="证明rotation_preserves_dot定理",
        description="90° rotation preserves dots of corresponding vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.8",
        stage=16,
        name="证明rotation_preserves_det定理",
        description="90° rotation preserves dets of corresponding vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.9",
        stage=16,
        name="证明reflection_equidistant定理",
        description="A point and its reflection are equidistant from points on the mirror.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.10",
        stage=16,
        name="证明rotated_90_creates_isosceles_right定理",
        description="Predicate: clockwise 90° rotation preserves distances.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.1",
        stage=17,
        name="证明reflected_vec_sum定理",
        description="Sum identity for a vector and its reflection.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.2",
        stage=17,
        name="证明stewart_theorem定理",
        description="Stewart's theorem (squared form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.3",
        stage=17,
        name="证明median_length定理",
        description="Median length formula (squared).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.4",
        stage=17,
        name="证明foot_perp_parametric定理",
        description="Parametric formula for the perpendicular foot.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.5",
        stage=17,
        name="证明median_inequality_distance定理",
        description="Predicate form of the median length formula.",
        task_type="theorem",
        hints=[]
    ),
]

# ========================================
# Lean Theorem 实验管理器
# ========================================

class LeanTheoremExperiment:
    """Lean Theorem 证明实验"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path,
                 verbosity: str = "full", seed_lib_path: Optional[Path] = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.error_verbosity = verbosity

        # 创建带时间戳的子文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 实验输出目录: {self.output_dir}")
        print(f"🔬 错误详细程度: {verbosity}")

        # 日志文件
        self.log_file = self.output_dir / "experiment.log"
        self.init_log()

        # 加载完整的 definition 库作为种子
        if seed_lib_path and seed_lib_path.exists():
            seed_file = seed_lib_path
        else:
            # 优先使用library_final.lean（definitions实验输出）
            seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "library_final.lean"
            if not seed_file.exists():
                # 回退到基础种子库
                seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "LeanGeoCore" / "theorem_library_seed.lean"
                if not seed_file.exists():
                    raise FileNotFoundError(f"种子库文件不存在: {seed_file}")

        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

        print(f"✅ 加载种子库: {seed_file}")
        print(f"📏 种子库大小: {len(self.seed)} 字符")

        # 库状态
        self.state = {
            "definitions": [],
            "theorems": [],
            "completed_tasks": [],
            "axiom_debt": []
        }

        # 尝试加载之前的状态
        state_file = self.output_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)

        self.attempts = []
        self.start_time = None
        self.total_time = 0

        # 初始化 Lean 验证器
        # 使用本地的LeanGeo项目
        lean_project_dir = Path(__file__).parent.parent / "LeanGeo"

        self.validator = SessionBackedValidator(
            seed_source=self.seed,
            lean_project_dir=lean_project_dir,
            cmd_timeout=600.0  # 增加到10分钟，避免首次加载Mathlib超时
        )

    def init_log(self):
        """初始化日志文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"""# Lean Theorem 证明日志

实验时间：{timestamp}
模型：{self.model}
任务类型：theorem

---

""")

    def log(self, message: str):
        """写入日志"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message)

    def save_state(self):
        """保存状态到文件"""
        state_file = self.output_dir / "state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def save_attempts(self):
        """保存所有尝试到文件"""
        attempts_file = self.output_dir / "attempts.json"
        with open(attempts_file, "w", encoding="utf-8") as f:
            attempts_data = [asdict(a) for a in self.attempts]
            json.dump(attempts_data, f, indent=2, ensure_ascii=False)

    def save_library(self):
        """保存完整库到 library_final.lean"""
        library_file = self.output_dir / "library_final.lean"
        library_content = self.validator.export_session_library(self.seed)
        with open(library_file, "w", encoding="utf-8") as f:
            f.write(library_content)
        print(f"\n📚 完整库已保存: {library_file}")

    def get_agent_theorems_prompt(self) -> str:
        """获取已证明的定理"""
        if not self.state["theorems"]:
            return "-- （尚无新证明的定理）\n"
        return "-- 已证明的定理\n" + "\n".join(self.state["theorems"]) + "\n"

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """构建任务提示"""
        context = f"""-- ========== 种子库（已加载，包含所有definitions）==========

种子库已包含所有基础定义和谓词，你可以直接使用。

-- ========== 已证明的定理 ==========

{self.get_agent_theorems_prompt()}
"""

        # 读取 Lean 语法指南
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "lean_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            syntax_guide = """
# Lean 4 定理证明参考

1. 定理格式：theorem name : statement := by tactics
2. 常用策略：intro, apply, rw, simp, ring, norm_num
3. 结构化证明：have, show, calc
"""

        prompt = f"""{context}

{syntax_guide}

-- ========== 任务 {task.id}: {task.name} ==========

{task.description}

请证明这个定理。你可以使用种子库中的所有定义和之前证明的定理。

提示：
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
-- ========== 上一次尝试的错误 ==========

错误信息（JSON格式）：
```json
{previous_error}
```

**JSON字段说明**：
- `error_type`: 错误类型（通常是 "tactic_failed"，表示策略失败）
- `line`: **出错的具体行号**（告诉你哪一行的证明策略失败了）
- `column`: 出错的列号（定位到具体位置）
- `context_and_goal`: **最关键的信息！**包含：
  * 当前的变量和假设（类型上下文）
  * "⊢" 符号（表示"需要证明"）
  * **待证明的目标**（这是你需要证明的表达式）

**如何使用错误信息修正证明**：
1. **定位错误行**：查看 `line` 和 `column`，找到是哪一行的策略失败了
2. **理解当前目标**：查看 `context_and_goal` 中 "⊢" 后面的表达式，这是当前需要证明的目标
3. **检查可用假设**：查看 "⊢" 前面的内容，这些是你可以使用的变量和假设
4. **选择正确策略**：
   - 如果目标是代数等式 → 试试 `ring` 或 `field_simp`
   - 如果需要展开定义 → 使用 `unfold`
   - 如果需要重写 → 使用 `rw`
   - 如果需要引入变量 → 使用 `intro`
   - 如果是线性不等式 → 试试 `linarith`

**常见错误模式**：
- "tactic 'ring' failed" → 可能需要先 `unfold` 展开定义
- "unsolved goals" → 证明不完整，需要继续添加策略
- "type mismatch" → 类型不匹配，检查函数定义的返回类型

请根据错误信息修正证明。只输出修正后的 Lean 代码。
"""
        elif attempt_num > 1:
            prompt += f"\n(这是第 {attempt_num} 次尝试，请改进证明策略)\n"

        prompt += "\n请只输出 Lean 定理证明代码，可以用 ```lean 代码块包裹。\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """执行单个任务"""
        print(f"\n{'='*60}")
        print(f"任务 {task.id}: {task.name}")
        print(f"{'='*60}\n")

        self.log(f"\n## 任务 {task.id}: {task.name}\n")
        self.log(f"**任务类型**: {task.task_type}\n")
        self.log(f"**描述**: {task.description}\n")

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"尝试 {attempt_num}/{max_attempts}...")
            self.log(f"\n### 尝试 {attempt_num}\n")

            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # 调用 API
                max_api_retries = 3
                api_retry_delay = 10

                for api_attempt in range(max_api_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=4096
                        )
                        break
                    except Exception as api_error:
                        error_str = str(api_error)
                        if "429" in error_str or "rate_limit" in error_str:
                            if api_attempt < max_api_retries - 1:
                                print(f"⚠️  API速率限制，等待{api_retry_delay}秒...")
                                time.sleep(api_retry_delay)
                                api_retry_delay *= 2
                                continue
                            else:
                                raise
                        else:
                            raise

                # 处理响应格式
                if isinstance(response, str):
                    # 如果返回的是字符串，尝试解析JSON
                    try:
                        response = json.loads(response)
                    except:
                        # 如果不是JSON，直接当作内容使用
                        agent_output = response
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
                else:
                    # 正常的对象格式
                    agent_output = response.choices[0].message.content
                    prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                    completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                    total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                elapsed = time.time() - start_time

                print(f"\n⏱️  耗时: {elapsed:.2f}秒")
                print(f"🔢 Tokens: {total_tokens}")

                self.log(f"**耗时**: {elapsed:.2f}秒\n")
                self.log(f"**Tokens**: {total_tokens}\n")

                # 提取 Lean 代码
                extracted_code = self.validator.extract_lean_code(agent_output)
                last_code = extracted_code
                print(f"\n代码：\n{extracted_code}\n")
                self.log(f"**代码**:\n```lean\n{extracted_code}\n```\n")

                # 自动验证
                print("🤖 自动验证中...")
                is_valid, compiler_output, raw_json_resp = self.validator.validate(
                    extracted_code,
                    self.get_library_context()
                )

                # 原始输出用于日志
                print(compiler_output)
                self.log(f"**验证结果**: {compiler_output}\n")

                # 格式化错误信息用于下次尝试（传入JSON）
                formatted_error = self._format_lean_error_to_json(
                    success=is_valid,
                    raw_json_resp=raw_json_resp,
                    text_output=compiler_output
                )

                # 记录尝试（保存原始完整错误JSON）
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,
                    success=(is_valid is True),
                    error_type="C" if is_valid is False else None,
                    compiler_output=json.dumps(raw_json_resp, ensure_ascii=False) if raw_json_resp else compiler_output,  # 保存JSON
                    timestamp=datetime.now().isoformat(),
                    time_elapsed=elapsed,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
                self.attempts.append(attempt)
                self.save_attempts()

                if is_valid:
                    print(f"✅ 任务 {task.id} 成功！\n")
                    self.log(f"✅ **任务成功**\n")

                    self.state["theorems"].append(extracted_code)
                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    self.save_library()
                    return True
                else:
                    print(f"❌ 验证失败，准备下一次尝试...\n")
                    previous_error = formatted_error  # 使用格式化后的错误
                    print(f"❌ 验证失败，准备下一次尝试...\n")
                    previous_error = compiler_output

            except Exception as e:
                print(f"❌ 出错: {e}\n")
                self.log(f"❌ **错误**: {e}\n")
                previous_error = str(e)

        print(f"❌ 任务 {task.id} 失败（已达最大尝试次数）\n")
        self.log(f"❌ **任务失败**\n")
        return False

    def _format_lean_error_to_json(self, success: bool, raw_json_resp: Dict[str, Any],
                                    text_output: str) -> str:
        """将Lean错误格式化为JSON"""
        if success:
            return "✅ 编译通过"

        if not raw_json_resp or "messages" not in raw_json_resp:
            # 没有JSON或无messages，返回文本
            return text_output

        # 提取第一个error消息
        for msg in raw_json_resp.get("messages", []):
            if isinstance(msg, dict) and msg.get("severity") == "error":
                pos = msg.get("pos") or {}
                data = msg.get("data") or ""

                # 构建JSON格式
                error_json = {
                    "error_type": "tactic_failed",  # 简化分类
                    "line": pos.get("line", "?"),
                    "column": pos.get("column", "?"),
                    "context_and_goal": data.strip()  # 保持多行文本（包含类型标注+目标）
                }

                return json.dumps(error_json, ensure_ascii=False, indent=2)

        # 没有找到error消息，返回原文本
        return text_output

    def get_library_context(self) -> str:
        """完整库上下文"""
        context = self.seed + "\n\n"
        if self.state["theorems"]:
            context += "-- 已证明的定理\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def run_all(self, max_tasks=None):
        """运行所有任务"""
        self.start_time = time.time()

        tasks_to_run = LEAN_TASKS[:max_tasks] if max_tasks else LEAN_TASKS
        print(f"🚀 开始运行 {len(tasks_to_run)} 个 theorem 任务\n")

        success_count = 0
        for task in tasks_to_run:
            if task.id in self.state["completed_tasks"]:
                print(f"⏭️  任务 {task.id} 已完成，跳过")
                success_count += 1
                continue

            if self.execute_task(task):
                success_count += 1

        self.total_time = time.time() - self.start_time

        # 输出总结
        print(f"\n{'='*60}")
        print("实验完成总结")
        print(f"{'='*60}")
        print(f"总任务数: {len(tasks_to_run)}")
        print(f"✅ 成功: {success_count}")
        print(f"❌ 失败: {len(tasks_to_run) - success_count}")
        print(f"总耗时: {self.total_time/60:.1f} 分钟")

        # 统计 sorry 和 axiom 使用情况
        sorry_count = 0
        axiom_count = 0
        for thm in self.state["theorems"]:
            if "sorry" in thm:
                sorry_count += 1
            if thm.strip().startswith("axiom "):
                axiom_count += 1

        if sorry_count > 0 or axiom_count > 0:
            print(f"🧾 未完成证明统计:")
            if sorry_count > 0:
                print(f"   - sorry 占位符: {sorry_count} 个")
            if axiom_count > 0:
                print(f"   - axiom 声明: {axiom_count} 个")

        self.save_library()

# ========================================
# 主程序
# ========================================

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Lean Theorem自动证明系统')
    parser.add_argument('--verbosity', type=str, default='full',
                        choices=['minimal', 'medium', 'no_recursive', 'full'],
                        help='错误信息详细程度')
    parser.add_argument('--output-suffix', type=str, default='',
                        help='输出目录后缀（用于消融实验分组）')
    parser.add_argument('--seed-lib', type=str, default=None,
                        help='种子库文件路径（默认使用LeanGeo/library_final.lean）')
    parser.add_argument('--max-tasks', type=int, default=None,
                        help='最大任务数（用于测试）')

    args = parser.parse_args()

    # 加载API配置
    script_dir = Path(__file__).resolve().parent.parent
    config_file = script_dir / "config" / "api_config.json"

    if not config_file.exists():
        print(f"❌ API配置文件不存在: {config_file}")
        print(f"请复制 config/api_config.example.json 为 config/api_config.json 并填入你的API密钥")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    API_KEY = config.get("api_key")
    BASE_URL = config.get("base_url", "https://api.openai.com/v1")
    MODEL = config.get("model", "gpt-4")

    if not API_KEY or API_KEY == "your-api-key-here":
        print(f"❌ 请在 {config_file} 中配置你的API密钥")
        sys.exit(1)

    # 输出目录
    if args.output_suffix:
        output_dir = script_dir / "lean_ablation" / f"group_{args.output_suffix}" / "theorems_only"
    else:
        output_dir = script_dir / "lean_auto_validated_250tasks" / "theorems_only"

    # 种子库路径
    seed_lib_path = Path(args.seed_lib) if args.seed_lib else None

    # 创建实验
    experiment = LeanTheoremExperiment(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
        base_output_dir=output_dir,
        verbosity=args.verbosity,
        seed_lib_path=seed_lib_path
    )

    # 设置日志捕获（同时输出到终端和文件）
    console_log = experiment.output_dir / "experiment.log"
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Tee类：同时输出到控制台和文件
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, data):
            for f in self.files:
                f.write(data)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    log_file = open(console_log, 'w', encoding='utf-8', buffering=1)

    # 重定向输出
    sys.stdout = Tee(original_stdout, log_file)
    sys.stderr = Tee(original_stderr, log_file)

    try:
        # 运行实验
        if args.max_tasks:
            print(f"🎯 限制运行前 {args.max_tasks} 个任务")
        experiment.run_all(max_tasks=args.max_tasks)
    finally:
        # 恢复原始输出
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()

