# Detection FEN Reconstruction Evaluation Contract

## Status

Feature 14.2.5 contract. Docs-only. Internal/test-only. Approved fixtures only.

This contract defines BLOCK 14 FEN failure codes and evaluation/report rules before the measured-piece FEN builder is implemented. It does not implement FEN reconstruction, change fixtures, change upload/API behavior, expose UI behavior, claim real screenshot support, or claim production accuracy.

## Purpose

BLOCK 14 must build FEN from measured outputs, not fixture truth. This contract keeps that boundary explicit for Feature 14.3 and later reporting.

The immediate purpose is to define:

- canonical BLOCK 14 failure codes
- FEN evaluation/report shape
- side-to-move truth rules
- generated FEN comparison rules
- conditions where reconstruction must fail instead of emitting fake or partial FEN

## Canonical Failure Codes

Feature 14.3 and later BLOCK 14 reporting should use these failure codes when applicable:

- `unsupported_fixture`
- `missing_square_sample`
- `duplicate_square_sample`
- `conflicting_square_rows`
- `not_measured_square`
- `missing_color`
- `missing_role`
- `ambiguous_color`
- `ambiguous_role`
- `unsupported_color`
- `unsupported_role`
- `missing_white_king`
- `missing_black_king`
- `duplicate_white_king`
- `duplicate_black_king`
- `invalid_side_to_move`
- `missing_side_to_move`
- `invalid_orientation`
- `fen_not_generated`

Existing lower-level failures may still be preserved as source failure reasons, but BLOCK 14 reports should map them into the canonical codes above when summarizing FEN reconstruction readiness.

## FEN Evaluation Report Shape

Each fixture-level FEN evaluation row should include:

- fixture id
- filename
- source
- style
- orientation
- measured row count
- measured piece count
- empty square count
- unsupported row count
- generated FEN, or `null`
- expected FEN for comparison only
- placement match boolean
- full FEN match boolean only when an explicit side-to-move source exists
- failure code
- failure reasons
- source stages represented
- confidence metadata summary when useful

Example shape:

```json
{
  "fixture_id": "owned_role-signal_white-bottom_dense-01",
  "filename": "owned_role-signal_white-bottom_dense-01.png",
  "source": "owned",
  "style": "role-signal",
  "orientation": "white-bottom",
  "measured_row_count": 64,
  "measured_piece_count": 12,
  "empty_square_count": 52,
  "unsupported_row_count": 0,
  "generated_fen": null,
  "expected_fen": "8/1b5r/2p2k2/1N1q1P2/4Q1n1/2K5/R5B1/8 w - - 0 1",
  "placement_match": null,
  "full_fen_match": null,
  "failure_code": "missing_side_to_move",
  "failure_reasons": ["missing_side_to_move"],
  "source_stages": ["square_sampling", "color_classifier", "role_classifier"],
  "confidence_summary": {
    "minimum_square_confidence": 0.5,
    "minimum_color_confidence": 0.5,
    "minimum_role_confidence": 0.5
  }
}
```

## Side-To-Move Rule

Side to move must come from explicit fixture or test metadata.

Feature 14.4 adds standalone `side_to_move` metadata to approved success fixtures in `cases.json`. The side-to-move value also appears inside fixture `expected_fen`, but `expected_fen` is comparison-only and must not be used as the source for reconstruction. Therefore:

- the FEN builder must not parse side to move from `expected_fen`
- full six-field FEN generation requires explicit `side_to_move` metadata
- 14.3 may build and compare piece placement only if approved
- 14.4 must report `missing_side_to_move` or `invalid_side_to_move` when full FEN output is requested without valid explicit side-to-move truth
- castling, en passant, halfmove, and fullmove fields may use conservative placeholders in 14.4; they are not detected game-state truth

## Generated FEN Comparison Rules

`expected_fen` may be used only in tests and reports for comparison.

Allowed comparison use:

- `expected_fen.split()[0]` may be used to compare piece placement
- the full `expected_fen` may be used for full FEN comparison only after explicit side-to-move truth exists outside `expected_fen`

Forbidden reconstruction use:

- do not use `expected_fen` to choose pieces
- do not use `expected_fen` to choose side to move
- do not use `expected_fen` to choose orientation
- do not use `expected_fen` to recover from missing measured rows
- do not use `expected_pieces` to choose detected role or color

## Failure Instead Of FEN

The builder/evaluator must return structured failure instead of FEN when measured data is unsafe.

Failure is required when:

- an occupied measured row is unsupported
- an occupied measured row is not measured
- role is missing
- color is missing
- role is ambiguous
- color is ambiguous
- role or color is unsupported
- square samples are missing or duplicated
- upstream rows conflict for the same square
- orientation is invalid
- side to move is invalid
- side to move is missing and full FEN is requested
- white king is missing
- black king is missing
- duplicate white kings exist
- duplicate black kings exist

The builder/evaluator must not emit fake FEN, partial FEN, or inferred FEN for these cases.

## Relationship To 14.3

Feature 14.3 may implement a placement builder from measured-piece rows.

If 14.3 proceeds before 14.4 side-to-move handling, it should:

- build placement from measured-piece rows only
- compare placement against `expected_fen.split()[0]` only in tests/reports
- leave full six-field FEN generation blocked with `missing_side_to_move`
- preserve unsupported measured rows as failures

## Relationship To 14.4, 14.5, And 14.6

Feature 14.4 defines explicit side-to-move and orientation handling. It keeps orientation handling upstream: once measured rows use canonical algebraic squares, FEN reconstruction must not apply a second board transform.

Feature 14.5 implements invalid-board failure states for missing and duplicate kings. It intentionally does not add check/checkmate, move-history, castling-rights, en-passant, halfmove/fullmove, engine, or broader legality validation.

Feature 14.6 records the approved-fixture readiness result in `docs/product/DETECTION_BLOCK_14_FEN_RECONSTRUCTION_READINESS_REPORT.md`. That report is a docs/test-only summary. It does not add production runtime reporting, CLI output, API behavior, upload integration, or UI behavior.

Until BLOCK 14 closeout, this contract remains the reporting guardrail that prevents fixture-only FEN reconstruction from being framed as upload/API behavior or production recognition accuracy.

## Scope Guardrails

- Approved fixtures only.
- Internal/test-only only.
- No upload/API integration.
- No public UI behavior.
- No fixture changes.
- No real screenshot support claim.
- No production accuracy claim.
