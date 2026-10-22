#!/usr/bin/env python3
"""
LitexGeo experiment with automatic validation
Uses golitex compiler for automatic validation and error feedback to Agent
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
# Data Structures
# ========================================

@dataclass
class Task:
    """Single task"""
    id: str
    stage: int
    name: str
    description: str
    task_type: str
    hints: List[str]

@dataclass
class TaskAttempt:
    """Single attempt record"""
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
# LitexGeo task definitions (same as before)
# ========================================

# Python code to generate 250 tasks


# 165 theorems extracted from geo.lit
LITEX_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="Prove distance_sq_coordinate_formula theorem",
        description="Expand distance_sq(a, b) into (Δx)^2 + (Δy)^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="Prove distance_sq_nonnegative theorem",
        description="Squared distance is always nonnegative.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="Prove distance_sq_symmetric theorem",
        description="distance_sq(a, b) = distance_sq(b, a).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.4",
        stage=1,
        name="Prove vec_dot_self_is_distance theorem",
        description="dot(vec(a, b), vec(a, b)) equals distance_sq(a, b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.5",
        stage=1,
        name="Prove distance_equality_to_dot theorem",
        description="Equal distances imply a related dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.6",
        stage=1,
        name="Prove point_difference_norm_pos theorem",
        description="Distinct points give strictly positive squared difference.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.7",
        stage=1,
        name="Prove distance_sq_translate theorem",
        description="Translating both endpoints preserves distance_sq.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.8",
        stage=1,
        name="Prove distance_sq_positive_of_ne theorem",
        description="a != b implies distance_sq(a, b) > 0.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.9",
        stage=1,
        name="Prove translated_difference_square theorem",
        description="Expand a translated coordinate difference squared.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="1.10",
        stage=1,
        name="Prove center_offset_square theorem",
        description="Squared offset from a center expands by bilinearity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.1",
        stage=2,
        name="Prove affine_combination_distance_sq theorem",
        description="Squared distance along an affine combination (p = (1-t)a + t b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.2",
        stage=2,
        name="Prove inner_product_distance_identity theorem",
        description="Relate a dot product to a combination of distance_sq terms.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.3",
        stage=2,
        name="Prove distance_expansion_identity theorem",
        description="Expand |u-v|^2 via |u|^2 + |v|^2 - 2 u·v style identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.4",
        stage=2,
        name="Prove affine_distance_from_parameter theorem",
        description="Predicate form: distance_sq symmetry.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.5",
        stage=2,
        name="Prove twice_dot_from_distances_direct theorem",
        description="Solve for 2 u·v from three distance_sq values.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.6",
        stage=2,
        name="Prove vec_coordinate_formula theorem",
        description="Unfold vec(a, b) to coordinate differences.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.7",
        stage=2,
        name="Prove dot_coordinate_formula theorem",
        description="Unfold dot(u, v) to the coordinate formula.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.8",
        stage=2,
        name="Prove det_coordinate_formula theorem",
        description="Unfold det(u, v) to the coordinate formula.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.9",
        stage=2,
        name="Prove dot_symmetric theorem",
        description="Dot product is symmetric: u·v = v·u.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="2.10",
        stage=2,
        name="Prove dot_commutative theorem",
        description="Dot product is commutative (same as symmetry).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.1",
        stage=3,
        name="Prove dot_add_left theorem",
        description="Dot is additive in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.2",
        stage=3,
        name="Prove dot_add_right theorem",
        description="Dot is additive in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.3",
        stage=3,
        name="Prove dot_square_sum theorem",
        description="Expand |u+v|^2 = |u|^2 + |v|^2 + 2 u·v.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.4",
        stage=3,
        name="Prove det_antisymmetric theorem",
        description="det(u, v) = -det(v, u).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.5",
        stage=3,
        name="Prove vec_add_path_x theorem",
        description="x-component of chained vectors adds.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.6",
        stage=3,
        name="Prove vec_add_path_y theorem",
        description="y-component of chained vectors adds.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.7",
        stage=3,
        name="Prove dot_from_cosine_law theorem",
        description="Recover a dot product from the law of cosines.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.8",
        stage=3,
        name="Prove vec_add theorem",
        description="Vector addition along a path: vec(a,b) + vec(b,c) = vec(a,c).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.9",
        stage=3,
        name="Prove vec_neg theorem",
        description="vec(b, a) = -vec(a, b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="3.10",
        stage=3,
        name="Prove dot_bilinear_expand theorem",
        description="Expand a bilinear combination of dots.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.1",
        stage=4,
        name="Prove dot_det_eliminate theorem",
        description="Eliminate mixed dot/det terms in a polynomial identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.2",
        stage=4,
        name="Prove dot_neg_left theorem",
        description="dot(-u, v) = -dot(u, v).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.3",
        stage=4,
        name="Prove det_neg_left theorem",
        description="det(-u, v) = -det(u, v).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.4",
        stage=4,
        name="Prove det_change_base theorem",
        description="Change-of-base formula for det.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.5",
        stage=4,
        name="Prove dot_change_base theorem",
        description="Change-of-base formula for dot.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.6",
        stage=4,
        name="Prove det_bilinear_right theorem",
        description="Det is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.7",
        stage=4,
        name="Prove dot_bilinear_right theorem",
        description="Dot is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.8",
        stage=4,
        name="Prove dot_scale_right theorem",
        description="Dot scales in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.9",
        stage=4,
        name="Prove det_scale_right theorem",
        description="Det scales in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="4.10",
        stage=4,
        name="Prove dot_squared_plus_det_squared theorem",
        description="|u|^2|v|^2 = (u·v)^2 + det(u,v)^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.1",
        stage=5,
        name="Prove dot_two_scale theorem",
        description="Predicate form of recovering dot from the cosine law.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.2",
        stage=5,
        name="Prove dot_sub_right_coordinate theorem",
        description="Coordinate form of dot(u, v-w).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.3",
        stage=5,
        name="Prove dot_scale_left theorem",
        description="Dot scales in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.4",
        stage=5,
        name="Prove dot_linear_left theorem",
        description="Dot is linear in the left argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.5",
        stage=5,
        name="Prove dot_linear_right theorem",
        description="Dot is linear in the right argument.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.6",
        stage=5,
        name="Prove collinear_det_expand theorem",
        description="Expand the collinearity det condition in coordinates.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.7",
        stage=5,
        name="Prove perpendicular_dot_expand theorem",
        description="Expand the perpendicularity dot condition in coordinates.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.8",
        stage=5,
        name="Prove collinear_symmetric theorem",
        description="Collinearity is symmetric in the three points (reorderings).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.9",
        stage=5,
        name="Prove collinear_midpoint theorem",
        description="The midpoint lies on the line through distinct endpoints (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="5.10",
        stage=5,
        name="Prove collinear_to_standard_det theorem",
        description="Normalize a collinearity statement to a standard det form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.1",
        stage=6,
        name="Prove collinear_equidistant_implies_midpoint theorem",
        description="Collinear and equidistant implies midpoint.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.2",
        stage=6,
        name="Prove parallelogram_diagonals theorem",
        description="Parallelogram diagonal vector/length identities.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.3",
        stage=6,
        name="Prove collinear_third theorem",
        description="Two collinear pairs sharing a side imply a third collinearity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.4",
        stage=6,
        name="Prove parallelogram_sides theorem",
        description="Opposite sides of a parallelogram are equal (vector form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.5",
        stage=6,
        name="Prove perpendicular_symmetric theorem",
        description="Perpendicularity of segments is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.6",
        stage=6,
        name="Prove parallel_symmetric theorem",
        description="Parallelism of segments is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.7",
        stage=6,
        name="Prove perpendicular_from_parallel theorem",
        description="A line perpendicular to one of two parallels is perpendicular to the other.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.8",
        stage=6,
        name="Prove equidistant_perp_bisector theorem",
        description="Equidistant points lie on the perpendicular bisector.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.9",
        stage=6,
        name="Prove parallelogram_diagonal_sum theorem",
        description="Sum of squared diagonals equals sum of squared sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="6.10",
        stage=6,
        name="Prove collinear_implies_midpoint_distance theorem",
        description="Collinearity implies a midpoint distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.1",
        stage=7,
        name="Prove equidistant_implies_perp_bisector_dot theorem",
        description="Equidistance implies the perp-bisector dot condition.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.2",
        stage=7,
        name="Prove parallel_implies_det_zero theorem",
        description="Parallel segments have det of direction vectors zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.3",
        stage=7,
        name="Prove parallelogram_midpoint_diagonals theorem",
        description="Diagonals of a parallelogram bisect each other.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.4",
        stage=7,
        name="Prove perp_dot_zero_coordinate theorem",
        description="Coordinate form of perpendicular => dot zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.5",
        stage=7,
        name="Prove perpendicular_implies_distance_sum theorem",
        description="Right angle gives the Pythagorean distance sum identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.6",
        stage=7,
        name="Prove perpendicular_bisector_property theorem",
        description="Predicate form of collinearity symmetry.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.7",
        stage=7,
        name="Prove perpendicular_bisector_equidistant_sq theorem",
        description="Points on the perp bisector are equidistant (squared).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.8",
        stage=7,
        name="Prove perpendicular_from_dot_zero theorem",
        description="dot = 0 of direction vectors implies perpendicular segments.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.9",
        stage=7,
        name="Prove parallelogram_coordinate_difference theorem",
        description="Coordinate difference form of a parallelogram.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="7.10",
        stage=7,
        name="Prove perpendicular_bisector_equidistant theorem",
        description="Perp bisector points are equidistant (predicate style).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.1",
        stage=8,
        name="Prove collinear_coordinates_imply_affine_parameter theorem",
        description="Place a test point on a line at a prescribed distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.2",
        stage=8,
        name="Prove on_line_implies_affine_parameter theorem",
        description="Membership on line_through_points gives an affine parameter (a != b, matching is_on_line).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.3",
        stage=8,
        name="Prove right_angle_vertex_distinct_from_foot_on_opposite_line theorem",
        description="In a right triangle, the right vertex is not the foot on the opposite side (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.4",
        stage=8,
        name="Prove right_angle_vertex_not_on_opposite_line theorem",
        description="The right-angle vertex does not lie on the opposite side line (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.5",
        stage=8,
        name="Prove right_triangle_foot_midpoints_distinct theorem",
        description="Feet/midpoints arising in a right triangle are distinct as needed (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.6",
        stage=8,
        name="Prove orthocenter_third_altitude theorem",
        description="Two altitudes determine the third: their intersection lies on the remaining altitude.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.7",
        stage=8,
        name="Prove equidistant_dot_half theorem",
        description="Equidistance implies a half-dot projection identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.8",
        stage=8,
        name="Prove segments_congruent_reflexive theorem",
        description="Segment congruence is reflexive.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.9",
        stage=8,
        name="Prove segments_congruent_symmetric theorem",
        description="Segment congruence is symmetric.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="8.10",
        stage=8,
        name="Prove segments_congruent_transitive theorem",
        description="Segment congruence is transitive.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.1",
        stage=9,
        name="Prove segments_congruent_from_distance_sq theorem",
        description="Predicate form of symmetric segment congruence.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.2",
        stage=9,
        name="Prove midpoint_equidistant theorem",
        description="A midpoint of a nondegenerate segment is equidistant from the endpoints (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.3",
        stage=9,
        name="Prove midpoint_half_distance theorem",
        description="Distance from endpoint to midpoint is half the segment (squared: factor 1/4; a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.4",
        stage=9,
        name="Prove one_dimensional_midpoint theorem",
        description="1D midpoint formula and consequences.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.5",
        stage=9,
        name="Prove centroid_distance theorem",
        description="Distance identities involving the centroid.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.6",
        stage=9,
        name="Prove midpoint_segment_ratio theorem",
        description="Midpoint vs affine parameter on a nondegenerate segment (a != b; p = (1-t)a + tb).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.7",
        stage=9,
        name="Prove double_midpoint_equal_sides theorem",
        description="Predicate form of midpoint equidistance.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.8",
        stage=9,
        name="Prove midpoint_coordinate_formula theorem",
        description="Coordinate formula for the midpoint of a nondegenerate segment (a != b).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.9",
        stage=9,
        name="Prove affine_dot_backward theorem",
        description="Backward direction of an affine-parameter dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="9.10",
        stage=9,
        name="Prove affine_dot_forward theorem",
        description="Forward direction of an affine-parameter dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.1",
        stage=10,
        name="Prove orthogonal_midpoint_scalar_finish theorem",
        description="Finish an orthogonal-midpoint computation with a scalar identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.2",
        stage=10,
        name="Prove orthogonal_midpoint_vector_core theorem",
        description="Core vector identity for midpoints of orthogonal segments.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.3",
        stage=10,
        name="Prove solve_cosine_for_dot theorem",
        description="Solve the cosine ratio for the underlying dot product.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.4",
        stage=10,
        name="Prove cosine_law theorem",
        description="Law of cosines: relate side distance_sq values to a dot product.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.5",
        stage=10,
        name="Prove isosceles_base_dot theorem",
        description="In an isosceles triangle, base angles give equal projection dots.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.6",
        stage=10,
        name="Prove angle_equality_cross_ratio theorem",
        description="Equal undirected angles via a cross-multiplied cosine ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.7",
        stage=10,
        name="Prove angle_in_semicircle_coordinate theorem",
        description="Angle in a semicircle, coordinate form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.8",
        stage=10,
        name="Prove isosceles_implies_equal_projections theorem",
        description="Isosceles triangle implies equal projections onto the base.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.9",
        stage=10,
        name="Prove vertical_angles_square_core theorem",
        description="Predicate form of the isosceles base-dot identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="10.10",
        stage=10,
        name="Prove vertical_angles_sign_core theorem",
        description="Same-sign cosine condition for vertical angles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.1",
        stage=11,
        name="Prove vertical_angles_equal theorem",
        description="Vertical angles are congruent (crossing segments ab, cd with a != b, c != d).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.2",
        stage=11,
        name="Prove cosine_square_to_det_square_ratio theorem",
        description="Pass between cos^2 ratios and det^2 ratios.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.3",
        stage=11,
        name="Prove congruent_angle_det_square_ratio theorem",
        description="Congruent angles imply matching det^2 cross ratios (nonzero arms).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.4",
        stage=11,
        name="Prove vertical_angles_dot_equal theorem",
        description="Vertical angles give equal dots of the forming vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.5",
        stage=11,
        name="Prove cross_product_positive_det_product_implies_same_sign theorem",
        description="Positive det products force matching orientation signs.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.6",
        stage=11,
        name="Prove cross_ratio_same_det_sign_implies_angle_congruence theorem",
        description="Matching cos^2 ratio and det sign imply angle congruence.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.7",
        stage=11,
        name="Prove sas_third_side theorem",
        description="SAS: the third side is determined (distance_sq identity).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.8",
        stage=11,
        name="Prove sas_congruence theorem",
        description="SAS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.9",
        stage=11,
        name="Prove sss_congruence theorem",
        description="SSS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="11.10",
        stage=11,
        name="Prove multiply_both_sides theorem",
        description="Algebraic helpers used by the ASA scalar elimination.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.1",
        stage=12,
        name="Prove add_equalities theorem",
        description="Prove the add_equalities theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.2",
        stage=12,
        name="Prove subtract_equalities theorem",
        description="Prove the subtract_equalities theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.3",
        stage=12,
        name="Prove zero_factor_law theorem",
        description="If a product is zero and one factor is nonzero, the other factor is zero.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.4",
        stage=12,
        name="Prove cancel_positive_right_factor theorem",
        description="Cancel a common strictly positive scalar factor.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.5",
        stage=12,
        name="Prove rearrange_sum theorem",
        description="Rearrange a - b - c = 0 into a = b + c.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.6",
        stage=12,
        name="Prove asa_scalar_core theorem",
        description="ASA scalar core identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.7",
        stage=12,
        name="Prove asa_angle_equations_bridge theorem",
        description="Bridge ASA angle equations to side relations.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.8",
        stage=12,
        name="Prove asa_congruence theorem",
        description="ASA congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.9",
        stage=12,
        name="Prove sss_dot_equal theorem",
        description="SSS implies corresponding vertex dots are equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="12.10",
        stage=12,
        name="Prove triangle_area_det theorem",
        description="Signed area of a triangle via det of two sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.1",
        stage=13,
        name="Prove similar_triangles_ratio theorem",
        description="Similar triangles have proportional corresponding sides.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.2",
        stage=13,
        name="Prove similar_triangles_dot theorem",
        description="Similar triangles: corresponding dots scale by the square of the ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.3",
        stage=13,
        name="Prove similar_triangles_det theorem",
        description="Similar triangles: corresponding dets scale by the square of the ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.4",
        stage=13,
        name="Prove aas_scalar_first_side theorem",
        description="Predicate form of sss_dot_equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.5",
        stage=13,
        name="Prove aas_scalar_last_side theorem",
        description="AAS: recover the last unknown side scalar.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.6",
        stage=13,
        name="Prove triangle_det_nonzero theorem",
        description="A nondegenerate triangle has nonzero side-det.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.7",
        stage=13,
        name="Prove triangle_det_square_positive theorem",
        description="Nondegenerate triangle => det^2 > 0.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.8",
        stage=13,
        name="Prove triangle_det_squared_vertex theorem",
        description="Det^2 expressed from a chosen vertex.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.9",
        stage=13,
        name="Prove triangle_congruence_AAStheorem",
        description="AAS congruence of triangles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="13.10",
        stage=13,
        name="Prove strict_triangle_one_side theorem",
        description="Strict triangle inequality helper on one side.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.1",
        stage=14,
        name="Prove triangle_inequality theorem",
        description="Triangle inequality for Euclidean distances.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.2",
        stage=14,
        name="Prove pythagorean_theorem theorem",
        description="Pythagorean theorem in squared-distance form.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.3",
        stage=14,
        name="Prove right_angle_implies_distance_relation theorem",
        description="A right angle implies the Pythagorean distance relation.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.4",
        stage=14,
        name="Prove isosceles_right_triangle_vertex_formula theorem",
        description="Predicate form of the Pythagorean theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.5",
        stage=14,
        name="Prove isosceles_right_hypotenuse_length theorem",
        description="Hypotenuse length of an isosceles right triangle.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.6",
        stage=14,
        name="Prove translated_circle_equation_gives_distance theorem",
        description="A translated circle equation yields equal distances to the center.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.7",
        stage=14,
        name="Prove circumcenter_equidistant theorem",
        description="Predicate: on-circle iff distance_sq equals r^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.8",
        stage=14,
        name="Prove thales_theorem theorem",
        description="Thales' theorem: angle in a semicircle is right.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.9",
        stage=14,
        name="Prove thales_converse theorem",
        description="Converse of Thales' theorem.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="14.10",
        stage=14,
        name="Prove circle_equation_gives_equal_distance theorem",
        description="First Cramer equation for a circle through points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.1",
        stage=15,
        name="Prove common_center_implies_concyclic theorem",
        description="A shared center with equal radii implies concyclic points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.2",
        stage=15,
        name="Prove concyclic_det_criterion_implies_concyclic theorem",
        description="Det criterion implies four points are concyclic.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.3",
        stage=15,
        name="Prove concyclic_det_criterion theorem",
        description="Determinant criterion for four concyclic points.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.4",
        stage=15,
        name="Prove nine_point_center theorem",
        description="Nine-point center coordinate identity.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.5",
        stage=15,
        name="Prove power_of_point_difference theorem",
        description="Power of a point as a difference of products of lengths.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.6",
        stage=15,
        name="Prove circumcenter_equidistant_triple theorem",
        description="Equidistance of the circumcenter from three vertices.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.7",
        stage=15,
        name="Prove concyclic_fourth_point theorem",
        description="Construct/verify a fourth concyclic point.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.8",
        stage=15,
        name="Prove equal_centered_norms_same_chord_coordinate theorem",
        description="Wu-method style quartic identity for a circle configuration.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.9",
        stage=15,
        name="Prove common_center_same_chord_cross_ratio theorem",
        description="Same center and chord length control an angle cross ratio.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="15.10",
        stage=15,
        name="Prove concyclic_same_chord_angles_congruent theorem",
        description="Concyclic points with the same chord have congruent inscribed angles.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.1",
        stage=16,
        name="Prove apollonius_theorem theorem",
        description="Apollonius' theorem for medians (squared form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.2",
        stage=16,
        name="Prove square_orthogonal_parallel_quadrilateral_coordinates theorem",
        description="(-x)^2 = x^2.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.3",
        stage=16,
        name="Prove orthogonal_coordinate_sum_square theorem",
        description="Square of equal.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.4",
        stage=16,
        name="Prove square_diagonal_length theorem",
        description="Square diagonal length.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.5",
        stage=16,
        name="Prove reflection_distance theorem",
        description="Reflection preserves distance to the mirror line setup.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.6",
        stage=16,
        name="Prove rotation_preserves_distance theorem",
        description="Rotation preserves distance.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.7",
        stage=16,
        name="Prove rotation_preserves_dot theorem",
        description="90° rotation preserves dots of corresponding vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.8",
        stage=16,
        name="Prove rotation_preserves_det theorem",
        description="90° rotation preserves dets of corresponding vectors.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.9",
        stage=16,
        name="Prove reflection_equidistant theorem",
        description="A point and its reflection are equidistant from points on the mirror.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="16.10",
        stage=16,
        name="Prove rotated_90_creates_isosceles_righttheorem",
        description="Predicate: clockwise 90° rotation preserves distances.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.1",
        stage=17,
        name="Prove reflected_vec_sum theorem",
        description="Sum identity for a vector and its reflection.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.2",
        stage=17,
        name="Prove stewart_theorem theorem",
        description="Stewart's theorem (squared form).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.3",
        stage=17,
        name="Prove median_length theorem",
        description="Median length formula (squared).",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.4",
        stage=17,
        name="Prove foot_perp_parametric theorem",
        description="Parametric formula for the perpendicular foot.",
        task_type="theorem",
        hints=[]
    ),
    Task(
        id="17.5",
        stage=17,
        name="Prove median_inequality_distance theorem",
        description="Predicate form of the median length formula.",
        task_type="theorem",
        hints=[]
    ),
]

# Total: 165 theorems
# Divided into 17 stages

# ========================================
# golitex validator（persistent session + try）
# ========================================

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
from litex_session import SessionBackedValidator

# Compatible with old name
GolitexValidator = SessionBackedValidator

# ========================================
# LitexGeo experiment manager (with automatic validation)
# ========================================

class LitexExperimentWithValidation:
    """with automatic validation LitexGeo experiment"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        # create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 experiment output directory: {self.output_dir}")

        # log file
        self.log_file = self.output_dir / "experiment_log.md"
        self.init_log()

        # load seed file
        seed_file = Path(__file__).parent.parent / "database" / "theorem_library_seed.lit"
        if not seed_file.exists():
            raise FileNotFoundError(
                f"seed file does not exist: {seed_file}\n"
                f"please ensure database/theorem_library_seed.lit file exists"
            )
        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

        # Library state
        self.state = {
            "definitions": [],
            "theorems": [],
            "axioms": [],
            "completed_tasks": []
        }

        self.attempts = []
        self.start_time = None
        self.total_time = 0

        # initialize validator（persistent session：seed only load once）
        self.validator = GolitexValidator(self.seed)

    def init_log(self):
        """initialize log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"""# LitexGeo experiment log

