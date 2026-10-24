# 第三方技能直接从上游安装

第三方正文只由上游维护，不复制到 `agent-skills`。本页所列 25 个技能已在 `Skillfile.json` 启用，与自有来源 `inspirepan/agent-skills` 一样，通过 `npx skills` 安装更新、跟上游最新版；不锁提交。核对日期：2026-10-24。

## 通用能力优先使用 Anthropic 官方源

- 通用技能：`anthropics/skills` 的 `frontend-design`、`pdf`、`skill-creator`。
- 指定前端作者：保留用户点名的 Jakub 系列；Emil 精简为设计原则、实现、审查、性能四项。
- 工具专项：Vercel 的浏览器、React、技能发现，以及 OpenAI 的 Playwright。
- 历史清单：保留已有 `nutlope/hallmark`，不因本轮整理额外扩充社区来源。

## 原 Skillfile 中的技能仍有上游入口

| 技能 | 用途 | 上游 |
|---|---|---|
| emil-design-eng | 界面与动画设计原则 | [emilkowalski/skills](https://github.com/emilkowalski/skills) |
| find-skills | 搜索可安装技能 | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| vercel-react-best-practices | React / Next.js 性能 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |
| make-interfaces-feel-better | 界面细节打磨 | [jakubkrehel/make-interfaces-feel-better](https://github.com/jakubkrehel/make-interfaces-feel-better) |
| hallmark | 页面设计与界面审查 | [nutlope/hallmark](https://github.com/nutlope/hallmark) |

```bash
npx skills add emilkowalski/skills -g -a codex claude-code -s emil-design-eng
npx skills add vercel-labs/skills -g -a codex claude-code -s find-skills
npx skills add vercel-labs/agent-skills -g -a codex claude-code -s vercel-react-best-practices
npx skills add jakubkrehel/make-interfaces-feel-better -g -a codex claude-code -s make-interfaces-feel-better
npx skills add nutlope/hallmark -g -a codex claude-code -s hallmark
```

Emil 的旧仓库 `emilkowalski/skill` 已重定向到 `emilkowalski/skills`。旧版 make-interfaces-feel-better 与新版 better 系列同时启用，不互相替换。

## Jakub 的 better 系列按界面职责拆分

来源：[jakubkrehel/skills](https://github.com/jakubkrehel/skills)。

| 技能 | 用途 |
|---|---|
| better-interface | 综合审查，调用下面六项 |
| better-ui | 表面、图标、阴影、交互细节 |
| better-typography | 字级、间距、换行、字体特性 |
| better-colors | 调色板、语义色、对比度 |
| better-accessibility | 键盘、焦点、ARIA、表单 |
| better-layout | 分组、对齐、响应式、阅读顺序 |
| better-writing | 按钮、错误、空状态等界面文案 |

使用 better-interface 时同时安装六个配套技能：

```bash
npx skills add jakubkrehel/skills -g -a codex claude-code -s better-interface better-ui better-typography better-colors better-accessibility better-layout better-writing
```

同仓库还提供 `interface-review`（代码变更审查）、`explain-interface`（分析现有界面）、`build-design`（实现设计稿）、`state-machine`（组件状态预览）、`variant`（方案对比）。安装时替换 `-s` 后的技能名即可。

## Emil 的技能覆盖动画构建、审查与性能

来源：[emilkowalski/skills](https://github.com/emilkowalski/skills)。

| 技能 | 用途 |
|---|---|
| emil-design-eng | 设计与动画原则 |
| animate | 实现动画与过渡 |
| review-animations | 审查已有动画 |
| animation-performance | 排查掉帧与动画性能 |

Emil 自动安装范围只保留这四项：

```bash
npx skills add emilkowalski/skills -g -a codex claude-code -s emil-design-eng animate review-animations animation-performance
```

## 原第三方副本改为从上游安装

| 技能 | 上游直装命令 |
|---|---|
| agent-browser | `npx skills add vercel-labs/agent-browser -g -a codex claude-code -s agent-browser` |
| frontend-design | `npx skills add anthropics/skills -g -a codex claude-code -s frontend-design` |
| pdf | `npx skills add anthropics/skills -g -a codex claude-code -s pdf` |
| skill-creator | `npx skills add anthropics/skills -g -a codex claude-code -s skill-creator` |
| playwright | `npx skills add openai/skills -g -a codex claude-code -s playwright` |

来源：[agent-browser](https://github.com/vercel-labs/agent-browser)、[Anthropic Skills](https://github.com/anthropics/skills)、[OpenAI Skills](https://github.com/openai/skills/tree/main/skills/.curated/playwright)。这五份第三方副本已从 `agent-skills` 移除；dotfiles 只记录来源、启用项与来源迁移。

## 初始化按清单补齐，日常由原生 CLI 更新

- 先用 `npx skills add <owner/repo> --list` 查看当前名称，再选择技能安装。
- `-g` 安装到用户级；`-a codex claude-code` 配置共享入口，klaude 读取同一 `~/.agents/skills/`。
- 新设备运行 `scripts/dotfiles.sh init`；已有设备拉取后运行 `status`、`update` 应用设备步骤，不会每次强制刷新已完成技能步骤。
- `scripts/setup-skills.sh` 默认补齐缺项、迁移已声明来源并解除旧 SHA ref；`--update` 刷新全部无冲突启用项；`--check` 只读检查本地来源与布局，不承诺已是上游最新。
- 日常更新运行 `npx skills update -g -y`；有迁移来源或新增启用项时运行 `scripts/setup-skills.sh --update`。
- 独立个人内容不会自动接管。未登记的旧目录先比较，再备份并切换；本机 Emil 的旧目录已按用户确认备份。
- 历史 `skills/`（含 `skills/commit/SKILL.md`）保留，不由同步器自动接管；不在 dotfiles 新增技能正文。

## 清单只维护来源与启用项，不锁提交

- 自有来源使用顶层 `repository`、`enabled`；第三方来源使用 `sources` 列表中的相同字段，不再维护 `revision`。
- 同名技能不重复启用；`replaces` 仅声明允许迁移的原仓库，不授权接管无来源记录的个人目录。
- 新增设备配置变化时新增更新步骤，不改写已发布步骤；005 承载解除旧提交锁定。上游内容升级不需要新增设备步骤。
