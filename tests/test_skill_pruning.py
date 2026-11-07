import importlib.util
from contextlib import chdir
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prune', ROOT / 'updates/20261107-001-prune-global-skills.py')
prune = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prune)


class PruningTests(unittest.TestCase):
    def test_only_upstream_owned_skills_are_removed_and_personal_entries_block_removal(self):
        retired = {
            'playwright': 'openai/skills',
            'unslop': 'backnotprop/pstack',
            'ketchup-video': 'backnotprop/pstack',
            'no-comments': 'backnotprop/pstack',
            'make-bot-ui': 'backnotprop/pstack',
        }
        kept = ['poteto-mode', 'bro', 'in-your-own-words', 'principle-prove-it-works', 'submit-pr']
        for ownership in ['upstream', 'foreign', 'untracked', 'mixed']:
            with self.subTest(ownership=ownership), tempfile.TemporaryDirectory() as temporary:
                home = Path(temporary)
                shared = home / '.agents/skills'
                claude = home / 'custom-claude/skills'
                config = home / 'custom-config'
                lock = home / 'state/skills/.skill-lock.json'
                lock.parent.mkdir(parents=True)
                claude.mkdir(parents=True)
                records = {name: {'source': 'backnotprop/pstack'} for name in kept}
                selected = []
                for name, source in retired.items():
                    if ownership == 'upstream' or (ownership == 'mixed' and name == 'playwright'):
                        records[name] = {'source': source}
                        selected.append(name)
                    elif ownership != 'untracked':
                        records[name] = {'source': 'personal/skills'}
                for name in [*retired, *kept]:
                    canonical = shared / name
                    canonical.mkdir(parents=True)
                    (canonical / 'SKILL.md').write_text(name)
                    (claude / name).symlink_to(canonical)
                lock.write_text(json.dumps({'skills': records}))
                env = {'XDG_STATE_HOME': str(home / 'state'), 'XDG_CONFIG_HOME': str(config),
                       'CLAUDE_CONFIG_DIR': str(claude.parent)}
                with patch.dict(os.environ, env, clear=True), patch.object(prune.subprocess, 'run') as run:
                    self.assertEqual(prune.check(ROOT, home), not selected)
                    if selected:
                        for directory in [claude, config / 'agents/skills', home / '.cursor/skills']:
                            directory.mkdir(parents=True, exist_ok=True)
                            entry = directory / 'playwright'
                            if entry.is_symlink():
                                entry.rename(home / 'saved-link')
                            entry.mkdir()
                            (entry / 'SKILL.md').write_text('personal')
                            with self.assertRaisesRegex(RuntimeError, '个人内容'):
                                prune.apply(ROOT, home)
                            run.assert_not_called()
                            self.assertEqual((entry / 'SKILL.md').read_text(), 'personal')
                            entry.rename(home / f'personal-{directory.parent.name}')
                        (home / 'saved-link').rename(claude / 'playwright')
                        cases = [
                            ('XDG_CONFIG_HOME', '', home / '.config/agents/skills'),
                            ('XDG_CONFIG_HOME', '   ', home / '   /agents/skills'),
                            ('CLAUDE_CONFIG_DIR', '', home / '.claude/skills'),
                            ('CLAUDE_CONFIG_DIR', ' \t ', home / '.claude/skills'),
                            ('CLAUDE_CONFIG_DIR', f' \t{claude.parent} \n', claude),
                        ]
                        for index, (variable, value, directory) in enumerate(cases):
                            with self.subTest(variable=variable, value=value), patch.dict(os.environ, {variable: value}), chdir(home):
                                directory.mkdir(parents=True, exist_ok=True)
                                entry = directory / 'playwright'
                                saved_link = home / f'fallback-link-{index}'
                                if entry.is_symlink():
                                    entry.rename(saved_link)
                                entry.mkdir()
                                (entry / 'SKILL.md').write_text('personal')
                                with self.assertRaisesRegex(RuntimeError, '个人内容'):
                                    prune.apply(ROOT, home)
                                run.assert_not_called()
                                self.assertEqual((entry / 'SKILL.md').read_text(), 'personal')
                                entry.rename(home / f'fallback-personal-{index}')
                                if saved_link.is_symlink():
                                    saved_link.rename(entry)
                        with self.assertRaisesRegex(RuntimeError, '仍有安装记录'):
                            prune.apply(ROOT, home)
                        run.reset_mock()

                    def remove(command, **kwargs):
                        self.assertEqual(command[:4], ['npx', '--yes', 'skills@1.7.4', 'remove'])
                        self.assertEqual(command[4:command.index('--global')], selected)
                        self.assertIn('codex', command)
                        self.assertIn('claude-code', command)
                        self.assertEqual(kwargs['env']['HOME'], str(home))
                        for name in selected:
                            (claude / name).rename(home / f'removed-link-{name}')
                            (shared / name).rename(home / f'removed-{name}')
                            del records[name]
                        lock.write_text(json.dumps({'skills': records}))

                    run.side_effect = remove
                    prune.apply(ROOT, home)
                    self.assertEqual(run.call_count, bool(selected))
                    self.assertTrue(prune.check(ROOT, home))
                    prune.apply(ROOT, home)
                    self.assertEqual(run.call_count, bool(selected))
                for name in [*kept, *(name for name in retired if name not in selected)]:
                    self.assertEqual((shared / name / 'SKILL.md').read_text(), name)
                    self.assertTrue((claude / name).is_symlink())


if __name__ == '__main__':
    unittest.main()
