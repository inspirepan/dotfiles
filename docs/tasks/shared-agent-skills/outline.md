# 共享技能与设备增量更新

1. 用户已确认
   - 自有 inspirepan/agent-skills 与全部第三方技能统一由 npx skills 安装更新，跟上游最新版，不锁提交。
   - dotfiles 只维护来源、启用列表、replaces、共享指令和设备更新步骤，不存新技能正文；历史 skills/ 保留。
   - 通用第三方能力优先 Anthropic；指定的 Jakub 系列保留，Emil 精简为四项。
   - 保留个人内容；仅原生锁中来源匹配的普通安装目录允许迁移，独立客户端内容保持冲突。
2. 已实现
   - scripts/dotfiles.sh init|status|update 共用清单；按顺序检查、执行、验证，失败停止。
   - Skillfile.json：8 个自有／改写技能、25 个第三方技能，移除全部 revision。
   - scripts/install-skills.py 委托 npx --yes skills@latest add owner/repo --global --agent codex claude-code --skill ... --yes --json；不自行下载内容。
   - 默认补齐缺项、迁移声明来源并解除旧 SHA ref；--update 刷新全部无冲突启用项，即使已经安装。
   - --check 只读检查本地来源、布局和旧 SHA ref，不联网判断是否最新；冲突保留并返回 2。
   - 新增 updates/20261024-005-latest-skills.py，check 使用本地计划，apply 使用 setup-skills.sh --update；已满足时不强制重跑。
   - 001..004 未修改；003 的 skills@1.7.4 与旧 Agent 列表仅用于历史 session-logs 移除，不依赖 revision，继续保留。
   - 日常推荐 npx skills update -g -y；新增项或迁移来源用 scripts/setup-skills.sh --update；dotfiles update 保持设备步骤语义。
3. 验证记录
   - 本轮 uv run --no-project python -m unittest discover -s tests -v：21 项通过。
   - uv run --script scripts/install-skills.py --help 通过；jj diff 确认 001..004 无改动。
   - 覆盖多来源无提交锁安装、已安装项显式刷新、旧 SHA ref 迁移、replaces、个人目录与独立 Claude 内容保护、只读检查、005 执行后不重复刷新。
   - 新设备流程测试执行全部五步与真实 Stow，npx 安装使用隔离替身；未在真实新设备上执行。
   - 本机真实 CLI 安装与设备 update 通过；33 项来源、无 SHA ref 或 SHA URL、共享目录和 Claude 链接逐项检查通过，共享 CLAUDE.md / AGENTS.md 链接通过。
   - scripts/setup-skills.sh --check：0 项待同步、0 项冲突；重复设备 update 未再次安装，status 显示全部五步完成。
   - hallmark 首次克隆在 300 秒超时；使用 SKILLS_CLONE_TIMEOUT_MS=600000 scripts/dotfiles.sh update 重试成功。
   - 独立代码审查未发现正确性问题。
4. 路径与交付
   - Skillfile.json 是来源与启用项的唯一配置；docs/third-party-skills.md 说明用途和选择原则。
   - emil-design-eng、find-skills、vercel-react-best-practices、make-interfaces-feel-better、hallmark 旧布局移至 ~/.local/state/dotfiles/backups/skills-native-cli-_swxh4f9/，含 content、shared-link 和原 .skill-lock.json；五项正文和原链接均已核验保留，可恢复。
   - 本机更新完成；后续运行 npx skills update -g -y，修改清单后运行 scripts/setup-skills.sh --update。
5. 本期不做
   - 自动合并个人技能、自动卸载清单中停用的技能、全量自动化系统初始化。
