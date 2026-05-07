# Detection BLOCK 11 Measurement Comparison

This report records BLOCK 11 / Feature 11.5 measurement comparison, blockers, and next-step decision.

BLOCK 11 remains internal/test-only. This report does not mark BLOCK 11 complete, change `/upload`, change public API contracts, change product UI, add fixture images, or claim production recognition accuracy.

## Feature Summary

- 11.1 Measurement contract exists in `docs/product/DETECTION_PIECE_RECOGNITION_MEASUREMENT_CONTRACT.md`.
- 11.2 Approved fixture expected-piece metadata audit passed and is documented in `docs/product/DETECTION_EXPECTED_PIECE_METADATA_AUDIT.md`.
- 11.3 Square sampling can classify approved fixture squares as `empty`, `occupied`, or `not_measured`.
- 11.4 Measurement compares square-sampling occupancy output against approved fixture `expected_pieces`.

## Current Measurement Result

- Fixture count: 8
- Total squares measured: 512
- Expected occupied squares: 167
- Sampled occupied squares: 167
- Empty-square correct count: 345
- Missing count: 0
- Extra count: 0
- Role/color unsupported count: 167

The current approved fixtures support occupancy comparison. They do not support a measured role/color recognition claim yet.

## Boundary Summary

Board-bound detection:

- Completed earlier as fixture-gated board rectangle measurement.
- It identifies board bounds for approved fixtures.
- It does not identify pieces.

Square mapping:

- Feature 11.3 derives 64 board squares from fixture `board_bounds`.
- It maps sampled regions to algebraic squares.
- It depends on known approved fixture metadata.

Occupancy detection:

- Features 11.3 and 11.4 measure whether a square appears empty or occupied.
- Current approved fixtures measured 167 sampled occupied squares against 167 expected occupied squares.
- This is not role/color piece recognition.

Role/color piece recognition:

- Not implemented.
- Not measured.
- Not claimed.
- Occupied squares are reported as `not_measured` for piece identity with `role_color_not_supported`.

Upload/API integration:

- Deferred and unchanged.
- `/upload` does not use BLOCK 11 measurement helpers.
- No public API contract changes were made.

## Blockers

- Role/color classifier does not exist yet.
- Piece identity cannot be claimed from occupancy sampling.
- Current measurements rely on approved fixtures and known `board_bounds`.
- Results do not prove behavior on user uploads, external screenshots, camera photos, overlays, unusual boards, or production traffic.
- Upload integration should remain deferred until role/color recognition, confidence/failure behavior, and fallback behavior have stronger internal measurement coverage.

## Decision

The next safest technical step after BLOCK 11 is a future internal/test-only role/color classifier experiment block using approved fixtures only.

The next block should:

- keep upload/API integration deferred
- keep product UI unchanged
- use approved fixtures only
- compare expected piece roles/colors against detected roles/colors
- report failures as measurements, not accuracy claims
- preserve Edit Board as the future user recovery path

UI polish remains separate future work unless explicitly selected as the active approved task.

## 11.5 Result

Feature 11.5 is implemented / ready for review.

BLOCK 11 is ready for a later closeout review, but it is not marked complete by this report.
