import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class InitializationTests(unittest.TestCase):
    def test_new_device_initializes_all_sources_then_updates_without_installing_again(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repo, home = base / 'repo', base / 'home'
            repo.mkdir()
            home.mkdir()
            for directory in ['scripts', 'updates']:
                shutil.copytree(ROOT / directory, repo / directory, ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copyfile(ROOT / 'Skillfile.json', repo / 'Skillfile.json')
            for package in ['zsh', 'git', 'config', 'ssh', 'claude', 'codex', 'klaude']:
                (repo / package).mkdir()
            shared = repo / 'claude/.claude/CLAUDE.md'
            shared.parent.mkdir()
            shared.write_text('instructions')
            codex = repo / 'codex/.codex/AGENTS.md'
            codex.parent.mkdir()
            codex.symlink_to('../../claude/.claude/CLAUDE.md')
            runner = load(repo / 'scripts/dotfiles.py', 'initialization_runner')
            installer = load(repo / 'scripts/install-skills.py', 'initialization_installer')
            config = installer.load_config(repo)
            sources = installer.sources(config)
            by_repository = {s['repository']: s for s in sources}
            names = {name for source in sources for name in source['enabled']}
            calls = []
            original_run = subprocess.run
            def run(command, **kwargs):
                if command[0].endswith('setup-skills.sh'):
                    return subprocess.CompletedProcess(command, installer.install(repo, home, update='--update' in command))
                if command[0] != 'npx':
                    return original_run(command, **kwargs)
                self.assertEqual(command[3], 'add')
                self.assertEqual(command[2], 'skills@latest')
                source = by_repository[command[4]]
                calls.append(source['repository'])
                lock = home / '.agents/.skill-lock.json'
                records = json.loads(lock.read_text()) if lock.exists() else {'skills': {}}
                for name in command[command.index('--skill') + 1:-2]:
                    target = home / '.agents/skills' / name
                    target.mkdir(parents=True)
                    (target / 'SKILL.md').write_text('installed')
                    client = home / '.claude/skills' / name
                    client.parent.mkdir(parents=True, exist_ok=True)
                    client.symlink_to(target)
                    records['skills'][name] = {'source': source['repository']}
                lock.write_text(json.dumps(records))
                return subprocess.CompletedProcess(command, 0, stdout='', stderr='')
            with patch.dict(os.environ, {'XDG_STATE_HOME': '', 'CLAUDE_CONFIG_DIR': str(home / '.claude')}), patch.object(subprocess, 'run', side_effect=run):
                runner.execute(repo, home, 'init')
                installed_count = len(calls)
                runner.execute(repo, home, 'update')
                self.assertEqual(len(calls), installed_count)
            state = json.loads((home / '.local/state/dotfiles/updates.json').read_text())
            self.assertTrue(state['initialized'])
            self.assertEqual(len(state['completed']), len(list((repo / 'updates').glob('[0-9]*.py'))))
            self.assertEqual(set(calls), {s['repository'] for s in sources})
            self.assertEqual({p.name for p in (home / '.agents/skills').iterdir()}, names)
            self.assertTrue((home / '.claude/CLAUDE.md').samefile(home / '.codex/AGENTS.md'))


if __name__ == '__main__':
    unittest.main()
