"""
Litex Persistent session validation for Litex 1.1.2-beta: using traditional REPL protocol.

Protocol (Litex 1.1.2-beta REPL):
  Start: litex -f <seed_file> -session
  On startup: outputs complete run JSON for seed file
  Input: send code followed by blank line (\\n\\n)
  Output: returns statement result JSON (may be wrapped in run envelope or standalone)
  Failed statements do not pollute the environment (soft failure, session continues)
  Parse/Type errors terminate the session (hard failure, must restart)
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
    relative_litex = script_dir.parent.parent / "LitexGeo" / "golitex" / "target" / "release" / "litex"

    candidates = [
        os.environ.get("LITEX_BIN"),
        str(relative_litex),  # relative path to compiled binary
        str(Path(__file__).resolve().parents[2] / "LitexGeo" / "golitex" / "target" / "release" / "litex"),
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
    """Indent each line of source code by given number of spaces."""
    pad = " " * spaces
    lines = source.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(pad + line if line.strip() else line for line in lines)


def wrap_in_try(source: str) -> str:
    """
    Wrap candidate code in try: block for safe testing.
    Failed code will be rolled back, successful code will be committed.
    """
    body = source.strip("\n")
    if not body.strip():
        return "try:\n    1 = 1\n"
    return "try:\n" + indent_block(body, 4) + "\n"


def extract_litex_code(agent_output: str) -> str:
    """Extract litex code from agent output (markdown code blocks)."""
    match = re.search(r"```litex\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*\n(.*?)\n```", agent_output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return agent_output.strip()


def thm_to_axiom(code: str) -> Optional[str]:
    """
    Convert thm declaration to axiom: keep the goal block, remove proof body.
    Used as fallback when theorem proof fails.
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

    # Find ? line and its indentation; goal continues at deeper indentation
    q_idx = None
    q_indent = None
    for i, line in enumerate(lines[1:], start=1):
        if line.lstrip().startswith("?"):
            q_idx = i
            q_indent = len(line) - len(line.lstrip(" "))
            break
    if q_idx is None or q_indent is None:
        return None

    # Find where proof body starts (return to same indentation level)
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


