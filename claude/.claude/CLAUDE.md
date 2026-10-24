# Language
Always respond in Chinese when answering user questions, including steps between tools
Always use Chinese for task lists, plan steps, and todo items
Use English for code comments, keep them concise

# Design Documents
Keep design docs very concise; match the style of the user's own outlines
- Write only the confirmed trunk; put unconfirmed ideas in a separate "待确认" section, never in the body
- Do not add details, edge cases, or rationale the user has not discussed
- Prefer nested numbered lists and short bullet fragments; use tables only for field/item lists
- Show formats with one short JSON example and inline comments, not long field specs
- Mark out-of-scope items as "本期不做" instead of designing them

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
For projects under ~/code/formless, write commit messages in English.

# Repository Management
You use this path for cloning GitHub repositories: ~/code/GITHUB

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
