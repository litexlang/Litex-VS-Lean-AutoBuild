"""
Lean persistent session validation: incremental validation using leanprover-community/repl (JSON stdin/stdout).

Protocol:
  Launch: `lake env <repl_bin>` (cwd = Lean project, with Mathlib search path)
  Command: one line JSON + blank line; response: JSON (may be multiline) + blank line
  Success: no message with severity=error → adopt returned env
  Failure: do not switch env (≈ Litex try RolledBack); success advances env (≈ Committed)

Note: REPL may still return a new env number when elaboration fails; this module intentionally ignores that number.
"""

from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Pre-built REPL in repository (lean_auto_build_system/.tools/repl)
_DEFAULT_REPL_REL = Path(__file__).resolve().parent / ".tools" / "repl" / ".lake" / "build" / "bin" / "repl"

# Fallback to directory with Mathlib when LeanGeo is empty
_FALLBACK_LEAN_PROJECTS = [
    Path(__file__).resolve().parents[2] / "LeanGeo",
]


def find_lake_bin() -> Optional[Path]:
    candidates = [
        os.environ.get("LAKE_BIN"),
        str(Path.home() / ".elan" / "bin" / "lake"),
        "lake",
    ]
    for c in candidates:
        if not c:
            continue
        if c == "lake":
            from shutil import which

            found = which("lake")
            if found:
                return Path(found)
            continue
        p = Path(c)
        if p.is_file() and os.access(p, os.X_OK):
            return p
    return None


def find_repl_bin() -> Optional[Path]:
    candidates = [
        os.environ.get("LEAN_REPL_BIN"),
        str(_DEFAULT_REPL_REL),
    ]
    for c in candidates:
        if not c:
            continue
        p = Path(c)
        if p.is_file() and os.access(p, os.X_OK):
            return p
    return None


def resolve_lean_project_dir(preferred: Optional[str | Path] = None) -> Path:
    """
    Select Lean project directory with Mathlib.
    Priority: explicit path / LEAN_PROJECT_DIR / LeanGeo (if lakefile exists) / golitex/lean.
    """
    env = os.environ.get("LEAN_PROJECT_DIR")
    candidates: List[Path] = []
    if preferred:
        candidates.append(Path(preferred))
    if env:
        candidates.append(Path(env))
    # lean_auto_build_system/../LeanGeo
    script_parent = Path(__file__).resolve().parent.parent
    candidates.append(script_parent.parent / "LeanGeo")
    candidates.extend(_FALLBACK_LEAN_PROJECTS)

    seen = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except Exception:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        if not rp.is_dir():
            continue
        if (rp / "lakefile.toml").exists() or (rp / "lakefile.lean").exists():
            return rp
    # Still return preferred/LeanGeo at the end, for clearer error messages upstream
    if preferred:
        return Path(preferred)
    return script_parent.parent / "LeanGeo"


