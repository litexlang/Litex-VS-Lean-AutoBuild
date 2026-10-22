#!/usr/bin/env python3
"""
with automatic validation LitexGeo experiment
using golitex compiler for automatic validation and provide error feedback to Agent
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

# Import validator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from litex_session import SessionBackedValidator

# compatible old name
GolitexValidator = SessionBackedValidator

# ========================================
# Data Structures
# ========================================

@dataclass
class Task:
    """single task"""
    id: str
    stage: int
    name: str
    description: str
    task_type: str
    hints: List[str]

@dataclass
class TaskAttempt:
    """single attempt record"""
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
# LitexGeo task definition（same as before）
# ========================================

# Python code to generate 250 tasks

LITEX_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="Define vec function",
        description="Define the vector from point A to point B, using coordinate differences (B(1)-A(1), B(2)-A(2)) to represent the directed line segment between two points in the plane.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="Define dot function",
        description="Define the dot product (inner product) of two vectors, computing u(1)*v(1) + u(2)*v(2), used to measure the projection relationship between vectors and the cosine of their angle.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="Define det function",
        description="Define the determinant of two vectors (scalar part of the cross product), computing u(1)*v(2) - u(2)*v(1), used to determine the relative orientation of vectors and area.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.4",
        stage=1,
        name="Define distance_sq function",
        description="Define the squared distance between two points, calculated through the dot product of a vector with itself, avoiding square root operations to maintain algebraic precision.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.5",
        stage=1,
        name="Define line function",
        description="Define a line represented by the general equation ax+by+c=0, returning the set of all points satisfying this equation, where coefficients a and b cannot both be zero.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.6",
        stage=1,
        name="Define line_of function",
        description="Define the line passing through two distinct points a and b, returning the set of all points collinear with vector ab, using zero determinant to characterize collinearity.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.7",
        stage=1,
        name="Define angle_cos_num function",
        description="Define the numerator part of the angle cosine, computing the numerator of the cosine value for an angle with vertex q and sides qp and qr, which is the dot product of the two vectors.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.8",
        stage=1,
        name="Define angle_cos_den function",
        description="Define the denominator part of the angle cosine, computing the denominator of the cosine value, which is the product of the squared lengths of the two sides, working with the numerator to obtain the normalized cosine value.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.9",
        stage=1,
        name="Define circle function",
        description="Define a circle with center o and radius r, returning the set of all points whose squared distance to the center equals r².",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.10",
        stage=1,
        name="Define is_on_segment predicate",
        description="Define the predicate for point p being on segment ab, requiring the existence of parameter t∈[0,1] such that p is a convex combination of a and b, characterizing points in the bounded segment interior or endpoints.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.1",
        stage=2,
        name="Define is_on_ray predicate",
        description="Determine whether point p is on the ray starting at a and passing through b, where there exists a non-negative parameter t such that p is an extension point of a along the ab direction.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.2",
        stage=2,
        name="Define is_collinear predicate",
        description="Determine whether three points p, q, r are collinear, characterized by the determinant of vectors pq and pr being zero.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.3",
        stage=2,
        name="Define are_segments_congruent predicate",
        description="Determine whether two segments AB and CD are congruent, meaning equal in length, represented by equal squared distances.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.4",
        stage=2,
        name="Define are_angles_congruent predicate",
        description="Determine whether two undirected angles ∠PQR and ∠UVW are congruent, using equal cosine values with the same sign to avoid supplementary angle confusion.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.5",
        stage=2,
        name="Define is_right_angle predicate",
        description="Determine whether ∠PQR is a right angle (90 degrees), characterized by the dot product of the two side vectors being zero to describe perpendicularity.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.6",
        stage=2,
        name="Define is_parallel predicate",
        description="Determine whether line AB and line CD are parallel, characterized by the determinant of direction vectors being zero.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.7",
        stage=2,
        name="Define is_perpendicular predicate",
        description="Determine whether line AB and line CD are perpendicular, characterized by the dot product of direction vectors being zero.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.8",
        stage=2,
        name="Define is_line predicate",
        description="Determine whether set L is a line, meaning there exist coefficients a, b, c not all zero such that L is the solution set of equation ax+by+c=0.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.9",
        stage=2,
        name="Define is_midpoint predicate",
        description="Determine whether m is the midpoint of segment ab, defined by taking the average of coordinates.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.10",
        stage=2,
        name="Define is_affine_combination predicate",
        description="Determine whether point p is an affine combination of points a and b, where parameter t is unrestricted and can represent any point on the segment or its extension.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.1",
        stage=3,
        name="Define is_centroid predicate",
        description="Determine whether point g is the centroid of triangle abc, meaning the arithmetic mean of the three vertex coordinates.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.2",
        stage=3,
        name="Define is_on_line predicate",
        description="Determine whether point p is on the line passing through points a and b, by checking if the point is in the line set line_of(a,b).",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.3",
        stage=3,
        name="Define is_on_extension predicate",
        description="Determine whether point p is on the extension of segment ab (beyond point b), where parameter t>1 indicates p is beyond b.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.4",
        stage=3,
        name="Define is_foot predicate",
        description="Determine whether point f is the foot of the perpendicular from point p to line ab, meaning f is on line ab and pf is perpendicular to ab.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.5",
        stage=3,
        name="Define is_angle_bisector predicate",
        description="Determine whether ray bd is the angle bisector of angle ∠abc, defined by angles ∠abd and ∠dbc being congruent.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.6",
        stage=3,
        name="Define is_triangle predicate",
        description="Determine whether three points a, b, c form a triangle, meaning the three points are not collinear.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.7",
        stage=3,
        name="Define is_isosceles predicate",
        description="Determine whether triangle abc is isosceles, meaning sides ab and ac have equal lengths.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.8",
        stage=3,
        name="Define is_equilateral predicate",
        description="Determine whether triangle abc is equilateral, meaning all three sides have equal lengths.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.9",
        stage=3,
        name="Define are_triangles_congruent predicate",
        description="Determine whether two triangles pqr and uvw are congruent (SSS), meaning corresponding three sides have equal lengths.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.10",
        stage=3,
        name="Define are_triangles_similar predicate",
        description="Determine whether two triangles pqr and uvw are similar (AAA), meaning corresponding three angles are congruent.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.1",
        stage=4,
        name="Define is_parallelogram predicate",
        description="Determine whether quadrilateral abcd is a parallelogram, meaning opposite sides are parallel (ab∥dc and ad∥bc).",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.2",
        stage=4,
        name="Define is_rectangle predicate",
        description="Determine whether quadrilateral abcd is a rectangle, meaning it is a parallelogram with one right angle.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.3",
        stage=4,
        name="Define is_rhombus predicate",
        description="Determine whether quadrilateral abcd is a rhombus, meaning it is a parallelogram with adjacent sides equal.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.4",
        stage=4,
        name="Define is_square predicate",
        description="Determine whether quadrilateral abcd is a square, meaning it is a rectangle with adjacent sides equal.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.5",
        stage=4,
        name="Define is_on_circle predicate",
        description="Determine whether point p is on a circle with center o and radius r, by checking if the squared distance equals the squared radius.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.6",
        stage=4,
        name="Define are_concyclic predicate",
        description="Determine whether four points a, b, c, d are concyclic, meaning there exists a center o such that all four points are equidistant from o.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.7",
        stage=4,
        name="Define is_diameter_endpoints predicate",
        description="Determine whether points a and b are endpoints of a diameter (with o as center), meaning o is the midpoint of segment ab.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.8",
        stage=4,
        name="Define rotated_90_cw predicate",
        description="Determine whether point q is obtained by rotating point p clockwise 90 degrees around point c, defined through coordinate transformation relationships.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.9",
        stage=4,
        name="Define rotated_90_ccw predicate",
        description="Determine whether point q is obtained by rotating point p counterclockwise 90 degrees around point c, defined through coordinate transformation relationships.",
        task_type="definition",
        hints=[]
    ),
    # definition task list ends
]
class LitexExperimentWithValidation:
    """with automatic validation  LitexGeo experiment"""

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
        seed_file = Path(__file__).parent.parent / "database" / "definition_library_seed.lit"
        if not seed_file.exists():
            raise FileNotFoundError(
                f"seed file does not exist: {seed_file}\n"
                f"please ensure database/definition_library_seed.lit file exists"
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
        """Append to log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def get_seed_prompt_blurb(self) -> str:
        """seed description for prompt：tell agent what already exists，prohibit duplicate definitions。"""
        return (
            "# ========== seed library（already loaded in validation environment，prohibit duplicate definitions）==========\n"
            "# Already have: points, vec, dot, det. Below is for reference only, do not have fn again.\n\n"
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
        # Brief seed prompt + only agent accumulated results (do not repeatedly stack seed as "library to append")
        context = self.get_seed_prompt_blurb()
        context += "\n# ========== current experiment library state（agent additions）==========\n\n"
        context += self.get_agent_library_prompt()

        # Read short guide
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "litex_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            # Fallback simplified version
            syntax_guide = """
# LiteX Syntax Reference

1. function definition：have fn name(arg Type) ReturnType = expression
2. predicate definition：prop name(arg Type): conditions
3. theorem proof：thm name: prove: forall ... => conclusion; proof_body
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
        """execute single task（automatic validation + feedback loop）"""
        print(f"\n{'='*60}")
        print(f"task {task.id}: {task.name}")
        print(f"{'='*60}\n")

        # record task start
        self.log(f"\n## task {task.id}: {task.name}\n")
        self.log(f"**task type**: {task.task_type}\n")
        self.log(f"**Description**: {task.description}\n")

        # definition tasks already covered by seed: no longer call agent to repeat have fn
        seed_skip = {
            "1.1": ("vec", "# vec already defined in seed library agent_library_seed.txt, no need to repeat definition"),
            "1.2": ("dot", "# dot already defined in seed library agent_library_seed.txt, no need to repeat definition"),
            "1.3": ("det", "# det already defined in seed library agent_library_seed.txt, no need to repeat definition"),
        }
        if task.id in seed_skip:
            _name, note = seed_skip[task.id]
            print(f"⏭️  Seed library already has {_name}, skip duplicate definition.\n")
            self.log(f"**skip**: seed library already has `{_name}`\n\n```litex\n{note}\n```\n")
            self.state["definitions"].append(note)
            self.state["completed_tasks"].append(task.id)
            self.save_state()
            return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"attempt {attempt_num}/{max_attempts}...")
            self.log(f"\n### attempt {attempt_num}\n")

            # build prompt（includes previous error）
            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # Call Agent with retry mechanism for rate limiting
                max_api_retries = 3
                api_retry_delay = 10  # seconds

                for api_attempt in range(max_api_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=4096
                        )
                        break  # success then exit retry loop
                    except Exception as api_error:
                        error_str = str(api_error)
                        # check if rate limit error
                        if "429" in error_str or "rate_limit" in error_str or "cooldown" in error_str:
                            if api_attempt < max_api_retries - 1:
                                print(f"⚠️  API rate limit, waiting {api_retry_delay}s before retry...")
                                time.sleep(api_retry_delay)
                                api_retry_delay *= 2  # exponential backoff
                                continue
                            else:
                                print(f"❌ API rate limit, max retries reached")
                                raise
                        else:
                            # other errors throw directly
                            raise

                agent_output = response.choices[0].message.content
                elapsed = time.time() - start_time

                # Extract tokens
                prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                print(f"\n⏱️  Time elapsed: {elapsed:.2f}s")
                print(f"🔢 Tokens: {total_tokens} (input: {prompt_tokens}, output: {completion_tokens})")

                # Record to log
                self.log(f"**Time elapsed**: {elapsed:.2f}s")
                self.log(f"**Tokens**: {total_tokens} (input: {prompt_tokens}, output: {completion_tokens})\n")

                # extract and output code once（no longer split Agent output / extracted code）
                extracted_code = self.validator.extract_litex_code(agent_output)
                last_code = extracted_code
                print(f"\nCode:\n{extracted_code}\n")
                self.log(f"**Code**:\n```litex\n{extracted_code}\n```\n")

                # automatic validation
                print("🤖 auto-validating...")
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
                    # validator unavailable，manual validation
                    print("\n⚠️  automatic validation unavailable，needs manual validation")
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
                print(f"❌ Exception occurred: {e}")
                import traceback
                traceback.print_exc()
                print(f"continue to attempt {attempt_num + 1} th attempt...")
                continue

        print(f"\n❌ task {task.id} after {max_attempts} attempts failed。")
        # If proof fails, use axiom as fallback to avoid downstream "by thm" breakage
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
            print("="*60)

            self.start_time = time.time()

            # limit task count
            tasks_to_run = LITEX_TASKS[:max_tasks] if max_tasks else LITEX_TASKS
            if max_tasks:
                print(f"🎯 Limit to first {max_tasks} tasks\n")

            # count successful and failed tasks
            completed_tasks = []
            failed_tasks = []

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
            print(f"✅ Success: {len(completed_tasks)}/{len(tasks_to_run)} tasks")
            print(f"❌ Failed: {len(failed_tasks)}/{len(tasks_to_run)} tasks")

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

    # Use definitions_only subdirectory under script directory
    output_dir = script_dir / "litex_auto_validated_250tasks" / "definitions_only"

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
