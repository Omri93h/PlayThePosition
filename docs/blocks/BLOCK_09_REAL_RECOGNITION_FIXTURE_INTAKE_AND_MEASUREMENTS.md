# BLOCK 09 — Real Recognition Fixture Intake and Measurements

## Status
In progress as a fixture-intake and measurement block.

## Purpose
Start controlled fixture intake and measured recognition experiments after the BLOCK 08 foundation.

This block measures behavior on approved fixtures only. It does not approve production accuracy claims, upload integration, or public API changes.

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

### 9.1 Approved fixture intake checklist and first candidate selection
- Status: implemented / ready for review.
- Define the checklist for approving fixture candidates.
- Identify the first small non-user fixture candidates.
- Do not add images yet unless explicitly approved in a later execute step.
- Checklist is documented in `docs/product/DETECTION_FIXTURE_INTAKE_CHECKLIST.md`.
- No fixture files/images were added and the approved manifest remains empty.

### 9.2 Add first approved non-user fixture set
- Status: implemented / ready for review.
- Add only explicitly approved non-user fixture images.
- Require source, licensing, approval, and expected metadata for every fixture.
- Keep the fixture set small and measurement-focused.
- Added four owned/generated synthetic PNG fixtures under `approved/`.
- Updated `approved/cases.json` with complete metadata.
- No upload/API behavior changed and no production accuracy claim is made.

### 9.3 Run decode/preprocess measurements on approved fixtures
- Status: implemented / ready for review.
- Measure decode/preprocess behavior on approved fixtures.
- Record supported format, dimensions, decode success/failure, and failure reasons.
- Do not wire results into `/upload`.
- Measurements are documented in `docs/product/DETECTION_DECODE_MEASUREMENTS.md`.
- Board-bounds measurements are handled separately in 9.4.

### 9.4 Run fixture-gated board-bounds measurements
- Status: implemented / ready for review.
- Run the internal fixture-gated board-bounds path on approved fixtures.
- Record bounds, confidence, failure stage, and failure reason.
- Report measurements only, not accuracy claims.
- Measurements are documented in `docs/product/DETECTION_BOARD_BOUNDS_MEASUREMENTS.md`.
- Piece recognition measurements remain future 9.5 work or later.

### 9.5 Measurement report and next-step decision
- Status: implemented / ready for review.
- Summarize fixture results, blockers, and reliability gaps.
- Decide whether to continue measurement work, improve board detection, or defer integration.
- Keep upload integration and public behavior changes out of scope unless separately approved later.
- Measurement summary and next-step decision are documented in `docs/product/DETECTION_MEASUREMENT_REPORT.md`.
- Decision: BLOCK 09 can move to closeout review after this report.
- Recommended next step: add a small approved non-synthetic or real-ish fixture set before upload integration.

## Guardrails
- Approved non-user fixtures only.
- Every fixture requires licensing/approval metadata.
- No raw user uploads.
- Experiments remain internal/test-only.
- Results must be framed as measurements, not accuracy claims.
- Edit Board remains the user recovery path for future user-facing detection work.

## Completion criteria
- Fixture intake policy is applied.
- First approved fixture set is added only after explicit approval.
- Decode/preprocess measurements are documented.
- Board-bounds measurements are documented.
- Blockers and the next decision are clearly recorded.
- No upload behavior, public API contract, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
