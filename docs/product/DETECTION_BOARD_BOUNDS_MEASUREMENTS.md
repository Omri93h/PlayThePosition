# Detection Board-Bounds Measurements

This report records BLOCK 09 / Feature 9.4 fixture-gated board-bounds measurements for the approved synthetic fixture set.

These are internal fixture-gated board-bounds measurements only. They do not measure piece recognition, FEN recognition, upload integration, public API behavior, or real-world recognition accuracy.

## Summary

- Approved fixture count: 4
- Fixture source: owned/generated synthetic PNG files
- Decode boundary: `decode_image_bytes`
- Board-bounds boundary: `detect_board_bounds_from_decoded_image`
- Detection status: all approved fixtures produced board bounds
- Bounds match status: all detected bounds match expected metadata
- Confidence: 0.7 for every fixture
- Bounds: `x=0`, `y=0`, `width=512`, `height=512` for every fixture

## Fixture Measurements

| Fixture | Detected | Bounds match | Bounds | Confidence |
| --- | --- | --- | --- | ---: |
| `synthetic_default_white-bottom_start-01.png` | yes | yes | `0,0 512x512` | 0.7 |
| `synthetic_default_black-bottom_start-01.png` | yes | yes | `0,0 512x512` | 0.7 |
| `synthetic_default_white-bottom_kings-rook-01.png` | yes | yes | `0,0 512x512` | 0.7 |
| `synthetic_default_black-bottom_kings-rook-01.png` | yes | yes | `0,0 512x512` | 0.7 |

## Notes

- The approved manifest is validated with existing images required before measurement.
- The test suite asserts stage, source, confidence floor, and exact expected bounds.
- These fixtures are synthetic/generated and intentionally controlled.
- Piece recognition measurements remain future 9.5 work or later.
- `/upload` behavior and public API contracts are unchanged.
