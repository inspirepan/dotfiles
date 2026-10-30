import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('herdr_menu', ROOT / 'updates/20261030-002-klaude-menu-first.py')
menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(menu)
spec = importlib.util.spec_from_file_location('herdr_mods', ROOT / 'updates/20261030-004-personal-herdr-mods.py')
mods = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mods)


class HerdrMenuTests(unittest.TestCase):
    def test_mod_drift_is_backed_up_and_repaired_without_patching_main(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            layout = home / '.config/herdr-app/layouts/main.json'
            layout.parent.mkdir(parents=True)
            layout.write_text('{"content":{"mod":"tabs"}}')
            before = layout.read_bytes()
            with redirect_stdout(io.StringIO()):
                mods.apply(ROOT, home)
            target = home / '.config/herdr-app/mods/klaude-menu/main.js'
            saved_link = target.with_suffix('.old-link')
            target.rename(saved_link)
            target.write_text('personal edit')
            self.assertFalse(mods.check(ROOT, home))
            with redirect_stdout(io.StringIO()):
                mods.apply(ROOT, home)
            self.assertTrue(mods.check(ROOT, home))
            backup, = (home / '.local/state/dotfiles/backups').iterdir()
            self.assertEqual((backup / target.relative_to(home)).read_text(), 'personal edit')
            self.assertEqual(layout.read_bytes(), before)
            mods.apply(ROOT, home)
            self.assertEqual(list(backup.parent.iterdir()), [backup])

    def test_layout_patch_preserves_other_preferences_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            layout = home / '.config/herdr-app/layouts/main.json'
            layout.parent.mkdir(parents=True)
            document = {'size': 42, 'children': [
                {'id': 'tabs', 'content': {'mod': 'tabs', 'props': {'custom': True}}},
                {'id': 'agents', 'content': {'mod': 'agents'}},
            ]}
            layout.write_text(json.dumps(document))
            original = layout.read_bytes()
            with redirect_stdout(io.StringIO()):
                menu.apply(ROOT, home)
            self.assertTrue(menu.check(ROOT, home))
            document['children'][0]['content']['mod'] = 'klaude-tabs'
            self.assertEqual(json.loads(layout.read_text()), document)
            backup, = (home / '.local/state/dotfiles/backups').iterdir()
            self.assertEqual((backup / '.config/herdr-app/layouts/main.json').read_bytes(), original)
            before = layout.stat().st_mtime_ns
            menu.apply(ROOT, home)
            self.assertEqual(layout.stat().st_mtime_ns, before)
            self.assertEqual(list(backup.parent.iterdir()), [backup])

    def test_missing_or_custom_layout_is_preserved_without_partial_deploy(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            self.assertFalse(menu.check(ROOT, home))
            with self.assertRaises(RuntimeError):
                menu.apply(ROOT, home)
            self.assertEqual(list(home.iterdir()), [])
            layout = home / '.config/herdr-app/layouts/main.json'
            layout.parent.mkdir(parents=True)
            layout.write_text('{"content":{"mod":"personal-tabs"}}')
            with self.assertRaises(RuntimeError):
                menu.apply(ROOT, home)
            self.assertEqual(layout.read_text(), '{"content":{"mod":"personal-tabs"}}')
            self.assertFalse((home / '.config/herdr-app/mods').exists())

    @unittest.skipUnless(shutil.which('node'), 'Node.js is required for the menu smoke test')
    def test_klaude_is_first_and_keyboard_shortcuts_match_the_display(self):
        subprocess.run(['node', str(ROOT / 'tests/herdr-menu-order.mjs')], check=True)