#!/usr/bin/env python3
"""
Lean Definition 自动构建系统
基于 LitexGeo definition 系统改编，适配 Lean 4
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
# Lean Definition 任务定义
# ========================================

# 从 litex 的 definition 任务导入描述
LEAN_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="定义vec函数",
        description="定义从点A到点B的向量，用坐标差(B.1-A.1, B.2-A.2)表示平面上两点间的有向线段。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="定义dot函数",
        description="定义两个向量的点积（内积），计算u.1*v.1 + u.2*v.2，用于衡量向量间的投影关系和夹角余弦。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="定义det函数",
        description="定义两个向量的行列式（外积的标量部分），计算u.1*v.2 - u.2*v.1，用于判断向量的相对方向和面积。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.4",
        stage=1,
        name="定义distance_sq函数",
        description="定义两点间距离的平方，通过向量与自身的点积来计算，避免平方根运算，保持代数精确性。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.5",
        stage=1,
        name="定义line函数",
        description="定义由一般方程ax+by+c=0表示的直线，返回满足该方程的所有点的集合，其中系数a、b不能同时为零。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.6",
        stage=1,
        name="定义line_of函数",
        description="定义通过两个不同点a、b的直线，返回所有满足与向量ab共线的点的集合，用行列式为零来刻画共线性。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.7",
        stage=1,
        name="定义angle_cos_num函数",
        description="定义角度余弦的分子部分，计算以q为顶点、qp和qr为两边的角的余弦值分子，即两向量的点积。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.8",
        stage=1,
        name="定义angle_cos_den函数",
        description="定义角度余弦的分母部分，计算余弦值分母，即两边长度平方的乘积，与分子配合得到标准化的余弦值。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.9",
        stage=1,
        name="定义circle函数",
        description="定义以点o为圆心、r为半径的圆，返回所有到圆心距离平方等于r²的点的集合。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.10",
        stage=1,
        name="定义is_on_segment谓词",
        description="定义点p在线段ab上的谓词，要求存在参数t∈[0,1]使得p是a和b的凸组合，刻画点在有界线段内部或端点。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.1",
        stage=2,
        name="定义is_on_ray谓词",
        description="判断点p是否在以a为起点、经过b的射线上，存在非负参数t使得p是a沿ab方向的延伸点。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.2",
        stage=2,
        name="定义is_collinear谓词",
        description="判断三点p、q、r是否共线，通过向量pq和pr的行列式为零来刻画。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.3",
        stage=2,
        name="定义are_segments_congruent谓词",
        description="判断两线段AB和CD是否全等，即长度相等，通过距离平方相等来表示。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.4",
        stage=2,
        name="定义are_angles_congruent谓词",
        description="判断两个无向角∠PQR和∠UVW是否全等，通过余弦值相等且同号来避免补角混淆。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.5",
        stage=2,
        name="定义is_right_angle谓词",
        description="判断∠PQR是否为直角（90度），通过两边向量的点积为零来刻画垂直关系。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.6",
        stage=2,
        name="定义is_parallel谓词",
        description="判断直线AB和直线CD是否平行，通过方向向量的行列式为零来刻画。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.7",
        stage=2,
        name="定义is_perpendicular谓词",
        description="判断直线AB和直线CD是否垂直，通过方向向量的点积为零来刻画。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.8",
        stage=2,
        name="定义is_line谓词",
        description="判断集合L是否为直线，即存在不全为零的系数a、b、c使得L是方程ax+by+c=0的解集。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.9",
        stage=2,
        name="定义is_midpoint谓词",
        description="判断m是否为线段ab的中点，通过坐标取平均值来定义。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="2.10",
        stage=2,
        name="定义is_affine_combination谓词",
        description="判断点p是否为点a和b的仿射组合，参数t不受限制，可表示线段、延长线上的任意点。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.1",
        stage=3,
        name="定义is_centroid谓词",
        description="判断点g是否为三角形abc的重心，即三顶点坐标的算术平均。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.2",
        stage=3,
        name="定义is_on_line谓词",
        description="判断点p是否在过两点a、b的直线上，通过点在直线集合line_of(a,b)中来判断。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.3",
        stage=3,
        name="定义is_on_extension谓词",
        description="判断点p是否在线段ab的延长线上（超过b点），参数t>1表示p在b之外。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.4",
        stage=3,
        name="定义is_foot谓词",
        description="判断点f是否为点p到直线ab的垂足，即f在直线ab上且pf垂直于ab。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.5",
        stage=3,
        name="定义is_angle_bisector谓词",
        description="判断射线bd是否为角∠abc的角平分线，通过∠abd和∠dbc全等来定义。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.6",
        stage=3,
        name="定义is_triangle谓词",
        description="判断三点a、b、c是否构成三角形，即三点不共线。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.7",
        stage=3,
        name="定义is_isosceles谓词",
        description="判断三角形abc是否为等腰三角形，即ab和ac两边长度相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.8",
        stage=3,
        name="定义is_equilateral谓词",
        description="判断三角形abc是否为等边三角形，即三边长度都相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.9",
        stage=3,
        name="定义are_triangles_congruent谓词",
        description="判断两个三角形pqr和uvw是否全等（SSS），即对应三边长度分别相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="3.10",
        stage=3,
        name="定义are_triangles_similar谓词",
        description="判断两个三角形pqr和uvw是否相似（AAA），即对应三个角分别全等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.1",
        stage=4,
        name="定义is_parallelogram谓词",
        description="判断四边形abcd是否为平行四边形，即对边分别平行（ab∥dc且ad∥bc）。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.2",
        stage=4,
        name="定义is_rectangle谓词",
        description="判断四边形abcd是否为矩形，即是平行四边形且有一个直角。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.3",
        stage=4,
        name="定义is_rhombus谓词",
        description="判断四边形abcd是否为菱形，即是平行四边形且邻边相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.4",
        stage=4,
        name="定义is_square谓词",
        description="判断四边形abcd是否为正方形，即是矩形且邻边相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.5",
        stage=4,
        name="定义is_on_circle谓词",
        description="判断点p是否在以o为圆心、r为半径的圆上，通过距离平方等于半径平方来判断。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.6",
        stage=4,
        name="定义are_concyclic谓词",
        description="判断四点a、b、c、d是否共圆，即存在一个圆心o使得四点到o的距离相等。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.7",
        stage=4,
        name="定义is_diameter_endpoints谓词",
        description="判断点a和b是否为圆的直径端点（o为圆心），即o是线段ab的中点。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.8",
        stage=4,
        name="定义rotated_90_cw谓词",
        description="判断点q是否为点p绕点c顺时针旋转90度得到的点，通过坐标变换关系来定义。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="4.9",
        stage=4,
        name="定义rotated_90_ccw谓词",
        description="判断点q是否为点p绕点c逆时针旋转90度得到的点，通过坐标变换关系来定义。",
        task_type="definition",
        hints=[]
    ),
    # 定义任务列表结束
]

# ========================================
# Lean 实验管理器
# ========================================

class LeanExperimentWithValidation:
    """带自动验证的 Lean Definition 实验"""

    def __init__(self, api_key: str, base_url: str, model: str, base_output_dir: Path,
                 verbosity: str = "full"):
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

        # 加载 Lean 种子库（从LeanGeo项目中）
        seed_file = Path(__file__).parent.parent.parent / "LeanGeo" / "LeanGeoCore" / "theorem_library_seed.lean"
        if not seed_file.exists():
            raise FileNotFoundError(f"种子库文件不存在: {seed_file}")

        with open(seed_file, "r", encoding="utf-8") as f:
            self.seed = f.read()

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

        # 初始化 Lean 验证器（持久 session）
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
            f.write(f"""# Lean Definition 构建日志

