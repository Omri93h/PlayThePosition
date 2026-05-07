# Next Agent Bootstrap

Use this handoff when a future ChatGPT session continues Play The Position.

## Files To Read First

Read these before giving guidance or prompts:

- `AGENTS.md`
- `docs/product/ASSISTANT_WORKFLOW.md`
- `docs/product/CODEX_PROMPT_TEMPLATES.md`
- `current_focus.md`
- `docs/product/PROGRESS.md`
- `docs/product/BLOCKS_INDEX.md`
- `docs/product/FEATURE_INDEX.md`
- the current `docs/blocks/BLOCK_*.md` referenced by `current_focus.md`

## Role

- ChatGPT is the product/dev orchestrator and reviewer.
- Codex performs repository edits.
- Omri pastes Codex results into ChatGPT.
- ChatGPT reviews scope, checks, and source-of-truth state, then gives Git commands and/or the next Codex prompt.
- Omri should only need to paste prompts/results and run copy-paste commands unless visual or product judgment is needed.

## Response Style

- Be concise.
- Be practical.
- Make prompts and commands easy to copy-paste.
- Do not give long explanations unless Omri asks.
- Do not print full files unless explicitly requested.

## Critical Workflow Rules

- Continue from the repo state; do not restart, redesign, or re-plan old work.
- For Codex PLAN results: approve or correct the plan, then give only the EXECUTE prompt.
- For Codex IMPLEMENTATION results: review scope, checks, changed files, and state before commit.
- If the implementation is clean, give exact commands:

```bash
git add <exact files>
git commit -m "<message>"
git push
git status
```

- If safe to continue, include the next Codex prompt in the same answer after the Git command section.
- Git command section must always come before the next Codex prompt.
- Never put Git commands after a Codex prompt.
- Do not say “commit X first if you didn’t already.”
- Assume Omri commits when commands are given.
- Do not require Omri to paste successful Git output every time; he will paste errors if needed.
- If checks fail, scope expands, docs overclaim, or unrelated files changed: do not commit; give a narrow fix prompt.
- Do not start next features or blocks until source-of-truth docs are correct.
- Manual validation is needed only when UI/product judgment matters.

## Current Continuation Point

- Project is in BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements.
- Features 10.1 through 10.4 are complete/committed.
- Feature 10.5 — Measurement comparison report and next-step decision is implemented / ready for review.
- Next process step is BLOCK 10 closeout review.
- BLOCK 10 is not complete.
- No upload/API integration has started.
- No production recognition accuracy claim has been made.
- No piece recognition measurement has started.

## Important Future Notes

- Future piece-recognition implementation should follow after fixture measurements, likely in a later block.
- Future Play Mode legal moves should include:
  - click a piece once to select it
  - selected square gets stroke/highlight
  - legal destination squares are shown
  - clicking the same selected square cancels selection
  - clicking a legal destination moves the piece
  - likely via `chess.js` or an equivalent approved library
- Future UI polish:
  - Side to move, Flip, and Reset should be visually aligned in one row in Play mode.
- Future footer/legal/trust pages:
  - About
  - How It Works
  - FAQ
  - Privacy Policy
  - Terms of Use
  - Contact
