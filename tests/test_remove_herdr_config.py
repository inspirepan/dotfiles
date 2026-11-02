import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'remove_herdr_config', ROOT / 'updates/20261103-001-remove-herdr-config.py'
)
remove_herdr_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remove_herdr_config)


class RemoveHerdrConfigTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repo'
        self.home = self.root / 'home'
        self.path = self.home / '.config/herdr/config.toml'
        self.path.parent.mkdir(parents=True)

    def test_dangling_managed_link_is_backed_up_once_without_touching_app(self):
        source = self.repo / 'config/.config/herdr/config.toml'
        self.path.symlink_to(source)
        app = self.home / '.config/herdr-app/settings.json'
        app.parent.mkdir()
        app.write_text('personal')
        self.assertFalse(remove_herdr_config.check(self.repo, self.home))
        remove_herdr_config.apply(self.repo, self.home)
        self.assertTrue(remove_herdr_config.check(self.repo, self.home))
        self.assertFalse(self.path.is_symlink())
        backup, = (self.home / '.local/state/dotfiles/backups').iterdir()
        self.assertEqual((backup / 'config.toml').readlink(), source)
        remove_herdr_config.apply(self.repo, self.home)
        self.assertEqual(list(backup.parent.iterdir()), [backup])
        self.assertEqual(app.read_text(), 'personal')

    def test_personal_config_is_preserved(self):
        self.path.write_text('personal')
        self.assertTrue(remove_herdr_config.check(self.repo, self.home))
        remove_herdr_config.apply(self.repo, self.home)
        self.assertEqual(self.path.read_text(), 'personal')
        self.assertFalse((self.home / '.local').exists())


if __name__ == '__main__':
    unittest.main()