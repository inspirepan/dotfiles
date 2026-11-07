# 共享技能与设备增量更新

当前阶段：2026-11-07 飞书文档五项登记完成；62 项测试、真实隔离安装与清理、独立审查及本机更新登记均通过。用户已授权仅提交本次相关改动并推送 main，排除无关配置修改；已发布步骤保持原文。

1. 用户已确认
   - 自有 inspirepan/agent-skills 与全部第三方技能统一由 npx skills 安装更新，跟上游最新版，不锁提交。
   - dotfiles 只维护来源、启用列表、replaces、共享指令和设备更新步骤；commit 正文迁入并推送 inspirepan/agent-skills 后删除重复正文，不再存技能正文。
   - 通用第三方能力优先 Anthropic；指定的 Jakub 系列保留，Emil 精简为四项。
   - 保留个人内容；仅原生锁中来源匹配的普通安装目录允许迁移，独立客户端内容保持冲突。
   - commit 唯一旧链接例外：来源必须为 inspirepan/agent-skills，共享 symlink 精确解析到当前仓库 skills/commit（允许悬空），Claude 入口缺失或 symlink 解析到同一旧目标；外来锁归属仍报冲突。
   - 安装前 shutil.move 备份匹配链接到 ~/.local/state/dotfiles/backups/ 唯一目录并打印；--check 只读。备份不包含正文，不因仓库正文已删除而失败。
   - 前阶段移除全局 playwright、unslop、ketchup-video、no-comments、make-bot-ui；保留 poteto-mode、bro、in-your-own-words 和全部 principle-*，这些保留项不新增自动安装登记。
   - submit-pr 仅在 klaude-code 项目卸载，由父 agent 单独处理；dotfiles 不操作项目技能。
   - 飞书官方 https://open.feishu.cn/lark-cli/skills/regular 仅启用 lark-doc、lark-wiki、lark-whiteboard、lark-drive、lark-shared；禁止整套安装。
   - 清理范围仅同一官方 well-known 来源的未启用受管 lark-*；保留集合只读 Skillfile.json。其他来源、无锁个人目录保留，独立客户端内容先报冲突。
2. 已实现
   - scripts/dotfiles.sh init|status|update 共用清单；按顺序检查、执行、验证，失败停止。
   - Skillfile.json：9 个自有／改写技能（含 commit）、29 个第三方技能，共 38 项，无 revision；已移除仅启用 playwright 的 openai/skills 来源，新增飞书官方 URL 来源五项。
   - scripts/install-skills.py 委托 npx --yes skills@latest add <来源> --global --agent codex claude-code --skill ... --yes；GitHub 保留 --json，飞书 well-known 不支持该选项，单独省略；不自行下载内容。
   - 默认补齐缺项、迁移声明来源并解除旧 SHA ref；--update 刷新全部无冲突启用项，即使已经安装。
   - --check 只读检查本地来源、布局和旧 SHA ref，不联网判断是否最新；冲突保留并返回 2。
   - 新增 updates/20261024-005-latest-skills.py，check 使用本地计划，apply 使用 setup-skills.sh --update；已满足时不强制重跑。
   - 新增 updates/20261024-006-commit-skill.py；002/004/005 的 plan 同样将已知旧 commit 链接视为待迁移，避免被前序步骤挡住。
   - 001..005 未修改；003 的 skills@1.7.4 与旧 Agent 列表仅用于历史 session-logs 移除，不依赖 revision，继续保留。
   - 日常推荐 npx skills update -g -y；新增项或迁移来源用 scripts/setup-skills.sh --update；dotfiles update 保持设备步骤语义。
   - 新增 updates/20261107-001-prune-global-skills.py 与 components.json 的 agents 条目；仅选择原生锁来源为 openai/skills 的 playwright，以及 backnotprop/pstack 的另外四项。固定已核对删除路径的 skills@1.7.4，显式选择技能和 Agent。
   - 无锁或其他来源安装保持原状；匹配来源但共享入口是 symlink、独立 Claude 或旧共享 Agent 入口是个人内容时，在调用 CLI 前报冲突。完成后核对锁与入口；重复执行无需再次调用 CLI。
   - 新增 updates/20261107-002-lark-document-skills.py 与 agents 登记。仅允许明确官方 URL；原生锁逐项核对 source、sourceType、sourceBaseUrl、sourceUrl，GitHub 沿用原归属规则。
   - 新步骤先检查删除入口冲突，再按现有安装器补齐缺项，显式选择同源未启用 lark-* 调用 skills@1.7.4 remove，最后复核来源锁及所有受影响入口。重复执行不调用 CLI，未来未启用项不整包安装。