Experiment time: {timestamp}
Model: {self.model}

---

""")

    def log(self, message: str):
        """append log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def get_seed_prompt_blurb(self) -> str:
        """seed description for prompt：tell agent what already exists，prohibit duplicate definitions。"""
        return (
            "# ========== seed library（already loaded in validation environment，prohibit duplicate definitions）==========\n"
            "# already have：points、vec、dot、det。below for reference only，do not have fn again。\n\n"
            + self.seed.strip()
            + "\n"
        )

    def get_agent_library_prompt(self) -> str:
        """current library in prompt: only newly written by this experiment agent definition/theorem, does not include seed text stacking."""
        parts = []
        if self.state["definitions"]:
            parts.append("# Concepts defined in this experiment\n" + "\n".join(self.state["definitions"]))
        if self.state["theorems"]:
            parts.append("# Theorems proven in this experiment\n" + "\n".join(self.state["theorems"]))
        if not parts:
            return "# (No new additions in this experiment yet)\n"
        return "\n\n".join(parts) + "\n"

    def get_library_context(self) -> str:
        """for complete library file export: seed + accumulated results."""
        context = self.seed + "\n\n"
        if self.state["definitions"]:
            context += "# Defined concepts\n" + "\n".join(self.state["definitions"]) + "\n\n"
        if self.state["theorems"]:
            context += "# Proven theorems\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """build task prompt（includes previous error feedback）"""
        # thin seed prompt + only agent accumulated results（do not repeatedly stack seed as "library to append" at the front）
        context = self.get_seed_prompt_blurb()
        context += "\n# ========== current experiment library state（agent additions）==========\n\n"
        context += self.get_agent_library_prompt()

        # read short guide
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "litex_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            # fallback simplified version
            syntax_guide = """
