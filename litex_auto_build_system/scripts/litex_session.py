"""
Litex 持久会话验证：用 `litex -isolated -session` + `try:` 做增量验证。

协议（golitex framed session）：
  启动后读 ready 事件；
  发送：run <id> <utf8字节数>\\n<source>；
  失败的 try 会 RolledBack，会话可继续；
  成功的 try 会 Committed，定义/定理进入环境。
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
    """按常见路径查找支持 -session 的 litex。"""
    # 构建相对路径
    script_dir = Path(__file__).resolve().parent
    relative_litex = script_dir.parent.parent / "LitexGeo" / "golitex" / "litex_0.9.116-beta_darwin_arm64" / "litex"

    candidates = [
        os.environ.get("LITEX_BIN"),
        str(relative_litex),  # 使用相对路径
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
    """把候选代码包进 try:，失败回滚、成功提交。"""
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
    把 thm 声明改成 axiom：保留 `? forall ...` 目标块，去掉证明体。
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

    # 找到 ? 行及其缩进；目标继续于更深缩进；回到同级缩进即证明体
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
    """从 session result / RolledBack 结构提取可读错误。"""
    parts: List[str] = ["❌ 验证失败（try 已回滚，会话继续）"]

    # 处理 event: "block" 类型的错误（包含trace字段）
    if event.get("event") == "block" and event.get("ok") is False:
        trace_str = event.get("trace", "")
        if trace_str:
            try:
                trace = json.loads(trace_str)
                error_type = trace.get("error_type", "error")
                line = trace.get("line", "?")
                message = trace.get("message", "")
                if message:
                    parts.append(f"\n({error_type}, 行 {line}):\n{message}")
                else:
                    parts.append(f"\n({error_type}, 行 {line})")
            except json.JSONDecodeError:
                parts.append(f"\n错误信息: {trace_str}")

    # 处理标准的 statement_results 结构
    for stmt in event.get("statement_results") or []:
        result = stmt.get("result") or {}
        execution = result.get("execution") or {}
        if execution.get("kind") != "RolledBack":
            # 也可能直接在 nested error
            pass
        err = execution.get("error") or event.get("error") or {}
        if isinstance(err, dict):
            msg = err.get("message") or err.get("msg") or ""
            kind = err.get("kind") or err.get("error_type") or "error"
            line = err.get("line", "?")
            if msg:
                parts.append(f"\n({kind}, 行 {line}):\n{msg}")
            if "statement" in err:
                parts.append(f"\n失败的语句:\n{err['statement']}")
            if "failed_goal" in err:
                parts.append(f"\n失败的目标:\n{err['failed_goal']}")
            unknown = err.get("unknown_result") or {}
            if isinstance(unknown, dict):
                if "type" in unknown:
                    parts.append(f"\n原因类型: {unknown['type']}")
                if "goal" in unknown:
                    parts.append(f"\n未知目标: {unknown['goal']}")

            # 递归提取所有 previous_error（完整的错误链，和旧系统一样）
            def extract_previous_errors(err_obj, depth=1):
                if "previous_error" not in err_obj:
                    return []

                prev_errors = []
                prev = err_obj["previous_error"]

                # 提取这一层的信息
                if "message" in prev:
                    prefix = "详细原因" if depth == 1 else f"原因{depth}"
                    prev_errors.append(f"\n{prefix}: {prev['message']}")

                if "failed_goal" in prev and "failed_goal" not in err_obj:
                    prev_errors.append(f"\n失败的目标:\n{prev['failed_goal']}")

                if "unknown_result" in prev:
                    unknown_prev = prev["unknown_result"]
                    if isinstance(unknown_prev, dict):
                        if "type" in unknown_prev:
                            prev_errors.append(f"\n原因类型: {unknown_prev['type']}")

                # 递归提取更深层
                prev_errors.extend(extract_previous_errors(prev, depth + 1))
                return prev_errors

            # 添加所有 previous_error 信息
            parts.extend(extract_previous_errors(err))
        # 兼容 statement_results 顶层直接带 failed_goal 的展示字段
        if "failed_goal" in result:
            parts.append(f"\n失败的目标:\n{result['failed_goal']}")

    # 处理event级别的error字段
    if event.get("error"):
        parts.append(f"\nerror: {json.dumps(event['error'], ensure_ascii=False)[:800]}")

    # 如果没有提取到任何有用信息，才dump整个event（但只作为最后手段）
    if len(parts) == 1:
        parts.append("\n（原始错误信息）：\n" + json.dumps(event, ensure_ascii=False)[:1200])

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
    """长生命周期 litex -session 进程。"""

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
            raise RuntimeError(f"litex session 未能 ready: {ready}; stderr={err[:500]}")
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
                # 非 JSON 行跳过
                continue
        return None

    def run_source(self, source: str, frame_id: Optional[str] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        在会话中跑一段源码（调用方决定是否包 try）。
        返回 (committed_ok, message, raw_event)
        """
        if not self.alive or not self.proc or not self.proc.stdin:
            return False, "❌ session 未启动", {}

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
            return False, "❌ session 管道断开", {}

        event = self._read_json(timeout=self.frame_timeout)
        if event is None:
            self.alive = False
            return False, f"❌ 编译超时（{int(self.frame_timeout)}秒）或 session 无响应", {}

        if event.get("event") == "skipped":
            self.alive = False
            return False, "❌ session 已因先前失败而 skipped，需要重启", event

        if event.get("event") == "protocol_error":
            return False, f"❌ session 协议错误:\n{json.dumps(event, ensure_ascii=False)[:800]}", event

        if _is_committed(event):
            return True, "✅ 编译通过（session try committed）", event

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
    给实验 runner 用的验证器：
    - 成功代码通过 try 提交进持久会话
    - 失败 try 回滚，不污染库
    - 可选：最终失败时 axiom 顶上
    """

    def __init__(self, seed_source: str, frame_timeout: float = 120.0):
        self.litex_bin = find_litex_bin()
        self.seed_source = seed_source
        self.frame_timeout = frame_timeout
        self.session: Optional[LitexPersistentSession] = None
        self.committed: List[str] = []  # 已成功提交的定义/定理（含 axiom）
        self.axioms: List[str] = []
        if self.litex_bin:
            print(f"✅ litex 编译器已加载（session 模式）: {self.litex_bin}")
            self._ensure_session()
        else:
            print("⚠️  未找到支持 -session 的 litex，将无法自动验证")

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
                print(f"⚠️  重放已提交代码失败: {msg[:200]}")
                break

    def extract_litex_code(self, agent_output: str) -> str:
        return extract_litex_code(agent_output)

    def validate(self, code: str, library_context: str = "") -> Tuple[Optional[bool], str]:
        """
        library_context 参数保留兼容；会话模式下忽略（库已在进程内）。
        """
        del library_context  # 会话内已有累积状态
        if not self.litex_bin:
            return None, "litex 编译器不可用"
        try:
            self._ensure_session()
        except Exception as e:
            return None, f"⚠️  无法启动 litex session: {e}"

        assert self.session is not None
        ok, msg, _event = self.session.run_try(code)
        if not ok and ("skipped" in msg or "无响应" in msg or "管道断开" in msg):
            try:
                if self.session:
                    self.session.close()
                self.session = None
                self._ensure_session()
                assert self.session is not None
                ok, msg, _event = self.session.run_try(code)
            except Exception as e:
                return False, f"{msg}\n重启 session 失败: {e}"
        if ok:
            self.committed.append(code)
        return ok, msg

    def commit_axiom_fallback(self, failed_code: str) -> Tuple[bool, str, Optional[str]]:
        """证不出时把 thm 改成 axiom 提交。返回 (ok, msg, axiom_code)。"""
        axiom = thm_to_axiom(failed_code)
        if not axiom:
            return False, "无法从失败代码生成 axiom", None
        ok, msg = self.validate(axiom)
        if ok:
            self.axioms.append(axiom)
            return True, f"✅ 已用 axiom 顶上（信任债 +1）\n{axiom}", axiom
        return False, f"axiom 提交失败: {msg}", axiom

    def close(self) -> None:
        if self.session:
            self.session.close()
            self.session = None

    def export_session_library(self, seed_source: str) -> str:
        """
        导出当前 session 累积库：种子 + 按提交顺序的全部 committed 代码。
        便于跑完后打开改 axiom。
        """
        parts = [
            "# ============================================================",
            "# LitexGeo AutoBuild — session 导出库",
            f"# committed 条目数: {len(self.committed)}",
            f"# axiom 债务数: {len(self.axioms)}",
            "# 用法: 搜 `^axiom ` 找到信任债，改回 thm + 证明即可。",
            "# ============================================================",
            "",
            seed_source.rstrip(),
            "",
        ]
        if self.axioms:
            parts.append("# ---------- 信任债索引（axiom）----------")
            for i, ax in enumerate(self.axioms, 1):
                first = next((ln.strip() for ln in ax.splitlines() if ln.strip()), "")
                parts.append(f"# {i}. {first}")
            parts.append("")

        parts.append("# ---------- session 已提交内容（定义 / thm / axiom）----------")
        parts.append("")
        for block in self.committed:
            parts.append(block.rstrip())
            parts.append("")
        return "\n".join(parts).rstrip() + "\n"
