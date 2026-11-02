import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("focus_border", ROOT / "updates/20261102-004-herdr-focus-border.py")
step = importlib.util.module_from_spec(spec)
spec.loader.exec_module(step)


class FocusBorderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.path = self.home / ".config/herdr-app/layouts/klaude.json"
        self.path.parent.mkdir(parents=True)
        self.layout = {"id": "root", "children": [{"content": {"tab": "active", "pane": {
            "focus": {"width": 1, "color": "accent"}, "border": {"width": 1, "color": "border"}
        }}}]}
        self.original = json.dumps(self.layout).encode()
        self.path.write_bytes(self.original)

    def test_apply_preserves_layout_and_is_idempotent(self):
        step.apply(ROOT, self.home)
        self.assertTrue(step.check(ROOT, self.home))
        result = json.loads(self.path.read_bytes())
        self.layout["children"][0]["content"]["pane"]["focus"] = step.FOCUS
        self.assertEqual(result, self.layout)
        backup, = (self.home / ".local/state/dotfiles/backups").glob("herdr-focus-border-*")
        self.assertEqual((backup / self.path.relative_to(self.home)).read_bytes(), self.original)
        before = self.path.read_bytes()
        step.apply(ROOT, self.home)
        self.assertEqual(self.path.read_bytes(), before)

    def test_runtime_override_is_preserved(self):
        state = self.path.parent / ".state/klaude.json"
        state.parent.mkdir()
        state.write_text(json.dumps({"file": self.layout}))
        with self.assertRaisesRegex(RuntimeError, "运行时状态"):
            step.apply(ROOT, self.home)
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertFalse(step.check(ROOT, self.home))

    def test_custom_focus_is_preserved(self):
        self.layout["children"][0]["content"]["pane"]["focus"]["color"] = "red"
        self.path.write_text(json.dumps(self.layout))
        with self.assertRaisesRegex(RuntimeError, "未覆盖"):
            step.apply(ROOT, self.home)
        self.assertEqual(json.loads(self.path.read_text()), self.layout)
