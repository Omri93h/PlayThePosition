# BLOCK 12 — Internal Role/Color Classifier Experiment

## Status

In progress as the current internal/test-only role/color classifier experiment block.

BLOCK 12 should extend BLOCK 11 from occupancy-only measurement toward fixture-measured piece identity. It must remain approved-fixture-only, internal/test-only, and measurement-only until explicitly approved otherwise.

## Purpose

Explore whether approved fixture images contain enough stable signal to classify occupied-square piece color and role in a controlled measurement setting.

This block does not approve upload integration, public API changes, product UI changes, production accuracy claims, user-facing recognition behavior, fixture image changes, or new fixture images.

## Non-goals

- No upload integration.
- No public API changes.
- No product UI changes.
- No production-grade recognition claim.
- No real-world screenshot accuracy claim.
- No raw user uploads.
- No unapproved fixture images.
- No fixture image edits.
- No replacement of the current upload/detection pipeline.
- No template matching or image-feature classifier unless a later feature plan explicitly approves changing direction.
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.

## Planned Features

### 12.1 Role/color classifier contract
- Status: implemented / ready for review.
- Defines the internal/test-only role/color classifier measurement contract in `docs/product/DETECTION_ROLE_COLOR_CLASSIFIER_CONTRACT.md`.
- Extends the BLOCK 11 output shape for expected vs detected piece role/color.
- Keeps unsupported or ambiguous samples as `not_measured`, `unsupported`, or `ambiguous`, not guesses.
- Keeps upload/API integration deferred.

### 12.2 Fixture signal audit for role/color feasibility
- Status: implemented / ready for review.
- Audits approved fixture images and metadata for role/color signal feasibility in `docs/product/DETECTION_ROLE_COLOR_SIGNAL_AUDIT.md`.
- Confirms color signal is feasible for a future internal/test-only color classifier experiment.
- Records role signal as ambiguous or unsupported under the current audit.
- Does not change fixture images.

### 12.3 Test-only color classifier experiment
- Status: planned.
- Implement a fixture-gated color classifier for occupied squares only.
- Use existing `board_bounds`, square mapping, occupancy sampling, and `expected_pieces`.
- Prefer deterministic marker/color sampling over broader image recognition.
- Return `not_measured` for ambiguous or unsupported samples.

### 12.4 Test-only role classifier experiment
- Status: planned.
- Implement a fixture-gated role classifier for occupied squares only.
- Start with fixture-specific marker sampling only if the signal is clear.
- Return `not_measured` for ambiguous or unsupported role samples.
- Do not infer role from board position or FEN.

### 12.5 Role/color measurement tests and report
- Status: planned.
- Compare expected piece role/color against detected role/color.
- Record `correct`, `wrong`, `missing`, `extra`, and `not_measured` outcomes.
- Publish a concise internal measurement report.
- Report failures as measurements, not accuracy claims.

### 12.6 Closeout / next-step decision
- Status: planned.
- Summarize BLOCK 12 measurement outcomes.
- Record role/color classifier blockers and limitations.
- Decide whether the next safe step is improved fixture signals, more approved fixtures, a revised classifier approach, or a later gated integration plan.

## Classifier Direction

BLOCK 12 should split color and role classification.

The first approved direction is fixture-specific marker/color sampling over approved fixtures:

- Use existing `board_bounds`.
- Use existing square mapping from BLOCK 11.
- Use existing occupancy sampling from BLOCK 11.
- Use approved fixture `expected_pieces` metadata for measurement.
- Classify only occupied squares.
- Return `not_measured` for unsupported or ambiguous samples.

Template matching, broader image-feature classifiers, CV/ML dependencies, or production-recognition approaches are out of scope unless a later approved plan explicitly changes direction.

## Measurement Contract

The detailed 12.1 contract is documented in `docs/product/DETECTION_ROLE_COLOR_CLASSIFIER_CONTRACT.md`.

Each measured occupied square should extend the BLOCK 11 measurement row with:

- expected piece role
- expected piece color
- detected piece role or `null`
- detected piece color or `null`
- role result: `correct` / `wrong` / `missing` / `extra` / `not_measured` / `unsupported` / `ambiguous`
- color result: `correct` / `wrong` / `missing` / `extra` / `not_measured` / `unsupported` / `ambiguous`
- combined role/color result
- confidence when available
- failure reason when unavailable or ambiguous
- source stage

Per-fixture summaries should include:

- expected occupied count
- measured occupied count
- color correct / wrong / not-measured counts
- role correct / wrong / not-measured counts
- combined role/color correct count
- blocker notes

## Guardrails

- Use approved fixtures only.
- Do not add or modify fixture images.
- Keep all experiments internal/test-only.
- Do not change `/upload` behavior or public API contracts.
- Do not expose detection metadata or details in product UI.
- Report measurements, not accuracy claims.
- Keep upload/API integration blocked until role/color measurement is stronger and explicitly approved.

## Completion Criteria

- BLOCK 12 role/color classifier contract is documented.
- Fixture signal feasibility is audited.
- Test-only color classifier experiment is measured or clearly blocked.
- Test-only role classifier experiment is measured or clearly blocked.
- Role/color measurement report is created.
- Next-step decision is recorded.
- No upload behavior, public API contract, UI change, fixture image change, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
