import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('klaude_agents', ROOT / 'updates/20261030-006-klaude-agent-title.py')
step = importlib.util.module_from_spec(spec)
spec.loader.exec_module(step)
title_spec = importlib.util.spec_from_file_location('agent_session_title', ROOT / 'updates/20261030-011-agent-session-title.py')
title_step = importlib.util.module_from_spec(title_spec)
title_spec.loader.exec_module(title_step)


class KlaudeAgentsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.layout = self.home / '.config/herdr-app/layouts/klaude.json'
        self.layout.parent.mkdir(parents=True)
        self.document = {'custom': [1, 2], 'children': [{'id': 'agents', 'content': {'mod': 'agents', 'props': {'x': 1}}}]}
        self.layout.write_text(json.dumps(self.document))
        self.original = self.layout.read_bytes()
        self.shared = self.layout.parent.parent / 'shared.json'
        self.shared.write_text('{"latest":true}')

    def test_deploy_backup_repair_and_repeat(self):
        target = next(iter(step.entries(ROOT, self.home)))
        target.parent.mkdir(parents=True)
        target.write_text('personal')
        step.apply(ROOT, self.home)
        self.assertTrue(step.check(ROOT, self.home))
        self.document['children'][0]['content']['mod'] = 'klaude-agents'
        self.assertEqual(json.loads(self.layout.read_text()), self.document)
        backup, = (self.home / '.local/state/dotfiles/backups').iterdir()
        self.assertEqual((backup / self.layout.relative_to(self.home)).read_bytes(), self.original)
        self.assertEqual((backup / target.relative_to(self.home)).read_text(), 'personal')
        self.assertEqual(self.shared.read_text(), '{"latest":true}')
        before = {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')}
        step.apply(ROOT, self.home)
        self.assertEqual(before, {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')})

    def test_conflicting_layout_stops_before_mod_changes(self):
        self.layout.write_text('{"id":"agents","content":{"mod":"custom"}}')
        self.assertFalse(step.check(ROOT, self.home))
        with self.assertRaises(RuntimeError):
            step.apply(ROOT, self.home)
        self.assertFalse((self.home / '.config/herdr-app/mods').exists())
        self.assertFalse((self.home / '.local').exists())

    @unittest.skipUnless(shutil.which('node'), 'Node.js is required')
    def test_real_render(self):
        subprocess.run(['node', str(ROOT / 'tests/herdr-agents-title.mjs')], check=True)

    def test_session_title_step_checks_both_links_without_writing(self):
        targets = []
        for mod in ('klaude-agents', 'klaude-pane'):
            self.assertFalse(title_step.check(ROOT, self.home))
            target = self.home / f'.config/herdr-app/mods/{mod}/main.js'
            target.parent.mkdir(parents=True)
            target.symlink_to(ROOT / f'config/.config/herdr-app/mods/{mod}/main.js')
            targets.append(target)
        before = {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')}
        self.assertTrue(title_step.check(ROOT, self.home))
        self.assertEqual(before, {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')})
        for target in targets:
            source = target.resolve()
            target.unlink()
            target.write_bytes(source.read_bytes())
            self.assertFalse(title_step.check(ROOT, self.home))
            target.unlink()
            target.symlink_to(source)
        self.assertEqual(title_step.SUPERSEDES, ('20261030-009-agent-folder-label',))
