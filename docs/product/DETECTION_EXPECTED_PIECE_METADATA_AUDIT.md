# Detection Expected-Piece Metadata Audit

This audit records BLOCK 11 / Feature 11.2 readiness for internal/test-only piece-recognition measurements.

It does not implement piece recognition, change fixture images, change `/upload`, change public API contracts, expose UI, or claim production accuracy.

## Audit Scope

Audited manifest:

- `services/api/tests/fixtures/detection/approved/cases.json`

Audited fixture count:

- 8 approved fixtures
- 4 synthetic fixtures
- 4 owned/generated real-ish fixtures

## Required Metadata

Every approved fixture must include:

- `id`
- `filename`
- `source`
- `style`
- `orientation`
- `board_bounds`
- `expected_pieces`
- `expected_fen`
- `license`

Every expected piece must include:

- `square`
- `piece`
- `color`

## Validation Rules

The validator now checks:

- expected-piece squares are valid algebraic squares from `a1` through `h8`
- expected-piece roles are `king`, `queen`, `rook`, `bishop`, `knight`, or `pawn`
- expected-piece colors are `white` or `black`
- expected-piece squares are unique within each fixture
- expected-piece occupied squares match `expected_fen`
- expected-piece colors and roles match the FEN piece codes
- empty squares are implied by absence from `expected_pieces`

The validator intentionally does not validate chess legality, side-to-move legality, check status, castling rights, en passant availability, or move legality.

## Audit Result

Result: passed.

The current approved fixture metadata is ready for Feature 11.3 planning and implementation.

## Current Fixture Coverage

- Starting position, white-bottom: synthetic and owned/generated real-ish.
- Starting position, black-bottom: synthetic and owned/generated real-ish.
- Sparse kings-plus-rook position, white-bottom: synthetic and owned/generated real-ish.
- Sparse kings-plus-rook position, black-bottom: synthetic.
- Middlegame position, white-bottom: owned/generated real-ish.

## Boundaries

- Internal/test-only only.
- Approved fixtures only.
- No new fixtures or image changes in 11.2.
- No upload/API behavior changes.
- No public API contract changes.
- No product UI changes.
- No production-grade or real-world recognition accuracy claims.
