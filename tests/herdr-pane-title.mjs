import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../config/.config/herdr-app/mods/klaude-pane/main.js', import.meta.url), 'utf8')
  .replace(/^import .*;\n/gm, '').replace('export default class Pane', 'globalThis.Pane = class Pane');
function el() {
  const node = { children: [], calls: {} };
  return new Proxy(node, { get(target, key) {
    if (key in target) return target[key];
    return (...args) => {
      target.calls[key] = args;
      if (key === 'child') target.children.push(args[0]);
      if (key === 'when' && args[0]) args[1](node.proxy);
      return node.proxy;
    };
  }, set(target, key, value) { target[key] = value; return true; } });
}
function element() { const e = el(); e.proxy = e; return e; }
let pane = { pane: 'p', program: { key: 'klaude', name: 'Klaude', agent: true }, title: '◐ Session title' };
const context = { View: class {}, div: element, svg: element, image: element, h_flex: element,
  panes: () => [{ pane: 'other', title: 'Wrong pane', program: pane.program }, pane], props: () => ({ pane: 'p' }), theme: () => ({}), home: () => '/home', run() {} };
vm.runInNewContext(source, context);
const app = new context.Pane();
function name() {
  const root = app.render({});
  const child = root.children.find(x => x?.calls?.font_medium);
  assert.ok(child.calls.flex_none && child.calls.truncate);
  assert.equal(child.calls.max_w[0], 260);
  const cwd = root.children.find(x => x?.children?.[0] === '/work/project');
  if (pane.cwd) assert.ok(cwd.calls.truncate && cwd.calls.flex_1);
  return child.children[0];
}
assert.equal(name(), '◐ Session title');
pane.cwd = '/work/project'; app.hovered = true; assert.equal(name(), '◐ Session title');
pane.title = ''; assert.equal(name(), 'Klaude');
pane = { ...pane, title: 'Other title', program: { key: 'other', name: 'Other', agent: true } };
assert.equal(name(), 'Other title');
for (const title of [' .config ', ' [P1] Session ', ' ◐ Updated title ']) {
  pane.title = title;
  assert.equal(name(), title.trim());
}
pane.title = '  '; assert.equal(name(), 'Other');
pane.title = null; assert.equal(name(), 'Other');
pane = { ...pane, title: 'Terminal title', program: { name: 'zsh', shell: true } };
assert.equal(name(), 'zsh');
pane.program = { name: 'Editor' };
assert.equal(name(), 'Terminal title');
console.log('Pane rendering passed.');