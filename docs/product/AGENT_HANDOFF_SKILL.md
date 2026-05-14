# Agent Handoff Skill

Use this guide when a new primary agent takes over Play That Position.

## First Move

Before planning or editing, inspect the repo state:

```bash
git status --short
```

Then read:

- `AGENTS.md`
- `current_focus.md`
- `docs/product/PROGRESS.md`
- `docs/product/BLOCKS_INDEX.md`
- `docs/product/FEATURE_INDEX.md`
- `docs/product/ASSISTANT_WORKFLOW.md`
- `docs/product/CODEX_PROMPT_TEMPLATES.md`
- `docs/product/NEXT_AGENT_BOOTSTRAP.md`
- the current block file under `docs/blocks/`

Use the repository docs as source of truth. Do not rely on stale chat memory.

## Active State

- Product name: Play That Position.
- Future domain/brand asset: `playthatposition.com`.
- Current development/runtime: localhost/internal only.
- Product direction: fast chess position intake, editable reconstructed board, confidence-aware detection, user correction through existing Edit mode, and later analysis/training workflows.
- Current active block: BLOCK 14 — Recognition Orchestration + FEN Reconstruction.
- Current active feature: 14.3.1 — Role-signal color classifier repair, implemented / ready for review.

BLOCK 14 status:

- 14.1 recognition orchestration contract is implemented.
- 14.2 measured-piece model is implemented.
- 14.2.5 FEN failure/evaluation contract is implemented.
- 14.3 placement-only FEN builder is implemented.
- 14.3 historical caveat: placement builder worked technically, but role-signal fixture placement mismatched because measured color classifier had wrong/ambiguous rows.
- 14.3.1 repairs the role-signal color classifier in the current repo state: all three owned role-signal fixtures classify 36 / 36 occupied-square colors correctly, and all three placement strings match `expected_fen.split()[0]`.
- Next safe step after 14.3.1 review/commit: plan 14.4 — Side-to-move and orientation handling.

## Hard Boundaries

- Do not claim production recognition accuracy.
- Do not say real screenshots work.
- Do not say upload/API integration exists.
- Do not start upload/API, public UI behavior, engine, legal moves, auth, payments, link-out, or SEO unless explicitly in scope.
- Keep BLOCK 14 internal/test-only and approved-fixture-only until explicitly approved otherwise.

## FEN And Truth Rules

- `expected_fen` is comparison-only.
- `expected_pieces` is test/scoring truth only.
- Classifiers and builders must not use `expected_fen` or `expected_pieces` as detection/build inputs.
- Side to move is missing outside `expected_fen`.
- Full six-field FEN remains blocked until explicit side-to-move truth is added.
- FEN placement may compare against `expected_fen.split()[0]` in tests/reports.
- Unsupported or incomplete measured data must return structured failure, not fake or partial FEN.

## Handling Codex Outputs

For implementation or important docs/state changes:

1. Review scope, checks, changed files, and `git status --short`.
2. If clean, give Git commands first.
3. Then give exactly one next Codex prompt if safe.

For PLAN-only results with no file changes:

- Do not provide Git commands.
- Approve/correct the plan and provide exactly one execute prompt.

Never provide multiple prompts, optional prompts, backup prompts, or unrelated future prompts in one response.

## Blockers And Next Safe Step

When a blocker appears:

- Record the blocker in the relevant source-of-truth docs.
- Keep the next step narrow.
- Do not proceed to the next feature if the blocker invalidates the current feature gate.

Current known BLOCK 14 blocker to watch:

- Full six-field FEN is blocked until 14.4 defines explicit side-to-move truth outside `expected_fen`.
