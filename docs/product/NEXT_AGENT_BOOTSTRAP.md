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
- After implementation or important docs/state changes, give Git commands first, then exactly one next Codex prompt when it is safe to continue.
- Never put Git commands after a Codex prompt.
- Never provide more than one Codex prompt in a single response.
- Do not include parallel, optional, backup, or later prompts for unrelated tasks.
- For PLAN-only Codex responses with no file changes, do not provide Git commands.
- Do not say “commit X first if you didn’t already.”
- Assume Omri commits when commands are given.
- Do not require Omri to paste successful Git output every time; he will paste errors if needed.
- If checks fail, scope expands, docs overclaim, or unrelated files changed: do not commit; give a narrow fix prompt.
- Do not start next features or blocks until source-of-truth docs are correct.
- Manual validation is needed only when UI/product judgment matters.
- Branding/logo/UI polish belongs in backlog or a future block unless it is the active approved task.
- If a non-active issue is raised during a block, capture it as backlog/future work or mention it briefly; do not provide a separate Codex prompt.
- Do not generate, create, or edit images unless Omri explicitly asks for image generation, creation, or editing.
- Treat screenshot/image feedback as product or UI feedback, not an image-generation request.

## Current Continuation Point

- Project is in BLOCK 11 — Internal Piece-Recognition Measurement Experiments.
- BLOCK 10 is completed as fixture-intake and measurement-only work.
- BLOCK 11 is completed as internal/test-only measurement work.
- Project is now moving into BLOCK 12 — Internal Role/Color Classifier Experiment.
- Current feature is 12.5 — Role/color measurement tests and report.
- Current step is implemented / ready for review.
- BLOCK 12 must remain internal/test-only and approved-fixture-only.
- No upload/API integration has started.
- No production recognition accuracy claim has been made.
- Current BLOCK 11 measurement compares occupancy only; role/color piece recognition remains unsupported and not implemented.
- BLOCK 12 is planned to explore role/color classification with fixture-specific marker/color sampling over approved fixtures only.
- The 12.1 role/color classifier contract is documented.
- The 12.2 fixture signal audit is documented; color signal is feasible for a future test-only color classifier, while role signal remains ambiguous or unsupported.
- The 12.3 test-only color classifier experiment is documented and implemented: 159 of 167 approved occupied squares classify correctly, with 8 ambiguous rows kept explicit.
- The 12.4 role classifier decision is documented and implemented as blocked/deferred on current approved fixtures.
- Role classification remains unavailable because current role signals are ambiguous or unsupported.
- The 12.5 role/color measurement report is documented and implemented: occupancy and color are measured on approved fixtures, role remains blocked/deferred, combined role/color success is unavailable, and FEN/upload integration remain blocked.
- Next planned feature is 12.6 — Closeout / next-step decision.
- Approved roadmap after BLOCK 12:
  - BLOCK 13 — Recognition Orchestration + FEN Reconstruction.
  - BLOCK 14 — Upload/API Integration Behind Internal Gate.
  - BLOCK 15 — Board Interaction / Game Mode Fixes.
  - BLOCK 16 — User-Facing Analyze Flow Polish.
- Upload/API integration remains deferred until BLOCK 12 and BLOCK 13 gates pass.

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
