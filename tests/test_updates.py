import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

runner = module(ROOT / 'scripts/dotfiles.py', 'updates')
installer = module(ROOT / 'scripts/install-skills.py', 'installer')
shared = module(ROOT / 'updates/20261024-001-shared-agent-instructions.py', 'shared')

class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repo'
        self.home = self.root / 'home'
        self.repo.mkdir()
        self.home.mkdir()
        (self.repo / 'updates').mkdir()
        self.env = patch.dict(os.environ, {'XDG_STATE_HOME': '', 'CLAUDE_CONFIG_DIR': str(self.home / '.claude')})
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_updates(self, mode='update'):
        with contextlib.redirect_stdout(io.StringIO()):
            runner.execute(self.repo, self.home, mode)

    def step(self, name, body):
        path = self.repo / 'updates' / f'{name}.py'
        path.write_text("DESCRIPTION = 'test'\ndef check(repository, home):\n    return (home / '" + name + "').exists()\ndef apply(repository, home):\n" + body + '\n')
        return path

    def test_order_and_resume_after_failure(self):
        self.step('001', "    (home / '001').touch()")
        self.step('002', "    if not (home / 'ready').exists():\n        raise RuntimeError('not ready')\n    (home / '002').touch()")
        self.step('003', "    assert (home / '002').exists()\n    (home / '003').touch()")
        with self.assertRaisesRegex(RuntimeError, 'not ready'):
            self.run_updates()
        state = json.loads((self.home / '.local/state/dotfiles/updates.json').read_text())
        self.assertEqual(list(state['completed']), ['001'])
        self.assertFalse((self.home / '003').exists())
        (self.home / 'ready').touch()
        self.run_updates()
        before = (self.home / '001').stat().st_mtime_ns
        self.run_updates()
        self.assertEqual((self.home / '001').stat().st_mtime_ns, before)
        self.assertTrue((self.home / '003').exists())

    def test_status_does_not_write_and_modified_step_rejected(self):
        step = self.step('001', "    (home / '001').touch()")
        self.run_updates('status')
        self.assertFalse((self.home / '.local').exists())
        self.run_updates()
        step.write_text(step.read_text() + '# changed\n')
        with self.assertRaisesRegex(ValueError, '已应用的更新被修改'):
            self.run_updates()

    def test_init_runs_stow_after_updates(self):
        self.step('001', "    (home / '001').touch()")
        with patch.object(runner.subprocess, 'run') as run:
            self.run_updates('init')
        self.assertEqual(run.call_args.args[0][0], 'stow')
        self.assertTrue(json.loads((self.home / '.local/state/dotfiles/updates.json').read_text())['initialized'])

    def test_completed_successor_prevents_old_behavior_even_when_successor_drifts(self):
        old = self.step('001', "    (home / '001').touch()")
        successor = self.step('002', "    (home / '001').unlink(missing_ok=True)\n    (home / '002').touch()")
        successor.write_text(successor.read_text() + "SUPERSEDES = ('001',)\n")
        self.run_updates()
        self.run_updates()
        self.assertFalse((self.home / '001').exists())
        (self.home / '002').unlink()
        self.run_updates()
        self.assertFalse((self.home / '001').exists())
        old.write_text(old.read_text() + '# changed\n')
        with self.assertRaisesRegex(ValueError, '已应用的更新被修改'):
            self.run_updates()

    def shared_source(self):
        source = self.repo / 'claude/.claude/CLAUDE.md'
        source.parent.mkdir(parents=True)
        source.write_text('shared instructions\n')
        codex = self.repo / 'codex/.codex/AGENTS.md'
        codex.parent.mkdir(parents=True)
        codex.symlink_to('../../claude/.claude/CLAUDE.md')
        return source

    def test_shared_instructions_new_existing_empty_and_repeat(self):
        source = self.shared_source()
        (self.home / '.codex').mkdir()
        (self.home / '.codex/AGENTS.md').touch()
        shared.apply(self.repo, self.home)
        self.assertTrue(shared.check(self.repo, self.home))
        self.assertTrue((self.home / '.claude/CLAUDE.md').samefile(source))
        shared.apply(self.repo, self.home)
        self.assertEqual(len(list((self.home / '.local/state/dotfiles/backups').iterdir())), 1)

    def test_different_personal_md_stops_before_any_mutation(self):
        self.shared_source()
        target = self.home / '.codex/AGENTS.md'
        target.parent.mkdir()
        target.write_text('personal')
        with self.assertRaisesRegex(RuntimeError, '先比较并合并'):
            shared.apply(self.repo, self.home)
        self.assertEqual(target.read_text(), 'personal')
        self.assertFalse((self.home / '.claude').exists())

    def config(self):
        (self.repo / 'Skillfile.json').write_text(json.dumps({'version': 1, 'repository': 'test/skills', 'enabled': ['demo']}))

    def install_record(self):
        path = self.home / '.agents/.skill-lock.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'version': 3, 'skills': {'demo': {'source': 'test/skills'}}}))

    def skill(self, relative):
        path = self.home / relative
        path.mkdir(parents=True)
        (path / 'SKILL.md').write_text('personal')
        return path

    def test_personal_skill_and_broken_symlink_preserved(self):
        self.config()
        target = self.skill('.agents/skills/demo')
        with patch.object(installer.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home), 2)
        run.assert_not_called()
        self.assertEqual((target / 'SKILL.md').read_text(), 'personal')
        shutil.rmtree(target)
        target.symlink_to(self.home / 'missing')
        self.assertEqual(installer.plan(self.repo, self.home)[2], ['demo'])
        with patch.object(installer.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home, update=True), 2)
        run.assert_not_called()

    def test_independent_claude_skill_blocks_managed_canonical_update(self):
        self.config()
        self.install_record()
        self.skill('.agents/skills/demo')
        self.skill('.claude/skills/demo')
        self.assertEqual(installer.plan(self.repo, self.home)[2], ['demo'])
        with patch.object(installer.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home, update=True), 2)
        run.assert_not_called()

    def test_cli_gets_unpinned_source_and_selection(self):
        self.config()
        def install(command, **kwargs):
            self.assertEqual(command[:5], ['npx', '--yes', 'skills@latest', 'add', 'test/skills'])
            self.assertEqual(command[-4:], ['--skill', 'demo', '--yes', '--json'])
            self.install_record()
            canonical = self.skill('.agents/skills/demo')
            client = self.home / '.claude/skills/demo'
            client.parent.mkdir(parents=True)
            client.symlink_to(canonical)
            return type('Result', (), {'returncode': 0})()
        with patch.object(installer.subprocess, 'run', side_effect=install), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home), 0)
        self.assertEqual(installer.plan(self.repo, self.home)[1:], ([], []))

    def test_cli_failure_is_not_success(self):
        self.config()
        with patch.object(installer.subprocess, 'run', return_value=type('Result', (), {'returncode': 1, 'stderr': 'offline', 'stdout': ''})()), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'offline'):
                installer.install(self.repo, self.home)

    def test_latest_step_migrates_sha_once_and_does_not_refresh_completed_step(self):
        self.config()
        self.install_record()
        lock = self.home / '.agents/.skill-lock.json'
        record = json.loads(lock.read_text())
        record['skills']['demo']['ref'] = 'a'*40
        lock.write_text(json.dumps(record))
        canonical = self.skill('.agents/skills/demo')
        client = self.home / '.claude/skills/demo'
        client.parent.mkdir(parents=True)
        client.symlink_to(canonical)
        (self.repo / 'scripts').mkdir()
        shutil.copyfile(ROOT / 'scripts/install-skills.py', self.repo / 'scripts/install-skills.py')
        shutil.copyfile(ROOT / 'updates/20261024-005-latest-skills.py', self.repo / 'updates/20261024-005-latest-skills.py')
        def apply(command, **kwargs):
            self.assertEqual(command, [str(self.repo / 'scripts/setup-skills.sh'), '--update'])
            self.install_record()
        with patch.object(runner.subprocess, 'run', side_effect=apply) as run:
            self.run_updates('status')
            run.assert_not_called()
            self.run_updates()
            run.assert_called_once()
            self.run_updates()
            run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
