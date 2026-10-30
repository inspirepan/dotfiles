import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../config/.config/herdr-app/mods/klaude-agents/main.js', import.meta.url), 'utf8')
  .replace(/^import .*;\n/gm, '').replace('export default class Agents', 'globalThis.Agents = class Agents');
function el() {
  const obj = { _children: [], idValue: null, calls: {} };
  const proxy = new Proxy(obj, { get(target, key) {
    if (key in target) return target[key];
    return (...args) => {
      target.calls[key] = args;
      if (key === 'id') target.idValue = args[0];
      if (key === 'child') target._children.push(args[0]);
      if (key === 'children') target._children.push(...args[0]);
      if (key === 'when' && args[0]) args[1](proxy);
      return proxy;
    };
  }});
  return proxy;
}
let sort = 'priority';
let sidebarWidth = 268;
let tab = { id: 'tab', name: '1', named: false };
const program = { key: 'klaude', name: 'Klaude', agent: true };
let ps = [
  { pane: 'p1', tab: 'tab', terminal: 't1', program, title: '◐ First session', cwd: '/Users/test/code/dev' },
  { pane: 'p2', tab: 'tab', terminal: 't2', program: { key: 'codex', name: 'Codex', agent: true }, title: '[P1] Second session', cwd: '/Users/test/code/dotfiles/' },
];
let list = ps.map((p, i) => ({ pane: p.pane, tab: 'tab', address: `t${i+1}`, space: 's', space_name: '~', status: 'idle', program: p.program, seq: i }));
const context = { View: class {}, div: el, image: el, svg: el, v_flex: el, h_flex: el,
  agents: () => list, panes: () => ps, terminals: () => [], focused: () => null,
  spaces: () => { throw new Error('Agent titles must not depend on tabs'); }, theme: () => ({}), props: () => ({}),
  shared: key => key === 'agents.sort' ? sort : null, layout: () => ({ id: 'sidebar', size: { px: sidebarWidth } }),
  run() {}, setShared() {}, setAgentOrder() {}, openOverlay() {}, closeOverlay() {}, window() {} };
vm.runInNewContext(source, context);
const app = new context.Agents();
app.folded = new Set(); app.changed = {}; app.pins = [];
app.track = () => {}; app.prunePins = () => {};
function rows() {
  const root = app.render({});
  const result = {};
  function walk(node) {
    if (!node || typeof node !== 'object') return;
    if (node.idValue?.startsWith('ag-t')) {
      const text = [];
      const collect = x => { if (typeof x === 'string') text.push(x); else if (x && typeof x === 'object') x._children?.forEach(collect); };
      collect(node); result[node.idValue] = text.join(' ');
    }
    node._children?.forEach(walk);
  }
  walk(root); return result;
}
for (sort of ['priority', 'grouped']) {
  let r = rows();
  assert.equal(r['ag-t1'], '◐ First session'); assert.equal(r['ag-t2'], '[P1] Second session');
  ps[0].title = '◐ 打招呼 · dotfiles';
  assert.equal(rows()['ag-t1'], '◐ 打招呼 · dotfiles');
  assert.equal(rows()['ag-t2'], '[P1] Second session');
  ps[0].title = '◐ First session';
  tab = { ...tab, name: 'Custom', named: true };
  r = rows(); assert.equal(r['ag-t1'], '◐ First session');
  tab = { ...tab, name: '1', named: true };
  r = rows(); assert.equal(r['ag-t1'], '◐ First session');
  tab = { ...tab, named: false };
}
for (sort of ['priority', 'grouped']) {
  for (const pinned of [false, true]) {
    app.pins = pinned ? ['t1'] : [];
    app.changed.t1 = { s: 'idle', at: Date.now() - 120000 };
    app.hovered = null;
    const root = app.render({});
    const find = (node, id) => node && typeof node === 'object' && (node.idValue === id ? node : node._children?.map(x => find(x, id)).find(Boolean));
    const row = find(root, 'ag-t1');
    const listBox = find(root, 'ag-list');
    assert.equal(root.calls.on_size_change, undefined);
    assert.equal(listBox.calls.w, undefined);
    assert.equal(listBox.calls.mx, undefined);
    assert.equal(listBox.calls.px[0], 8);
    assert.ok(listBox.calls.flex_1 && listBox.calls.min_h[0] === 0 && listBox.calls.overflow_y_scrollbar);
    assert.ok(row.calls.on_click);
    const textBox = row._children.find(x => x && typeof x === 'object' && x.calls.truncate);
    assert.ok(textBox.calls.flex_1 && textBox.calls.min_w?.[0] === 0 && textBox.calls.overflow_hidden);
    assert.deepEqual(textBox._children, ['◐ First session']);
    const time = row._children.at(-2);
    assert.ok(time.calls.flex_none);
    assert.equal(time.calls.w, undefined);
    assert.ok(time._children.includes('2m'));
    app.hovered = 't1';
    const hovered = find(app.render({}), 'ag-t1');
    assert.equal(hovered._children.length, row._children.length);
    assert.equal(find(hovered, 'pin-t1').idValue, 'pin-t1');
    assert.deepEqual(hovered._children.find(x => x?.calls?.truncate)._children, ['◐ First session']);
    assert.ok(row._children.at(-1).calls.flex_none);
  }
}
app.hovered = null;
app.changed = {};
for (const title of [' .config ', ' [P1] Session ', ' ◐ ']) {
  ps[0].title = title;
  assert.equal(rows()['ag-t1'], title.trim());
}
ps[0].title = '  ';
assert.equal(rows()['ag-t1'], 'dev');
ps[0].title = null;
assert.equal(rows()['ag-t1'], 'dev');
ps[0].cwd = '/';
assert.equal(rows()['ag-t1'], '/');
ps[0].cwd = null;
assert.equal(rows()['ag-t1'], 'Klaude');
list[0].program = null;
assert.equal(rows()['ag-t1'], '-');
list[0].program = program;
ps[0].cwd = '/Users/test/code/dev';
ps = ps.filter(p => p.pane !== 'p1');
assert.equal(rows()['ag-t1'], 'Klaude');
ps.unshift({ pane: 'p1', tab: 'different-tab', title: 'Wrong pane', cwd: '/wrong' });
assert.equal(rows()['ag-t1'], 'Klaude');
ps[0].tab = 'tab';
list[0].status = 'working';
ps[0].title = '◐ 很长的中文会话标题，用于检查状态图标仍保留空间';
const find = (node, id) => node && typeof node === 'object' && (node.idValue === id ? node : node._children?.map(x => find(x, id)).find(Boolean));
for (const width of [180, 200, 268, 420]) {
  sidebarWidth = width;
  const root = app.render({});
  const listBox = find(root, 'ag-list');
  assert.equal(listBox.calls.w, undefined);
  assert.equal(root.calls.on_size_change, undefined);
  const row = find(root, 'ag-t1');
  assert.ok(row._children.find(x => x?.calls?.truncate).calls.min_w);
  const spinner = row._children.at(-1);
  assert.equal(spinner.calls.size[0], 12);
  assert.ok(spinner.calls.flex_none && spinner.calls.spin);
}
sidebarWidth = 76;
const rail = find(app.render({}), 'ag-list');
assert.equal(rail.calls.w, undefined);
assert.equal(rail.calls.px[0], 0);
sidebarWidth = 268;
ps[0].title = '◐ First session';
app.pins = [];
ps = [{ ...ps[0], program: { key: 'other', name: 'Other', agent: true } }];
list = [{ ...list[0], app: 'other', program: ps[0].program }];
assert.match(rows()['ag-t1'], /◐ First session/);
console.log('Agents rendering passed.');
