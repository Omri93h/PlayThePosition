# BLOCK 11 — Internal Piece-Recognition Measurement Experiments

## Status
Planned as the current internal/test-only piece-recognition measurement block.

BLOCK 11 should measure whether approved fixtures can support expected-vs-detected piece-recognition experiments. It must remain internal and test-only until explicitly approved otherwise.

## Purpose
Explore piece-recognition feasibility using approved fixture metadata and controlled measurement outputs.

This block does not approve upload integration, public API changes, product UI changes, production accuracy claims, or user-facing recognition behavior.

## Non-goals
- No upload integration.
- No public API changes.
- No product UI changes.
- No production-grade recognition claim.
- No raw user uploads.
- No unapproved fixture images.
- No replacement of the current upload/detection pipeline.
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.

## Planned features

### 11.1 BLOCK 11 definition and measurement contract
- Status: implemented / ready for review.
- Define expected-vs-detected piece measurement outputs.
- Keep measurement records internal/test-only.
- Document boundaries between board bounds, square mapping, piece recognition, FEN generation, and upload/API integration.
- Measurement contract is documented in `docs/product/DETECTION_PIECE_RECOGNITION_MEASUREMENT_CONTRACT.md`.

### 11.2 Approved fixture expected-piece metadata audit
- Status: implemented / ready for review.
- Verify approved fixture metadata has expected pieces for every measured position.
- Identify whether existing approved fixtures are enough for first measurements.
- Do not add fixtures unless a later approved feature explicitly requires them.
- Audit is documented in `docs/product/DETECTION_EXPECTED_PIECE_METADATA_AUDIT.md`.
- Existing approved fixtures are ready for 11.3.

### 11.3 Test-only square sampling / piece marker extraction experiment
- Status: implemented / ready for review.
- Design a controlled test-only way to sample fixture squares or extract owned fixture markers.
- Keep this separate from production upload flow.
- Do not claim real image recognition accuracy from this experiment.
- Added an internal/test-only square sampling helper that derives 64 square regions from approved fixture `board_bounds`.
- The helper classifies squares as `empty`, `occupied`, or `not_measured`.
- The helper does not classify piece role or color.
- Invalid bounds and unsupported orientations return `not_measured` rows instead of crashing.

### 11.4 Piece-recognition measurement tests and report
- Status: implemented / ready for review.
- Compare expected pieces against detected pieces.
- Record per-square outcomes:
  - expected piece
  - detected piece
  - correct
  - wrong
  - missing
  - extra
- Record per-position summaries.
- Publish a concise measurement report.
- Measurement report is documented in `docs/product/DETECTION_PIECE_RECOGNITION_MEASUREMENTS.md`.
- Current measurements compare expected occupied squares against 11.3 square-sampling occupancy output.
- Role/color recognition remains unsupported and is reported as `not_measured` with `role_color_not_supported`.
- No upload/API behavior, UI behavior, fixture image, or production recognition behavior changed.

### 11.5 Measurement comparison, blockers, and next-step decision
- Status: planned.
- Summarize piece-recognition measurement outcomes.
- Record blockers and limitations.
- Decide whether the next safe step is more fixture coverage, improved sampling/recognition experiments, or a later gated integration plan.

## Measurement contract

Each measured fixture should produce internal/test-only records with:

- fixture id
- filename
- source/style/orientation
- square
- expected piece/color or empty
- detected piece/color or empty
- result: correct / wrong / missing / extra
- not_measured status for skipped or unsupported square/fixture measurements
- confidence when available
- failure reason when available
- source stage

Position summaries should include:

- expected occupied squares
- detected occupied squares
- correct count
- wrong count
- missing count
- extra count
- not_measured count
- notes/blockers

## Guardrails
- Use approved fixtures only.
- Do not add unapproved images, raw user uploads, broad datasets, or unclear-license assets.
- Keep all experiments internal/test-only.
- Do not change `/upload` behavior or public API contracts.
- Do not expose detection metadata or details in product UI.
- Report measurements, not accuracy claims.
- Keep Edit Board as the future user recovery path.

## Completion criteria
- BLOCK 11 measurement contract is documented.
- Approved fixture expected-piece metadata is audited.
- Test-only square sampling / marker extraction experiment is measured or clearly blocked.
- Piece-recognition measurement report is created.
- Next-step decision is recorded.
- No upload behavior, public API contract, UI change, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
