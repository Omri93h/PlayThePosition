# Detection Piece-Recognition Measurements

This report records BLOCK 11 / Feature 11.4 internal measurement results.

These are test-only measurements on approved fixtures. They do not change `/upload`, public API contracts, product UI, fixture images, or production recognition behavior.

## Scope

Measured fixtures:

- 8 approved fixtures from `services/api/tests/fixtures/detection/approved/cases.json`
- 4 synthetic fixtures
- 4 owned/generated real-ish fixtures

Measured signal:

- square occupancy from the Feature 11.3 square sampler
- expected occupied squares from approved fixture `expected_pieces`

Not measured yet:

- piece role recognition
- piece color recognition
- FEN generation from sampled pieces
- upload/API integration
- production or real-world recognition accuracy

## Result Mapping

- Expected empty + sampled empty: `correct`
- Expected occupied + sampled empty: `missing`
- Expected empty + sampled occupied: `extra`
- Sample `not_measured`: `not_measured`
- Expected occupied + sampled occupied: occupancy match, but piece identity is `not_measured` with `role_color_not_supported`

`wrong` is reserved for a later role/color classifier that returns an incorrect piece or color. Feature 11.4 does not produce `wrong` results because role/color classification is not supported yet.

## Aggregate Summary

- Fixture count: 8
- Total squares measured: 512
- Expected occupied squares: 167
- Sampled occupied squares: 167
- Empty-square correct count: 345
- Occupancy-matched occupied count: 167
- Missing count: 0
- Extra count: 0
- Role/color unsupported count: 167
- Not-measured count: 167

## Fixture Summary

| Fixture group | Fixtures | Expected occupied | Sampled occupied | Missing | Extra | Role/color unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Synthetic approved fixtures | 4 | 70 | 70 | 0 | 0 | 70 |
| Owned/generated real-ish fixtures | 4 | 97 | 97 | 0 | 0 | 97 |
| Total | 8 | 167 | 167 | 0 | 0 | 167 |

## Limitations

- The square sampler detects only occupied/empty/not-measured states.
- A sampled occupied square is not a recognized chess piece yet.
- Role and color remain unsupported for all occupied squares.
- Results are limited to the current approved fixture set.
- These measurements do not prove behavior on user uploads, external screenshots, camera photos, overlays, unusual boards, or production traffic.

## Blockers Before Broader Recognition Work

- Add an explicit role/color extraction experiment before reporting piece identity measurements.
- Keep expected-vs-detected role/color output separate from occupancy measurements.
- Continue using approved fixtures only until fixture policy changes are explicitly approved.
- Keep upload/API integration deferred until role/color measurement, confidence/failure behavior, and fallback behavior have stronger coverage.

## 11.4 Result

Feature 11.4 is implemented / ready for review.

The current approved fixtures support occupancy comparison, but they do not yet support a measured role/color recognition claim.
