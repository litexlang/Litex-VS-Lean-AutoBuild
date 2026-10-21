#!/usr/bin/env python3
"""
带自动验证的 LitexGeo 实验
使用 golitex 编译器自动验证，并将错误反馈给 Agent
"""

import os
import json
import subprocess
import tempfile
import re
import sys
from openai import OpenAI
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time

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
# LitexGeo 任务定义（同之前）
# ========================================

# 生成 250 个任务的Python代码


# 从geo.lit提取的165个theorem
LITEX_TASKS = [
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

# 总计: 165 个theorem
# 分为 17 个stage

# ========================================
# golitex 验证器（持久 session + try）
# ========================================

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from litex_session import SessionBackedValidator

# 兼容旧名
GolitexValidator = SessionBackedValidator

# ========================================
# LitexGeo 实验管理器（带自动验证）
# ========================================

class LitexExperimentWithValidation:
    """带自动验证的 LitexGeo 实验"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        # 创建带时间戳的子文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 实验输出目录: {self.output_dir}")

        # 日志文件
        self.log_file = self.output_dir / "experiment_log.md"
        self.init_log()

        # 加载种子文件
        seed_file = Path(__file__).parent.parent / "database" / "theorem_library_seed.lit"
        if not seed_file.exists():
            raise FileNotFoundError(
                f"种子文件不存在: {seed_file}\n"
                f"请确保 database/theorem_library_seed.lit 文件存在"
            )
        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

        # 库状态
        self.state = {
            "definitions": [],
            "theorems": [],
            "axioms": [],
            "completed_tasks": []
        }

        self.attempts = []
        self.start_time = None
        self.total_time = 0

        # 初始化验证器（持久 session：seed 只 load 一次）
        self.validator = GolitexValidator(self.seed)

    def init_log(self):
        """初始化日志文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"""# LitexGeo 实验日志

实验时间：{timestamp}
模型：{self.model}

---

""")

    def log(self, message: str):
        """追加日志"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def get_seed_prompt_blurb(self) -> str:
        """提示词用的薄种子说明：告诉 agent 已有什么，禁止重复定义。"""
        return (
            "# ========== 种子库（已在验证环境中加载，禁止重复定义）==========\n"
            "# 已有：points、vec、dot、det。下面仅供阅读参考，不要再次 have fn。\n\n"
            + self.seed.strip()
            + "\n"
        )

    def get_agent_library_prompt(self) -> str:
        """提示词里的「当前库」：只有本实验 agent 新写出的定义/定理，不含种子正文堆叠。"""
        parts = []
        if self.state["definitions"]:
            parts.append("# 本实验已定义的概念\n" + "\n".join(self.state["definitions"]))
        if self.state["theorems"]:
            parts.append("# 本实验已证明的定理\n" + "\n".join(self.state["theorems"]))
        if not parts:
            return "# （尚无本实验新增定义/定理）\n"
        return "\n\n".join(parts) + "\n"

    def get_library_context(self) -> str:
        """完整库文件导出用：种子 + 累积产物。"""
        context = self.seed + "\n\n"
        if self.state["definitions"]:
            context += "# 已定义的概念\n" + "\n".join(self.state["definitions"]) + "\n\n"
        if self.state["theorems"]:
            context += "# 已证明的定理\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """构建任务提示（包含上次的错误反馈）"""
        # 薄种子提示 + 仅 agent 累积产物（不把种子当「待追加库」反复堆在最前）
        context = self.get_seed_prompt_blurb()
        context += "\n# ========== 当前实验库状态（agent 新增）==========\n\n"
        context += self.get_agent_library_prompt()

        # 读取短指南
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "litex_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            # 后备的简化版本
            syntax_guide = """
# LiteX 语法参考

1. 函数定义：have fn name(arg Type) ReturnType = expression
2. 谓词定义：prop name(arg Type): conditions
3. 定理证明：thm name: prove: forall ... => conclusion; proof_body
"""

        prompt = f"""{context}

