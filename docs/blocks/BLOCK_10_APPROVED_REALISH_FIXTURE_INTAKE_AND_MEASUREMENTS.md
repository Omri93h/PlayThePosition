# BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements

## Status
In progress as the current approved real-ish fixture-intake and measurement block.

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
- Status: complete/committed.
- Decide which real-ish non-user fixture candidates are eligible.
- Record source, ownership/licensing, privacy, expected position, and approval status before adding images.
- Prefer owned/generated/hand-created approximations if external screenshots are not cleanly approved.
- Source approval and candidate selection are documented in `docs/product/DETECTION_REALISH_FIXTURE_SOURCE_APPROVAL.md`.
- No images or approved manifest entries are added in 10.1.

### 10.2 Add first approved real-ish non-user fixture set
- Status: complete/committed.
- Add only explicitly approved and licensed fixtures.
- Keep the fixture set tiny and measurement-focused.
- Do not add raw user uploads, dumps, broad datasets, or unclear-license screenshots.
- Added four owned/generated real-ish PNG fixtures under the approved fixture path.
- Updated approved fixture metadata with ownership/licensing notes, expected FENs, expected pieces, board bounds, and decode/board-bounds measurement expectations.
- Added deterministic fixture-generation tooling under `tooling/scripts/`.
- No copied Chess.com or Lichess screenshots/assets were used.
- No upload/API behavior changed and no recognition accuracy is claimed.

### 10.3 Run decode/preprocess measurements on real-ish fixtures
- Status: complete/committed.
- Measure decode/preprocess behavior on the approved real-ish fixture set.
- Record supported format, dimensions, decode success/failure, and failure reasons.
- Do not wire results into `/upload`.
- Measurements are documented in `docs/product/DETECTION_REALISH_DECODE_MEASUREMENTS.md`.
- All four owned/generated real-ish fixtures decode successfully through the internal decode boundary.
- Board-bounds measurements are covered separately in 10.4.
- No upload/API behavior changed and no recognition accuracy is claimed.

### 10.4 Run board-bounds measurements on real-ish fixtures
- Status: complete/committed.
- Run the internal fixture-gated board-bounds path on approved real-ish fixtures.
- Record detected/not detected, bounds, confidence, failure stage, and failure reason.
- Report measurements only, not accuracy claims.
- Measurements are documented in `docs/product/DETECTION_REALISH_BOARD_BOUNDS_MEASUREMENTS.md`.
- All four owned/generated real-ish fixtures produced board bounds matching expected metadata.
- Piece recognition measurements remain future work.
- No upload/API behavior changed and no recognition accuracy is claimed.

### 10.5 Measurement comparison report and next-step decision
- Status: current/planned; not implemented.
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