def _extract_failure_info(result: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extract failure information from statement result or run result.
    Returns (phase, obligation) tuple.

    New format (1.1.2-beta): uses errors[] array with 'obligation' field
    Old format: uses why_failed with 'goal' field (kept for compatibility)
    """
    # NEW FORMAT: Check errors array (1.1.2-beta)
    errors = result.get("errors", [])
    if errors:
        # Get first error
        first_error = errors[0]
        phase = first_error.get("phase", "unknown")
        obligation = first_error.get("obligation", "")
        return phase, obligation

    # OLD FORMAT: Check statement-level why_failed (for compatibility)
    why_failed = result.get("why_failed", {})
    if why_failed:
        phase = why_failed.get("phase", "unknown")
        goal = why_failed.get("goal", "")
        return phase, goal

    # OLD FORMAT: Check if this is a run result with failed statements
    if result.get("kind") == "run":
        for stmt in result.get("statement_results", []):
            if stmt.get("statement_result") == "rejected":
                wf = stmt.get("why_failed", {})
                phase = wf.get("phase", "unknown")
                goal = wf.get("goal", "")
                return phase, goal

    return "unknown", ""


def _format_error_message(result: Dict[str, Any]) -> str:
    """Format a readable error message from result JSON."""
    parts: List[str] = ["❌ Validation failed"]

    # Check for session termination (hard error)
    # NOTE: In 1.1.2-beta batch mode, session_terminated is always false
    # Hard errors (parse/type errors) are indicated by errors[].phase = "parse"
    if result.get("session_terminated"):
        termination = result.get("termination", {})
        phase = termination.get("phase", "unknown")
        message = termination.get("message", "Session terminated")
        parts.append(f"\n🔴 Hard error ({phase}): {message}")
        parts.append("\n⚠️  Session must be restarted")
        return "".join(parts)

    # Check for soft failure
    phase, goal = _extract_failure_info(result)
    if goal:
        parts.append(f"\nFailed at phase: {phase}")
        parts.append(f"\nCould not prove: {goal}")

    # Add diagnostic info from errors array (new format)
    errors = result.get("errors", [])
    if errors:
        first_error = errors[0]
        category = first_error.get("category", "")
        message = first_error.get("message", "")
        if category:
            parts.append(f"\nError category: {category}")
        if message and message != goal:  # Don't duplicate the goal message
            parts.append(f"\nDetails: {message}")

        # Add source location if available (for parse errors)
        source_loc = first_error.get("source_location", {})
        if source_loc:
            line = source_loc.get("line", "")
            column = source_loc.get("column", "")
            if line:
                loc_str = f"line {line}"
                if column:
                    loc_str += f", column {column}"
                parts.append(f"\nLocation: {loc_str}")
    else:
        # Fallback to old format for compatibility
        why_failed = result.get("why_failed", {})
        if result.get("kind") == "run":
            # Extract from first failed statement
            for stmt in result.get("statement_results", []):
                if stmt.get("statement_result") == "rejected":
                    why_failed = stmt.get("why_failed", {})
                    break

        diagnostic = why_failed.get("diagnostic", {})
        if diagnostic:
            category = diagnostic.get("category", "")
            message = diagnostic.get("message", "")
            if category:
                parts.append(f"\nError category: {category}")
            if message:
                parts.append(f"\nDetails: {message}")

    # Add statement if available
    statement = result.get("statement", "")
    if not statement and result.get("kind") == "run":
        for stmt in result.get("statement_results", []):
            if stmt.get("statement_result") == "rejected":
                statement = stmt.get("statement", "")
                break
    if statement:
        parts.append(f"\nStatement: {statement}")

    return "".join(parts)


class LitexPersistentSession:
    """
    Long-lived litex -session process for Litex 1.1.2-beta.
    Uses traditional REPL protocol (not framed protocol).
    """

    def __init__(self, litex_bin: str, seed_source: str, frame_timeout: float = 120.0):
        self.litex_bin = litex_bin
        self.seed_source = seed_source
        self.frame_timeout = frame_timeout
        self.proc: Optional[subprocess.Popen] = None
        self._stdout_q: "queue.Queue[Optional[str]]" = queue.Queue()
        self._reader: Optional[threading.Thread] = None
        self._seed_path: Optional[str] = None
        self._counter = 0
        self.alive = False

    def start(self) -> None:
        """Start the litex session process."""
        self.close()

        # Write seed source to temporary file
        seed_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".lit", delete=False, encoding="utf-8"
        )
        seed_file.write(self.seed_source)
        seed_file.close()
        self._seed_path = seed_file.name

        # Start process: litex -f <seed> -session
        # Note: bufsize=0 for unbuffered (immediate) output
        self.proc = subprocess.Popen(
            [self.litex_bin, "-f", self._seed_path, "-session"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,  # Use binary mode for unbuffered I/O
            bufsize=0,
        )

        # Start stdout reader thread
        self._reader = threading.Thread(target=self._enqueue_stdout, daemon=True)
        self._reader.start()

        # Wait a moment for process to start
        time.sleep(0.5)

        # Check if process is still running
        if self.proc.poll() is not None:
            err = self._drain_stderr()
            self.close()
            raise RuntimeError(f"Litex session failed to start: stderr={err[:500]}")

        # Note: Litex 1.1.2-beta session mode does NOT output seed validation on startup
        # The seed file is loaded silently, validation output only appears when code is submitted
        # We validate the seed by sending a simple test statement
        self.alive = True

        # Send a harmless test to verify session is responsive
        test_ok, test_msg, _ = self.run_source("1 = 1")
        if not test_ok:
            self.close()
            raise RuntimeError(f"Session test failed: {test_msg}")

    def _enqueue_stdout(self) -> None:
        """Background thread to read stdout line by line."""
        assert self.proc and self.proc.stdout
        try:
            for line in self.proc.stdout:
                # Decode from bytes to string
                self._stdout_q.put(line.decode('utf-8', errors='replace'))
        finally:
            self._stdout_q.put(None)

    def _drain_stderr(self) -> str:
        """Read all available stderr content."""
        if not self.proc or not self.proc.stderr:
            return ""
        try:
            return self.proc.stderr.read() or ""
        except Exception:
            return ""

    def _read_json(self, timeout: float) -> Optional[Dict[str, Any]]:
        """
        Read one JSON object from stdout.
        Handles multi-line JSON by accumulating lines until valid JSON is formed.
        """
        deadline = time.time() + timeout
        json_lines: List[str] = []
        brace_count = 0
        in_json = False

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

            stripped = line.strip()
            if not stripped:
                continue

            # Skip non-JSON lines (like "Litex REPL" banner)
            if not in_json and not stripped.startswith("{"):
                continue

            # Accumulate JSON lines (use original line to preserve formatting)
            json_lines.append(line.rstrip('\n\r'))

            # Track brace depth
            for char in line:
                if char == "{":
                    brace_count += 1
                    in_json = True
                elif char == "}":
                    brace_count -= 1

            # When braces are balanced, try to parse
            if in_json and brace_count == 0:
                try:
                    json_text = "\n".join(json_lines)
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    # Malformed JSON, continue accumulating
                    continue

        return None

    def run_source(self, source: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Run a piece of source code in the session.
        Returns (success, message, raw_result)
        """
        if not self.alive or not self.proc or not self.proc.stdin:
            return False, "❌ Session not started", {}

        self._counter += 1

        try:
            # Send code followed by blank line (REPL protocol)
            # Encode to bytes for unbuffered binary mode
            self.proc.stdin.write(source.encode('utf-8'))
            self.proc.stdin.write(b"\n\n")  # blank line terminates the block
            self.proc.stdin.flush()
        except BrokenPipeError:
            self.alive = False
            return False, "❌ Session pipe broken", {}

        # Read result
        result = self._read_json(timeout=self.frame_timeout)
        if result is None:
            self.alive = False
            return False, f"❌ Validation timeout ({int(self.frame_timeout)}s) or session not responding", {}

        # Check for hard error (session terminated)
        if result.get("session_terminated"):
            self.alive = False
            err_msg = _format_error_message(result)
            return False, err_msg, result

        # Check result format (may be run envelope or standalone statement)
        if result.get("kind") == "run":
            # Run envelope format
            if result.get("run_result") == "success":
                return True, "✅ Validation passed", result
            else:
                err_msg = _format_error_message(result)
                return False, err_msg, result

        elif "statement_result" in result:
            # Standalone statement format
            if result.get("statement_result") == "accepted":
                return True, "✅ Validation passed", result
            else:
                err_msg = _format_error_message(result)
                return False, err_msg, result

        else:
            # Unknown format
            return False, "❌ Unexpected result format", result

    def run_try(self, code: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Run code wrapped in try: block for safe testing."""
        return self.run_source(wrap_in_try(code))

    def close(self) -> None:
        """Close the session and clean up resources."""
        self.alive = False
        if self.proc and self.proc.stdin:
            try:
                self.proc.stdin.write(b"exit\n")
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
    Validator for experiment runner:
    - Successful code is committed into persistent session
    - Failed code does not pollute the library (soft failure)
    - Optional: use axiom as fallback when proof finally fails
    """

    def __init__(self, seed_source: str, frame_timeout: float = 120.0):
        self.litex_bin = find_litex_bin()
        self.seed_source = seed_source
        self.frame_timeout = frame_timeout
        self.session: Optional[LitexPersistentSession] = None
        self.committed: List[str] = []  # successfully committed definitions/theorems (includes axioms)
        self.axioms: List[str] = []
        if self.litex_bin:
            print(f"✅ Litex compiler loaded (session mode): {self.litex_bin}")
            self._ensure_session()
        else:
            print("⚠️  Litex not found, auto-validation will not be available")

    def _ensure_session(self) -> None:
        """Ensure session is alive, restart if needed."""
        if self.session and self.session.alive:
            return
        if self.litex_bin:
            try:
                self.session = LitexPersistentSession(
                    self.litex_bin, self.seed_source, self.frame_timeout
                )
                self.session.start()
                print("✅ Session started successfully")
            except Exception as e:
                print(f"⚠️  Failed to start session: {e}")
                self.session = None

    def extract_litex_code(self, agent_output: str) -> str:
        """Extract litex code from agent output."""
        return extract_litex_code(agent_output)

    def validate(self, code: str, library_context: str = "") -> Tuple[Optional[bool], str, Dict[str, Any]]:
        """
        Validate code using persistent session.

        Note: Litex 1.1.2-beta does not support try: blocks for safe testing.
        Failed code will remain uncommitted (soft failure), session continues.

        Returns:
            (is_valid, output_message, raw_json_result)
            - is_valid: True=success, False=failure, None=unavailable
            - output_message: human-readable message
            - raw_json_result: raw JSON result from litex
        """
        if not self.session:
            return None, "Litex session not available", {}

        self._ensure_session()
        if not self.session or not self.session.alive:
            return None, "Cannot start or restart session", {}

        # Validate directly (no try: wrapper since it's not supported in 1.1.2-beta)
        is_valid, output, raw_result = self.session.run_source(code)

        # If successful, record as committed
        if is_valid:
            self.committed.append(code.strip())

        return is_valid, output, raw_result

    def axiomize_thm(self, thm_code: str) -> bool:
        """Convert theorem to axiom and validate."""
        axiom = thm_to_axiom(thm_code)
        if not axiom:
            return False

        ok, _, _ = self.validate(axiom)
        if ok:
            self.axioms.append(axiom)
            return True
        return False

    def commit_axiom_fallback(self, failed_code: str) -> Tuple[Optional[bool], str, Optional[str]]:
        """
        When proof fails, convert theorem to axiom and commit as fallback.
        Returns (success, message, axiom_code)
        """
        axiom = thm_to_axiom(failed_code)
        if not axiom:
            return False, "Cannot generate axiom from failed code", None

        ok, msg, _event = self.validate(axiom)
        if ok:
            self.axioms.append(axiom)
            return True, f"✅ Axiom fallback successful (trust debt +1)\n{axiom}", axiom
        return False, f"Axiom commit failed: {msg}", axiom

    def export_session_library(self, seed_source: str) -> str:
        """Export accumulated session library (seed + committed definitions)."""
        parts = [seed_source.strip(), ""]
        if self.committed:
            parts.append("# Verified definitions/theorems from experiments")
            parts.append("\n\n".join(self.committed))
        return "\n".join(parts)

    def close(self) -> None:
        """Close session and clean up resources."""
        if self.session:
            self.session.close()
            self.session = None
