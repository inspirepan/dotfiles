import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer_multi', ROOT / 'scripts/install-skills.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class MultiSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.repo = self.home / 'repo'
        self.repo.mkdir()
        self.config = {'version': 1, 'repository': 'own/skills', 'revision': 'a'*40, 'enabled': ['own-skill'], 'sources': [{'repository': 'third/skills', 'revision': 'b'*40, 'enabled': ['external']}]}
        self.lock = self.home / '.agents/.skill-lock.json'
        env = patch.dict(os.environ, {'XDG_STATE_HOME': '', 'CLAUDE_CONFIG_DIR': str(self.home / '.claude')})
        env.start()
        self.addCleanup(env.stop)
        self.save()

    def save(self):
        (self.repo / 'Skillfile.json').write_text(json.dumps(self.config))

    def installed(self, name, source, revision):
        target = self.home / '.agents/skills' / name
        target.mkdir(parents=True, exist_ok=True)
        (target / 'SKILL.md').write_text('installed')
        client = self.home / '.claude/skills' / name
        client.parent.mkdir(parents=True, exist_ok=True)
        if not client.is_symlink():
            client.symlink_to(target)
        records = json.loads(self.lock.read_text()) if self.lock.exists() else {'skills': {}}
        records['skills'][name] = {'source': source, 'ref': revision}
        self.lock.write_text(json.dumps(records))

    def test_each_source_has_separate_pinned_cli_call(self):
        calls = []
        def run(command, **kwargs):
            source = next(s for s in installer.sources(self.config) if s['repository'] in command[4])
            self.assertEqual(command[4], f"https://github.com/{source['repository']}/tree/{source['revision']}")
            selected = command[command.index('--skill')+1:-2]
            self.assertEqual(selected, source['enabled'])
            calls.append(source['repository'])
            for name in selected:
                self.installed(name, source['repository'], source['revision'])
            return type('Result', (), {'returncode': 0})()
        with patch.object(installer.subprocess, 'run', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home), 0)
        self.assertEqual(calls, ['own/skills', 'third/skills'])
        with patch.object(installer.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home), 0)
        run.assert_not_called()

    def test_only_declared_origin_can_migrate(self):
        self.installed('own-skill', 'own/skills', 'a'*40)
        self.installed('external', 'old/source', 'b'*40)
        self.assertEqual(installer.plan(self.repo, self.home)[2], ['external'])
        self.config['sources'][0]['replaces'] = ['old/source']
        self.save()
        _, pending, conflicts = installer.plan(self.repo, self.home)
        self.assertEqual(pending, ['external'])
        self.assertEqual(conflicts, [])

    def test_same_revision_does_not_hide_source_change(self):
        self.config['sources'][0]['revision'] = 'a'*40
        self.config['sources'][0]['replaces'] = ['old/source']
        self.save()
        self.installed('own-skill', 'own/skills', 'a'*40)
        self.installed('external', 'old/source', 'a'*40)
        self.assertEqual(installer.plan(self.repo, self.home)[1], ['external'])

    def test_duplicate_name_rejected_before_install(self):
        self.config['sources'][0]['enabled'] = ['own-skill']
        self.save()
        with self.assertRaisesRegex(ValueError, '只能启用一个来源'):
            installer.plan(self.repo, self.home)

    def test_personal_external_is_preserved_while_other_source_installs(self):
        target = self.home / '.agents/skills/external'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('personal')
        def run(command, **kwargs):
            self.assertIn('own/skills', command[4])
            self.installed('own-skill', 'own/skills', 'a'*40)
            return type('Result', (), {'returncode': 0})()
        with patch.object(installer.subprocess, 'run', side_effect=run), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.install(self.repo, self.home), 2)
        self.assertEqual((target / 'SKILL.md').read_text(), 'personal')


if __name__ == '__main__':
    unittest.main()
