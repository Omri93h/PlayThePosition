# Detection Decode Measurements

This report records BLOCK 09 / Feature 9.3 decode/preprocess measurements for the approved synthetic fixture set.

These are decode/preprocess measurements only. They do not measure board recognition, piece recognition, FEN recognition, upload integration, or production accuracy.

## Summary

- Approved fixture count: 4
- Fixture source: owned/generated synthetic PNG files
- Decode boundary: `decode_image_bytes`
- Decode status: all approved fixtures decode successfully
- Format: PNG
- Dimensions: 512 x 512
- Mode: RGB
- Byte-size range: 3,592 to 7,363 bytes

## Fixture Measurements

| Fixture | Decode status | Format | Dimensions | Mode | Bytes |
| --- | --- | --- | --- | --- | ---: |
| `synthetic_default_white-bottom_start-01.png` | success | png | 512 x 512 | RGB | 7,361 |
| `synthetic_default_black-bottom_start-01.png` | success | png | 512 x 512 | RGB | 7,363 |
| `synthetic_default_white-bottom_kings-rook-01.png` | success | png | 512 x 512 | RGB | 3,592 |
| `synthetic_default_black-bottom_kings-rook-01.png` | success | png | 512 x 512 | RGB | 3,606 |

## Notes

- The approved manifest is validated with existing images required.
- The test suite asserts expected decode format, dimensions, mode, and byte-size constraints.
- Board-bounds measurements remain future work for Feature 9.4.
- `/upload` behavior and public API contracts are unchanged.
