import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('herdr_app', ROOT / 'updates/20261030-001-herdr-app.py')
herdr_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(herdr_app)


class HerdrAppTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repo'
        self.home = self.root / 'home'
        self.home.mkdir()
        shutil.copytree(ROOT / 'config/.config/herdr-app', self.repo / 'config/.config/herdr-app')

    def apply(self):
        with redirect_stdout(io.StringIO()):
            herdr_app.apply(self.repo, self.home)

    def test_new_home_check_is_read_only_and_apply_is_idempotent(self):
        self.assertFalse(herdr_app.check(self.repo, self.home))
        self.assertEqual(list(self.home.iterdir()), [])
        self.apply()
        self.assertTrue(herdr_app.check(self.repo, self.home))
        links = {path: path.lstat().st_mtime_ns for path in herdr_app.entries(self.repo, self.home)}
        self.apply()
        self.assertEqual(links, {path: path.lstat().st_mtime_ns for path in links})
        self.assertFalse((self.home / '.local').exists())

    def test_existing_files_are_backed_up_and_runtime_state_is_untouched(self):
        directory = self.home / '.config/herdr-app'
        directory.mkdir(parents=True)
        (directory / 'settings.json').write_text('{"font_size": 17}')
        (directory / 'shared.json').write_text('{"layout": "personal"}')
        (directory / 'programs.json').symlink_to('missing-personal-programs.json')
        self.apply()
        backup, = (self.home / '.local/state/dotfiles/backups').iterdir()
        self.assertEqual((backup / '.config/herdr-app/settings.json').read_text(), '{"font_size": 17}')
        self.assertEqual((backup / '.config/herdr-app/programs.json').readlink(), Path('missing-personal-programs.json'))
        self.assertEqual((directory / 'shared.json').read_text(), '{"layout": "personal"}')
        self.assertTrue(herdr_app.check(self.repo, self.home))
        self.apply()
        self.assertEqual(list(backup.parent.iterdir()), [backup])
        self.assertEqual(set(directory.iterdir()), {
            directory / 'keys.json', directory / 'settings.json', directory / 'programs.json',
            directory / 'themes', directory / 'shared.json',
        })

    def test_directory_conflict_is_detected_before_any_changes(self):
        directory = self.home / '.config/herdr-app'
        (directory / 'programs.json').mkdir(parents=True)
        (directory / 'settings.json').write_text('personal')
        with self.assertRaises(RuntimeError):
            self.apply()
        self.assertFalse((directory / 'keys.json').exists())
        self.assertEqual((directory / 'settings.json').read_text(), 'personal')
        self.assertFalse((self.home / '.local').exists())

    def test_symlinked_parent_is_not_followed(self):
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        (self.home / '.config').symlink_to(elsewhere)
        with self.assertRaises(RuntimeError):
            self.apply()
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_missing_source_is_detected_before_any_changes(self):
        source = self.repo / 'config/.config/herdr-app/programs.json'
        source.rename(source.with_suffix('.saved'))
        with self.assertRaises(RuntimeError):
            self.apply()
        self.assertEqual(list(self.home.iterdir()), [])


if __name__ == '__main__':
    unittest.main()