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

STOW_PACKAGES = ("zsh", "git", "config", "ssh", "claude", "codex", "klaude")


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


def execute(repository, home, mode, components=(), verbose=False):
    readonly = mode in ("status", "check")
    if verbose and not readonly:
        raise ValueError("--verbose 仅支持 status/check")
    if components and mode == "init":
        raise ValueError("init 不支持组件筛选，请使用 status 或 update")
    grouping = json.loads((repository / "updates/components.json").read_text()) if components else {}
    unknown = set(components) - set(grouping.values())
    if unknown:
        raise ValueError(f"未知组件：{', '.join(sorted(unknown))}")
    state_dir = home / ".local/state/dotfiles"
    path = state_dir / "updates.json"

    def process():
        messages = []
        pending_steps = False
        state = read_state(path)
        available = list(steps(repository))
        if components and set(grouping) != {identifier for identifier, _, _ in available}:
            raise ValueError("组件清单与更新步骤不一致，请检查 updates/components.json")
        superseded = set()
        for identifier, digest, step in available:
            previous = state["completed"].get(identifier)
            if previous and previous["sha256"] != digest:
                raise ValueError(f"已应用的更新被修改：{identifier}；请新增更新步骤")
            if previous:
                superseded.update(getattr(step, "SUPERSEDES", ()))
        for identifier, digest, step in available:
            if components and grouping[identifier] not in components:
                continue
            if identifier in superseded:
                if readonly and verbose:
                    messages.append(f"已由后续步骤取代：{identifier} — {step.DESCRIPTION}")
                elif not readonly:
                    print(f"已由后续步骤取代：{identifier} — {step.DESCRIPTION}", flush=True)
                continue
            previous = state["completed"].get(identifier)
            if readonly and previous:
                if verbose:
                    messages.append(f"已登记（未复查）：{identifier} — {step.DESCRIPTION}")
                continue
            satisfied = step.check(repository, home)
            label = "已完成" if previous and satisfied else "可登记" if satisfied else "待执行"
            if readonly:
                if label != "已完成":
                    pending_steps = True
                if verbose or label != "已完成":
                    messages.append(f"{label}：{identifier} — {step.DESCRIPTION}")
                continue
            print(f"{label}：{identifier} — {step.DESCRIPTION}", flush=True)
            if not satisfied:
                step.apply(repository, home)
            if not step.check(repository, home):
                raise RuntimeError(f"更新验证失败：{identifier}")
            state["completed"][identifier] = {"sha256": digest, "description": step.DESCRIPTION}
            save_state(path, state)
        if mode == "init":
            subprocess.run(["stow", "--no-folding", "--dir", str(repository), "--target", str(home), *STOW_PACKAGES], check=True)
            state["initialized"] = True
            save_state(path, state)
        if readonly:
            if pending_steps:
                selection = "".join(f" --component {component}" for component in components)
                messages.append(f"建议：先处理冲突，再运行 scripts/dotfiles.sh update{selection} 应用或登记待办。")
            if (not components or "agents" in components) and (repository / "Skillfile.json").exists():
                spec = importlib.util.spec_from_file_location("dotfiles_skills", Path(__file__).with_name("install-skills.py"))
                installer = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(installer)
                _, pending, conflicts = installer.plan(repository, home)
                if pending:
                    messages.append("技能待同步：" + ", ".join(pending) + "；建议运行 scripts/setup-skills.sh --update。")
                for name in conflicts:
                    messages.append(f"技能冲突：{name}；建议检查 ~/.agents/skills/{name} 与 Claude skills 入口（含 CLAUDE_CONFIG_DIR），比较来源和个人内容，确认并备份后再处理。")
                if verbose and not pending and not conflicts:
                    messages.append("技能检查通过：本地来源、入口和旧 SHA ref；未联网检查最新版。")
            if not components:
                packages = [package for package in STOW_PACKAGES if (repository / package).is_dir()]
                if packages:
                    try:
                        result = subprocess.run(
                            ["stow", "--simulate", "--verbose=1", "--no-folding", "--dir", str(repository), "--target", str(home), *packages],
                            capture_output=True, text=True, env={**os.environ, "HOME": str(home)},
                        )
                    except FileNotFoundError as error:
                        raise RuntimeError("Stow 预演失败：未找到 stow，请先安装 GNU Stow。") from error
                    output = "\n".join(line for line in (result.stdout + result.stderr).splitlines()
                                       if line != "WARNING: in simulation mode so not modifying filesystem.")
                    if result.returncode and "would cause conflicts:" not in output:
                        raise RuntimeError(f"Stow 预演失败（退出码 {result.returncode}）：{output}")
                    if output:
                        messages.append(f"Stow 只读预演（目标 {home}）：\n{output}")
                        messages.append("建议：先比较并合并冲突中的个人内容，备份后再处理；目录链接先确认归属，勿直接使用 --adopt。确认预演结果并处理冲突后，按 docs/setup-guide.md Phase 3 的 Stow 命令重建链接。预演未修改任何文件。")
                    elif verbose:
                        messages.append("Stow 只读预演通过，无待处理链接或冲突。")
            elif verbose:
                messages.append("组件模式跳过 Stow 只读预演；运行不带 --component 的 status/check 检查全部链接。")
            print("\n".join(messages) if messages else "检查完成，无待办或冲突。", flush=True)
        else:
            print("更新已应用并验证。" if mode == "update" else "Stow 初始化及更新已应用并验证。")

    if readonly:
        process()
    else:
        state_dir.mkdir(parents=True, exist_ok=True)
        with (state_dir / "updates.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            process()


def main():
    repository = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["status", "check", "update", "init"])
    parser.add_argument("--verbose", action="store_true", help="显示完整检查结果；仅支持 status/check")
    parser.add_argument(
        "--component", action="append", default=[],
        choices=sorted(set(json.loads((repository / "updates/components.json").read_text()).values())),
        help="仅处理指定组件，可重复指定；不支持 init",
    )
    args = parser.parse_args()
    if args.mode == "init" and args.component:
        parser.error("init 不支持 --component，请使用 status 或 update")
    if args.verbose and args.mode not in ("status", "check"):
        parser.error("--verbose 仅支持 status/check")
    execute(repository, Path.home(), args.mode, args.component, verbose=args.verbose)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"dotfiles 更新停止：{error}") from error
