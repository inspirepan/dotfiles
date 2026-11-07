"""Ensure shared instructions are linked for the response style update."""

from pathlib import Path
import runpy

DESCRIPTION = "更新 Claude Code 与 Codex 的回答风格指令"

shared = runpy.run_path(str(Path(__file__).with_name("20261024-001-shared-agent-instructions.py")))
check = shared["check"]
apply = shared["apply"]
