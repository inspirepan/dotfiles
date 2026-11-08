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

    def run_updates(self, mode='update', components=(), verbose=False):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            runner.execute(self.repo, self.home, mode, components, verbose=verbose)
        return output.getvalue()

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

    def test_status_and_check_are_identical_readonly_and_concise(self):
        self.step('001', "    raise AssertionError('apply must not run')")
        before = sorted(self.root.rglob('*'))
        with patch.object(runner.subprocess, 'run') as run:
            status = self.run_updates('status')
            self.assertEqual(self.run_updates('check'), status)
            self.assertIn('待执行：001', status)
            self.assertIn('建议', status)
            run.assert_not_called()
        self.assertEqual(sorted(self.root.rglob('*')), before)

    def test_default_hides_completed_and_superseded_verbose_shows_all(self):
        self.step('001', "    (home / '001').touch()")
        successor = self.step('002', "    (home / '002').touch()")
        successor.write_text(successor.read_text() + "SUPERSEDES = ('001',)\n")
        self.run_updates()
        state = self.home / '.local/state/dotfiles/updates.json'
        before = (state.read_bytes(), state.stat().st_mtime_ns)
        for mode in ('status', 'check'):
            with self.subTest(mode=mode):
                self.assertEqual(self.run_updates(mode), '检查完成，无待办或冲突。\n')
                output = self.run_updates(mode, verbose=True)
                self.assertIn('已登记（未复查）：002', output)
                self.assertIn('已由后续步骤取代：001', output)
        self.assertEqual((state.read_bytes(), state.stat().st_mtime_ns), before)
        state.unlink()
        self.assertIn('可登记：002', self.run_updates('check'))

    def test_registered_steps_are_not_rechecked_but_hashes_are_verified(self):
        step = self.step('001', "    (home / '001').touch()")
        step.write_text(step.read_text().replace("return (home / '001').exists()", "raise AssertionError('registered check must not run')"))
        digest = next(runner.steps(self.repo))[1]
        state = self.home / '.local/state/dotfiles/updates.json'
        state.parent.mkdir(parents=True)
        state.write_text(json.dumps({'version': 1, 'completed': {'001': {'sha256': digest}}}))
        for mode in ('status', 'check'):
            self.assertEqual(self.run_updates(mode), '检查完成，无待办或冲突。\n')
            self.assertIn('已登记（未复查）', self.run_updates(mode, verbose=True))
        step.write_text(step.read_text() + '# changed\n')
        for mode in ('status', 'check'):
            with self.assertRaisesRegex(ValueError, '已应用的更新被修改'):
                self.run_updates(mode)

    def test_skill_conflicts_are_named_even_when_step_only_returns_false(self):
        (self.repo / 'Skillfile.json').write_text(json.dumps({
            'version': 1, 'repository': 'inspirepan/agent-skills', 'enabled': ['commit'],
        }))
        target = self.skill('.agents/skills/commit')
        self.step('001', "    raise AssertionError('apply must not run')")
        (self.repo / 'updates/components.json').write_text(json.dumps({'001': 'agents'}))
        before = sorted(self.root.rglob('*'))
        with patch.object(runner.subprocess, 'run') as run:
            for mode in ('status', 'check'):
                output = self.run_updates(mode, ['agents'])
                self.assertIn('技能冲突：commit', output)
                self.assertIn('~/.agents/skills/commit', output)
                self.assertIn('Claude', output)
                self.assertIn('待执行：001', output)
            run.assert_not_called()
        self.assertEqual(sorted(self.root.rglob('*')), before)
        self.assertEqual((target / 'SKILL.md').read_text(), 'personal')

    def test_skill_pending_and_independent_claude_conflict(self):
        self.config()
        output = self.run_updates('check')
        self.assertIn('技能待同步：demo', output)
        self.assertIn('scripts/setup-skills.sh --update', output)
        self.install_record()
        self.skill('.agents/skills/demo')
        client = self.skill('.claude/skills/demo')
        self.assertIn('技能冲突：demo', self.run_updates('status'))
        self.assertEqual((client / 'SKILL.md').read_text(), 'personal')

    @unittest.skipUnless(shutil.which('stow'), 'GNU Stow is required')
    def test_stow_simulation_links_conflicts_and_source_symlink(self):
        source = self.shared_source()
        target = self.home / '.codex/AGENTS.md'
        target.parent.mkdir()
        claude = self.home / '.claude/CLAUDE.md'
        claude.parent.mkdir()
        claude.symlink_to(os.path.relpath(source, claude.parent))
        for kind in ('missing', 'file', 'wrong', 'source-link'):
            with self.subTest(kind=kind):
                if os.path.lexists(target):
                    target.unlink()
                if kind == 'file':
                    target.write_text('personal')
                elif kind == 'wrong':
                    target.symlink_to(self.home / 'missing')
                elif kind == 'source-link':
                    target.symlink_to(os.path.relpath(self.repo / 'codex/.codex/AGENTS.md', target.parent))
                before = sorted(self.root.rglob('*'))
                output = self.run_updates('check')
                if kind == 'source-link':
                    self.assertEqual(output, '检查完成，无待办或冲突。\n')
                    self.assertIn('Stow 只读预演通过', self.run_updates('status', verbose=True))
                else:
                    self.assertIn('.codex/AGENTS.md', output)
                    self.assertIn('LINK:' if kind == 'missing' else 'would cause conflicts:', output)
                    self.assertIn('备份', output)
                self.assertEqual(sorted(self.root.rglob('*')), before)

    @unittest.skipUnless(shutil.which('stow'), 'GNU Stow is required')
    def test_stow_respects_ignores_and_existing_folded_parent(self):
        source = self.repo / 'ssh/.ssh'
        source.mkdir(parents=True)
        (source / 'config').write_text('ssh config')
        (self.home / '.ssh').symlink_to(os.path.relpath(source, self.home))
        package = self.repo / 'ssh'
        for name in ('README.md', '.gitignore', 'file~'):
            (package / name).write_text('ignored by Stow defaults')
        before = sorted(self.root.rglob('*'))
        self.assertEqual(self.run_updates('check'), '检查完成，无待办或冲突。\n')
        self.assertEqual(sorted(self.root.rglob('*')), before)
        (self.home / '.stow-global-ignore').write_text('^global-only$\nREADME\\.md$\n\\.gitignore$\nfile~$\n')
        (package / 'global-only').write_text('global ignore')
        before = sorted(self.root.rglob('*'))
        self.assertEqual(self.run_updates('check'), '检查完成，无待办或冲突。\n')
        self.assertEqual(sorted(self.root.rglob('*')), before)
        (package / '.stow-local-ignore').write_text('^local-only$\nREADME\\.md$\n\\.gitignore$\nfile~$\nglobal-only$\n')
        (package / 'local-only').write_text('local ignore')
        before = sorted(self.root.rglob('*'))
        self.assertEqual(self.run_updates('status'), '检查完成，无待办或冲突。\n')
        self.assertTrue((self.home / '.ssh').is_symlink())
        self.assertEqual((source / 'config').read_text(), 'ssh config')
        self.assertEqual(sorted(self.root.rglob('*')), before)

    def test_stow_missing_or_failed_is_reported(self):
        (self.repo / 'ssh').mkdir()
        with patch.object(runner.subprocess, 'run', side_effect=FileNotFoundError):
            with self.assertRaisesRegex(RuntimeError, '未找到 stow'):
                self.run_updates('check')
        result = type('Result', (), {'returncode': 2, 'stdout': '', 'stderr': 'invalid option'})()
        with patch.object(runner.subprocess, 'run', return_value=result) as run:
            with self.assertRaisesRegex(RuntimeError, 'Stow 预演失败.*invalid option'):
                self.run_updates('status')
            self.assertEqual(run.call_args.args[0][1:4], ['--simulate', '--verbose=1', '--no-folding'])

    def test_component_check_skips_unrelated_skills_and_stow(self):
        self.shared_source()
        self.config()
        self.skill('.agents/skills/demo')
        self.step('001', "    raise AssertionError('apply must not run')")
        (self.repo / 'updates/components.json').write_text(json.dumps({'001': 'herdr'}))
        output = self.run_updates('check', ['herdr'])
        self.assertNotIn('技能', output)
        self.assertNotIn('Stow', output)
        self.assertIn('update --component herdr', output)
        self.assertIn('跳过 Stow', self.run_updates('check', ['herdr'], verbose=True))

    def test_component_isolation_multiple_selection_and_shared_progress(self):
        blocked = self.step('001', "    raise RuntimeError('unrelated conflict')")
        blocked.write_text(blocked.read_text().replace(
            "    return (home / '001').exists()", "    raise RuntimeError('unrelated conflict')"))
        self.step('002', "    (home / '002').touch()")
        self.step('003', "    (home / '003').touch()")
        (self.repo / 'updates/components.json').write_text(json.dumps({
            '001': 'agents', '002': 'herdr', '003': 'karabiner',
        }))
        self.run_updates('status', ['herdr'])
        self.assertFalse((self.home / '.local').exists())
        self.run_updates(components=['herdr'])
        before = (self.home / '002').stat().st_mtime_ns
        self.assertFalse((self.home / '003').exists())
        self.run_updates(components=['herdr', 'karabiner'])
        self.assertEqual((self.home / '002').stat().st_mtime_ns, before)
        state = json.loads((self.home / '.local/state/dotfiles/updates.json').read_text())
        self.assertEqual(list(state['completed']), ['002', '003'])
        with self.assertRaisesRegex(RuntimeError, 'unrelated conflict'):
            self.run_updates()

    def test_component_failure_resumes_and_keeps_global_hash_checks(self):
        other = self.step('001', "    (home / '001').touch()")
        self.step('002', "    (home / '002').touch()")
        successor = self.step('003', "    if not (home / 'ready').exists():\n        raise RuntimeError('not ready')\n    (home / '002').unlink(missing_ok=True)\n    (home / '003').touch()")
        successor.write_text(successor.read_text() + "SUPERSEDES = ('002',)\n")
        (self.repo / 'updates/components.json').write_text(json.dumps({
            '001': 'agents', '002': 'herdr', '003': 'herdr',
        }))
        self.run_updates(components=['agents'])
        with self.assertRaisesRegex(RuntimeError, 'not ready'):
            self.run_updates(components=['herdr'])
        state = json.loads((self.home / '.local/state/dotfiles/updates.json').read_text())
        self.assertEqual(list(state['completed']), ['001', '002'])
        (self.home / 'ready').touch()
        self.run_updates(components=['herdr'])
        self.run_updates(components=['herdr'])
        self.assertFalse((self.home / '002').exists())
        self.assertTrue((self.home / '003').exists())
        other.write_text(other.read_text() + '# changed\n')
        for mode in ('update', 'status', 'check'):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, '已应用的更新被修改'):
                self.run_updates(mode, components=['herdr'])

    def test_invalid_component_selection_is_rejected(self):
        self.step('001', "    (home / '001').touch()")
        manifest = self.repo / 'updates/components.json'
        manifest.write_text(json.dumps({'001': 'herdr'}))
        with self.assertRaisesRegex(ValueError, '未知组件'):
            self.run_updates(components=['missing'])
        with self.assertRaisesRegex(ValueError, 'init 不支持'):
            self.run_updates('init', ['herdr'])
        self.assertFalse((self.home / '.local').exists())
        manifest.write_text(json.dumps({'missing': 'herdr'}))
        with self.assertRaisesRegex(ValueError, '组件清单与更新步骤不一致'):
            self.run_updates(components=['herdr'])
        self.assertFalse((self.home / '001').exists())

    def test_repository_components_cover_steps_and_superseded_steps(self):
        grouping = json.loads((ROOT / 'updates/components.json').read_text())
        available = list(runner.steps(ROOT))
        self.assertEqual(set(grouping), {identifier for identifier, _, _ in available})
        for identifier, _, step in available:
            for previous in getattr(step, 'SUPERSEDES', ()):
                self.assertEqual(grouping[identifier], grouping[previous])

    def test_cli_component_selection_and_rejected_arguments(self):
        with patch.object(runner.sys, 'argv', ['dotfiles', 'status', '--component', 'herdr', '--component', 'agents']), patch.object(runner, 'execute') as execute:
            runner.main()
        execute.assert_called_once_with(ROOT, Path.home(), 'status', ['herdr', 'agents'], verbose=False)
        with patch.object(runner.sys, 'argv', ['dotfiles', 'check', '--verbose']), patch.object(runner, 'execute') as execute:
            runner.main()
        execute.assert_called_once_with(ROOT, Path.home(), 'check', [], verbose=True)
        for arguments in (['init', '--component', 'herdr'], ['update', '--component', 'missing'], ['init', '--verbose'], ['update', '--verbose']):
            with self.subTest(arguments=arguments), patch.object(runner.sys, 'argv', ['dotfiles', *arguments]), patch.object(runner, 'execute') as execute, contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as stopped:
                    runner.main()
                self.assertEqual(stopped.exception.code, 2)
                execute.assert_not_called()

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
