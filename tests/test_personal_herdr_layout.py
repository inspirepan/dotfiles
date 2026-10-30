import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('personal_layout', ROOT / 'updates/20261030-003-personal-herdr-layout.py')
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


class PersonalLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.main = self.home / '.config/herdr-app/layouts/main.json'
        self.main.parent.mkdir(parents=True)
        self.personal = self.main.with_name('klaude.json')
        self.original = b'{ "size": 42, "children": [{"content":{"mod":"tabs","props":{"custom":true}}}, {"content":{"mod":"agents"}}] }\n'
        self.document = json.loads(self.original)
        self.document['children'][0]['content']['mod'] = 'klaude-tabs'
        self.main.write_text(json.dumps(self.document, indent=4) + '\n')
        self.patched = self.main.read_bytes()
        self.backups = self.home / '.local/state/dotfiles/backups'
        backup = self.backups / 'klaude-menu-fixture/.config/herdr-app/layouts/main.json'
        backup.parent.mkdir(parents=True)
        backup.write_bytes(self.original)
        self.shared = self.home / '.config/herdr-app/shared.json'
        self.shared.write_text('{"layout":"main","space.colors":{"latest":"blue"}}\n')

    def apply(self):
        with redirect_stdout(io.StringIO()):
            layout.apply(ROOT, self.home)

    def test_restore_exact_bytes_preserve_custom_layout_and_repeat_without_backup(self):
        shared = self.shared.read_bytes()
        before = sorted(self.home.rglob('*'))
        self.assertFalse(layout.check(ROOT, self.home))
        self.assertEqual(sorted(self.home.rglob('*')), before)
        self.apply()
        self.assertEqual(self.main.read_bytes(), self.original)
        self.assertEqual(self.personal.read_bytes(), self.patched)
        self.assertEqual(self.shared.read_bytes(), shared)
        backup, = self.backups.glob('personal-herdr-layout-*')
        self.assertEqual((backup / self.main.relative_to(self.home)).read_bytes(), self.patched)
        before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob('*') if p.is_file()}
        self.assertTrue(layout.check(ROOT, self.home))
        self.apply()
        self.assertEqual({p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob('*') if p.is_file()}, before)

    def test_same_personal_layout_is_preserved(self):
        self.personal.write_text(json.dumps(self.document))
        original = self.personal.read_bytes()
        self.apply()
        self.assertEqual(self.personal.read_bytes(), original)
        self.assertEqual(self.main.read_bytes(), self.original)

    def test_later_app_upgrade_and_personal_edits_do_not_repeat_migration(self):
        self.apply()
        self.main.write_text('{"version":"new","children":[{"content":{"mod":"tabs"}}]}')
        personal = json.loads(self.personal.read_text())
        personal['size'] = 88
        self.personal.write_text(json.dumps(personal))
        before = {p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        self.assertTrue(layout.check(ROOT, self.home))
        self.apply()
        self.assertEqual({p: p.read_bytes() for p in self.home.rglob('*') if p.is_file()}, before)

    def test_different_personal_layout_conflicts_before_any_write(self):
        self.personal.write_text('{"content":{"mod":"custom"}}')
        original = self.personal.read_bytes()
        with self.assertRaisesRegex(RuntimeError, '个人布局.*未覆盖'):
            self.apply()
        self.assertEqual(self.personal.read_bytes(), original)
        self.assertEqual(self.main.read_bytes(), self.patched)
        self.assertEqual(list(self.backups.glob('personal-herdr-layout-*')), [])

    def test_modified_main_conflicts_before_any_write(self):
        self.document['size'] = 99
        self.main.write_text(json.dumps(self.document))
        before = self.main.read_bytes()
        with self.assertRaisesRegex(RuntimeError, '可能有用户修改'):
            self.apply()
        self.assertEqual(self.main.read_bytes(), before)
        self.assertFalse(self.personal.exists())
        self.assertEqual(list(self.backups.glob('personal-herdr-layout-*')), [])

    def test_concurrent_main_change_is_not_overwritten(self):
        replace = layout.os.replace
        def concurrent_change(source, target):
            replace(source, target)
            if target == self.personal:
                self.main.write_text('{"user":"latest"}')
        with patch.object(layout.os, 'replace', side_effect=concurrent_change):
            with self.assertRaisesRegex(RuntimeError, '布局已变化'):
                self.apply()
        self.assertEqual(self.main.read_text(), '{"user":"latest"}')
