import json
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
step = runpy.run_path(str(ROOT / 'updates/20261118-001-prune-pstack-skills.py'))


class PstackPruningTests(unittest.TestCase):
    def test_removes_managed_entries_and_stale_locks_without_touching_personal_skills(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            home = Path(temporary)
            shared = home / '.agents/skills'
            claude = home / '.claude/skills'
            shared.mkdir(parents=True)
            claude.mkdir(parents=True)
            owned = shared / 'poteto-mode'
            owned.mkdir()
            link = claude / owned.name
            link.symlink_to(owned)
            stale_link = claude / 'statechart'
            stale_link.symlink_to(shared / stale_link.name)
            keep = {'principle-prove-it-works': 'backnotprop/pstack', 'reflect': 'personal/skills'}
            for name in [*keep, 'setup-pstack']:
                (shared / name).mkdir()
            lock = shared.parent / '.skill-lock.json'

            def write_lock(sources):
                lock.write_text(json.dumps({'skills': {name: {'source': source} for name, source in sources.items()}}))

            write_lock({**keep, owned.name: 'backnotprop/pstack', stale_link.name: 'backnotprop/pstack'})
            saved = home / 'old-link'
            stale_link.rename(saved)
            stale_link.mkdir()
            with patch('subprocess.run') as run:
                self.assertFalse(step['check'](ROOT, home))
                with self.assertRaisesRegex(RuntimeError, '个人内容'):
                    step['apply'](ROOT, home)
                run.assert_not_called()
                self.assertTrue(owned.is_dir())
                stale_link.rename(home / 'personal-copy')
                saved.rename(stale_link)

                def removed(command, **kwargs):
                    if command[0] == 'trash':
                        self.assertEqual(set(command[1:]), {str(link), str(owned), str(stale_link)})
                        for index, path in enumerate(command[1:]):
                            Path(path).rename(home / f'trashed-{index}')
                    else:
                        self.assertEqual(command[:4], ['npx', '--yes', 'skills@1.7.4', 'remove'])
                        self.assertEqual(command[4:command.index('--global')], ['poteto-mode', 'statechart'])
                        write_lock(keep)

                run.side_effect = removed
                step['apply'](ROOT, home)
                self.assertTrue(step['check'](ROOT, home))
                step['apply'](ROOT, home)
                self.assertEqual(run.call_count, 2)
            for name in [*keep, 'setup-pstack']:
                self.assertTrue((shared / name).is_dir())
