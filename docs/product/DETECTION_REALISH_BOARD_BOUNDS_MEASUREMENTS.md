# Detection Real-Ish Board-Bounds Measurements

This report records BLOCK 10 / Feature 10.4 board-bounds measurements for the approved real-ish fixture set.

These are fixture-gated board-bounds measurements only. They do not measure piece recognition, FEN recognition, upload integration, public API behavior, real-world recognition accuracy, or production accuracy.

## Summary

- Real-ish fixture count: 4
- Fixture source: owned/generated real-ish PNG files
- Decode boundary: `decode_image_bytes`
- Board-bounds boundary: `detect_board_bounds_from_decoded_image`
- Detection summary: all four approved real-ish fixtures produced board bounds
- Bounds match summary: all detected bounds match expected metadata
- Confidence summary: all measurements returned confidence `0.7`
- Failure reasons: none recorded for this fixture set

## Fixture Measurements

| Fixture | Source / style | Detected | Bounds | Expected match | Confidence | Stage / source | Failure reason |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `owned_web_white-bottom_start-01.png` | owned / web-default | yes | `x=0, y=0, width=512, height=512` | yes | 0.7 | `grid` / `fixture_gated_decoded_board_bounds` | none |
| `owned_web_black-bottom_start-01.png` | owned / web-default | yes | `x=0, y=0, width=512, height=512` | yes | 0.7 | `grid` / `fixture_gated_decoded_board_bounds` | none |
| `owned_chesscom-like_white-bottom_kings-rook-01.png` | owned / chesscom-like | yes | `x=0, y=0, width=512, height=512` | yes | 0.7 | `grid` / `fixture_gated_decoded_board_bounds` | none |
| `owned_lichess-like_white-bottom_middlegame-01.png` | owned / lichess-like | yes | `x=0, y=0, width=512, height=512` | yes | 0.7 | `grid` / `fixture_gated_decoded_board_bounds` | none |

## Notes

- The approved manifest is validated with existing images required.
- The test suite asserts expected board bounds, confidence minimum, stage, and source for `source: "owned"` fixtures only.
- Existing BLOCK 09 synthetic board-bounds measurements remain documented separately in `docs/product/DETECTION_BOARD_BOUNDS_MEASUREMENTS.md`.
- The approved real-ish fixtures are owned/generated and full-board visible; these results should not be generalized to real uploaded screenshots.
- Piece recognition measurements remain future work.
- `/upload` behavior and public API contracts are unchanged.
