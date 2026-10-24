# 共享技能与设备增量更新

1. 用户已确认
   - 自有 inspirepan/agent-skills 与全部第三方技能统一由 npx skills 安装更新，跟上游最新版，不锁提交。
   - dotfiles 只维护来源、启用列表、replaces、共享指令和设备更新步骤；commit 正文迁入并推送 inspirepan/agent-skills 后删除重复正文，不再存技能正文。
   - 通用第三方能力优先 Anthropic；指定的 Jakub 系列保留，Emil 精简为四项。
   - 保留个人内容；仅原生锁中来源匹配的普通安装目录允许迁移，独立客户端内容保持冲突。
   - commit 唯一旧链接例外：来源必须为 inspirepan/agent-skills，共享 symlink 精确解析到当前仓库 skills/commit（允许悬空），Claude 入口缺失或 symlink 解析到同一旧目标；外来锁归属仍报冲突。
   - 安装前 shutil.move 备份匹配链接到 ~/.local/state/dotfiles/backups/ 唯一目录并打印；--check 只读。备份不包含正文，不因仓库正文已删除而失败。
2. 已实现
   - scripts/dotfiles.sh init|status|update 共用清单；按顺序检查、执行、验证，失败停止。
   - Skillfile.json：9 个自有／改写技能（新增 commit）、25 个第三方技能，共 34 项，无 revision。
   - scripts/install-skills.py 委托 npx --yes skills@latest add owner/repo --global --agent codex claude-code --skill ... --yes --json；不自行下载内容。
   - 默认补齐缺项、迁移声明来源并解除旧 SHA ref；--update 刷新全部无冲突启用项，即使已经安装。
   - --check 只读检查本地来源、布局和旧 SHA ref，不联网判断是否最新；冲突保留并返回 2。
   - 新增 updates/20261024-005-latest-skills.py，check 使用本地计划，apply 使用 setup-skills.sh --update；已满足时不强制重跑。
   - 新增 updates/20261024-006-commit-skill.py；002/004/005 的 plan 同样将已知旧 commit 链接视为待迁移，避免被前序步骤挡住。
   - 001..005 未修改；003 的 skills@1.7.4 与旧 Agent 列表仅用于历史 session-logs 移除，不依赖 revision，继续保留。
   - 日常推荐 npx skills update -g -y；新增项或迁移来源用 scripts/setup-skills.sh --update；dotfiles update 保持设备步骤语义。
3. 验证记录
   - commit 迁移本轮 uv run --no-project python -m unittest discover -s tests -v：23 项通过；使用临时 HOME 与 CLI 替身，新设备流程运行真实 Stow。
   - 已覆盖新设备安装 34 项、六步完成后不重复安装、旧 commit 链接目标存在／缺失、Claude 入口缺失、只读检查、备份先于 CLI、独立内容与外来来源保护。
   - jj diff 确认 001..005 无改动；skills/commit 已移入废纸篓，dotfiles 不再保留重复正文。
   - 上游 commit/SKILL.md 与 dotfiles 原文 cmp 相同，npx skills 本地 --list 发现 9 项含 commit；已提交并推送 origin/main 4a85ca07（feat(commit): 迁入个人 jj 提交技能）。
   - 本机真实 dotfiles update 将悬空旧链接备份后，通过 npx skills 安装 commit；安装记录来源为 inspirepan/agent-skills。
   - 已逐项核验 34 项来源、无 SHA ref、共享目录与 Claude 链接；commit 安装正文、上游正文、原始备份字节一致。
   - scripts/setup-skills.sh --check：0 项待同步、0 项冲突；重复设备 update 未再次安装，status 显示全部六步完成。
   - 正确性与维护性独立审查均未发现问题；未在真实新设备上执行初始化。
   - 005 阶段 hallmark 曾在 300 秒克隆超时；使用 SKILLS_CLONE_TIMEOUT_MS=600000 重试成功。
4. 路径与交付
   - Skillfile.json 是来源与启用项的唯一配置；docs/third-party-skills.md 说明用途和选择原则。
   - emil-design-eng、find-skills、vercel-react-best-practices、make-interfaces-feel-better、hallmark 旧布局移至 ~/.local/state/dotfiles/backups/skills-native-cli-_swxh4f9/，含 content、shared-link 和原 .skill-lock.json；五项正文和原链接均已核验保留，可恢复。
   - commit 原正文备份：~/.local/state/dotfiles/backups/commit-upstream-content-o129kan1/content/；原 shared-link 与 claude-link：~/.local/state/dotfiles/backups/legacy-commit-9_7_lis8/，均已核验保留，可恢复。
   - 上游源码位于 ~/code/GITHUB/agent-skills，工作区干净、main 与 origin/main 均为 4a85ca07；使用 jj describe && jj new 提交三个迁入相关文件。
   - 本机迁移和验证完成；其他设备拉取 dotfiles 后运行 status 与 update，应用 commit 启用和旧链接迁移。
   - 后续日常运行 npx skills update -g -y，修改清单后运行 scripts/setup-skills.sh --update。
5. 本期不做
   - 自动合并个人技能、自动卸载清单中停用的技能、全量自动化系统初始化。
