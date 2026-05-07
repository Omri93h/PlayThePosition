# Detection Role/Color Signal Audit

This report records BLOCK 12 / Feature 12.2 fixture signal audit for role/color feasibility.

The audit is internal/test-only and approved-fixture-only. It does not implement classifier code, change fixtures, change `/upload`, expose product UI, or claim production recognition accuracy.

## Scope

Audited manifest:

- `services/api/tests/fixtures/detection/approved/cases.json`

Approved fixture count:

- 8 fixtures
- 4 synthetic fixtures
- 4 owned/generated real-ish fixtures

Occupied-square signal count:

- 167 expected occupied squares
- 167 occupied-square signals measured

Styles audited:

- `synthetic` / `default`
- `owned` / `web-default`
- `owned` / `chesscom-like`
- `owned` / `lichess-like`

## Audit Method

The audit uses existing `board_bounds` and square mapping from approved fixture metadata.

For each expected occupied square, it samples the existing square inner region and compares candidate piece/marker pixels against local square background. The sampled signature is used only to inspect whether visual signal appears separable enough for a future internal classifier experiment.

The audit does not infer role from FEN, square identity, starting position, or chess rules. Expected fixture metadata is used only to group measured signals by expected color and role.

## Color Feasibility

Result: feasible for a 12.3 test-only color classifier experiment.

All approved fixtures contain both white and black occupied-square samples with strong white/black signal separation under the current audit heuristic:

| Fixture | Source / style | Orientation | Occupied squares | Color result | Signal distance |
| --- | --- | --- | ---: | --- | ---: |
| `synthetic_default_white-bottom_start-01` | `synthetic` / `default` | `white-bottom` | 32 | feasible | 182.21 |
| `synthetic_default_black-bottom_start-01` | `synthetic` / `default` | `black-bottom` | 32 | feasible | 182.21 |
| `synthetic_default_white-bottom_kings-rook-01` | `synthetic` / `default` | `white-bottom` | 3 | feasible | 250.22 |
| `synthetic_default_black-bottom_kings-rook-01` | `synthetic` / `default` | `black-bottom` | 3 | feasible | 250.22 |
| `owned_web_white-bottom_start-01` | `owned` / `web-default` | `white-bottom` | 32 | feasible | 173.85 |
| `owned_web_black-bottom_start-01` | `owned` / `web-default` | `black-bottom` | 32 | feasible | 173.85 |
| `owned_chesscom-like_white-bottom_kings-rook-01` | `owned` / `chesscom-like` | `white-bottom` | 3 | feasible | 281.13 |
| `owned_lichess-like_white-bottom_middlegame-01` | `owned` / `lichess-like` | `white-bottom` | 30 | feasible | 298.23 |

Color feasibility here means the approved fixtures appear suitable for a future internal/test-only color classifier experiment. It is not a production probability or user-facing recognition claim.

## Role Feasibility

Result: not feasible for a broad role classifier yet.

The role signal is currently ambiguous or unsupported:

| Fixture | Source / style | Orientation | Occupied squares | Role result | Reason | Minimum role distance |
| --- | --- | --- | ---: | --- | --- | ---: |
| `synthetic_default_white-bottom_start-01` | `synthetic` / `default` | `white-bottom` | 32 | ambiguous | role signals overlap | 0.00 |
| `synthetic_default_black-bottom_start-01` | `synthetic` / `default` | `black-bottom` | 32 | ambiguous | role signals overlap | 0.00 |
| `synthetic_default_white-bottom_kings-rook-01` | `synthetic` / `default` | `white-bottom` | 3 | unsupported | insufficient role coverage | n/a |
| `synthetic_default_black-bottom_kings-rook-01` | `synthetic` / `default` | `black-bottom` | 3 | unsupported | insufficient role coverage | n/a |
| `owned_web_white-bottom_start-01` | `owned` / `web-default` | `white-bottom` | 32 | ambiguous | role signals overlap | 0.00 |
| `owned_web_black-bottom_start-01` | `owned` / `web-default` | `black-bottom` | 32 | ambiguous | role signals overlap | 0.00 |
| `owned_chesscom-like_white-bottom_kings-rook-01` | `owned` / `chesscom-like` | `white-bottom` | 3 | unsupported | insufficient role coverage | n/a |
| `owned_lichess-like_white-bottom_middlegame-01` | `owned` / `lichess-like` | `white-bottom` | 30 | ambiguous | role signals overlap | 6.52 |

Sparse kings-plus-rook fixtures contain too few roles to support a full role classifier audit. Starting-position fixtures contain all six roles, but role signatures overlap under the current square-signal audit. The owned `lichess-like` middlegame contains all six roles, but separation remains low.

## Blockers And Ambiguity Notes

- Role signal is not clearly separable enough for a broad role classifier.
- Sparse fixtures are useful for color and occupancy checks, but they do not cover all six roles.
- Starting-position fixtures may repeat visual signatures across different roles under the current signature method.
- The audit intentionally does not use expected FEN, square identity, or chess position rules to infer role.
- Upload/API integration remains blocked.

## Recommendation

Feature 12.3 may proceed as an internal/test-only color classifier experiment using approved fixtures only.

Feature 12.4 should not claim broad role classification from the current audit. Before or during 12.4, the project should either:

- keep role classification as `not_measured` / `ambiguous` where signal overlaps
- explicitly limit any role experiment to measured fixture groups where signal is separable
- improve approved fixture signals in a later approved feature if broader role classification remains blocked

## 12.2 Result

Feature 12.2 is implemented / ready for review.

BLOCK 12 remains in progress. No classifier implementation, fixture changes, upload/API integration, product UI changes, or production accuracy claims were added.
