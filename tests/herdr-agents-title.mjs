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
  { pane: 'p1', tab: 'tab', terminal: 't1', program, title: '◐ First session' },
  { pane: 'p2', tab: 'tab', terminal: 't2', program, title: '◐ Second session' },
];
let list = ps.map((p, i) => ({ pane: p.pane, tab: 'tab', address: `t${i+1}`, space: 's', space_name: '~', status: 'idle', program, app: 'klaude', seq: i }));
const context = { View: class {}, div: el, image: el, svg: el, v_flex: el, h_flex: el,
  agents: () => list, panes: () => ps, terminals: () => [], focused: () => null,
  spaces: () => [{ tabs: [tab] }], theme: () => ({}), props: () => ({}),
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
  assert.match(r['ag-t1'], /First session/); assert.match(r['ag-t2'], /Second session/);
  ps[0].title = '◐ Upgrade @scope/pkg';
  assert.match(rows()['ag-t1'], /Upgrade @scope\/pkg/);
  ps[0].title = '◐ First session';
  tab = { ...tab, name: 'Custom', named: true };
  r = rows(); assert.match(r['ag-t1'], /Custom/); assert.doesNotMatch(r['ag-t1'], /First session/);
  tab = { ...tab, name: '1', named: true };
  r = rows(); assert.doesNotMatch(r['ag-t1'], /First session/);
  tab = { ...tab, named: false };
}
for (sort of ['priority', 'grouped']) {
  for (const pinned of [false, true]) {
    app.pins = pinned ? ['t1'] : [];
    app.changed.t1 = { s: 'idle', at: Date.now() - 120000 };
    const root = app.render({});
    const find = (node, id) => node && typeof node === 'object' && (node.idValue === id ? node : node._children?.map(x => find(x, id)).find(Boolean));
    const row = find(root, 'ag-t1');
    const listBox = find(root, 'ag-list');
    assert.equal(listBox.calls.w[0], 268);
    assert.equal(listBox.calls.min_w?.[0], 0);
    assert.ok(row.calls.w_full && row.calls.min_w?.[0] === 0 && row.calls.on_click);
    const textBox = row._children.find(x => x && typeof x === 'object' && x.calls.gap?.[0] === 5);
    assert.ok(textBox.calls.flex_1 && textBox.calls.min_w?.[0] === 0 && textBox.calls.overflow_hidden);
    assert.ok(textBox._children.every(x => x.calls.flex_1 && x.calls.min_w?.[0] === 0 && x.calls.overflow_hidden && x.calls.truncate && !x.calls.max_w));
    const clock = row._children.find(x => x && typeof x === 'object' && x._children.includes('2m'));
    assert.ok(clock?.calls.flex_none);
    assert.ok(row._children.at(-1).calls.flex_none);
  }
}
let notifications = 0;
for (const width of [200, 420, 180]) {
  const root = app.render({});
  root.calls.on_size_change[0]({ width, height: 300 }, { notify: () => notifications++ });
  const listBox = app.render({})._children.find(x => x?.idValue === 'ag-list');
  assert.equal(listBox.calls.w[0], width);
  assert.equal(sidebarWidth, 268);
}
assert.equal(notifications, 3);
const root = app.render({});
root.calls.on_size_change[0]({ width: 180, height: 400 }, { notify: () => notifications++ });
assert.equal(notifications, 3);
app.pins = [];
ps = [{ ...ps[0], program: { key: 'other', name: 'Other', agent: true } }];
list = [{ ...list[0], app: 'other', program: ps[0].program }];
assert.doesNotMatch(rows()['ag-t1'], /First session/);
console.log('Agents rendering passed.');
