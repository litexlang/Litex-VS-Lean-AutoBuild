"""
Lean 持久会话验证：用 leanprover-community/repl（JSON stdin/stdout）做增量验证。

协议：
  启动：`lake env <repl_bin>`（cwd = Lean 工程，带 Mathlib 搜索路径）
  命令：一行 JSON + 空行；响应：JSON（可多行）+ 空行
  成功：无 severity=error 的 message → 采纳返回的 env
  失败：不切换 env（≈ Litex try RolledBack）；成功则 env 前进（≈ Committed）

注意：REPL 在 elaborates 失败时仍可能返回新的 env 编号；本模块故意忽略该编号。
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

# 仓库内预构建的 REPL（lean_auto_build_system/.tools/repl）
_DEFAULT_REPL_REL = Path(__file__).resolve().parent / ".tools" / "repl" / ".lake" / "build" / "bin" / "repl"

# 空 LeanGeo 时回退到已装 Mathlib 的目录
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
    选定带 Mathlib 的 Lean 工程目录。
    优先：显式路径 / LEAN_PROJECT_DIR / LeanGeo（若有 lakefile）/ golitex/lean。
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
    # 最后仍返回 preferred/LeanGeo，让上层报错更清晰
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
    """已有 env 时不能再 import；去掉顶层 import / open 行（保留注释与代码）。"""
    lines = code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: List[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("import ") or stripped.startswith("prelude"):
            continue
        out.append(line)
    return "\n".join(out).strip()


def lean_code_is_noop(code: str) -> bool:
    """纯空白/行注释：不送 REPL（避免 unexpected end of input）。"""
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
    """#check / #print 等查询成功也不写入累积库。"""
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
    """从REPL响应中提取详细错误信息"""
    parts: List[str] = ["❌ 验证失败（env 未前进，会话继续）"]

    for msg in resp.get("messages") or []:
        if not isinstance(msg, dict) or msg.get("severity") != "error":
            continue

        # 提取位置信息
        pos = msg.get("pos") or {}
        line = pos.get("line", "?")
        col = pos.get("column", "?")

        # 提取错误数据
        data = (msg.get("data") or "").strip()

        # 格式化错误信息
        error_parts = [f"❌ 编译错误 (行 {line}:{col}):"]

        # 分割错误信息，提取关键部分
        if data:
            lines = data.split('\n')
            # 第一行通常是错误类型
            if lines:
                error_parts.append(lines[0])

            # 提取详细信息
            detail_lines = []
            for i, line_text in enumerate(lines[1:], 1):
                stripped = line_text.strip()
                if stripped:
                    # 识别重要的错误信息
                    if stripped.startswith('⊢') or stripped.startswith('|') or stripped.startswith('expected'):
                        detail_lines.append(f"  {stripped}")
                    else:
                        detail_lines.append(stripped)

            if detail_lines:
                error_parts.append("\n".join(detail_lines))

        parts.append("\n".join(error_parts))

    # 如果没有提取到有用信息，显示原始响应
    if len(parts) == 1:
        raw = json.dumps(resp, ensure_ascii=False)[:800]
        parts.append(f"原始响应:\n{raw}")

    return "\n\n".join(parts)


class LeanPersistentSession:
    """长生命周期 lake env + leanprover-community/repl 进程。"""

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
            # 第一次加载种子库时保留import（因为use_env=False）
            # REPL只能在没有env时使用import语句
            ok, msg, resp = self.run_command(seed, use_env=False)
            if not ok:
                self.close()
                raise RuntimeError(f"seed 加载失败: {msg}\n{json.dumps(resp, ensure_ascii=False)[:500]}")

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
            # 非阻塞尽量读；进程活着时 stderr 可能阻塞，限制时间
            chunks: List[str] = []
            self.proc.stderr.flush()
            return "".join(chunks)
        except Exception:
            return ""

    def _read_json_response(self, timeout: float) -> Optional[Dict[str, Any]]:
        """读到空行分隔的一块文本，再 json.loads（支持多行 pretty JSON）。"""
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
                    # 可能还不完整；继续攒（极少见）
                    buf.append(line)
                    continue
            buf.append(line)
        return None

    def run_command(
        self, cmd: str, *, use_env: bool = True
    ) -> Tuple[bool, str, Dict[str, Any]]:
        if not self.alive or not self.proc or not self.proc.stdin:
            return False, "❌ REPL session 未启动", {}

        payload: Dict[str, Any] = {"cmd": cmd}
        if use_env:
            if self.env is None:
                return False, "❌ REPL env 尚未建立（seed 未加载？）", {}
            payload["env"] = self.env

        try:
            self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n\n")
            self.proc.stdin.flush()
        except BrokenPipeError:
            self.alive = False
            return False, "❌ REPL 管道断开", {}

        resp = self._read_json_response(timeout=self.cmd_timeout)
        if resp is None:
            self.alive = False
            err = ""
            if self.proc and self.proc.stderr:
                try:
                    # 进程可能已挂，尽量读一点 stderr
                    pass
                except Exception:
                    pass
            return False, f"❌ 编译超时（{int(self.cmd_timeout)}秒）或 REPL 无响应{err}", {}

        if _messages_have_error(resp):
            # 关键：不采纳 resp["env"]
            return False, _format_repl_errors(resp), resp

        if "env" in resp:
            self.env = resp["env"]
        return True, "✅ 编译通过（REPL env committed）", resp

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
        # 清空队列残渣
        while not self._stdout_q.empty():
            try:
                self._stdout_q.get_nowait()
            except Exception:
                break


