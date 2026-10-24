import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rename', ROOT / 'updates/20261024-003-klaude-session-logs.py')
rename = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rename)


class RenameTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.repo = self.home / 'repo'
        self.repo.mkdir()
        (self.repo / 'Skillfile.json').write_text(json.dumps({'repository': 'inspirepan/agent-skills'}))
        self.lock = self.home / '.agents/.skill-lock.json'
        self.lock.parent.mkdir()
        self.canonical = self.home / '.agents/skills/session-logs'
        self.canonical.mkdir(parents=True)
        (self.canonical / 'SKILL.md').write_text('personal or managed')
        env = patch.dict(os.environ, {'XDG_STATE_HOME': '', 'CLAUDE_CONFIG_DIR': str(self.home / '.claude')})
        env.start()
        self.addCleanup(env.stop)

    def record(self, source):
        self.lock.write_text(json.dumps({'skills': {'session-logs': {'source': source}}}))

    def test_personal_skill_is_preserved(self):
        self.record('someone/else')
        with patch.object(rename.subprocess, 'run') as run:
            self.assertTrue(rename.check(self.repo, self.home))
            rename.apply(self.repo, self.home)
        run.assert_not_called()
        self.assertTrue((self.canonical / 'SKILL.md').exists())

    def test_independent_client_is_not_removed(self):
        self.record('inspirepan/agent-skills')
        client = self.home / '.claude/skills/session-logs'
        client.mkdir(parents=True)
        (client / 'SKILL.md').write_text('personal')
        with patch.object(rename.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, '个人内容'):
                rename.apply(self.repo, self.home)
        run.assert_not_called()
        self.assertEqual((client / 'SKILL.md').read_text(), 'personal')

    def test_independent_legacy_shared_agent_is_preserved(self):
        self.record('inspirepan/agent-skills')
        legacy = self.home / '.cursor/skills/session-logs'
        legacy.mkdir(parents=True)
        (legacy / 'SKILL.md').write_text('personal')
        with patch.object(rename.subprocess, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, '个人内容'):
                rename.apply(self.repo, self.home)
        run.assert_not_called()
        self.assertEqual((legacy / 'SKILL.md').read_text(), 'personal')

    def test_owned_install_uses_cli_and_requires_verified_removal(self):
        self.record('inspirepan/agent-skills')
        def remove(command, **kwargs):
            self.assertEqual(command[:5], ['npx', '--yes', 'skills@1.7.4', 'remove', 'session-logs'])
            self.assertIn('claude-code', command)
            self.assertIn('codex', command)
            self.lock.write_text('{"skills": {}}')
        with patch.object(rename.subprocess, 'run', side_effect=remove):
            rename.apply(self.repo, self.home)
        self.assertTrue(rename.check(self.repo, self.home))
        self.record('inspirepan/agent-skills')
        with patch.object(rename.subprocess, 'run'):
            with self.assertRaisesRegex(RuntimeError, '仍被其他 Agent 使用'):
                rename.apply(self.repo, self.home)


if __name__ == '__main__':
    unittest.main()
