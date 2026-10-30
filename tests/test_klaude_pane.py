import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('klaude_pane', ROOT / 'updates/20261030-007-klaude-pane-title.py')
step = importlib.util.module_from_spec(spec)
spec.loader.exec_module(step)


class KlaudePaneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.layout = self.home / '.config/herdr-app/layouts/klaude.json'
        self.layout.parent.mkdir(parents=True)
        self.document = {'children': [{'content': {'pane': {'header': {'content': {'mod': 'pane', 'props': {'x': 1}}}}}}]}
        self.layout.write_text(json.dumps(self.document))

    def test_backup_deploy_and_repeat(self):
        original = self.layout.read_bytes()
        target = next(iter(step.entries(ROOT, self.home)))
        target.parent.mkdir(parents=True)
        target.write_text('personal')
        step.apply(ROOT, self.home)
        self.assertTrue(step.check(ROOT, self.home))
        self.document['children'][0]['content']['pane']['header']['content']['mod'] = 'klaude-pane'
        self.assertEqual(json.loads(self.layout.read_text()), self.document)
        backup, = (self.home / '.local/state/dotfiles/backups').iterdir()
        self.assertEqual((backup / self.layout.relative_to(self.home)).read_bytes(), original)
        self.assertEqual((backup / target.relative_to(self.home)).read_text(), 'personal')
        self.assertTrue(all(p.is_symlink() and not p.readlink().is_absolute() for p in step.entries(ROOT, self.home)))
        before = {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')}
        step.apply(ROOT, self.home)
        self.assertEqual(before, {p: p.lstat().st_mtime_ns for p in self.home.rglob('*')})

    def test_missing_and_conflicting_layout_preserved(self):
        for content in ('{"children": []}', '{"content":{"pane":{"header":{"content":{"mod":"custom"}}}}}'):
            self.layout.write_text(content)
            self.assertFalse(step.check(ROOT, self.home))
            with self.assertRaises(RuntimeError):
                step.apply(ROOT, self.home)
            self.assertEqual(self.layout.read_text(), content)
            self.assertFalse((self.home / '.local').exists())
        self.layout.unlink()
        with self.assertRaises(RuntimeError):
            step.apply(ROOT, self.home)

    @unittest.skipUnless(shutil.which('node'), 'Node.js is required')
    def test_renderer(self):
        subprocess.run(['node', str(ROOT / 'tests/herdr-pane-title.mjs')], check=True)