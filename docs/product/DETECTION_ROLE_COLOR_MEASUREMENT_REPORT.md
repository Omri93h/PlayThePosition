# Detection Role/Color Measurement Report

This report records BLOCK 12 / Feature 12.5 role/color measurement results.

The report is internal/test-only and approved-fixture-only. It does not implement role classification, change fixtures, change `/upload`, expose product UI, or claim production recognition accuracy.

## Scope

Approved manifest:

- `services/api/tests/fixtures/detection/approved/cases.json`

Fixture count:

- 8 approved fixtures
- 4 synthetic fixtures
- 4 owned/generated real-ish fixtures

## Combined Measurement Summary

Occupancy from BLOCK 11:

- Total squares: 512
- Expected occupied squares: 167
- Sampled occupied squares: 167
- Empty-square correct count: 345
- Missing count: 0
- Extra count: 0

Color from Feature 12.3:

- Occupied squares: 167
- Correct color classifications: 159
- Ambiguous color rows: 8
- Wrong color classifications: 0

Role from Feature 12.4:

- Role classification: blocked/deferred
- Detected role: `null`
- Role result: `not_measured`, `unsupported`, or `ambiguous`
- Combined role/color success: unavailable

## What Each Result Means

Occupancy means a square has a marker or piece-like signal under approved fixture conditions.

Color means a white/black marker signal was measured on approved fixtures only.

Role remains unclassified. The current approved fixtures do not support a broad measured role classifier because role signals are ambiguous or unsupported.

Piece identity is not recognized. Full piece identity would require both color and role to be measured from image signal.

Upload/API integration remains blocked and unchanged.

BLOCK 13 FEN reconstruction remains blocked until role identity is measurable.

## Per-Stage Status

| Stage | Status | Current result | Boundary |
| --- | --- | --- | --- |
| Board bounds | measured earlier | fixture-gated board rectangle detection exists | not upload/API |
| Square mapping | measured earlier | 64 squares derived from approved `board_bounds` | approved fixtures only |
| Occupancy | measured | 167 / 167 expected occupied squares sampled occupied | not piece identity |
| Color | measured with caveats | 159 correct, 8 ambiguous, 0 wrong | not production accuracy |
| Role | blocked/deferred | no role classifier implemented | no combined identity |
| FEN reconstruction | blocked | unavailable | requires role identity |
| Upload/API integration | blocked | unchanged | future gated work only |

## Blockers

- Role signals overlap in fixtures with all six roles.
- Sparse fixtures cover too few roles for broad role classification.
- Color measurement alone cannot produce piece identity.
- Combined role/color success is unavailable.
- FEN reconstruction from detected pieces remains blocked.
- Upload/API integration remains blocked.

## Recommendation

Feature 12.5 supports moving to Feature 12.6 closeout / next-step decision.

The likely next-step decision after BLOCK 12 should be one of:

- improve approved fixture role signals in a later approved fixture block
- design a revised internal role-classifier strategy using measurable image signal
- keep role classification unsupported and prevent FEN reconstruction or upload/API integration from proceeding

BLOCK 13 recognition orchestration and FEN reconstruction should not start until role identity is measurable or explicitly replanned around the current blocker.

## 12.5 Result

Feature 12.5 is implemented / ready for review.

BLOCK 12 remains in progress. No role classifier code, fixture changes, upload/API integration, product UI changes, or production accuracy claims were added.