实验时间：{timestamp}
模型：{self.model}

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

    def get_seed_prompt_blurb(self) -> str:
        """获取种子库的简要说明"""
        return f"""# ========== 种子库（已在验证环境中加载）==========

{self.seed}

"""

    def get_agent_library_prompt(self) -> str:
        """获取 agent 累积产物的提示文本"""
        parts = []
        if self.state["definitions"]:
            parts.append("# 已定义的概念\n" + "\n".join(self.state["definitions"]))
        if self.state["theorems"]:
            parts.append("# 已证明的定理\n" + "\n".join(self.state["theorems"]))
        if not parts:
            return "# （尚无本实验新增定义/定理）\n"
        return "\n\n".join(parts) + "\n"

    def get_library_context(self) -> str:
        """完整库文件导出用：种子 + 累积产物"""
        context = self.seed + "\n\n"
        if self.state["definitions"]:
            context += "-- 已定义的概念\n" + "\n".join(self.state["definitions"]) + "\n\n"
        if self.state["theorems"]:
            context += "-- 已证明的定理\n" + "\n".join(self.state["theorems"]) + "\n\n"
        return context

    def build_prompt(self, task: Task, attempt_num: int, previous_error: str = None) -> str:
        """构建任务提示"""
        context = self.get_seed_prompt_blurb()
        context += "\n-- ========== 当前实验库状态（agent 新增）==========\n\n"
        context += self.get_agent_library_prompt()

        # 读取 Lean 语法指南
        syntax_guide_path = Path(__file__).parent.parent / "prompts" / "lean_short_guide.md"
        if syntax_guide_path.exists():
            with open(syntax_guide_path, "r", encoding="utf-8") as f:
                syntax_guide = f.read()
        else:
            syntax_guide = """
# Lean 4 语法参考

1. 函数定义：def name (arg : Type) : ReturnType := expression
2. 定理证明：theorem name : statement := by proof_tactics
3. 结构定义：structure Name where fields...
"""

        prompt = f"""{context}

{syntax_guide}

-- ========== 任务 {task.id}: {task.name} ==========

{task.description}

重要：种子库已包含基础导入和 Point 定义。请基于此构建新定义。

提示：
"""
        for hint in task.hints:
            prompt += f"- {hint}\n"

        if previous_error:
            prompt += f"""
-- ========== 上一次尝试的错误 ==========

错误信息：
```
{previous_error}
```

**如何理解并修正错误**：

1. **定位错误位置**：查看错误消息中的行号和列号
2. **理解错误类型**：
   - "type mismatch" → 类型不匹配，检查函数返回类型
   - "unknown identifier" → 未定义的标识符，确保使用了正确的名称
   - "expected ..." → 语法错误，检查语法格式
3. **常见问题**：
   - 函数定义要用 `def`，谓词返回 `Prop`
   - 元组访问用 `.1` 和 `.2`
   - 确保类型注解正确（如 `Point`, `ℝ`）

请根据错误信息修正你的代码。只输出修正后的 Lean 代码。
"""
        elif attempt_num > 1:
            prompt += f"\n(这是第 {attempt_num} 次尝试，请改进你的答案)\n"

        prompt += "\n请只输出 Lean 代码，可以用 ```lean 代码块包裹。\n"

        return prompt

    def execute_task(self, task: Task, max_attempts: int = 5) -> bool:
        """执行单个任务（自动验证 + 反馈循环）"""
        print(f"\n{'='*60}")
        print(f"任务 {task.id}: {task.name}")
        print(f"{'='*60}\n")

        self.log(f"\n## 任务 {task.id}: {task.name}\n")
        self.log(f"**任务类型**: {task.task_type}\n")
        self.log(f"**描述**: {task.description}\n")

        # 种子已覆盖的定义任务：不再调用 agent 重复定义
        seed_skip = {
            "1.1": ("vec", "-- vec 已在种子库 lean_library_seed.txt 中定义，无需重复定义"),
            "1.2": ("dot", "-- dot 已在种子库 lean_library_seed.txt 中定义，无需重复定义"),
            "1.3": ("det", "-- det 已在种子库 lean_library_seed.txt 中定义，无需重复定义"),
        }
        if task.id in seed_skip:
            _name, note = seed_skip[task.id]
            print(f"⏭️  种子库已有 {_name}，跳过重复定义。\n")
            self.log(f"**跳过**: 种子库已有 `{_name}`\n\n```lean\n{note}\n```\n")
            self.state["definitions"].append(note)
            self.state["completed_tasks"].append(task.id)
            self.save_state()
            return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"尝试 {attempt_num}/{max_attempts}...")
            self.log(f"\n### 尝试 {attempt_num}\n")

            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # 调用 API，带重试机制
                max_api_retries = 3
                api_retry_delay = 10

                for api_attempt in range(max_api_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=4096
                        )
                        # 调试：打印响应类型
                        print(f"DEBUG: response type = {type(response)}")
                        if isinstance(response, str):
                            print(f"DEBUG: response content (first 200 chars) = {response[:200]}")
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
                                print(f"❌ API速率限制，已达最大重试次数")
                                raise
                        else:
                            raise

                # 处理响应格式
                if isinstance(response, str):
                    # 如果返回的是字符串，尝试解析JSON
                    try:
                        import json
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

                print(f"DEBUG: agent_output length = {len(agent_output) if agent_output else 0}")
                print(f"DEBUG: agent_output preview = {agent_output[:300] if agent_output else 'None'}")

                elapsed = time.time() - start_time

                print(f"\n⏱️  耗时: {elapsed:.2f}秒")
                print(f"🔢 Tokens: {total_tokens}")

                self.log(f"**耗时**: {elapsed:.2f}秒")
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

                # 直接使用编译器输出作为错误信息
                formatted_error = compiler_output

                # 记录尝试（保存原始完整错误）
                attempt = TaskAttempt(
                    task_id=task.id,
                    attempt_number=attempt_num,
                    agent_output=extracted_code,
                    success=(is_valid is True),
                    error_type="C" if is_valid is False else None,
                    compiler_output=compiler_output,  # 原始完整错误
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

                    # 保存到状态
                    if task.task_type == "definition":
                        self.state["definitions"].append(extracted_code)
                    else:
                        self.state["theorems"].append(extracted_code)

                    self.state["completed_tasks"].append(task.id)
                    self.save_state()
                    self.save_library()
                    return True
                else:
                    print(f"❌ 验证失败，准备下一次尝试...\n")
                    previous_error = formatted_error  # 使用格式化后的错误

            except Exception as e:
                print(f"❌ 出错: {e}\n")
                self.log(f"❌ **错误**: {e}\n")
                previous_error = str(e)

        print(f"❌ 任务 {task.id} 失败（已达最大尝试次数）\n")
        self.log(f"❌ **任务失败**（{max_attempts} 次尝试）\n")
        return False

    def run_all(self, max_tasks=None):
        """运行所有任务"""
        self.start_time = time.time()

        tasks_to_run = LEAN_TASKS[:max_tasks] if max_tasks else LEAN_TASKS
        print(f"🚀 开始运行 {len(tasks_to_run)} 个 definition 任务\n")

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
        print(f"成功: {success_count}")
        print(f"失败: {len(tasks_to_run) - success_count}")
        print(f"总耗时: {self.total_time/60:.1f} 分钟")
        print(f"Axiom 债务: {len(self.state['axiom_debt'])} 条")

        self.save_library()

# ========================================
# 主程序
# ========================================

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Lean Definition自动构建系统')
    parser.add_argument('--verbosity', type=str, default='full',
                        choices=['minimal', 'medium', 'no_recursive', 'full'],
                        help='错误信息详细程度')
    parser.add_argument('--output-suffix', type=str, default='',
                        help='输出目录后缀（用于消融实验分组）')
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
        output_dir = script_dir / "lean_ablation" / f"group_{args.output_suffix}" / "definitions_only"
    else:
        output_dir = script_dir / "lean_auto_validated_250tasks" / "definitions_only"

    # 创建实验
    experiment = LeanExperimentWithValidation(
        api_key=API_KEY,
        base_url=BASE_URL,
        model=MODEL,
        base_output_dir=output_dir,
        verbosity=args.verbosity
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

