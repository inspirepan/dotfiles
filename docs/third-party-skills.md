# 第三方技能直接从上游安装

只记录来源和安装命令，不复制技能正文。本页不参与 `scripts/dotfiles.sh update` 自动安装；`Skillfile.json` 仍管理自有共享仓库。核对日期：2026-10-24。

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

Emil 的旧仓库 `emilkowalski/skill` 已重定向到 `emilkowalski/skills`。旧版 make-interfaces-feel-better 与新版 better 系列分开记录，不自动替换。

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
| improve-animations | 整体动画审查与改进计划 |
| find-animation-opportunities | 寻找适合增加动画的位置 |
| animation-performance | 排查掉帧与动画性能 |
| animation-vocabulary | 描述动画需求 |
| apple-design | Apple 界面与动效原则 |
| pick-ui-library | 选择界面组件库 |
| prototype | 创建多个可比较原型 |
| mobile-native | 优化移动网页体验 |
| break-ui | 用极端内容检查界面 |
| animate-expo | React Native / Expo 动效 |
| ask-sonner | Sonner 提示组件用法 |

按需选择，例如：

```bash
npx skills add emilkowalski/skills -g -a codex claude-code -s emil-design-eng animate review-animations animation-performance
```

## 现有共享仓库中的技能也有上游入口

| 技能 | 上游直装命令 |
|---|---|
| agent-browser | `npx skills add vercel-labs/agent-browser -g -a codex claude-code -s agent-browser` |
| frontend-design | `npx skills add anthropics/skills -g -a codex claude-code -s frontend-design` |

来源：[agent-browser](https://github.com/vercel-labs/agent-browser)、[Anthropic Skills](https://github.com/anthropics/skills)。当前共享仓库副本与上游不保证内容一致；本轮仅记录来源，未迁移或删除副本。

## 新设备按需安装，已有设备保留现状

- 先用 `npx skills add <owner/repo> --list` 查看当前名称，再选择技能安装。
- `-g` 安装到用户级；`-a codex claude-code` 配置共享入口，klaude 读取同一 `~/.agents/skills/`。
- 本页命令安装当时的上游版本，尚未固定第三方提交，也未纳入自动初始化。
- 自有 `commit` 仍位于 `skills/commit/SKILL.md`；它与第三方目录分开维护。
