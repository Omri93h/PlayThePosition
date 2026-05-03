# Assistant Workflow

This document captures how Omri works with ChatGPT and Codex on Play The Position.

## Response Style

- Be concise.
- Do not give long explanations unless Omri asks.
- Prefer easy copy-paste prompts and commands.
- Give exact commands, not vague instructions.
- Do not print full files unless explicitly requested.
- Summarize long command output; paste detailed logs only when a failure needs debugging.

## Roles

- ChatGPT is the orchestrator and reviewer, not the direct coder.
- Codex does the repository edits.
- Omri should do nothing manually except paste prompts/results and run copy-paste commands when needed.
- Omri should only need visual or product judgment when the work needs human taste, validation, or approval.
- Development is block-driven and feature-by-feature.

## Plan Then Execute

Codex must PLAN first.

Use `docs/product/CODEX_PROMPT_TEMPLATES.md` for short reusable PLAN, EXECUTE, FIX, docs-only, and block closeout prompts.

1. Codex reads the current source-of-truth docs and `current_focus.md`.
2. Codex creates a plan for the current feature only.
3. ChatGPT reviews, approves, or corrects the plan.
4. Only after plan approval does ChatGPT give Codex an EXECUTE prompt.
5. Codex implements only the approved scope.

Do not implement before plan approval.

## Implementation Handoff

After implementation, Codex must return:

- changed files
- exact summary
- checks run and results
- self-review against scope
- repo hygiene notes
- `git status --short`
- suggested commit message

ChatGPT reviews the Codex handoff before commit, including:

- scope control
- unrelated file changes
- test/check results
- repo hygiene
- stale or overclaiming docs
- whether manual validation is needed

## Commit Flow

Prefer one feature = one commit.

If implementation is good, ChatGPT gives exact copy-paste commands:

```bash
git add <exact files>
git commit -m "<message>"
git push
git status
```

After the commit/push command section, ChatGPT should include the next Codex prompt immediately when it is safe to continue.

When ChatGPT gives both Git commands and a next Codex prompt in the same response, the Git command section must always come first. The next Codex prompt must come only after those commands. Never put Git commands after a Codex prompt.

Git commands must always match the latest Codex response and the exact changed files from that response.

Omri does not need to paste successful commit output every time. If commit, push, or checks fail, Omri will paste the error and ChatGPT gives a fix prompt.

## Stop Rules

- If tests or checks fail, do not commit.
- If Codex expands scope, touches unrelated files, or docs overclaim reality, stop and fix.
- If source-of-truth docs are stale, repair docs before the next feature.
- Avoid docs-only state churn unless repairing source-of-truth docs, planning roadmap, or closing a block.
- Fix manual-validation issues inside the current uncommitted feature before committing.
- Manual validation checkpoints must happen when UI or product quality needs review.
- Do not blindly continue into future blocks.
- Do not mark a block complete until implementation, automated checks, review, and any needed manual validation are done.
