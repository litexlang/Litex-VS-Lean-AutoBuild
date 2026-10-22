"""
Litex Persistent session validation: using `litex -isolated -session` + `try:` for incremental validation.

Protocol (golitex framed session):
  Read ready event after startup;
  Send: run <id> <utf8byte count>\\n<source>;
  Failed try will be RolledBack, session can continue;
  Successful try will be Committed, definition/theorem enters environment.
"""

from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def find_litex_bin() -> Optional[str]:
    """Find litex that supports -session by common paths."""
    # Build relative path
    script_dir = Path(__file__).resolve().parent
    relative_litex = script_dir.parent.parent / "LitexGeo" / "golitex" / "litex_0.9.116-beta_darwin_arm64" / "litex"

    candidates = [
        os.environ.get("LITEX_BIN"),
        str(relative_litex),  # use relative path
        str(Path(__file__).resolve().parents[2] / "LitexGeo" / "golitex" / "litex_0.9.116-beta_darwin_arm64" / "litex"),
        "/opt/homebrew/bin/litex",
        "litex",
    ]
    for path in candidates:
        if not path:
            continue
        if path == "litex":
            from shutil import which

            found = which("litex")
            if found and _litex_supports_session(found):
                return found
            continue
        if os.path.isfile(path) and os.access(path, os.X_OK) and _litex_supports_session(path):
            return path
    return None


