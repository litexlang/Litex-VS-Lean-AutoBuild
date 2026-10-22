"""Lean experiment prompt / library context: thin seed prompts aligned with Litex side."""

from __future__ import annotations

from typing import Dict, List, Optional


def seed_prompt_blurb(library_seed: str) -> str:
    """Thin seed description for prompts: existing definitions, no duplication."""
    return (
        "# ========== Seed library (already loaded in validation environment, do not redefine) ==========\n"
        "# Already defined: Point, vec, dot, det (including imports). Below for reference only, do not def/import again.\n\n"
        + library_seed.strip()
        + "\n"
    )


def agent_library_prompt(definitions: List[str], theorems: List[str]) -> str:
    """'Current library' in the prompt: only definitions/theorems newly written by this experiment's agent."""
    parts: List[str] = []
    if definitions:
        parts.append("-- Definitions from this experiment\n" + "\n\n".join(definitions))
    if theorems:
        parts.append("-- Theorems proven in this experiment\n" + "\n\n".join(theorems))
    if not parts:
        return "-- (No new definitions/theorems from this experiment yet)\n"
    return "\n\n".join(parts) + "\n"


def full_library_context(
    library_seed: str, definitions: List[str], theorems: List[str]
) -> str:
    """Complete library file/validation use: seed + accumulated artifacts."""
    context = library_seed + "\n\n"
    if definitions:
        context += "-- ========== Defined concepts ==========\n\n"
        context += "\n\n".join(definitions) + "\n\n"
    if theorems:
        context += "-- ========== Proven theorems ==========\n\n"
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
    """Build complete prompt for Agent (thin seed + agent accumulation + guide + task)."""
    prompt = f"""{seed_prompt_blurb(library_seed)}

# ========== Current experiment library state (agent additions) ==========

{agent_library_prompt(definitions, theorems)}

{syntax_guide}

# ========== Task {task_id}: {task_name} ==========

**Description**: {task_description}

**Task type**: {task_type}

Important: Point / vec / dot / det already exist in the seed library. If the task is to 'define' them, output a comment stating they are already defined in the seed library, do not def again.

"""
    if hints:
        prompt += "**Hints**:\n"
        for hint in hints:
            prompt += f"- {hint}\n"
        prompt += "\n"

    if previous_error:
        prompt += f"""# ========== Previous attempt error ==========

{previous_error}

Please fix the code based on the error message.

"""

    prompt += """Please provide complete Lean code. Return only code, no additional explanation.

⚠️ Important reminders:
1. Do not include import statements (seed library already contains them)
2. Do not redefine Point, vec, dot, det (seed library already defines them)
3. Only write new definitions or theorems
"""
    return prompt


SEED_SKIP_NOTES: Dict[str, tuple] = {
    "1.1": ("vec", "-- vec is already defined in seed library agent_library_seed.txt, no need to redefine"),
    "1.2": ("dot", "-- dot is already defined in seed library agent_library_seed.txt, no need to redefine"),
    "1.3": ("det", "-- det is already defined in seed library agent_library_seed.txt, no need to redefine"),
}


def maybe_seed_skip_note(task_id: str, task_name: str) -> Optional[tuple]:
    """If task is covered by seed, return (symbol, note); otherwise None."""
    if task_id not in SEED_SKIP_NOTES:
        return None
    name, note = SEED_SKIP_NOTES[task_id]
    if f"define{name}" in task_name.lower() or name in task_name.lower():
        return name, note
    return None
