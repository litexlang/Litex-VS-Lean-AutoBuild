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

# 导入验证器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from litex_session import SessionBackedValidator

# 兼容旧名
GolitexValidator = SessionBackedValidator

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

LITEX_TASKS = [
    Task(
        id="1.1",
        stage=1,
        name="定义vec函数",
        description="定义从点A到点B的向量，用坐标差(B[1]-A[1], B[2]-A[2])表示平面上两点间的有向线段。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.2",
        stage=1,
        name="定义dot函数",
        description="定义两个向量的点积（内积），计算u[1]*v[1] + u[2]*v[2]，用于衡量向量间的投影关系和夹角余弦。",
        task_type="definition",
        hints=[]
    ),
    Task(
        id="1.3",
        stage=1,
        name="定义det函数",
        description="定义两个向量的行列式（外积的标量部分），计算u[1]*v[2] - u[2]*v[1]，用于判断向量的相对方向和面积。",
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
        seed_file = Path(__file__).parent.parent / "database" / "definition_library_seed.lit"
        if not seed_file.exists():
            raise FileNotFoundError(
                f"种子文件不存在: {seed_file}\n"
                f"请确保 database/definition_library_seed.lit 文件存在"
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

        # 种子已覆盖的定义任务：不再调用 agent 重复 have fn
        seed_skip = {
            "1.1": ("vec", "# vec 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
            "1.2": ("dot", "# dot 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
            "1.3": ("det", "# det 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
        }
        if task.id in seed_skip:
            _name, note = seed_skip[task.id]
            print(f"⏭️  种子库已有 {_name}，跳过重复定义。\n")
            self.log(f"**跳过**: 种子库已有 `{_name}`\n\n```litex\n{note}\n```\n")
            self.state["definitions"].append(note)
            self.state["completed_tasks"].append(task.id)
            self.save_state()
            return True

        previous_error = None
        last_code = None

        for attempt_num in range(1, max_attempts + 1):
            print(f"尝试 {attempt_num}/{max_attempts}...")
            self.log(f"\n### 尝试 {attempt_num}\n")

            # 构建 prompt（包含上次错误）
            prompt = self.build_prompt(task, attempt_num, previous_error)
            start_time = time.time()

            try:
                # 调用 Agent，带重试机制处理速率限制
                max_api_retries = 3
                api_retry_delay = 10  # 秒

                for api_attempt in range(max_api_retries):
                    try:
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=4096
                        )
                        break  # 成功则跳出重试循环
                    except Exception as api_error:
                        error_str = str(api_error)
                        # 检查是否是速率限制错误
                        if "429" in error_str or "rate_limit" in error_str or "cooldown" in error_str:
                            if api_attempt < max_api_retries - 1:
                                print(f"⚠️  API速率限制，等待{api_retry_delay}秒后重试...")
                                time.sleep(api_retry_delay)
                                api_retry_delay *= 2  # 指数退避
                                continue
                            else:
                                print(f"❌ API速率限制，已达最大重试次数")
                                raise
                        else:
                            # 其他错误直接抛出
                            raise

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
        """运行所有任务"""
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
            print("="*60)

            self.start_time = time.time()

            # 限制任务数量
            tasks_to_run = LITEX_TASKS[:max_tasks] if max_tasks else LITEX_TASKS
            if max_tasks:
                print(f"🎯 限制运行前 {max_tasks} 个任务\n")

            # 统计成功和失败的任务
            completed_tasks = []
            failed_tasks = []

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
            print(f"✅ 成功: {len(completed_tasks)}/{len(tasks_to_run)} 个任务")
            print(f"❌ 失败: {len(failed_tasks)}/{len(tasks_to_run)} 个任务")

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

    # 使用脚本所在目录下的 definitions_only 子目录
    output_dir = script_dir / "litex_auto_validated_250tasks" / "definitions_only"

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
