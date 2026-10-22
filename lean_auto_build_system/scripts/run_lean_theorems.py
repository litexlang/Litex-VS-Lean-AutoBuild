#!/usr/bin/env python3
"""
Lean Theorem Automated Proof System
Prove theorems based on complete definition library
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

# Import Lean validator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lean_session import SessionBackedValidator

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
# Lean Theorem Task Definitions (consistent with litex)
# ========================================

LEAN_TASKS = [
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
        name="Prove triangle_congruence_AAS theorem",
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
        name="Prove rotated_90_creates_isosceles_right theorem",
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

# ========================================
# Lean Theorem Experiment Manager
# ========================================

class LeanTheoremExperiment:
    """Lean Theorem Proof Experiment"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path,
                 verbosity: str = "full", seed_lib_path: Optional[Path] = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.error_verbosity = verbosity

        # create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 Experiment output directory: {self.output_dir}")
        print(f"🔬 Error verbosity level: {verbosity}")

        # Log file
        self.log_file = self.output_dir / "experiment.log"
        self.init_log()

        # Load complete definition library as seed
        if seed_lib_path and seed_lib_path.exists():
            seed_file = seed_lib_path
        else:
            # prioritize use oflibrary_final.lean（definitions experiment output）
            seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "library_final.lean"
            if not seed_file.exists():
                # fallback to basic seed library
                seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "LeanGeoCore" / "theorem_library_seed.lean"
                if not seed_file.exists():
                    raise FileNotFoundError(f"Seed library file does not exist: {seed_file}")

        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

        print(f"✅ Loaded seed library: {seed_file}")
        print(f"📏 Seed library size: {len(self.seed)} characters")

        # Library state
        self.state = {
            "definitions": [],
            "theorems": [],
            "completed_tasks": [],
            "axiom_debt": []
        }

        # Try to load previous state
        state_file = self.output_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)

        self.attempts = []
        self.start_time = None
        self.total_time = 0

        # Initialize Lean validator
        # Use local LeanGeo project
        lean_project_dir = Path(__file__).parent.parent / "LeanGeo"

        self.validator = SessionBackedValidator(
            seed_source=self.seed,
            lean_project_dir=lean_project_dir,
            cmd_timeout=600.0  # Increase to 10 minutes to avoid timeout on first Mathlib load
        )

    def init_log(self):
        """Initialize log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"""# Lean Theorem Proof Log

Experiment time: {timestamp}
Model: {self.model}
Task type: theorem

---

""")

    def log(self, message: str):
        """Write to log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message)

    def save_state(self):
        """Save state to file"""
        state_file = self.output_dir / "state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def save_attempts(self):
        """Save all attempts to file"""
        attempts_file = self.output_dir / "attempts.json"
        with open(attempts_file, "w", encoding="utf-8") as f:
            attempts_data = [asdict(a) for a in self.attempts]
            json.dump(attempts_data, f, indent=2, ensure_ascii=False)

    def save_library(self):
        """Save complete library to library_final.lean"""
        library_file = self.output_dir / "library_final.lean"
        library_content = self.validator.export_session_library(self.seed)
        with open(library_file, "w", encoding="utf-8") as f:
            f.write(library_content)
        print(f"\n📚 Complete library saved: {library_file}")

    def get_agent_theorems_prompt(self) -> str:
        """Get proven theorems"""
        if not self.state["theorems"]:
            return "-- (No newly proven theorems yet)\n"
        return "-- Proven theorems\n" + "\n".join(self.state["theorems"]) + "\n"

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """Build task prompt"""
        context = f"""-- ========== Seed Library (loaded, contains all definitions) ==========

The seed library contains all basic definitions and predicates, which you can use directly.

-- ========== Proven Theorems ==========

{self.get_agent_theorems_prompt()}
"""

        # read Lean syntax guide
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "lean_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            syntax_guide = """
# Lean 4 Theorem Proving Reference

1. Theorem format: theorem name : statement := by tactics
2. Common tactics: intro, apply, rw, simp, ring, norm_num
3. Structured proofs: have, show, calc
"""

        prompt = f"""{context}

{syntax_guide}

-- ========== task {task.id}: {task.name} ==========

{task.description}

Please prove this theorem. You can use all definitions from the seed library and previously proven theorems.

Hints:
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
-- ========== Previous Attempt Error ==========

Error information (JSON format):
```json
{previous_error}
```

**JSON field descriptions**:
- `error_type`: Error type (usually "tactic_failed", indicating tactic failure)
- `line`: **Specific line number of error** (tells you which line of proof tactic failed)
- `column`: Column number of error (locates specific position)
- `context_and_goal`: **Most critical information!** Contains:
  * Current variables and hypotheses (type context)
  * "⊢" symbol (means "need to prove")
  * **Goal to prove** (this is the expression you need to prove)