# LiteX syntax reference

1. function definition：have fn name(arg Type) ReturnType = expression
2. predicate definition：prop name(arg Type): conditions
3. theoremProve ：thm name: prove: forall ... => conclusion; proof_body
"""

        prompt = f"""{context}

{syntax_guide}

# ========== task {task.id}: {task.name} ==========

{task.description}

Important: in seed library vec / dot / det / points already exist。if task is to "define" them，please output a comment stating already defined in seed library，do not have fn again。

Hints:
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
# ========== previous attempt error ==========

{previous_error}

please fix your code based on error information and short guide。only output corrected LiteX code。
"""
        elif attempt_num > 1:
            prompt += f"\n(this is attempt {attempt_num} th attempt，please refer to short guide to improve your answer)\n"

        prompt += "\nplease only output LiteX code, can be wrapped in ```litex code block。\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """execute single task (automatic validation + feedback loop)"""
        print(f"\n{'='*60}")
        print(f"task {task.id}: {task.name}")
        print(f"{'='*60}\n")

        # record task start
        self.log(f"\n## task {task.id}: {task.name}\n")
        self.log(f"**task type**: {task.task_type}\n")
        self.log(f"**Description**: {task.description}\n")

        # comment out old seed_skip logic - now we are doing theorem tasks，not duplicate definitions
        # seed_skip = {
        #     "1.1": ("vec", "# vec already defined in seed library litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit, no need to repeat definition"),
        #     "1.2": ("dot", "# dot already defined in seed library litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit, no need to repeat definition"),
        #     "1.3": ("det", "# det already defined in seed library litex_auto_validated_250tasks/definitions_only/run_20260920_145809/library_final.lit, no need to repeat definition"),
        # }
        # if task.id in seed_skip:
        #     _name, note = seed_skip[task.id]
        #     print(f"⏭️  seed library already has {_name}, skip duplicate definition.\n")
        #     self.log(f"**skip**: seed library already has `{_name}`\n\n```litex\n{note}\n```\n")
        #     self.state["definitions"].append(note)
        #     self.state["completed_tasks"].append(task.id)
        #     self.save_state()
        #     return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"attempt {attempt_num}/{max_attempts}...")
            self.log(f"\n### attempt {attempt_num}\n")

            # build prompt（includes previous error）
            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # call Agent
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4096
                )

                agent_output = response.choices[0].message.content
                elapsed = time.time() - start_time

                # extract tokens
                prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                print(f"\n⏱️  Time elapsed: {elapsed:.2f}s")
                print(f"🔢 Tokens: {total_tokens} (input: {prompt_tokens}, output: {completion_tokens})")

                # record to log
                self.log(f"**Time elapsed**: {elapsed:.2f}s")
                self.log(f"**Tokens**: {total_tokens} (input: {prompt_tokens}, output: {completion_tokens})\n")

                # extract and output code once（no longer split Agent output / extracted code）
                extracted_code = self.validator.extract_litex_code(agent_output)
                last_code = extracted_code
                print(f"\nCode:\n{extracted_code}\n")
                self.log(f"**Code**:\n```litex\n{extracted_code}\n```\n")

                # automatic validation
                print("🤖 Automatic validation in progress...")
                is_valid, compiler_output, raw_result = self.validator.validate(
                    extracted_code,
                    self.get_library_context()
                )

                print(compiler_output)
                self.log(f"**validation result**: {compiler_output}\n")

                # record attempt
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,  # save extracted code
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
                    # compilation passed，automatically accept
                    print(f"\n✅ task {task.id} completed（compiler validation passed）！\n")
                    self.log(f"\n✅ **task completed！**\n")

                    if task.task_type == "definition":
                        self.state["definitions"].append(extracted_code)
                    else:
                        self.state["theorems"].append(extracted_code)

                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    return True

                elif is_valid is False:
                    # compilation failed，provide error feedback to Agent
                    print(f"\n❌ compilation failed，provide error feedback to Agent，attempt to fix...\n")
                    self.log(f"\n❌ **compilation failed，continue attempting...**\n")

                    # directly use compiler raw error output
                    previous_error = compiler_output
                    continue

                else:
                    # validator unavailable, manual validation
                    print("\n⚠️  Automatic validation unavailable, manual validation required")
                    print("Accept(y) / Reject(n) / Retry(r):")
                    user_input = input().strip().lower()

                    if user_input == 'y':
                        print(f"\n✅ task {task.id} completed！\n")

                        if task.task_type == "definition":
                            self.state["definitions"].append(agent_output)
                        else:
                            self.state["theorems"].append(agent_output)

                        self.state["completed_tasks"].append(task.id)
                        self.save_state()
                        return True
                    else:
                        feedback = input("Please provide feedback: ")
                        previous_error = feedback
                        continue

            except Exception as e:
                print(f"❌ exception occurred: {e}")
                import traceback
                traceback.print_exc()
                print(f"continue to attempt {attempt_num + 1} th attempt...")
                continue

        print(f"\n❌ task {task.id} after {max_attempts} attempts failed。")
        # if cannot prove use axiom as fallback，avoid downstream "by thm" breakage
        if last_code and task.task_type == "theorem" and self.validator.litex_bin:
            ax_ok, ax_msg, axiom_code = self.validator.commit_axiom_fallback(last_code)
            print(ax_msg)
            self.log(f"**axiom fallback**:\n```litex\n{axiom_code or ''}\n```\n{ax_msg}\n")
            if ax_ok and axiom_code:
                self.state.setdefault("axioms", []).append(axiom_code)
                self.state["theorems"].append(axiom_code)
                self.save_state()
        return False

    def run_all(self, max_tasks=None):
        """Run all tasks

        Args:
            max_tasks: limit number of tasks to run, None means run all
        """
        # Setup log redirection to experiment.log in run directory
        console_log = self.output_dir / "experiment.log"
        log_file = open(console_log, 'w', encoding='utf-8', buffering=1)

        # save original stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # create Tee class to output to both console and file
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

        # redirect output (output to both console and file)
        sys.stdout = Tee(original_stdout, log_file)
        sys.stderr = Tee(original_stderr, log_file)

        try:
            print("\n" + "="*60)
            print("LitexGeo geometry library construction experiment（automatic validation）")
            print("="*60)
            print(f"Model: {self.model}")
            print(f"Validator: {'litex session ✅' if self.validator.litex_bin else 'manual validation'}")
            print(f"Output directory: {self.output_dir}")
            print(f"Console log: {console_log}")
            if max_tasks:
                print(f"🎯 Limit to first {max_tasks} tasks")
            print("="*60)

            self.start_time = time.time()

            # count successful and failed tasks
            completed_tasks = []
            failed_tasks = []

            # select tasks to run
            tasks_to_run = LITEX_TASKS[:max_tasks] if max_tasks else LITEX_TASKS
            total_tasks = len(tasks_to_run)

            for task in tasks_to_run:
                success = self.execute_task(task)
                if success:
                    completed_tasks.append(task.id)
                else:
                    failed_tasks.append(task.id)
                    print(f"\n⚠️  task {task.id} failed，continue to next task...\n")

            # Print summary
            print("\n" + "="*60)
            print("Experiment Completed Summary")
            print("="*60)
            print(f"✅ Success: {len(completed_tasks)}/{total_tasks} tasks")
            print(f"❌ Failed: {len(failed_tasks)}/{total_tasks} tasks")

            if completed_tasks:
                print(f"\nSuccessful tasks: {', '.join(completed_tasks)}")
            if failed_tasks:
                print(f"\nFailed tasks: {', '.join(failed_tasks)}")

            # Add total time and total token statistics
            total_time = time.time() - self.start_time
            print(f"\n⏱️  Total time: {total_time/60:.1f} minutes")

            # Count total tokens
            total_tokens_used = sum(a.total_tokens for a in self.attempts)
            print(f"🔢 Total tokens: {total_tokens_used}")

            print("="*60)

            self.total_time = time.time() - self.start_time
            self.generate_report()
            # Export complete session library first (before closing session)
            self.export_final_library()

        finally:
            # restore original output
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            log_file.close()
            try:
                self.validator.close()
            except Exception:
                pass
            print(f"\n✅ Experiment completed, log saved to: {console_log}")

    def export_final_library(self):
        """Export complete library from session to disk, convenient for modifying axiom afterwards."""
        self.save_state()

        # Complete library based on session submission order
        if hasattr(self.validator, "export_session_library"):
            lib_text = self.validator.export_session_library(self.seed)
        else:
            lib_text = self.get_library_context()

        library_path = self.output_dir / "library_final.lit"
        library_path.write_text(lib_text, encoding="utf-8")

        axioms = list(getattr(self.validator, "axioms", None) or self.state.get("axioms") or [])
        debt_lines = [
            "# LitexGeo Trust Debt (axiom) List",
            "",
            f"Total {len(axioms)} items. Change corresponding `axiom` back to `thm` and add proof to repay debt.",
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

        print(f"\n📦 Exported session complete library: {library_path}")
        print(f"🧾 axiom debt list: {debt_path}（{len(axioms)}  items)")

    def save_state(self):
        """save current state"""
        with open(self.output_dir / "state.json", "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

        with open(self.output_dir / "attempts.json", "w", encoding="utf-8") as f:
            json.dump([asdict(a) for a in self.attempts], f, ensure_ascii=False, indent=2)

    def generate_report(self):
        """Generate report (same as before)"""
        # ... omitted, same as before
        pass

# ========================================
# main function
# ========================================

def main():
    import sys

    # load API configuration
    script_dir = Path(__file__).resolve().parent.parent
    config_file = script_dir / "config" / "api_config.json"

    if not config_file.exists():
        print(f"❌ API configuration file does not exist: {config_file}")
        print(f"Please copy config/api_config.example.json to config/api_config.json and fill in your API key")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    api_key = config.get("api_key")
    base_url = config.get("base_url", "https://api.openai.com/v1")
    model = config.get("model", "gpt-4")

    if not api_key or api_key == "your-api-key-here":
        print(f"❌ Please configure your API key in {config_file}")
        sys.exit(1)

    # Use theorems_only subdirectory in script directory
    output_dir = script_dir / "litex_auto_validated_250tasks" / "theorems_only"

    # check command line arguments: limit task count
    max_tasks = None
    if len(sys.argv) > 1:
        try:
            max_tasks = int(sys.argv[1])
            print(f"🎯 Limit to first {max_tasks} tasks")
        except ValueError:
            print(f"❌ Parameter error: {sys.argv[1]} is not a valid number")
            sys.exit(1)

    experiment = LitexExperimentWithValidation(api_key, base_url, model, output_dir)
    experiment.run_all(max_tasks=max_tasks)

if __name__ == "__main__":
    main()
