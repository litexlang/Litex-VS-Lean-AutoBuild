"""Lean 实验 prompt / 库上下文：与 Litex 侧对齐的薄种子提示。"""

from __future__ import annotations

from typing import Dict, List, Optional


def seed_prompt_blurb(library_seed: str) -> str:
    """提示词用的薄种子说明：已有定义，禁止重复。"""
    return (
        "# ========== 种子库（已在验证环境中加载，禁止重复定义）==========\n"
        "# 已有：Point、vec、dot、det（含 import）。下面仅供阅读参考，不要再次 def / import。\n\n"
        + library_seed.strip()
        + "\n"
    )


def agent_library_prompt(definitions: List[str], theorems: List[str]) -> str:
    """提示词里的「当前库」：只有本实验 agent 新写出的定义/定理。"""
    parts: List[str] = []
    if definitions:
        parts.append("-- 本实验已定义的概念\n" + "\n\n".join(definitions))
    if theorems:
        parts.append("-- 本实验已证明的定理\n" + "\n\n".join(theorems))
    if not parts:
        return "-- （尚无本实验新增定义/定理）\n"
    return "\n\n".join(parts) + "\n"


def full_library_context(
    library_seed: str, definitions: List[str], theorems: List[str]
) -> str:
    """完整库文件/验证用：种子 + 累积产物。"""
    context = library_seed + "\n\n"
    if definitions:
        context += "-- ========== 已定义的概念 ==========\n\n"
        context += "\n\n".join(definitions) + "\n\n"
    if theorems:
        context += "-- ========== 已证明的定理 ==========\n\n"
        context += "\n\n".join(theorems) + "\n\n"
    return context


def build_agent_prompt(
    *,
    library_seed: str,
    definitions: List[str],
    theorems: List[str],
    syntax_guide: str,
    task_id: str,
    task_name: str,
    task_description: str,
    task_type: str,
    hints: Optional[List[str]] = None,
    previous_error: Optional[str] = None,
) -> str:
    """构建给 Agent 的完整 prompt（薄种子 + agent 累积 + 指南 + 任务）。"""
    prompt = f"""{seed_prompt_blurb(library_seed)}

# ========== 当前实验库状态（agent 新增）==========

{agent_library_prompt(definitions, theorems)}

{syntax_guide}

# ========== 任务 {task_id}: {task_name} ==========

**描述**: {task_description}

**任务类型**: {task_type}

重要：种子库里的 Point / vec / dot / det 已存在。若任务是「定义」它们，请输出一行注释说明已在种子库中定义，不要再次 def。

"""
    if hints:
        prompt += "**提示**:\n"
        for hint in hints:
            prompt += f"- {hint}\n"
        prompt += "\n"

    if previous_error:
        prompt += f"""# ========== 上一次尝试的错误 ==========

{previous_error}

请根据错误信息修正代码。

"""

    prompt += """请提供完整的 Lean 代码。只返回代码，不要额外解释。

⚠️ 重要提醒：
1. 不要包含 import 语句（种子库已经包含了）
2. 不要重新定义 Point, vec, dot, det（种子库已经定义了）
3. 只写新的定义或定理
"""
    return prompt


SEED_SKIP_NOTES: Dict[str, tuple] = {
    "1.1": ("vec", "-- vec 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
    "1.2": ("dot", "-- dot 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
    "1.3": ("det", "-- det 已在种子库 agent_library_seed.txt 中定义，无需重复定义"),
}


def maybe_seed_skip_note(task_id: str, task_name: str) -> Optional[tuple]:
    """若任务被种子覆盖，返回 (symbol, note)；否则 None。"""
    if task_id not in SEED_SKIP_NOTES:
        return None
    name, note = SEED_SKIP_NOTES[task_id]
    if f"定义{name}" in task_name or name in task_name.lower():
        return name, note
    return None