def _litex_supports_session(bin_path: str) -> bool:
    try:
        result = subprocess.run(
            [bin_path, "-help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return "-session" in out
    except Exception:
        return False


def indent_block(source: str, spaces: int = 4) -> str:
    pad = " " * spaces
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(pad + line if line.strip() else line for line in lines)


def wrap_in_try(source: str) -> str:
    """wrap candidate code in try:，failed rollback, successful commit。"""
    body = source.strip("\n")
    if not body.strip():
        return "try:\n    1 = 1\n"
    return "try:\n" + indent_block(body, 4) + "\n"


def extract_litex_code(agent_output: str) -> str:
    match = re.search(r"```litex\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return agent_output.strip()


def thm_to_axiom(code: str) -> Optional[str]:
    """
    Convert thm declaration to axiom：keep `? forall ...` goal block，remove proof body。
    """
    text = code.strip()
    if not text.startswith("thm "):
        return None
    lines = text.split("\n")
    header = lines[0]
    name_match = re.match(r"thm\s+(\w+)\s*:", header)
    if not name_match:
        return None
    name = name_match.group(1)

    # find ? line and its indentation；goal continues at deeper indentation；return to same indentation level means proof body
    q_idx = None
    q_indent = None
    for i, line in enumerate(lines[1:], start=1):
        if line.lstrip().startswith("?"):
            q_idx = i
            q_indent = len(line) - len(line.lstrip(" "))
            break
    if q_idx is None or q_indent is None:
        return None

    end = len(lines)
    for i in range(q_idx + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent <= q_indent:
            end = i
            break

    goal_lines = lines[q_idx:end]
    return f"axiom {name}:\n" + "\n".join(goal_lines).rstrip() + "\n"


def _format_rollback_error(event: Dict[str, Any]) -> str:
    """Extract readable error from session result / RolledBack structure。"""
    parts: List[str] = ["❌ validation failed (try rolled back, session continues)"]

    # Handle event: "block" type error (contains trace field)
    if event.get("event") == "block" and event.get("ok") is False:
        trace_str = event.get("trace", "")
        if trace_str:
            try:
                trace = json.loads(trace_str)
                error_type = trace.get("error_type", "error")
                line = trace.get("line", "?")
                message = trace.get("message", "")
                if message:
                    parts.append(f"\n({error_type}, line {line}):\n{message}")
                else:
                    parts.append(f"\n({error_type}, line {line})")
            except json.JSONDecodeError:
                parts.append(f"\nerror message: {trace_str}")

    # Handle standard statement_results structure
    for stmt in event.get("statement_results") or []:
        result = stmt.get("result") or {}
        execution = result.get("execution") or {}
        if execution.get("kind") != "RolledBack":
            # may also be directly in nested error
            pass
        err = execution.get("error") or event.get("error") or {}
        if isinstance(err, dict):
            msg = err.get("message") or err.get("msg") or ""
            kind = err.get("kind") or err.get("error_type") or "error"
            line = err.get("line", "?")
            if msg:
                parts.append(f"\n({kind}, line {line}):\n{msg}")
            if "statement" in err:
                parts.append(f"\nfailed statement:\n{err['statement']}")
            if "failed_goal" in err:
                parts.append(f"\nfailed goal:\n{err['failed_goal']}")
            unknown = err.get("unknown_result") or {}
            if isinstance(unknown, dict):
                if "type" in unknown:
                    parts.append(f"\nReason type: {unknown['type']}")
                if "goal" in unknown:
                    parts.append(f"\nUnknown goal: {unknown['goal']}")

            # recursively extract all previous_error（complete error chain，same as old system）
            def extract_previous_errors(err_obj, depth=1):
                if "previous_error" not in err_obj:
                    return []

                prev_errors = []
                prev = err_obj["previous_error"]

                # extract this layer information
                if "message" in prev:
                    prefix = "Detailed reason" if depth == 1 else f"Reason{depth}"
                    prev_errors.append(f"\n{prefix}: {prev['message']}")

                if "failed_goal" in prev and "failed_goal" not in err_obj:
                    prev_errors.append(f"\nfailed goal:\n{prev['failed_goal']}")

                if "unknown_result" in prev:
                    unknown_prev = prev["unknown_result"]
                    if isinstance(unknown_prev, dict):
                        if "type" in unknown_prev:
                            prev_errors.append(f"\nReason type: {unknown_prev['type']}")

                # recursively extract deeper layers
                prev_errors.extend(extract_previous_errors(prev, depth + 1))
                return prev_errors

            # Add all previous_error information
            parts.extend(extract_previous_errors(err))
        # Compatible with statement_results top-level failed_goal display field
        if "failed_goal" in result:
            parts.append(f"\nfailed goal:\n{result['failed_goal']}")

    # Handle event-level error field
    if event.get("error"):
        parts.append(f"\nerror: {json.dumps(event['error'], ensure_ascii=False)[:800]}")

    # Only dump entire event if no useful information extracted (as last resort)
    if len(parts) == 1:
        parts.append("\n（raw error message）：\n" + json.dumps(event, ensure_ascii=False)[:1200])

    return "".join(parts)


def _is_committed(event: Dict[str, Any]) -> bool:
    if event.get("ok") is False:
        return False
    results = event.get("statement_results") or []
    if not results:
        return bool(event.get("ok"))
    for stmt in results:
        result = stmt.get("result") or {}
        execution = result.get("execution") or {}
        kind = execution.get("kind")
        if kind == "RolledBack":
            return False
        if stmt.get("outcome") == "error" or result.get("kind") == "error":
            return False
    return True


class LitexPersistentSession:
    """Long-lived litex -session process."""

    def __init__(self, litex_bin: str, seed_source: str, frame_timeout: float = 120.0):
        self.litex_bin = litex_bin
        self.seed_source = seed_source
        self.frame_timeout = frame_timeout
        self.proc: Optional[subprocess.Popen] = None
        self._stdout_q: "queue.Queue[Optional[str]]" = queue.Queue()
        self._reader: Optional[threading.Thread] = None
        self._seed_path: Optional[str] = None
        self._frame_counter = 0
        self.alive = False

    def start(self) -> None:
        self.close()
        seed_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".lit", delete=False, encoding="utf-8"
        )
        seed_file.write(self.seed_source)
        seed_file.close()
        self._seed_path = seed_file.name

        self.proc = subprocess.Popen(
            [self.litex_bin, "-isolated", "-session", "-f", self._seed_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._reader = threading.Thread(target=self._enqueue_stdout, daemon=True)
        self._reader.start()
        ready = self._read_json(timeout=30.0)
        if not ready or ready.get("event") != "ready":
            err = self._drain_stderr()
            self.close()
            raise RuntimeError(f"litex session failed to ready: {ready}; stderr={err[:500]}")
        self.alive = True

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
            return self.proc.stderr.read() or ""
        except Exception:
            return ""

    def _read_json(self, timeout: float) -> Optional[Dict[str, Any]]:
        deadline = time.time() + timeout
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
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                # skip non-JSON lines
                continue
        return None

    def run_source(self, source: str, frame_id: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run a piece of source code in the session (caller decides whether to wrap in try).
        Returns (committed_ok, message, raw_event)
        """
        if not self.alive or not self.proc or not self.proc.stdin:
            return False, "❌ session not started", {}

        self._frame_counter += 1
        fid = frame_id or f"f{self._frame_counter}"
        data = source.encode("utf-8")
        header = f"run {fid} {len(data)}\n"
        try:
            self.proc.stdin.write(header)
            self.proc.stdin.write(source)
            self.proc.stdin.flush()
        except BrokenPipeError:
            self.alive = False
            return False, "❌ session pipe broken", {}

        event = self._read_json(timeout=self.frame_timeout)
        if event is None:
            self.alive = False
            return False, f"❌ compilation timeout（{int(self.frame_timeout)}seconds）or session not responding", {}

        if event.get("event") == "skipped":
            self.alive = False
            return False, "❌ session already skipped due to previous failure，needs restart", event

        if event.get("event") == "protocol_error":
            return False, f"❌ session protocol error:\n{json.dumps(event, ensure_ascii=False)[:800]}", event

        if _is_committed(event):
            return True, "✅ compilation passed（session try committed）", event

        return False, _format_rollback_error(event), event

    def run_try(self, code: str, frame_id: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        return self.run_source(wrap_in_try(code), frame_id=frame_id)

    def close(self) -> None:
        self.alive = False
        if self.proc and self.proc.stdin:
            try:
                self.proc.stdin.write("close\n")
                self.proc.stdin.flush()
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
        if self._seed_path:
            try:
                os.unlink(self._seed_path)
            except Exception:
                pass
            self._seed_path = None


class SessionBackedValidator:
    """
    validator for experiment runner：
    - successful code committed via try into persistent session
    - failed try rollback，does not pollute library
    - optional: use axiom as fallback when finally failed
    """

    def __init__(self, seed_source: str, frame_timeout: float = 120.0):
        self.litex_bin = find_litex_bin()
        self.seed_source = seed_source
        self.frame_timeout = frame_timeout
        self.session: Optional[LitexPersistentSession] = None
        self.committed: List[str] = []  # successfully committed definitions/theorem（includes axiom）
        self.axioms: List[str] = []
        if self.litex_bin:
            print(f"✅ litex compiler loaded (session mode): {self.litex_bin}")
            self._ensure_session()
        else:
            print("⚠️  did not find litex supporting -session, will not be able to auto-validate")

    def _ensure_session(self) -> None:
        if self.session and self.session.alive:
            return
        if not self.litex_bin:
            return
        self.session = LitexPersistentSession(
            self.litex_bin, self.seed_source, frame_timeout=self.frame_timeout
        )
        self.session.start()
        for code in self.committed:
            ok, msg, _ = self.session.run_try(code)
            if not ok:
                print(f"⚠️  replaying committed code failed: {msg[:200]}")
                break

    def extract_litex_code(self, agent_output: str) -> str:
        return extract_litex_code(agent_output)

    def validate(self, code: str, library_context: str = "") -> Tuple[Optional[bool], str]:
        """
        library_context parameter kept for compatibility; ignored in session mode (library already in process).
        """
        del library_context  # session already has accumulated state
        if not self.litex_bin:
            return None, "litex compiler unavailable"
        try:
            self._ensure_session()
        except Exception as e:
            return None, f"⚠️  Cannot start litex session: {e}"

        assert self.session is not None
        ok, msg, _event = self.session.run_try(code)
        if not ok and ("skipped" in msg or "not responding" in msg or "pipe broken" in msg):
            try:
                if self.session:
                    self.session.close()
                self.session = None
                self._ensure_session()
                assert self.session is not None
                ok, msg, _event = self.session.run_try(code)
            except Exception as e:
                return False, f"{msg}\nrestart session failed: {e}"
        if ok:
            self.committed.append(code)
        return ok, msg

    def commit_axiom_fallback(self, failed_code: str) -> Tuple[bool, str, Optional[str]]:
        """Convert thm to axiom and submit when proof fails. Returns (ok, msg, axiom_code)."""
        axiom = thm_to_axiom(failed_code)
        if not axiom:
            return False, "cannot generate axiom from failed code", None
        ok, msg = self.validate(axiom)
        if ok:
            self.axioms.append(axiom)
            return True, f"✅ Used axiom as fallback (trust debt +1)\n{axiom}", axiom
        return False, f"axiom commitfailed: {msg}", axiom

    def close(self) -> None:
        if self.session:
            self.session.close()
            self.session = None

    def export_session_library(self, seed_source: str) -> str:
        """
        Export current session accumulated library: seed + all committed code in submission order.
        Convenient to open and modify axiom after run.
        """
        parts = [
            "# ============================================================",
            "# LitexGeo AutoBuild — session exported library",
            f"# committed entries: {len(self.committed)}",
            f"# axiom debt: {len(self.axioms)}",
            "# Usage: search `^axiom ` to find trust debt, change back to thm + proof.",
            "# ============================================================",
            "",
            seed_source.rstrip(),
            "",
        ]
        if self.axioms:
            parts.append("# ---------- Trust Debt Index (axiom) ----------")
            for i, ax in enumerate(self.axioms, 1):
                first = next((ln.strip() for ln in ax.splitlines() if ln.strip()), "")
                parts.append(f"# {i}. {first}")
            parts.append("")

        parts.append("# ---------- session committed content (definition / thm / axiom) ----------")
        parts.append("")
        for block in self.committed:
            parts.append(block.rstrip())
            parts.append("")
        return "\n".join(parts).rstrip() + "\n"
