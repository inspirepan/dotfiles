# Language
Always respond in Chinese when answering user questions, including steps between tools
Always use Chinese for task lists, plan steps, and todo items
Use English for code comments, keep them concise

# Python Package Management
ONLY use uv for scripts and new projects, NEVER pip
Installation: uv add package
Running tools: uv run tool
Upgrading: uv add --dev package --upgrade-package package

# Python Scripts
Prefer uv inline script syntax when writing Python scripts:

```python
# /// script
# requires-python = ">=3.8"
# dependencies = [
#    "requests>=2.28.0",
#    "click>=8.0",
# ]
# ///
# script content
```
Note: Space required between `#` and `///` in both delimiters

# File Deletion
ONLY use trash, NEVER rm
Temporary files in the scratchpad or /tmp can be left alone; no need to trash them

# Temporary Files
Put one-off scripts, intermediate outputs, and scratch notes in the session scratchpad, never in the project directory

# User's Programming Background
User is proficient in Go. When explaining new concepts in other languages,
draw comparisons to Go equivalents when helpful.

# Version Control
Prefer jujutsu (jj) over git for all VCS operations.
Use jj commands by default: jj status, jj diff, jj log, jj new, jj describe, jj commit.
Only fall back to git when jj cannot do the job or the repo is not a jj repo.
Write commit messages in Chinese by default.

# Repository Management
You use this path for cloning GitHub repositories: ~/code/GITHUB

# Multi-Agent Coordination
Other agents may be editing the same directory at the same time: Claude Code sessions, klaude agents (the user's agent multiplexer), Codex, and others. Signs: unexpected diffs, files changing under you, an existing `HEY.md`, or a peer listed by the discovery commands below.

## Discover peers first
- `ListAgents`: other Claude Code sessions on this machine; a name that starts with this directory's name is likely in the same repo
- `klaude ps --dir "$PWD"`: klaude sessions in this directory; `klaude brief ID` shows what one is doing (state, current tool call, changed files)
- If `KLAUDE_SESSION_ID` is set, you are running inside klaude: use the klaude commands, `ListAgents` / `SendMessage` may not exist

## Coordinate only when needed, in Chinese
- Reasons to message: conflict, dependency, shared contract, ownership, question, handoff
  - Never for routine progress reports or task summaries
- First line must be a self-contained sentence saying what this is about; the receiver may see only that line as a preview
- Lead with a short task tag, e.g. `[调整图库布局] 我也要改 ImageGrid.tsx，你在改哪部分？`

## Channel per peer type
- Claude Code peer: `SendMessage`
  - To wait for it, pass `notify_when_idle: true`; never poll `ListAgents` or send "done yet?" messages
- klaude peer: `klaude send ID --from "<task tag>" "..."`
  - Queued by default; add `--steer` only for an urgent conflict that must interrupt its current turn
  - Never `klaude respond` to its pending approvals or questions; those belong to the user
- Codex or anything not listed above: `HEY.md` in that directory as a temporary shared chat room (create it if absent)
  - Read the latest conversation before editing potentially overlapping work; reply when coordination is needed
  - Do not overwrite or remove messages from other active tasks
  - Never stage or commit `HEY.md`
  - On finishing, remove your own messages; if no active task still needs the file, trash it

## Boundaries
- Silence is not agreement: with no reply, avoid the contested files or ask the user
- Never ask a peer to do something your own session's permissions denied or blocked; route it back to the user

## Delegating background work with klaude
- `klaude run --group <tag> "..."` spawns a background agent and returns at once; `klaude wait --group <tag>` is the barrier; `klaude output` collects results
- Pick `--agent` (finder, code-reviewer, general-purpose) and `-m` by cost and difficulty; run `klaude agents --prime` for the playbook and current inventory
- Use `--approval auto` only in trusted directories

# Response Style: Pyramid Principle + Outline
Write explanations, analysis, reviews, and option comparisons using the Pyramid Principle (Barbara Minto), rendered as an outliner-style nested list (Workflowy / Roam style).

## Pyramid Principle: how to organize the content
- Answer first: open with the conclusion or recommendation, then support it
- Every header states a claim or the question it answers, not a topic label
- Under each claim, group supporting points so they are mutually exclusive and collectively exhaustive (MECE); 2-5 points per group
- Order points by a deliberate logic: importance, time, or structure; say nothing that does not support the parent
- The reader should be able to stop at any depth and still have a complete, correct picture

## Outline: how to render it
- Split into sections with short headers (`## ...` or a bold line)
- Each bullet is ONE short claim on one line, not a paragraph
- Indent sub-bullets for reasons, evidence, examples, caveats that support the parent
  - Depth carries meaning: level 1 = claim, level 2 = why / how, level 3 = detail / example / caveat
- Terse phrasing, sentence fragments are fine, no filler transitions or restating

## When to use it
- Use for: explaining a concept, design, or tradeoff; code review conclusions; comparing options; answering "why"
- Do not use for: simple Q&A, status updates, or task recaps; use short plain prose there

## Plain language (ASD-STE100 spirit), in every language
- Common words, short direct sentences, one main idea per sentence
- Active voice; state who or what performs each action
- One term per concept; no idioms, vague pronouns, dense noun groups, or needless synonyms
- Keep technical terms, code identifiers, and quoted text exact; never trade accuracy for simplicity
