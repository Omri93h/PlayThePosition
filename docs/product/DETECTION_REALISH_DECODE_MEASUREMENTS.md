# Detection Real-Ish Decode Measurements

This report records BLOCK 10 / Feature 10.3 decode/preprocess measurements for the approved real-ish fixture set.

These are decode/preprocess measurements only. They do not measure board recognition, piece recognition, FEN recognition, upload integration, public API behavior, or production accuracy.

## Summary

- Real-ish fixture count: 4
- Fixture source: owned/generated real-ish PNG files
- Decode boundary: `decode_image_bytes`
- Decode status: all approved real-ish fixtures decode successfully
- Format: PNG
- Dimensions: 512 x 512
- Mode: RGB
- Byte-size range: 3,490 to 11,566 bytes

## Fixture Measurements

| Fixture | Source / style | Decode status | Format | Dimensions | Mode | Bytes |
| --- | --- | --- | --- | --- | --- | ---: |
| `owned_web_white-bottom_start-01.png` | owned / web-default | success | png | 512 x 512 | RGB | 9,177 |
| `owned_web_black-bottom_start-01.png` | owned / web-default | success | png | 512 x 512 | RGB | 9,176 |
| `owned_chesscom-like_white-bottom_kings-rook-01.png` | owned / chesscom-like | success | png | 512 x 512 | RGB | 3,490 |
| `owned_lichess-like_white-bottom_middlegame-01.png` | owned / lichess-like | success | png | 512 x 512 | RGB | 11,566 |

## Notes

- The approved manifest is validated with existing images required.
- The test suite asserts expected decode format, dimensions, mode, and byte-size constraints for `source: "owned"` fixtures only.
- Existing BLOCK 09 synthetic decode measurements remain documented separately in `docs/product/DETECTION_DECODE_MEASUREMENTS.md`.
- Board-bounds measurements for the real-ish fixture set remain future work for Feature 10.4.
- `/upload` behavior and public API contracts are unchanged.