**How to use error information to fix proof**:
1. **Locate error line**: Check `line` and `column` to find which line's tactic failed
2. **Understand current goal**: Check the expression after "⊢" in `context_and_goal`, this is the current goal to prove
3. **Check available hypotheses**: Check the content before "⊢", these are the variables and hypotheses you can use
4. **Choose correct tactic**:
   - If goal is algebraic equation → try `ring` or `field_simp`
   - If need to unfold definition → use `unfold`
   - If need to rewrite → use `rw`
   - If need to introduce variables → use `intro`
   - If linear inequality → try `linarith`

**Common error patterns**:
- "tactic 'ring' failed" → may need to `unfold` definitions first
- "unsolved goals" → proof incomplete, need to continue adding tactics
- "type mismatch" → type mismatch, check function definition return type

Please fix the proof based on error information. Only output the corrected Lean code.
"""
        elif attempt_num > 1:
            prompt += f"\n(This is attempt {attempt_num}, please improve proof strategy)\n"

        prompt += "\nPlease only output Lean theorem proof code, can be wrapped in ```lean code block.\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """Execute single task"""
        print(f"\n{'='*60}")
        print(f"Task {task.id}: {task.name}")
        print(f"{'='*60}\n")

        self.log(f"\n## Task {task.id}: {task.name}\n")
        self.log(f"**Task type**: {task.task_type}\n")
        self.log(f"**Description**: {task.description}\n")

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"Attempt {attempt_num}/{max_attempts}...")
            self.log(f"\n### Attempt {attempt_num}\n")

            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # Call API
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
                                print(f"⚠️  API rate limit, waiting {api_retry_delay} seconds...")
                                time.sleep(api_retry_delay)
                                api_retry_delay *= 2
                                continue
                            else:
                                raise
                        else:
                            raise

                # Handle response format
                if isinstance(response, str):
                    # If return is string, try to parse JSON
                    try:
                        response = json.loads(response)
                    except:
                        # If not JSON, use directly as content
                        agent_output = response
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
                else:
                    # Normal object format
                    agent_output = response.choices[0].message.content
                    prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                    completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                    total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                elapsed = time.time() - start_time

                print(f"\n⏱️  Time elapsed: {elapsed:.2f}s")
                print(f"🔢 Tokens: {total_tokens}")

                self.log(f"**Time elapsed**: {elapsed:.2f}s\n")
                self.log(f"**Tokens**: {total_tokens}\n")

                # Extract Lean code
                extracted_code = self.validator.extract_lean_code(agent_output)
                last_code = extracted_code
                print(f"\nCode:\n{extracted_code}\n")
                self.log(f"**Code**:\n```lean\n{extracted_code}\n```\n")

                # Auto validation
                print("🤖 Auto-validating...")
                is_valid, compiler_output, raw_json_resp = self.validator.validate(
                    extracted_code,
                    self.get_library_context()
                )

                # Raw output for logging
                print(compiler_output)
                self.log(f"**Validation result**: {compiler_output}\n")

                # format error message for next attempt（pass in JSON）
                formatted_error = self._format_lean_error_to_json(
                    success=is_valid,
                    raw_json_resp=raw_json_resp,
                    text_output=compiler_output
                )

                # record attempt（save raw complete error JSON）
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,
                    success=(is_valid is True),
                    error_type="C" if is_valid is False else None,
                    compiler_output=json.dumps(raw_json_resp, ensure_ascii=False) if raw_json_resp else compiler_output,  # save JSON
                    timestamp=datetime.now().isoformat(),
                    time_elapsed=elapsed,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
                self.attempts.append(attempt)
                self.save_attempts()

                if is_valid:
                    print(f"✅ Task {task.id} succeeded!\n")
                    self.log(f"✅ **Task succeeded**\n")

                    self.state["theorems"].append(extracted_code)
                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    self.save_library()
                    return True
                else:
                    print(f"❌ Validation failed, preparing next attempt...\n")
                    previous_error = formatted_error  # Use formatted error
                    print(f"❌ Validation failed, preparing next attempt...\n")
                    previous_error = compiler_output

            except Exception as e:
                print(f"❌ Error: {e}\n")
                self.log(f"❌ **Error**: {e}\n")
                previous_error = str(e)

        print(f"❌ Task {task.id} failed (max attempts reached)\n")
        self.log(f"❌ **Task failed**\n")
        return False

    def _format_lean_error_to_json(self, success: bool, raw_json_resp: Dict[str, Any],
                                    text_output: str) -> str:
        """Format Lean error to JSON"""
        if success:
            return "✅ Compilation passed"

        if not raw_json_resp or "messages" not in raw_json_resp:
            # No JSON or no messages, return text
            return text_output

        # Extract first error message
        for msg in raw_json_resp.get("messages", []):
            if isinstance(msg, dict) and msg.get("severity") == "error":
                pos = msg.get("pos") or {}
                data = msg.get("data") or ""

                # Build JSON format
                error_json = {
                    "error_type": "tactic_failed",  # Simplified classification
                    "line": pos.get("line", "?"),
                    "column": pos.get("column", "?"),
                    "context_and_goal": data.strip()  # Keep multiline text (includes type annotation + goal)
                }

                return json.dumps(error_json, ensure_ascii=False, indent=2)

        # No error message found, return original text
        return text_output

    def get_library_context(self) -> str:
        """Complete library context"""
        context = self.seed + "\n\n"
        if self.state["theorems"]:
            context += "-- Proven theorems\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def run_all(self, max_tasks=None):
        """Run all tasks"""
        self.start_time = time.time()

        tasks_to_run = LEAN_TASKS[:max_tasks] if max_tasks else LEAN_TASKS
        print(f"🚀 Starting {len(tasks_to_run)} theorem tasks\n")

        success_count = 0
        for task in tasks_to_run:
            if task.id in self.state["completed_tasks"]:
                print(f"⏭️  Task {task.id} already completed, skipping")
                success_count += 1
                continue

            if self.execute_task(task):
                success_count += 1

        self.total_time = time.time() - self.start_time

        # Output summary
        print(f"\n{'='*60}")
        print("Experiment Summary")
        print(f"{'='*60}")
        print(f"Total tasks: {len(tasks_to_run)}")
        print(f"✅ Succeeded: {success_count}")
        print(f"❌ Failed: {len(tasks_to_run) - success_count}")
        print(f"Total time: {self.total_time/60:.1f} minutes")

        # Count sorry and axiom usage
        sorry_count = 0
        axiom_count = 0
        for thm in self.state["theorems"]:
            if "sorry" in thm:
                sorry_count += 1
            if thm.strip().startswith("axiom "):
                axiom_count += 1

        if sorry_count > 0 or axiom_count > 0:
            print(f"🧾 Incomplete proof statistics:")
            if sorry_count > 0:
                print(f"   - sorry placeholders: {sorry_count}")
            if axiom_count > 0:
                print(f"   - axiom declarations: {axiom_count}")

        self.save_library()

# ========================================
# Main Program
# ========================================

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Lean Theorem Automated Proof System')
    parser.add_argument('--verbosity', type=str, default='full',
                        choices=['minimal', 'medium', 'no_recursive', 'full'],
                        help='Error message verbosity level')
    parser.add_argument('--output-suffix', type=str, default='',
                        help='Output directory suffix (for ablation experiment grouping)')
    parser.add_argument('--seed-lib', type=str, default=None,
                        help='seed library file path（default to useLeanGeo/library_final.lean）')
    parser.add_argument('--max-tasks', type=int, default=None,
                        help='Maximum number of tasks (for testing)')

    args = parser.parse_args()

    # Load API configuration
    script_dir = Path(__file__).resolve().parent.parent
    config_file = script_dir / "config" / "api_config.json"

    if not config_file.exists():
        print(f"❌ API config file does not exist: {config_file}")
        print(f"Please copy config/api_config.example.json to config/api_config.json and fill in your API key")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    API_KEY = config.get("api_key")
    BASE_URL = config.get("base_url", "https://api.openai.com/v1")
    MODEL = config.get("model", "gpt-4")

    if not API_KEY or API_KEY == "your-api-key-here":
        print(f"❌ Please configure your API key in {config_file}")
        sys.exit(1)

    # Output directory
    if args.output_suffix:
        output_dir = script_dir / "lean_ablation" / f"group_{args.output_suffix}" / "theorems_only"
    else:
        output_dir = script_dir / "lean_auto_validated_250tasks" / "theorems_only"

    # Seed library path
    seed_lib_path = Path(args.seed_lib) if args.seed_lib else None

    # Create experiment
    experiment = LeanTheoremExperiment(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
        base_output_dir=output_dir,
        verbosity=args.verbosity,
        seed_lib_path=seed_lib_path
    )

    # Setup log capture (output to both terminal and file)
    console_log = experiment.output_dir / "experiment.log"
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Tee class: output to both console and file
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

    # Redirect output
    sys.stdout = Tee(original_stdout, log_file)
    sys.stderr = Tee(original_stderr, log_file)

    try:
        # Run experiment
        if args.max_tasks:
            print(f"🎯 Limiting to first {args.max_tasks} tasks")
        experiment.run_all(max_tasks=args.max_tasks)
    finally:
        # Restore original output
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()

