#!/usr/bin/env python3
"""
Lean Definition Automated Build System
Adapted from LitexGeo definition system for Lean 4
"""

import os
import json
import sys
import argparse
from openai import OpenAI
from pathlib import Path
from typing import List, Optional, Tuple
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
# Lean Definition task definition
# ========================================

# import descriptions from litex definition taskss
LEAN_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="Define vec function",
        description="Define the vector from point A to point B, using coordinate differences (B.1-A.1, B.2-A.2) to represent the directed line segment between two points in the plane.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="Define dot function",
        description="Define the dot product (inner product) of two vectors, computing u.1*v.1 + u.2*v.2, used to measure the projection relationship between vectors and the cosine of their angle.",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="Define det function",
        description="Define the determinant of two vectors (scalar part of the cross product), computing u.1*v.2 - u.2*v.1, used to determine the relative orientation of vectors and area.",
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

# ========================================
# Lean experiment manager
# ========================================

class LeanExperimentWithValidation:
    """with automatic validation Lean Definition experiment"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path,
                 verbosity: str = "full"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.error_verbosity = verbosity

        # create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = base_output_dir / f"run_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"📁 experiment output directory: {self.output_dir}")
        print(f"🔬 error verbosity level: {verbosity}")

        # log file
        self.log_file = self.output_dir / "experiment.log"
        self.init_log()

        # load Lean seed library (from LeanGeo project)
        seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "LeanGeoCore" / "definition_library_seed.lean"
        if not seed_file.exists():
            raise FileNotFoundError(f"seed library file does not exist: {seed_file}")

        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

        # Library state
        self.state = {
            "definitions": [],
            "theorems": [],
            "completed_tasks": [],
            "axiom_debt": []
        }

        # attempt to load previous state
        state_file = self.output_dir / "state.json"
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)

        self.attempts = []
        self.start_time = None
        self.total_time = 0

        # initialize Lean validator（persistent session）
        # use local LeanGeo project
        lean_project_dir = Path(__file__).parent.parent / "LeanGeo"

        self.validator = SessionBackedValidator(
            seed_source=self.seed,
            lean_project_dir=lean_project_dir,
            cmd_timeout=600.0  # increase to 10 minutes，avoid timeout on first Mathlib load
        )

    def init_log(self):
        """initialize log file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"""# Lean Definition Build Log

experiment time：{timestamp}
Model: {self.model}

---

""")

    def log(self, message: str):
        """Write to log"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(message)

    def save_state(self):
        """save state to file"""
        state_file = self.output_dir / "state.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def save_attempts(self):
        """save all attempts to file"""
        attempts_file = self.output_dir / "attempts.json"
        with open(attempts_file, "w", encoding="utf-8") as f:
            attempts_data = [asdict(a) for a in self.attempts]
            json.dump(attempts_data, f, indent=2, ensure_ascii=False)

    def save_library(self):
        """save complete library to library_final.lean"""
        library_file = self.output_dir / "library_final.lean"
        library_content = self.validator.export_session_library(self.seed)
        with open(library_file, "w", encoding="utf-8") as f:
            f.write(library_content)
        print(f"\n📚 complete library saved: {library_file}")

    def get_seed_prompt_blurb(self) -> str:
        """get seed library brief description"""
        return f"""# ========== seed library（already loaded in validation environment）==========

{self.seed}

"""

    def get_agent_library_prompt(self) -> str:
        """Get prompt text for agent accumulated results"""
        parts = []
        if self.state["definitions"]:
            parts.append("# defined concepts\n" + "\n".join(self.state["definitions"]))
        if self.state["theorems"]:
            parts.append("# proven theorems\n" + "\n".join(self.state["theorems"]))
        if not parts:
            return "# （no new additions in this experiment yetdefinition/theorem）\n"
        return "\n\n".join(parts) + "\n"

    def get_library_context(self) -> str:
        """for complete library file export：seed + accumulated results"""
        context = self.seed + "\n\n"
        if self.state["definitions"]:
            context += "-- defined concepts\n" + "\n".join(self.state["definitions"]) + "\n\n"
        if self.state["theorems"]:
            context += "-- proven theorems\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """build task prompt"""
        context = self.get_seed_prompt_blurb()
        context += "\n-- ========== current experiment library state（agent additions）==========\n\n"
        context += self.get_agent_library_prompt()

        # read Lean syntax guide
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "lean_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            syntax_guide = """
# Lean 4 Syntax Reference