{syntax_guide}

# ========== 任务 {task.id}: {task.name} ==========

{task.description}

重要：种子库里的 vec / dot / det / points 已存在。若任务是「定义」它们，请输出一行注释说明已在种子库中定义，不要再次 have fn。

提示：
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
# ========== 上一次尝试的错误 ==========

{previous_error}

请根据错误信息和短指南修正你的代码。只输出修正后的 LiteX 代码。
"""
        elif attempt_num > 1:
            prompt += f"\n(这是第 {attempt_num} 次尝试，请参考短指南改进你的答案)\n"

        prompt += "\n请只输出 LiteX 代码，可以用 ```litex 代码块包裹。\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """执行单个任务（自动验证 + 反馈循环）"""
        print(f"\n{'='*60}")
        print(f"任务 {task.id}: {task.name}")
        print(f"{'='*60}\n")

        # 记录任务开始
        self.log(f"\n## 任务 {task.id}: {task.name}\n")
        self.log(f"**任务类型**: {task.task_type}\n")
        self.log(f"**描述**: {task.description}\n")

        # 注释掉旧的seed_skip逻辑 - 现在我们做的是theorem任务，不是重复定义
        # seed_skip = {
        #     "1.1": ("vec", "# vec 已在种子库 litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit 中定义，无需重复定义"),
        #     "1.2": ("dot", "# dot 已在种子库 litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit 中定义，无需重复定义"),
        #     "1.3": ("det", "# det 已在种子库 litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit 中定义，无需重复定义"),
        # }
        # if task.id in seed_skip:
        #     _name, note = seed_skip[task.id]
        #     print(f"⏭️  种子库已有 {_name}，跳过重复定义。\n")
        #     self.log(f"**跳过**: 种子库已有 `{_name}`\n\n```litex\n{note}\n```\n")
        #     self.state["definitions"].append(note)
        #     self.state["completed_tasks"].append(task.id)
        #     self.save_state()
        #     return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"尝试 {attempt_num}/{max_attempts}...")
            self.log(f"\n### 尝试 {attempt_num}\n")

            # 构建 prompt（包含上次错误）
            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # 调用 Agent
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096
                )

                agent_output = response.choices[0].message.content
                elapsed = time.time() - start_time

                # 提取 token
                prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                print(f"\n⏱️  耗时: {elapsed:.2f}秒")
                print(f"🔢 Tokens: {total_tokens} (输入: {prompt_tokens}, 输出: {completion_tokens})")

                # 记录到日志
                self.log(f"**耗时**: {elapsed:.2f}秒")
                self.log(f"**Tokens**: {total_tokens} (输入: {prompt_tokens}, 输出: {completion_tokens})\n")

                # 提取并只输出一次代码（不再分 Agent 输出 / 提取的代码）
                extracted_code = self.validator.extract_litex_code(agent_output)
                last_code = extracted_code
                print(f"\n代码：\n{extracted_code}\n")
                self.log(f"**代码**:\n```litex\n{extracted_code}\n```\n")

                # 自动验证
                print("🤖 自动验证中...")
                is_valid, compiler_output = self.validator.validate(
                    extracted_code,
                    self.get_library_context()
                )

                print(compiler_output)
                self.log(f"**验证结果**: {compiler_output}\n")

                # 记录尝试
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,  # 保存提取后的代码
                    success=(is_valid is True),
                    error_type="C" if is_valid is False else None,
                    compiler_output=compiler_output,
                    timestamp=datetime.now().isoformat(),
                    time_elapsed=elapsed,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
                self.attempts.append(attempt)

                if is_valid is True:
                    # 编译通过，自动接受
                    print(f"\n✅ 任务 {task.id} 完成（编译器验证通过）！\n")
                    self.log(f"\n✅ **任务完成！**\n")

                    if task.task_type == "definition":
                        self.state["definitions"].append(extracted_code)
                    else:
                        self.state["theorems"].append(extracted_code)

                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    return True

                elif is_valid is False:
                    # 编译失败，将错误反馈给 Agent
                    print(f"\n❌ 编译失败，将错误反馈给 Agent，尝试修正...\n")
                    self.log(f"\n❌ **编译失败，继续尝试...**\n")

                    # 直接使用编译器的原始错误输出
                    previous_error = compiler_output
                    continue

                else:
                    # 验证器不可用，人工验证
                    print("\n⚠️  自动验证不可用，需要人工验证")
                    print("接受(y) / 拒绝(n) / 重试(r):")
                    user_input = input().strip().lower()

                    if user_input == 'y':
                        print(f"\n✅ 任务 {task.id} 完成！\n")

                        if task.task_type == "definition":
                            self.state["definitions"].append(agent_output)
                        else:
                            self.state["theorems"].append(agent_output)

                        self.state["completed_tasks"].append(task.id)
                        self.save_state()
                        return True
                    else:
                        feedback = input("请提供反馈: ")
                        previous_error = feedback
                        continue

            except Exception as e:
                print(f"❌ 发生异常: {e}")
                import traceback
                traceback.print_exc()
                print(f"继续第 {attempt_num + 1} 次尝试...")
                continue

        print(f"\n❌ 任务 {task.id} 在 {max_attempts} 次尝试后失败。")
        # 证不出则 axiom 顶上，避免下游 by thm 断链
        if last_code and task.task_type == "theorem" and self.validator.litex_bin:
            ax_ok, ax_msg, axiom_code = self.validator.commit_axiom_fallback(last_code)
            print(ax_msg)
            self.log(f"**axiom 回退**:\n```litex\n{axiom_code or ''}\n```\n{ax_msg}\n")
            if ax_ok and axiom_code:
                self.state.setdefault("axioms", []).append(axiom_code)
                self.state["theorems"].append(axiom_code)
                self.save_state()
        return False

    def run_all(self, max_tasks=None):
        """运行所有任务

        Args:
            max_tasks: 限制运行的任务数量，None表示运行全部
        """
        # 设置日志重定向到运行目录下的 experiment.log
        console_log = self.output_dir / "experiment.log"
        log_file = open(console_log, 'w', encoding='utf-8', buffering=1)

        # 保存原始的 stdout 和 stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # 创建 Tee 类来同时输出到控制台和文件
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

        # 重定向输出（同时输出到控制台和文件）
        sys.stdout = Tee(original_stdout, log_file)
        sys.stderr = Tee(original_stderr, log_file)

        try:
            print("\n" + "="*60)
            print("LitexGeo 几何库构建实验（自动验证）")
            print("="*60)
            print(f"模型: {self.model}")
            print(f"验证器: {'litex session ✅' if self.validator.litex_bin else '人工验证'}")
            print(f"输出目录: {self.output_dir}")
            print(f"控制台日志: {console_log}")
            if max_tasks:
                print(f"🎯 限制任务数: 前 {max_tasks} 个")
            print("="*60)

            self.start_time = time.time()

            # 统计成功和失败的任务
            completed_tasks = []
            failed_tasks = []

            # 选择要运行的任务
            tasks_to_run = LITEX_TASKS[:max_tasks] if max_tasks else LITEX_TASKS
            total_tasks = len(tasks_to_run)

            for task in tasks_to_run:
                success = self.execute_task(task)
                if success:
                    completed_tasks.append(task.id)
                else:
                    failed_tasks.append(task.id)
                    print(f"\n⚠️  任务 {task.id} 失败，继续下一个任务...\n")

            # 打印总结
            print("\n" + "="*60)
            print("实验完成总结")
            print("="*60)
            print(f"✅ 成功: {len(completed_tasks)}/{total_tasks} 个任务")
            print(f"❌ 失败: {len(failed_tasks)}/{total_tasks} 个任务")

            if completed_tasks:
                print(f"\n成功的任务: {', '.join(completed_tasks)}")
            if failed_tasks:
                print(f"\n失败的任务: {', '.join(failed_tasks)}")

            # 添加总耗时和总token统计
            total_time = time.time() - self.start_time
            print(f"\n⏱️  总耗时: {total_time/60:.1f} 分钟")

            # 统计总token数
            total_tokens_used = sum(a.total_tokens for a in self.attempts)
            print(f"🔢 总 Tokens: {total_tokens_used}")

            print("="*60)

            self.total_time = time.time() - self.start_time
            self.generate_report()
            # 跑完先导出 session 整库（在 close session 之前）
            self.export_final_library()

        finally:
            # 恢复原始输出
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            log_file.close()
            try:
                self.validator.close()
            except Exception:
                pass
            print(f"\n✅ 实验完成，日志已保存到: {console_log}")

    def export_final_library(self):
        """把 session 里得到的整库落盘，方便事后改 axiom。"""
        self.save_state()

        # 以 session 提交顺序为准的完整库
        if hasattr(self.validator, "export_session_library"):
            lib_text = self.validator.export_session_library(self.seed)
        else:
            lib_text = self.get_library_context()

        library_path = self.output_dir / "library_final.lit"
        library_path.write_text(lib_text, encoding="utf-8")

        axioms = list(getattr(self.validator, "axioms", None) or self.state.get("axioms") or [])
        debt_lines = [
            "# LitexGeo 信任债（axiom）清单",
            "",
            f"共 {len(axioms)} 条。把对应 `axiom` 改回 `thm` 并补证明即可还债。",
            "",
        ]
        for i, ax in enumerate(axioms, 1):
            debt_lines.append(f"## {i}")
            debt_lines.append("")
            debt_lines.append("```litex")
            debt_lines.append(ax.rstrip())
            debt_lines.append("```")
            debt_lines.append("")
        debt_path = self.output_dir / "axioms_debt.md"
        debt_path.write_text("\n".join(debt_lines), encoding="utf-8")

        print(f"\n📦 已导出 session 整库: {library_path}")
        print(f"🧾 axiom 债务清单: {debt_path}（{len(axioms)} 条）")

    def save_state(self):
        """保存当前状态"""
        with open(self.output_dir / "state.json", "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

        with open(self.output_dir / "attempts.json", "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in self.attempts], f, ensure_ascii=False, indent=2)

    def generate_report(self):
        """生成报告（同之前）"""
        # ... 省略，与之前相同
        pass

# ========================================
# 主函数
# ========================================

def main():
    import sys

    # 加载API配置
    script_dir = Path(__file__).resolve().parent.parent
    config_file = script_dir / "config" / "api_config.json"

    if not config_file.exists():
        print(f"❌ API配置文件不存在: {config_file}")
        print(f"请复制 config/api_config.example.json 为 config/api_config.json 并填入你的API密钥")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    api_key = config.get("api_key")
    base_url = config.get("base_url", "https://api.openai.com/v1")
    model = config.get("model", "gpt-4")

    if not api_key or api_key == "your-api-key-here":
        print(f"❌ 请在 {config_file} 中配置你的API密钥")
        sys.exit(1)

    # 使用脚本所在目录下的 theorems_only 子目录
    output_dir = script_dir / "litex_auto_validated_250tasks" / "theorems_only"

    # 检查命令行参数：限制任务数量
    max_tasks = None
    if len(sys.argv) > 1:
        try:
            max_tasks = int(sys.argv[1])
            print(f"🎯 限制运行前 {max_tasks} 个任务")
        except ValueError:
            print(f"❌ 参数错误: {sys.argv[1]} 不是有效数字")
            sys.exit(1)

    experiment = LitexExperimentWithValidation(api_key, base_url, model, output_dir)
    experiment.run_all(max_tasks=max_tasks)

if __name__ == "__main__":
    main()
