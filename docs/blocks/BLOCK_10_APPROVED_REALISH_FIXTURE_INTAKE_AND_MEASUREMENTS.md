# BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements

## Status
Planned as the current approved real-ish fixture-intake and measurement block.

## Purpose
Add a tiny approved non-user / real-ish fixture set and measure it before upload integration.

This block continues measurement-only recognition work. It does not approve production accuracy claims, upload integration, public API changes, or user-facing recognition changes.

## Non-goals
- No upload integration.
- No public API changes.
- No production-grade recognition claim.
- No raw user uploads.
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.

## Planned features

### 10.1 Fixture source approval and candidate selection
- Decide which real-ish non-user fixture candidates are eligible.
- Record source, ownership/licensing, privacy, expected position, and approval status before adding images.
- Prefer owned/generated/hand-created approximations if external screenshots are not cleanly approved.

### 10.2 Add first approved real-ish non-user fixture set
- Add only explicitly approved and licensed fixtures.
- Keep the fixture set tiny and measurement-focused.
- Do not add raw user uploads, dumps, broad datasets, or unclear-license screenshots.

### 10.3 Run decode/preprocess measurements on real-ish fixtures
- Measure decode/preprocess behavior on the approved real-ish fixture set.
- Record supported format, dimensions, decode success/failure, and failure reasons.
- Do not wire results into `/upload`.

### 10.4 Run board-bounds measurements on real-ish fixtures
- Run the internal fixture-gated board-bounds path on approved real-ish fixtures.
- Record detected/not detected, bounds, confidence, failure stage, and failure reason.
- Report measurements only, not accuracy claims.

### 10.5 Measurement comparison report and next-step decision
- Compare real-ish fixture measurements against the BLOCK 09 synthetic-only measurements.
- Record blockers and reliability gaps.
- Decide whether to add more fixtures, improve board-bounds detection, measure piece recognition, defer integration, or plan a later gated upload integration step.

## Guardrails
- Fixtures must be non-user and explicitly approved/licensed.
- Prefer owned/generated/hand-created approximations if external screenshots are not cleanly approved.
- Do not copy Chess.com or Lichess screenshots unless licensing/approval is explicit.
- Do not store raw user uploads.
- Results must be framed as measurements, not accuracy claims.
- Do not change `/upload` behavior or public API contracts.
- Keep Edit Board as the user recovery path for any future user-facing detection work.

## Completion criteria
- Fixture source approval decision is recorded.
- First real-ish approved fixture set is added only after explicit approval.
- Decode/preprocess measurements are documented.
- Board-bounds measurements are documented.
- Comparison against synthetic-only measurements is documented.
- Next-step decision is recorded.
- No upload behavior, public API contract, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