class SessionBackedValidator:
    """
    给实验 runner 用的验证器：
    - seed 启动时 commit 一次
    - validate(code) 只发增量；成功前进 env，失败回滚（不切换 env）
    - library_context 参数保留兼容，会话模式下忽略
    - REPL 不可用时回退到 lake env lean 整文件
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
            print(f"✅ Lean 工程: {self.lean_project_dir}")
            try:
                self._ensure_session()
                self.mode = "repl"
                print("✅ 验证模式: Lean REPL session（增量 env）")
            except Exception as e:
                print(f"⚠️  REPL session 启动失败，回退整文件: {e}")
                self.mode = "file"
        elif self.lake_bin:
            print(f"✅ lake: {self.lake_bin}")
            print(f"⚠️  未找到 REPL（可设 LEAN_REPL_BIN），回退 lake env lean 整文件")
            print(f"📚 Lean 工程: {self.lean_project_dir}")
            self.mode = "file"
        else:
            print("⚠️  lake 未找到，将无法自动验证")

    @property
    def lake_bin_ok(self) -> bool:
        return self.lake_bin is not None

    def _ensure_session(self) -> None:
        if self.session and self.session.alive and self.session.env is not None:
            return
        if not self.lake_bin or not self.repl_bin:
            raise RuntimeError("lake/repl 不可用")
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
                print(f"⚠️  重放已提交代码失败: {msg[:200]}")
                break

    def extract_lean_code(self, agent_output: str) -> str:
        return extract_lean_code(agent_output)

    def validate(self, code: str, library_context: str = "") -> Tuple[Optional[bool], str, Dict[str, Any]]:
        if self.mode == "none":
            return None, "lake 不可用", {}

        if self.mode == "repl":
            return self._validate_repl(code)

        return self._validate_file(code, library_context)

    def _validate_repl(self, code: str) -> Tuple[Optional[bool], str, Dict[str, Any]]:
        if lean_code_is_noop(code):
            # 空/纯注释：视为通过，不推进（与「种子已有、无需再定义」一致）
            return True, "✅ 编译通过（空增量 / 仅注释，env 不变）", {}

        body = strip_imports_for_incremental(code)
        if not body.strip():
            return True, "✅ 编译通过（空增量 / 仅注释，env 不变）", {}

        try:
            self._ensure_session()
        except Exception as e:
            return None, f"⚠️  无法启动 Lean REPL session: {e}", {}

        assert self.session is not None
        ok, msg, resp = self.session.run_command(body, use_env=True)
        if not ok and ("无响应" in msg or "管道断开" in msg or "超时" in msg):
            try:
                if self.session:
                    self.session.close()
                self.session = None
                self._ensure_session()
                assert self.session is not None
                ok, msg, resp = self.session.run_command(body, use_env=True)
            except Exception as e:
                return False, f"{msg}\n重启 REPL 失败: {e}", {}
        if ok and should_record_commit(code):
            self.committed.append(code)
        return ok, msg, resp

    def _validate_file(self, code: str, library_context: str) -> Tuple[Optional[bool], str, Dict[str, Any]]:
        import tempfile

        if not self.lake_bin:
            return None, "lake 不可用", {}

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
                return True, "✅ 编译通过（整文件回退）", {}
            return False, self._parse_lean_file_errors(output), {}
        except subprocess.TimeoutExpired:
            return False, f"❌ 编译超时（{int(self.cmd_timeout)}秒）", {}
        except Exception as e:
            return False, f"❌ 验证失败: {e}", {}
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
                error_parts = [f"❌ 编译错误 (行 {line_num}:{col}): {error_type}"]
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
        return f"❌ 编译失败:\n{output[:500]}"

    def close(self) -> None:
        if self.session:
            self.session.close()
            self.session = None

    def export_session_library(self, seed_source: str) -> str:
        parts = [
            "-- ============================================================",
            "-- LeanGeo AutoBuild — REPL session 导出库",
            f"-- committed 条目数: {len(self.committed)}",
            "-- ============================================================",
            "",
            seed_source.rstrip(),
            "",
            "-- ---------- session 已提交内容 ----------",
            "",
        ]
        for block in self.committed:
            parts.append(block.rstrip())
            parts.append("")
        return "\n".join(parts).rstrip() + "\n"


# 兼容旧名
LeanValidator = SessionBackedValidator