1. function definition：def name (arg : Type) : ReturnType := expression
2. theorem proof：theorem name : statement := by proof_tactics
3. structure definition：structure Name where fields...
"""

        prompt = f"""{context}

{syntax_guide}

-- ========== task {task.id}: {task.name} ==========

{task.description}

Important: seed library already includes basic imports and Point definition。please build new definitions based on this。

Hints:
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
-- ========== previous attempt error ==========

error message：
```
{previous_error}
```

**how to understand and fix errors**：

1. **locate error position**：check line and column numbers in error message
2. **understand error type**：
   - "type mismatch" → type mismatch，check function return type
   - "unknown identifier" → undefined identifier，ensure correct names are used
   - "expected ..." → syntax error，check syntax format
3. **Common issues**:
   - function definitions use `def`，predicate returns `Prop`
   - Tuple access uses `.1` and `.2`
   - Ensure type annotations are correct (e.g., `Point`, `ℝ`)

please fix your code based on error information。only output corrected Lean code。
"""
        elif attempt_num > 1:
            prompt += f"\n(this is attempt {attempt_num} th attempt，please improve your answer)\n"

        prompt += "\nplease only output Lean code，can be wrapped in ```lean code block。\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """execute single task（automatic validation + feedback loop）"""
        print(f"\n{'='*60}")
        print(f"task {task.id}: {task.name}")
        print(f"{'='*60}\n")

        self.log(f"\n## task {task.id}: {task.name}\n")
        self.log(f"**task type**: {task.task_type}\n")
        self.log(f"**Description**: {task.description}\n")

        # definition taskss already covered by seed：no longer call agent to repeat definitions
        seed_skip = {
            "1.1": ("vec", "-- vec already in seed library lean_library_seed.txt defined in，no need to repeat definition"),
            "1.2": ("dot", "-- dot already in seed library lean_library_seed.txt defined in，no need to repeat definition"),
            "1.3": ("det", "-- det already in seed library lean_library_seed.txt defined in，no need to repeat definition"),
        }
        if task.id in seed_skip:
            _name, note = seed_skip[task.id]
            print(f"⏭️  seed library already has {_name}，skip duplicate definition。\n")
            self.log(f"**skip**: seed library already has `{_name}`\n\n```lean\n{note}\n```\n")
            self.state["definitions"].append(note)
            self.state["completed_tasks"].append(task.id)
            self.save_state()
            return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"attempt {attempt_num}/{max_attempts}...")
            self.log(f"\n### attempt {attempt_num}\n")

            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # call API with retry mechanism
                max_api_retries = 3
                api_retry_delay = 10

                for api_attempt in range(max_api_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=4096
                        )
                        # DEBUG：print response type
                        print(f"DEBUG: response type = {type(response)}")
                        if isinstance(response, str):
                            print(f"DEBUG: response content (first 200 chars) = {response[:200]}")
                        break
                    except Exception as api_error:
                        error_str = str(api_error)
                        if "429" in error_str or "rate_limit" in error_str:
                            if api_attempt < max_api_retries - 1:
                                print(f"⚠️  API rate limit, waiting{api_retry_delay}seconds...")
                                time.sleep(api_retry_delay)
                                api_retry_delay *= 2
                                continue
                            else:
                                print(f"❌ API rate limit, reached maximum retries")
                                raise
                        else:
                            raise

                # handle response format
                if isinstance(response, str):
                    # if return is string，attempt to parseJSON
                    try:
                        import json
                        response = json.loads(response)
                    except:
                        # if notJSON，use directly as content
                        agent_output = response
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
                else:
                    # normal object format
                    agent_output = response.choices[0].message.content
                    prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
                    completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
                    total_tokens = response.usage.total_tokens if hasattr(response, 'usage') else 0

                print(f"DEBUG: agent_output length = {len(agent_output) if agent_output else 0}")
                print(f"DEBUG: agent_output preview = {agent_output[:300] if agent_output else 'None'}")

                elapsed = time.time() - start_time

                print(f"\n⏱️  Time elapsed: {elapsed:.2f}s")
                print(f"🔢 Tokens: {total_tokens}")

                self.log(f"**Time elapsed**: {elapsed:.2f}s")
                self.log(f"**Tokens**: {total_tokens}\n")

                # extract Lean code
                extracted_code = self.validator.extract_lean_code(agent_output)
                last_code = extracted_code
                print(f"\nCode:\n{extracted_code}\n")
                self.log(f"**Code**:\n```lean\n{extracted_code}\n```\n")

                # automatic validation
                print("🤖 auto-validating...")
                is_valid, compiler_output, raw_json_resp = self.validator.validate(
                    extracted_code,
                    self.get_library_context()
                )

                # raw output for logging
                print(compiler_output)
                self.log(f"**validation result**: {compiler_output}\n")

                # directly use compiler output as error message
                formatted_error = compiler_output

                # record attempt（save raw complete error）
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,
                    success=(is_valid is True),
                    error_type="C" if is_valid is False else None,
                    compiler_output=compiler_output,  # raw complete error
                    timestamp=datetime.now().isoformat(),
                    time_elapsed=elapsed,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
                self.attempts.append(attempt)
                self.save_attempts()

                if is_valid:
                    print(f"✅ task {task.id} success！\n")
                    self.log(f"✅ **tasksuccess**\n")

                    # save to state
                    if task.task_type == "definition":
                        self.state["definitions"].append(extracted_code)
                    else:
                        self.state["theorems"].append(extracted_code)

                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    self.save_library()
                    return True
                else:
                    print(f"❌ validation failed, prepare next attempt...\n")
                    previous_error = formatted_error  # use formatted error

            except Exception as e:
                print(f"❌ error occurred: {e}\n")
                self.log(f"❌ **error**: {e}\n")
                previous_error = str(e)

        print(f"❌ task {task.id} failed（reached maximum attempts）\n")
        self.log(f"❌ **task failed**（{max_attempts} th attempt）\n")
        return False

    def run_all(self, max_tasks=None):
        """run all tasks"""
        self.start_time = time.time()

        tasks_to_run = LEAN_TASKS[:max_tasks] if max_tasks else LEAN_TASKS
        print(f"🚀 start running {len(tasks_to_run)}  definition tasks\n")

        success_count = 0
        for task in tasks_to_run:
            if task.id in self.state["completed_tasks"]:
                print(f"⏭️  task {task.id} already completed，skip")
                success_count += 1
                continue

            if self.execute_task(task):
                success_count += 1

        self.total_time = time.time() - self.start_time

        # output summary
        print(f"\n{'='*60}")
        print("experiment completion summary")
        print(f"{'='*60}")
        print(f"total tasks: {len(tasks_to_run)}")
        print(f"success: {success_count}")
        print(f"failed: {len(tasks_to_run) - success_count}")
        print(f"Total time: {self.total_time/60:.1f} minutes")
        print(f"Axiom debt: {len(self.state['axiom_debt'])} items")

        self.save_library()

# ========================================
# Main Program
# ========================================

if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Lean Definition Automated Build System')
    parser.add_argument('--verbosity', type=str, default='full',
                        choices=['minimal', 'medium', 'no_recursive', 'full'],
                        help='error message verbosity level')
    parser.add_argument('--output-suffix', type=str, default='',
                        help='output directory suffix (for ablation experiment grouping)')
    parser.add_argument('--max-tasks', type=int, default=None,
                        help='maximum number of tasks（for testing）')

    args = parser.parse_args()

    # load API configuration
    script_dir = Path(__file__).resolve().parent.parent
    config_file = script_dir / "config" / "api_config.json"

    if not config_file.exists():
        print(f"❌ API configuration file does not exist: {config_file}")
        print(f"Please copy config/api_config.example.json to config/api_config.json and fill in your API key")
        sys.exit(1)

    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    API_KEY = config.get("api_key")
    BASE_URL = config.get("base_url", "https://api.openai.com/v1")
    MODEL = config.get("model", "gpt-4")

    if not API_KEY or API_KEY == "your-api-key-here":
        print(f"❌ Please configure your API key in {config_file} configure your API key")
        sys.exit(1)

    # output directory
    if args.output_suffix:
        output_dir = script_dir / "lean_ablation" / f"group_{args.output_suffix}" / "definitions_only"
    else:
        output_dir = script_dir / "lean_auto_validated_250tasks" / "definitions_only"

    # create experiment
    experiment = LeanExperimentWithValidation(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
        base_output_dir=output_dir,
        verbosity=args.verbosity
    )

    # setup log capture（output to both terminal and file）
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

    # redirect output
    sys.stdout = Tee(original_stdout, log_file)
    sys.stderr = Tee(original_stderr, log_file)

    try:
        # run experiment
        if args.max_tasks:
            print(f"🎯 limit to first {args.max_tasks} task")
        experiment.run_all(max_tasks=args.max_tasks)
    finally:
        # restore original output
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        log_file.close()

