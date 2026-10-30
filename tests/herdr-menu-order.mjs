import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../config/.config/herdr-app/mods/klaude-menu/main.js", import.meta.url), "utf8")
  .replace(/^import .*;\n/gm, "")
  .replace("export default class NewMenu", "globalThis.Menu = class NewMenu");
let keyHandler;
const calls = [];
const chain = new Proxy({}, { get: (_target, key) => (...args) => {
  if (key === "on_key_down") keyHandler = args[0];
  return chain;
} });
const context = {
  View: class {},
  div: () => chain, svg: () => chain, image: () => chain,
  h_flex: () => chain, v_flex: () => chain,
  theme: () => ({}), spaces: () => [{ id: "space", active: true }],
  window: () => ({ platform: "macos" }), props: () => ({}),
  closeOverlay: () => {}, run: (...args) => calls.push(args),
};
vm.runInNewContext(source, context);

for (const keys of [
  ["claude", "codex", "opencode", "klaude"],
  ["klaude", "codex", "claude"],
  ["claude", "codex"],
]) {
  const menu = new context.Menu();
  menu.agents = [...keys.map(key => ({ key, name: key, installed: true, run: [key] })),
    { key: "pi", name: "pi", installed: false }];
  const rows = [];
  menu.row = (id, _icon, name, action, hint, enabled) => rows.push({ id, action, hint, enabled });
  menu.render();
  const expected = keys.includes("klaude") ? ["klaude", ...keys.filter(key => key !== "klaude")] : keys;
  const agents = rows.filter(row => [...keys, "pi"].includes(row.id));
  assert.deepEqual(agents.map(row => row.id), [...expected, "pi"]);
  expected.forEach((key, index) => {
    assert.equal(agents[index].hint, `⌘ ${index + 1}`);
    calls.length = 0;
    keyHandler({ modifiers: { platform: true }, key: String(index + 1) });
    assert.equal(calls[0][0], "tab.new");
    assert.equal(calls[0][1].argv[0], key);
    calls.length = 0;
    agents[index].action();
    assert.equal(calls[0][1].argv[0], key);
  });
  assert.equal(agents.at(-1).enabled, false);
}
console.log("Klaude menu order, clicks and keyboard shortcuts passed.");