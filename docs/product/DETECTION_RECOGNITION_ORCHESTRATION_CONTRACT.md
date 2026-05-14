# Detection Recognition Orchestration Contract

## Status

Feature 14.1 contract. Internal/test-only. Approved fixtures only.

This document defines how measured detection outputs are combined into measured-piece rows before FEN building. It does not define upload/API integration, product UI behavior, real screenshot support, or production recognition accuracy.

## Purpose

Recognition orchestration joins existing fixture-gated measurement outputs by fixture and square so later BLOCK 14 features can build FEN from measured data.

The orchestration layer must not use fixture expectations to decide detected pieces. Fixture expectations are allowed only for tests and measurement comparison.

## Inputs

The orchestration contract uses these inputs:

- `fixture_id`
- `filename`
- approved `board_bounds`
- `orientation`
- square samples from `square_sampling.py`
- occupancy state from square samples
- color classifier rows from `color_classifier.py`
- role classifier rows from `role_classifier.py`
- explicit side-to-move source

The side-to-move source must be explicit. Feature 14.4 stores it in approved fixture `side_to_move` metadata. Fixture `expected_fen` includes side to move too, but `expected_fen` is comparison-only and must not be used as the source for reconstruction.

## Join Rule

Rows are combined by:

- `fixture_id`
- `square`

Every square in the 64-square board should have one square sample row. Occupied squares that are eligible for reconstruction should also have matching color and role rows.

Missing, duplicate, or conflicting rows must be treated as orchestration failures, not silently repaired.

## Output Rows

The orchestration output should produce one row per square.

Each output row should include:

- `fixture_id`
- `filename`
- `square`
- `orientation`
- occupancy state
- detected color
- detected role
- row category
- confidence metadata from upstream stages where available
- source stages
- failure reasons

## Row Categories

### Measured Piece

A measured-piece row means:

- square sample says the square is occupied
- color classifier provides a measured color
- role classifier provides a measured role
- upstream color and role results are usable for reconstruction
- no blocking failure reason exists for that square

Only measured-piece rows may become pieces in later FEN reconstruction.

### Empty Square

An empty-square row means:

- square sample says the square is empty
- no role is attached
- no color is attached
- no piece should be emitted for that square in FEN

Empty rows are valid reconstruction inputs.

### Unsupported / Not-Measured Square

An unsupported or not-measured row means at least one required upstream signal is not usable.

Examples:

- square sample is `not_measured`
- occupied square has missing color
- occupied square has missing role
- color result is `ambiguous`, `unsupported`, `missing`, `extra`, or `not_measured`
- role result is `ambiguous`, `unsupported`, `missing`, `extra`, or `not_measured`
- fixture or orientation is unsupported

Unsupported or not-measured rows must block FEN reconstruction when the square is required to resolve an occupied piece.

## Failure Rules

The orchestration layer should return clear failure states when data cannot safely produce measured pieces.

Required failures include:

- `missing_role`
- `missing_color`
- `ambiguous_role`
- `ambiguous_color`
- `invalid_orientation`
- `invalid_side_to_move`
- `unsupported_fixture`
- `missing_white_king`
- `missing_black_king`
- `duplicate_white_king`
- `duplicate_black_king`
- `not_measured_square`
- `conflicting_square_rows`
- `missing_square_sample`
- `missing_color_row`
- `missing_role_row`

Invalid data must return failure, not fake FEN.

## FEN Boundary

Feature 14.1 does not build FEN. It defines the input contract for later FEN building.

Hard rules:

- Never use `expected_fen` to build FEN.
- Never use `expected_pieces` to choose detected role or color.
- `expected_fen` is only for test comparison.
- `expected_pieces` is only for test comparison and scoring.
- Later FEN building must consume measured-piece rows and empty-square rows only.
- If required measured data is invalid or missing, later FEN building must return failure instead of fake or partial FEN.

## Side-To-Move Boundary

Side to move must be supplied by an explicit internal/test-only source before full FEN generation.

Feature 14.4 uses approved fixture `side_to_move` metadata as that source. The orchestrator must not parse side to move from `expected_fen` for reconstruction.

## Scope Guardrails

- Internal/test-only.
- Approved fixtures only.
- No upload/API behavior.
- No public UI behavior.
- No real screenshot support claim.
- No production accuracy claim.
- No engine or legal-move behavior.

## 14.2 Handoff

Feature 14.2 should implement the internal measured-piece model described here. It should preserve source stages, confidence metadata, and failure reasons so 14.3 can build FEN only when the measured board state is complete enough.