def extract_lean_code(agent_output: str) -> str:
    match = re.search(r"```lean\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return agent_output.strip()


def strip_imports_for_incremental(code: str) -> str:
    """Cannot import again when env already exists; remove top-level import/open lines (keep comments and code)."""
    lines = code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: List[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("import ") or stripped.startswith("prelude"):
            continue
        out.append(line)
    return "\n".join(out).strip()


def lean_code_is_noop(code: str) -> bool:
    """Pure whitespace/line comments: don't send to REPL (avoid unexpected end of input)."""
    text = code.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return True
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        return False
    return True


def should_record_commit(code: str) -> bool:
    """Successful #check / #print queries also not written to accumulated library."""
    if lean_code_is_noop(code):
        return False
    body = strip_imports_for_incremental(code)
    for line in body.split("\n"):
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        if s.startswith("#"):
            continue
        return True
    return False

def _messages_have_error(resp: Dict[str, Any]) -> bool:
    for msg in resp.get("messages") or []:
        if isinstance(msg, dict) and msg.get("severity") == "error":
            return True
    return False


def _format_repl_errors(resp: Dict[str, Any]) -> str:
    """Extract detailed error information from REPL response"""
    parts: List[str] = ["❌ Validation failed (env not advanced, session continues)"]

    for msg in resp.get("messages") or []:
        if not isinstance(msg, dict) or msg.get("severity") != "error":
            continue

        # Extract position information
        pos = msg.get("pos") or {}
        line = pos.get("line", "?")
        col = pos.get("column", "?")

        # Extract error data
        data = (msg.get("data") or "").strip()

        # Format error message
        error_parts = [f"❌ Compilation error (line {line}:{col}):"]

        # Split error message, extract key parts
        if data:
            lines = data.split('\n')
            # First line is usually the error type
            if lines:
                error_parts.append(lines[0])

            # Extract detailed information
            detail_lines = []
            for i, line_text in enumerate(lines[1:], 1):
                stripped = line_text.strip()
                if stripped:
                    # Identify important error messages
                    if stripped.startswith('⊢') or stripped.startswith('|') or stripped.startswith('expected'):
                        detail_lines.append(f"  {stripped}")
                    else:
                        detail_lines.append(stripped)

            if detail_lines:
                error_parts.append("\n".join(detail_lines))

        parts.append("\n".join(error_parts))

    # If no useful information extracted, show raw response
    if len(parts) == 1:
        raw = json.dumps(resp, ensure_ascii=False)[:800]
        parts.append(f"Raw response:\n{raw}")

    return "\n\n".join(parts)


class LeanPersistentSession:
    """Long-lived lake env + leanprover-community/repl process."""

    def __init__(
        self,
        lean_project_dir: Path,
        lake_bin: Path,
        repl_bin: Path,
        seed_source: str,
        cmd_timeout: float = 180.0,
    ):
        self.lean_project_dir = Path(lean_project_dir)
        self.lake_bin = Path(lake_bin)
        self.repl_bin = Path(repl_bin)
        self.seed_source = seed_source
        self.cmd_timeout = cmd_timeout
        self.proc: Optional[subprocess.Popen] = None
        self._stdout_q: "queue.Queue[Optional[str]]" = queue.Queue()
        self._reader: Optional[threading.Thread] = None
        self.env: Optional[int] = None
        self.alive = False

    def start(self) -> None:
        self.close()
        self.proc = subprocess.Popen(
            [str(self.lake_bin), "env", str(self.repl_bin)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=str(self.lean_project_dir),
        )
        self._reader = threading.Thread(target=self._enqueue_stdout, daemon=True)
        self._reader.start()
        self.alive = True
        self.env = None

        seed = self.seed_source.strip()
        if seed:
            # Keep imports when loading seed library for the first time (because use_env=False)
            # REPL can only use import statements when there is no env
            ok, msg, resp = self.run_command(seed, use_env=False)
            if not ok:
                self.close()
                raise RuntimeError(f"Seed loading failed: {msg}\n{json.dumps(resp, ensure_ascii=False)[:500]}")

    def _enqueue_stdout(self) -> None:
        assert self.proc and self.proc.stdout
        try:
            for line in self.proc.stdout:
                self._stdout_q.put(line)
        finally:
            self._stdout_q.put(None)

    def _drain_stderr(self) -> str:
        if not self.proc or not self.proc.stderr:
            return ""
        try:
            # Non-blocking read as much as possible; stderr may block while process is alive, limit time
            chunks: List[str] = []
            self.proc.stderr.flush()
            return "".join(chunks)
        except Exception:
            return ""

    def _read_json_response(self, timeout: float) -> Optional[Dict[str, Any]]:
        """Read text block until blank line, then json.loads (supports multiline pretty JSON)."""
        deadline = time.time() + timeout
        buf: List[str] = []
        while time.time() < deadline:
            remaining = deadline - time.time()
            try:
                line = self._stdout_q.get(timeout=min(0.5, max(remaining, 0.01)))
            except queue.Empty:
                if self.proc and self.proc.poll() is not None:
                    return None
                continue
            if line is None:
                return None
            if line == "\n" or line.strip() == "":
                if not buf:
                    continue
                text = "".join(buf).strip()
                if not text:
                    buf = []
                    continue
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # May not be complete yet; continue accumulating (very rare)
                    buf.append(line)
                    continue
            buf.append(line)
        return None

    def run_command(
        self, cmd: str, *, use_env: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        if not self.alive or not self.proc or not self.proc.stdin:
            return False, "❌ REPL session not started", {}

        payload: Dict[str, Any] = {"cmd": cmd}
        if use_env:
            if self.env is None:
                return False, "❌ REPL env not established (seed not loaded?)", {}
            payload["env"] = self.env

        try:
            self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n\n")
            self.proc.stdin.flush()
        except BrokenPipeError:
            self.alive = False
            return False, "❌ REPL pipe broken", {}

        resp = self._read_json_response(timeout=self.cmd_timeout)
        if resp is None:
            self.alive = False
            err = ""
            if self.proc and self.proc.stderr:
                try:
                    # Process may be hung, try to read a bit of stderr
                    pass
                except Exception:
                    pass
            return False, f"❌ Compilation timeout ({int(self.cmd_timeout)}s) or REPL no response{err}", {}

        if _messages_have_error(resp):
            # Critical: do not adopt resp["env"]
            return False, _format_repl_errors(resp), resp

        if "env" in resp:
            self.env = resp["env"]
        return True, "✅ Compilation passed (REPL env committed)", resp

    def close(self) -> None:
        self.alive = False
        self.env = None
        if self.proc:
            try:
                if self.proc.stdin:
                    self.proc.stdin.close()
            except Exception:
                pass
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None
        # Clear queue residue
        while not self._stdout_q.empty():
            try:
                self._stdout_q.get_nowait()
            except Exception:
                break


class SessionBackedValidator:
    """
    Validator for experiment runner:
    - Seed commits once on startup
    - validate(code) only sends increments; success advances env, failure rolls back (does not switch env)
    - library_context parameter kept for compatibility, ignored in session mode
    - Falls back to lake env lean whole file when REPL unavailable
    """

    def __init__(
        self,
        seed_source: str,
        lean_project_dir: Optional[str | Path] = None,
        cmd_timeout: float = 180.0,
    ):
        self.seed_source = seed_source
        self.cmd_timeout = cmd_timeout
        self.lake_bin = find_lake_bin()
        self.repl_bin = find_repl_bin()
        self.lean_project_dir = resolve_lean_project_dir(lean_project_dir)
        self.session: Optional[LeanPersistentSession] = None
        self.committed: List[str] = []
        self.mode = "none"  # "repl" | "file" | "none"

        if self.lake_bin and self.repl_bin:
            print(f"✅ lake: {self.lake_bin}")
            print(f"✅ Lean REPL: {self.repl_bin}")
            print(f"✅ Lean project: {self.lean_project_dir}")
            try:
                self._ensure_session()
                self.mode = "repl"
                print("✅ Validation mode: Lean REPL session (incremental env)")
            except Exception as e:
                print(f"⚠️  REPL session startup failed, falling back to whole file: {e}")
                self.mode = "file"
        elif self.lake_bin:
            print(f"✅ lake: {self.lake_bin}")
            print(f"⚠️  REPL not found (can set LEAN_REPL_BIN), falling back to lake env lean whole file")
            print(f"📚 Lean project: {self.lean_project_dir}")
            self.mode = "file"
        else:
            print("⚠️  lake not found, will not be able to auto-validate")

    @property
    def lake_bin_ok(self) -> bool:
        return self.lake_bin is not None

    def _ensure_session(self) -> None:
        if self.session and self.session.alive and self.session.env is not None:
            return
        if not self.lake_bin or not self.repl_bin:
            raise RuntimeError("lake/repl unavailable")
        self.session = LeanPersistentSession(
            lean_project_dir=self.lean_project_dir,
            lake_bin=self.lake_bin,
            repl_bin=self.repl_bin,
            seed_source=self.seed_source,
            cmd_timeout=self.cmd_timeout,
        )
        self.session.start()
        for code in self.committed:
            body = strip_imports_for_incremental(code)
            if not body.strip():
                continue
            ok, msg, _ = self.session.run_command(body, use_env=True)
            if not ok:
                print(f"⚠️  Replay of committed code failed: {msg[:200]}")
                break

    def extract_lean_code(self, agent_output: str) -> str:
        return extract_lean_code(agent_output)

    def validate(self, code: str, library_context: str = "") -> Tuple[Optional[bool], str, Dict[str, Any]]:
        if self.mode == "none":
            return None, "lake unavailable", {}

        if self.mode == "repl":
            return self._validate_repl(code)

        return self._validate_file(code, library_context)

    def _validate_repl(self, code: str) -> Tuple[Optional[bool], str, Dict[str, Any]]:
        if lean_code_is_noop(code):
            # Empty/pure comments: consider passed, do not advance (consistent with "seed already has it, no need to redefine")
            return True, "✅ Compilation passed (empty increment / comments only, env unchanged)", {}

        body = strip_imports_for_incremental(code)
        if not body.strip():
            return True, "✅ Compilation passed (empty increment / comments only, env unchanged)", {}

        try:
            self._ensure_session()
        except Exception as e:
            return None, f"⚠️  Cannot start Lean REPL session: {e}", {}

        assert self.session is not None
        ok, msg, resp = self.session.run_command(body, use_env=True)
        if not ok and ("no response" in msg or "pipe broken" in msg or "timeout" in msg):
            try:
                if self.session:
                    self.session.close()
                self.session = None
                self._ensure_session()
                assert self.session is not None
                ok, msg, resp = self.session.run_command(body, use_env=True)
            except Exception as e:
                return False, f"{msg}\nREPL restart failed: {e}", {}
        if ok and should_record_commit(code):
            self.committed.append(code)
        return ok, msg, resp

    def _validate_file(self, code: str, library_context: str) -> Tuple[Optional[bool], str, Dict[str, Any]]:
        import tempfile

        if not self.lake_bin:
            return None, "lake unavailable", {}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".lean", delete=False, encoding="utf-8"
        ) as f:
            f.write((library_context or self.seed_source) + "\n" + code)
            temp_file = f.name

        try:
            result = subprocess.run(
                [str(self.lake_bin), "env", "lean", temp_file],
                capture_output=True,
                text=True,
                timeout=int(self.cmd_timeout),
                cwd=str(self.lean_project_dir),
            )
            output = (result.stdout or "") + (result.stderr or "")
            if result.returncode == 0 and "error:" not in output.lower():
                self.committed.append(code)
                return True, "✅ Compilation passed (whole file fallback)", {}
            return False, self._parse_lean_file_errors(output), {}
        except subprocess.TimeoutExpired:
            return False, f"❌ Compilation timeout ({int(self.cmd_timeout)}s)", {}
        except Exception as e:
            return False, f"❌ Validation failed: {e}", {}
        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

    @staticmethod
    def _parse_lean_file_errors(output: str) -> str:
        errors: List[str] = []
        lines = output.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            error_match = re.match(r"^(.+):(\d+):(\d+): error: (.+)$", line)
            if error_match:
                _file, line_num, col, error_type = error_match.groups()
                error_parts = [f"❌ Compilation error (line {line_num}:{col}): {error_type}"]
                i += 1
                details: List[str] = []
                while i < len(lines):
                    if re.match(r"^(.+):(\d+):(\d+): error:", lines[i]):
                        break
                    if lines[i].startswith("warning:") or lines[i].startswith("info:"):
                        break
                    if lines[i].strip():
                        details.append(lines[i])
                    i += 1
                if details:
                    error_parts.append("\n".join(details))
                errors.append("\n".join(error_parts))
                continue
            i += 1
        if errors:
            return "\n\n".join(errors)
        return f"❌ Compilation failed:\n{output[:500]}"

    def close(self) -> None:
        if self.session:
            self.session.close()
            self.session = None

    def export_session_library(self, seed_source: str) -> str:
        parts = [
            "-- ============================================================",
            "-- LeanGeo AutoBuild — REPL session export library",
            f"-- committed entries count: {len(self.committed)}",
            "-- ============================================================",
            "",
            seed_source.rstrip(),
            "",
            "-- ---------- session committed content ----------",
            "",
        ]
        for block in self.committed:
            parts.append(block.rstrip())
            parts.append("")
        return "\n".join(parts).rstrip() + "\n"


# Compatible old name
LeanValidator = SessionBackedValidator
