# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run verified, ordered dotfiles updates with per-device progress."""

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import sys

sys.dont_write_bytecode = True


def read_state(path):
    state = json.loads(path.read_text()) if path.exists() else {"version": 1, "completed": {}}
    if state.get("version") != 1 or not isinstance(state.get("completed"), dict):
        raise ValueError(f"无法识别应用记录：{path}")
    return state


def save_state(path, state):
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        json.dump(state, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
        temporary = stream.name
    os.replace(temporary, path)


def steps(repository):
    for path in sorted((repository / "updates").glob("[0-9]*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield path.stem, hashlib.sha256(path.read_bytes()).hexdigest(), module


def execute(repository, home, mode):
    state_dir = home / ".local/state/dotfiles"
    path = state_dir / "updates.json"

    def process():
        state = read_state(path)
        for identifier, digest, step in steps(repository):
            previous = state["completed"].get(identifier)
            if previous and previous["sha256"] != digest:
                raise ValueError(f"已应用的更新被修改：{identifier}；请新增更新步骤")
            satisfied = step.check(repository, home)
            label = "已完成" if previous and satisfied else "可登记" if satisfied else "待执行"
            print(f"{label}：{identifier} — {step.DESCRIPTION}", flush=True)
            if mode == "status":
                continue
            if not satisfied:
                step.apply(repository, home)
            if not step.check(repository, home):
                raise RuntimeError(f"更新验证失败：{identifier}")
            state["completed"][identifier] = {"sha256": digest, "description": step.DESCRIPTION}
            save_state(path, state)
        if mode == "init":
            packages = ["zsh", "git", "config", "ssh", "claude", "codex", "klaude"]
            subprocess.run(["stow", "--no-folding", "--dir", str(repository), "--target", str(home), *packages], check=True)
            state["initialized"] = True
            save_state(path, state)
        if mode != "status":
            print("更新已应用并验证。" if mode == "update" else "Stow 初始化及更新已应用并验证。")

    if mode == "status":
        process()
    else:
        state_dir.mkdir(parents=True, exist_ok=True)
        with (state_dir / "updates.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            process()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["status", "update", "init"])
    args = parser.parse_args()
    execute(Path(__file__).resolve().parents[1], Path.home(), args.mode)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"dotfiles 更新停止：{error}") from error
