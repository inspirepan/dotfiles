"""Install commit from the shared upstream and migrate its known legacy links."""

import importlib.util
import os
import subprocess

DESCRIPTION = "commit 改由 agent-skills 安装，备份已知旧链接"


def installer(repository):
    spec = importlib.util.spec_from_file_location("dotfiles_skills", repository / "scripts/install-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(repository, home):
    _, pending, conflicts = installer(repository).plan(repository, home)
    return not pending and not conflicts


def apply(repository, home):
    subprocess.run([str(repository / "scripts/setup-skills.sh")], env={**os.environ, "HOME": str(home)}, check=True)