3. 验证记录
   - 飞书阶段：uv run --no-project python -m unittest discover -s tests -v，62 项通过；临时 HOME 与 CLI 替身覆盖新机共 38 项且飞书只选五项、整套删除其余 23 项、重复无 CLI、动态清单保留集合、未来额外技能、外来与无锁个人内容、独立客户端与共享 symlink、锁四字段归属验证和卸载后验证失败。
   - 本阶段新增测试及初始化替身使用 patch.dict(os.environ, ..., clear=True)，仅传入测试所需环境；初始化继续运行真实 Stow。
   - 父 agent 实测：env -i 隔离临时 HOME，原生 CLI 对官方 URL 显式 --skill 五项且不带 --json，安装成功；新 HOME 仅五项锁记录，source=open.feishu.cn、sourceType=well-known、sourceBaseUrl 为精确官方 URL。带 --json 的 well-known 安装会被 CLI 拒绝。
   - 真实隔离清理：临时 HOME 中五项真实安装加二十三项旧备份，构造同源锁与客户端链接；实际运行新步骤及原生 CLI，28 项清理为精确五项。重复执行未调用 CLI。
   - 本机其余 23 项 lark 已卸载，备份 /tmp/klaude-lark-removal.v1Fm2C/lark-skills.tar.gz。setup-skills.sh --check 为 0 项待同步、0 项冲突；dotfiles.sh update --component agents 连续两次成功，status 全部完成，原生 CLI 清单仅保留确认的五项 lark。
   - 本阶段独立正确性与维护性审查未发现问题；正确性审查隔离运行新增五项测试通过。
   - 2026-11-07：uv run --no-project python -m unittest discover -s tests -v，57 项通过。新增一项测试覆盖五个受管技能、其他来源、无锁、混合来源、个人 Claude 与旧 Agent 入口保护、自定义配置路径、卸载后验证与重复执行；初始化测试改为 33 项。
   - 本轮设备步骤单元测试使用临时 HOME 与 CLI 替身；真实执行 npx skills remove -g -y playwright unslop ketchup-video no-comments make-bot-ui，CLI 确认移除五项。
   - 对比卸载前后全局清单：123 → 118，仅移除上述五项；bro、in-your-own-words、poteto-mode 与全部 24 项 principle-* 均保留。klaude-code 项目 submit-pr 已移入废纸篓。
   - scripts/dotfiles.sh update --component agents 与 status --component agents 均成功，新步骤已登记完成。jq 统计清单为 9 / 24 / 33；jj diff 确认未改已发布步骤。
   - 独立审查发现配置环境变量为空时，入口保护路径与 CLI 回退不一致；已按 CLI 规则修正，补充空值／空白值保护场景，57 项测试再次通过。测试环境隔离宿主环境变量。
   - 修正后备份本机 updates.json，在更新器锁内仅撤销本轮未发布步骤的旧完成记录，再运行 update 与 status；新哈希登记成功，旧步骤记录保留。
   - 安全事项：一次失败测试的 Mock 信息展开宿主环境，凭证出现在子会话工具输出及可能保存的本机会话日志中；未写入仓库或另存文件。已隔离测试环境；需告知用户评估日志访问范围并轮换相关凭证，不在此记录值。
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
   - 飞书阶段审查文件：Skillfile.json、scripts/install-skills.py、updates/20261107-002-lark-document-skills.py、updates/components.json、tests/test_lark_skills.py、tests/test_skill_initialization.py、AGENTS.md、docs/setup-guide.md、docs/third-party-skills.md、本 outline。
   - 本机已完成；其他设备取得这些变更后运行 scripts/dotfiles.sh status --component agents 与 scripts/dotfiles.sh update --component agents。新设备按原指南运行 init，只安装五项飞书技能。
   - 本轮同步 AGENTS.md、docs/setup-guide.md、docs/third-party-skills.md 的当前数量与精简范围，保留 playwright 从自有副本迁往上游的历史。
   - 后续：其他设备拉取后运行 scripts/dotfiles.sh update --component agents；本次提交范围仅技能配置、安装器、设备步骤、测试与文档，排除 herdr settings。
   - 本轮卸载前备份：/tmp/klaude-skills-removal.pgqHyg/global-skills.tar.gz 与 project-submit-pr.tar.gz；全局技能可从上游重新安装，项目 submit-pr 也可从版本历史恢复。
   - Skillfile.json 是来源与启用项的唯一配置；docs/third-party-skills.md 说明用途和选择原则。
   - emil-design-eng、find-skills、vercel-react-best-practices、make-interfaces-feel-better、hallmark 旧布局移至 ~/.local/state/dotfiles/backups/skills-native-cli-_swxh4f9/，含 content、shared-link 和原 .skill-lock.json；五项正文和原链接均已核验保留，可恢复。
   - commit 原正文备份：~/.local/state/dotfiles/backups/commit-upstream-content-o129kan1/content/；原 shared-link 与 claude-link：~/.local/state/dotfiles/backups/legacy-commit-9_7_lis8/，均已核验保留，可恢复。
   - 上游源码位于 ~/code/GITHUB/agent-skills，工作区干净、main 与 origin/main 均为 4a85ca07；使用 jj describe && jj new 提交三个迁入相关文件。
   - 本机迁移和验证完成；其他设备拉取 dotfiles 后运行 status 与 update，应用 commit 启用和旧链接迁移。
   - 后续日常运行 npx skills update -g -y，修改清单后运行 scripts/setup-skills.sh --update。
5. 本期不做
   - 自动合并个人技能、按清单差集卸载任意来源、全量自动化系统初始化；仅支持明确确认的全局五项精简与飞书官方同源范围收敛。
