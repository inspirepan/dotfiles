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


installer = load(ROOT / 'scripts/install-skills.py', 'lark_installer')
step = load(ROOT / 'updates/20261107-002-lark-document-skills.py', 'lark_step')

# The other 23 skills in the official source at the time of this change.
EXTRAS = [
    'lark-approval', 'lark-apps', 'lark-attendance', 'lark-base', 'lark-calendar',
    'lark-contact', 'lark-event', 'lark-im', 'lark-mail', 'lark-markdown',
    'lark-meeting', 'lark-minutes', 'lark-note', 'lark-okr', 'lark-openapi-explorer',
    'lark-sheets', 'lark-skill-maker', 'lark-slides', 'lark-task', 'lark-vc',
    'lark-vc-agent', 'lark-workflow-meeting-summary', 'lark-workflow-standup-report',
]


class LarkSkillsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.repo = self.home / 'repo'
        (self.repo / 'scripts').mkdir(parents=True)
        shutil.copyfile(ROOT / 'scripts/install-skills.py', self.repo / 'scripts/install-skills.py')
        self.config = installer.load_config(ROOT)
        self.source = next(s for s in installer.sources(self.config) if s['repository'] == installer.LARK_SOURCE)
        self.enabled = self.source['enabled']
        self.save_config()
        self.lock = self.home / 'state/skills/.skill-lock.json'
        self.lock.parent.mkdir(parents=True)
        self.records = {}
        self.calls = []
        env = patch.dict(os.environ, {
            'XDG_STATE_HOME': str(self.home / 'state'),
            'XDG_CONFIG_HOME': str(self.home / 'config'),
            'CLAUDE_CONFIG_DIR': str(self.home / 'claude'),
        }, clear=True)
        env.start()
        self.addCleanup(env.stop)

    def save_config(self):
        (self.repo / 'Skillfile.json').write_text(json.dumps(self.config))

    def record(self, name):
        return {
            'source': 'open.feishu.cn', 'sourceType': 'well-known',
            'sourceBaseUrl': installer.LARK_SOURCE,
            'sourceUrl': f'{installer.LARK_SOURCE}/.well-known/agent-skills/{name}.tar.gz',
        }

    def installed(self, name, record):
        target = self.home / '.agents/skills' / name
        target.mkdir(parents=True, exist_ok=True)
        (target / 'SKILL.md').write_text(name)
        client = self.home / 'claude/skills' / name
        client.parent.mkdir(parents=True, exist_ok=True)
        if not client.is_symlink():
            client.symlink_to(target)
        if record is not None:
            self.records[name] = record
        self.lock.write_text(json.dumps({'skills': self.records}))

    def install_enabled(self):
        for source in installer.sources(self.config):
            for name in source['enabled']:
                self.installed(name, self.record(name) if source == self.source else {'source': source['repository']})

    def cli(self, command, **kwargs):
        self.calls.append(command)
        self.assertNotIn('--all', command)
        self.assertNotIn('*', command)
        if command[3] == 'add':
            self.assertEqual(command[4], installer.LARK_SOURCE)
            self.assertNotIn('--json', command)
            selected = command[command.index('--skill') + 1:command.index('--yes', 2)]
            self.assertEqual(selected, self.enabled)
            for name in selected:
                self.installed(name, self.record(name))
        else:
            self.assertEqual(command[:4], ['npx', '--yes', 'skills@1.7.4', 'remove'])
            self.assertIn('codex', command)
            self.assertIn('claude-code', command)
            for name in command[4:command.index('--global')]:
                (self.home / 'claude/skills' / name).unlink()
                shutil.rmtree(self.home / '.agents/skills' / name)
                del self.records[name]
            self.lock.write_text(json.dumps({'skills': self.records}))
        return subprocess.CompletedProcess(command, 0, stdout='', stderr='')

    def test_full_source_removes_only_other_23_and_repeat_has_no_cli(self):
        self.install_enabled()
        for name in EXTRAS:
            self.installed(name, self.record(name))
        for name, record in [('lark-personal', None), ('lark-other', {'source': 'personal/skills'})]:
            self.installed(name, record)
        self.installed('unrelated', self.record('unrelated'))
        with patch.object(subprocess, 'run', side_effect=self.cli):
            self.assertFalse(step.check(self.repo, self.home))
            step.apply(self.repo, self.home)
            self.assertEqual(len(self.calls), 1)
            self.assertEqual(self.calls[0][4:self.calls[0].index('--global')], EXTRAS)
            self.assertTrue(step.check(self.repo, self.home))
            step.apply(self.repo, self.home)
            self.assertEqual(len(self.calls), 1)
        for name in [*self.enabled, 'lark-personal', 'lark-other', 'unrelated']:
            self.assertEqual((self.home / '.agents/skills' / name / 'SKILL.md').read_text(), name)

    def test_missing_five_installed_before_extra_cleanup_and_manifest_controls_retention(self):
        self.source['enabled'] = []
        self.install_enabled()
        self.source['enabled'] = self.enabled
        self.save_config()
        self.installed('lark-future', self.record('lark-future'))
        with patch.object(subprocess, 'run', side_effect=self.cli):
            step.apply(self.repo, self.home)
            self.assertEqual([command[3] for command in self.calls], ['add', 'remove'])
            self.assertTrue(step.check(self.repo, self.home))
        self.source['enabled'] = self.enabled[1:]
        self.save_config()
        self.calls.clear()
        with patch.object(subprocess, 'run', side_effect=self.cli):
            step.apply(self.repo, self.home)
        self.assertEqual(self.calls[0][4:self.calls[0].index('--global')], self.enabled[:1])

    def test_independent_clients_and_shared_symlink_block_before_cli(self):
        self.install_enabled()
        name = EXTRAS[0]
        self.installed(name, self.record(name))
        canonical = self.home / '.agents/skills' / name
        for directory in [self.home / 'claude/skills', self.home / '.cursor/skills', self.home / 'config/agents/skills']:
            with self.subTest(directory=directory):
                directory.mkdir(parents=True, exist_ok=True)
                entry = directory / name
                if entry.is_symlink():
                    entry.unlink()
                entry.mkdir()
                (entry / 'SKILL.md').write_text('personal')
                with patch.object(subprocess, 'run') as run, self.assertRaisesRegex(RuntimeError, '个人内容'):
                    step.apply(self.repo, self.home)
                run.assert_not_called()
                self.assertEqual((entry / 'SKILL.md').read_text(), 'personal')
                shutil.rmtree(entry)
        canonical.rename(self.home / 'personal')
        canonical.symlink_to(self.home / 'personal')
        with patch.object(subprocess, 'run') as run, self.assertRaisesRegex(RuntimeError, '个人内容'):
            step.apply(self.repo, self.home)
        run.assert_not_called()

    def test_url_lock_must_match_all_origin_fields(self):
        self.install_enabled()
        name = self.enabled[0]
        for field, value in [
            ('source', 'other.example'), ('sourceType', 'github'),
            ('sourceBaseUrl', 'https://open.feishu.cn/other'),
            ('sourceUrl', f'{installer.LARK_SOURCE}/.well-known/agent-skills/other.tar.gz'),
        ]:
            with self.subTest(field=field):
                self.records[name] = {**self.record(name), field: value}
                self.lock.write_text(json.dumps({'skills': self.records}))
                self.assertEqual(installer.plan(self.repo, self.home)[2], [name])
                self.installed(EXTRAS[0], {**self.record(EXTRAS[0]), field: value})
                self.assertEqual(step.managed(self.repo, self.home, installer), [])
                with patch.object(subprocess, 'run') as run:
                    self.assertEqual(installer.install(self.repo, self.home), 2)
                run.assert_not_called()
        self.source['repository'] = 'https://other.example/skills'
        self.save_config()
        with self.assertRaisesRegex(ValueError, '飞书官方'):
            installer.load_config(self.repo)

    def test_cli_success_without_removing_lock_or_entry_fails_verification(self):
        self.install_enabled()
        name = EXTRAS[0]
        self.installed(name, self.record(name))
        with patch.object(subprocess, 'run'), self.assertRaisesRegex(RuntimeError, '未通过验证'):
            step.apply(self.repo, self.home)
        def remove_record(command, **kwargs):
            del self.records[name]
            self.lock.write_text(json.dumps({'skills': self.records}))
        with patch.object(subprocess, 'run', side_effect=remove_record), self.assertRaisesRegex(RuntimeError, '入口未移除'):
            step.apply(self.repo, self.home)


if __name__ == '__main__':
    unittest.main()
