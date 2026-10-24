"""Follow upstream skills without pinned commit refs."""

import importlib.util
import os
import subprocess

DESCRIPTION = "共享技能改用上游最新版，解除旧提交锁定"


def installer(repository):
    spec = importlib.util.spec_from_file_location("dotfiles_skills", repository / "scripts/install-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(repository, home):
    _, pending, conflicts = installer(repository).plan(repository, home)
    return not pending and not conflicts


def apply(repository, home):
    subprocess.run([str(repository / "scripts/setup-skills.sh"), "--update"], env={**os.environ, "HOME": str(home)}, check=True)
