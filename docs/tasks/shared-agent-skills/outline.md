# 共享技能与设备增量更新

1. 用户已确认
   - agent-skills 只保留自写／持续改写技能；第三方直接通过 npx skills 从上游安装。
   - dotfiles 维护各来源的完整提交、启用列表和设备更新步骤。
   - 通用第三方能力优先 Anthropic；指定的 Jakub 系列保留，Emil 精简为四项。
   - 保留个人内容；本机未登记的旧 Emil 目录经用户确认先备份，再交给原生 CLI 安装。
2. 已实现
   - scripts/dotfiles.sh init|status|update 共用清单；按顺序检查、执行、验证，失败停止。
   - 四个步骤：共享 MD、原生技能安装、日志技能更名、第三方上游安装；已发布步骤不改写。
   - 清单：8 个自有／改写技能，25 个第三方技能；9 个第三方来源分别固定 SHA。
   - replaces 只允许迁移原生锁中归属匹配的旧来源；个人目录或独立客户端内容仍保留并报冲突。
   - 不复制第三方正文到 agent-skills；移除 agent-browser、frontend-design、pdf、playwright、skill-creator 五份副本。
   - klaude 的内置安装与资源打包已在此前移除，本轮没有修改应用代码。
3. 验证记录
   - 19 项 dotfiles 回归通过，覆盖多来源固定版本、来源迁移、个人内容保护和重复更新。
   - 新设备流程测试执行全部四步与真实 Stow，npx 安装使用隔离替身；未在真实新设备上执行。
   - 本机最终 33 项来源锁、固定提交、Claude 链接与重复更新通过；个人 commit 校验值不变，Emil 原目录备份完整。
   - 此前 klaude make pre-push 通过：3927 项测试通过，1 项跳过，4 项网络测试未运行；本轮未重跑应用检查。
4. 路径与交付
   - agent-skills 清理提交：b6c88558d4a40a4cd45d7ac4f9d11715b2129782。
   - Skillfile.json 是来源与启用项的唯一配置；docs/third-party-skills.md 说明用途和选择原则。
   - Emil 旧目录备份：~/.local/state/dotfiles/backups/emil-design-eng-upstream-bqecjz2r/emil-design-eng。
   - dotfiles 本轮提交包括多来源安装、第四个增量步骤及上述选择原则；其他设备拉取后运行 status 与 update，新设备运行 init。
5. 本期不做
   - 自动合并个人技能、自动卸载清单中停用的技能、全量自动化系统初始化。
