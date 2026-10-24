# 共享技能与设备增量更新

1. 用户已确认
   - 技能内容集中在 `agent-skills`；使用 Vercel `npx skills` 安装。
   - dotfiles 只维护来源、完整提交、启用列表及设备更新步骤。
   - 移除 klaude 内置技能机制，不再随应用打包。
   - 保留个人技能；旧技能无名称特例。
2. 已实现
   - `scripts/dotfiles.sh init|status|update`；按顺序检查、执行、验证，失败停止。
   - 本机 `~/.local/state/dotfiles/updates.json` 登记成功项；已登记步骤正文不可改写。
   - 第一步：Claude / Codex 共用 MD；不同个人内容停止合并，空文件或相同内容先备份。
   - 第二步：Vercel CLI 安装；薄适配层检查同名个人内容；来源记录交给 CLI。
   - 第三步：session-logs 更名为 klaude-session-logs；原生 CLI 清理受管旧名，个人同名入口保留。
   - 第三方技能只在 docs/third-party-skills.md 记录上游与安装命令，本轮不自动安装。
   - klaude 移除系统安装调用、子模块、打包检查；保留用户、项目发现与目录链接。
3. 已验证
   - 原生 CLI 按远端固定提交安装全部 13 个技能；源码逐文件与发布版本一致。
   - 本机重复 update 与 status：三步均完成；setup-skills --check 为 0 项待同步、0 冲突。
   - 本轮四个开发链接已备份后改为原生安装；已有两个个人 commit 技能校验值未变化。
   - Claude / Codex 指令指向同一文件；dotfiles 隔离回归 13 项通过。
   - klaude make pre-push 全套通过：3927 项测试通过、1 项跳过、4 项网络测试未运行；格式、静态检查、前端及 Python 构建、wheel/sdist 校验通过。
   - 新设备初始化经隔离测试验证 Stow 调用，未在真实新设备上执行。
4. 版本与交付
   - agent-skills 已推送：159694eac392e87514d6cd1f9287a3bf0477bb3e。
   - klaude-code 已推送：9062906ae57f；技能改为独立安装。
   - dotfiles 本轮固定上述 agent-skills SHA，13 个启用项包含 klaude-session-logs；旧 session-logs 安装与来源锁已清理。
   - 第三方目录保留原 5 项来源，新增 Jakub better 系列、Emil 动画与前端系列、已有副本的上游直装入口。
   - 其他设备下一步：拉取 dotfiles，运行 scripts/dotfiles.sh status 和 scripts/dotfiles.sh update；不同个人内容保留并停止，比较处理后重试。
5. 本期不做
   - 自动合并个人技能、自动卸载停用技能、全量自动化系统初始化。
