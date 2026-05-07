# Agent Instructions — Play The Position

This repository is for **Play The Position**.

Product:
A web app that converts a chess position screenshot into a live, editable chessboard position.

Core flow:
Screenshot upload → position detection → FEN → live board → edit/correct → copy/share/open in chess.com analyzer.

## First action in every new session
Before coding, read these files:
- `AGENTS.md`
- `current_focus.md`
- `docs/product/PRODUCT_VISION.md`
- `docs/product/MVP_SCOPE.md`
- `docs/product/DECISIONS.md`
- `docs/product/PROGRESS.md`
- `docs/product/ASSISTANT_WORKFLOW.md`
- `docs/product/CODEX_PROMPT_TEMPLATES.md`
- `docs/product/NEXT_AGENT_BOOTSTRAP.md`
- `docs/product/BLOCKS_INDEX.md`
- `docs/product/FEATURE_INDEX.md`
- `docs/product/FUTURE_PLANS.md`
- the relevant current block file under `docs/blocks/`

## Development workflow
Always work in this sequence:

1. Onboard / understand context
2. Plan the current feature only
3. Wait for approval before implementation when working interactively
4. Execute only the approved scope
5. Add or update tests
6. Run relevant checks
7. Review the implementation
8. Suggest the next smallest feature

## Current-feature rule
Only work on the feature listed in `current_focus.md`.

Do not:
- jump to later blocks
- mix multiple features
- build future plans before MVP is complete
- add accounts, payments, collections, SEO, or engine analysis before the MVP blocks are complete

## Repository structure
- `apps/web` — frontend app
- `services/api` — backend API
- `packages/contracts` — shared API contracts/schemas/types
- `tests/e2e` — end-to-end tests
- `docs/product` — product-level documentation
- `docs/blocks` — block-by-block execution plan
- `prompts` — reusable prompts for agent workflow
- `tooling/scripts` — helper scripts

## Technical direction
Preferred initial stack:
- Frontend: React + Vite + TypeScript + Tailwind
- Backend: Python + FastAPI
- Frontend tests: Vitest / Testing Library
- Backend tests: Pytest
- E2E tests: Playwright
- Contracts: OpenAPI-first or shared schema-first contracts

## Code quality rules
- Keep files small and focused.
- Split files before they become large or hard to reason about.
- Prefer simple architecture over clever abstractions.
- Reuse existing code before creating new files.
- Add tests for every feature.
- Do not leave dead code, unused files, or vague TODOs.
- Keep frontend, backend, contracts, and tests clearly separated.

## UI design rules
When touching UI, follow `docs/product/DESIGN_DIRECTION.md`. Keep the product modern, premium, clean, dark-first, chess-inspired without copying chess.com or lichess, mobile-responsive, and restrained with green accents.

## Review rules
After every executed feature, provide:
1. What changed
2. Files changed
3. Commands/checks run and results
4. Self-review result
5. Repo hygiene notes
6. `git status --short`
7. Suggested commit message
8. Suggested next feature

Before returning, perform a strict self-review for scope violations, unnecessary files, repo hygiene issues, deleted or risky changes, missing or weak tests, accessibility basics when UI changed, and whether the work is safe to commit.

Do not commit automatically. Do not delete files without explicit approval. Do not move to the next feature automatically.

## Output rules
Be concise. Do not print full files, long logs, or repeated summaries. Return only changed files, check results, blockers, self-review, git status, suggested commit message, and next step. When commands produce long output, summarize only failures or final status. Do not paste full command logs unless there is a failure that needs debugging.

When handing work back to Omri after implementation or important docs/state changes, follow `docs/product/ASSISTANT_WORKFLOW.md`: Git commands first, then exactly one next Codex prompt when safe. Do not provide Git commands for PLAN-only responses with no file changes.

## Out-of-scope until MVP completion
- User accounts
- Saved collections
- Payments / subscriptions
- Internal engine analysis
- SEO pages
- Programmatic content pages
- Leaderboards / competitions
