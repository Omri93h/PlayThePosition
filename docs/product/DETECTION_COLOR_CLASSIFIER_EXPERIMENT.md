# Detection Color Classifier Experiment

This report records BLOCK 12 / Feature 12.3 test-only color classifier experiment.

The classifier is internal/test-only, approved-fixture-only, and measurement-only. It does not implement role classification, change fixtures, change `/upload`, expose product UI, or claim production recognition accuracy.

## Scope

Approved manifest:

- `services/api/tests/fixtures/detection/approved/cases.json`

Fixture count:

- 8 approved fixtures
- 4 synthetic fixtures
- 4 owned/generated real-ish fixtures

Occupied-square count:

- 167 expected occupied squares

## Experiment Method

The experiment reuses the 12.2 signal audit helper. For each approved fixture, it:

- samples expected occupied squares from approved `board_bounds`
- builds fixture-local white/black reference signatures from sampled occupied-square signal
- classifies occupied-square color by nearest white/black reference only when separation is clear
- returns `ambiguous`, `unsupported`, or `not_measured` rather than guessing

The classifier does not infer color from FEN, square identity, starting position, chess rules, or product UI state.

## Measurement Result

Aggregate result:

- Occupied squares: 167
- Measured color count: 159
- Correct color count: 159
- Wrong color count: 0
- Missing count: 0
- Extra count: 0
- Not measured count: 0
- Unsupported count: 0
- Ambiguous count: 8

Per-fixture result:

| Fixture | Source / style | Orientation | Occupied squares | Measured colors | Correct | Ambiguous | Blocker notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `synthetic_default_white-bottom_start-01` | `synthetic` / `default` | `white-bottom` | 32 | 28 | 28 | 4 | `ambiguous_color` |
| `synthetic_default_black-bottom_start-01` | `synthetic` / `default` | `black-bottom` | 32 | 28 | 28 | 4 | `ambiguous_color` |
| `synthetic_default_white-bottom_kings-rook-01` | `synthetic` / `default` | `white-bottom` | 3 | 3 | 3 | 0 | none |
| `synthetic_default_black-bottom_kings-rook-01` | `synthetic` / `default` | `black-bottom` | 3 | 3 | 3 | 0 | none |
| `owned_web_white-bottom_start-01` | `owned` / `web-default` | `white-bottom` | 32 | 32 | 32 | 0 | none |
| `owned_web_black-bottom_start-01` | `owned` / `web-default` | `black-bottom` | 32 | 32 | 32 | 0 | none |
| `owned_chesscom-like_white-bottom_kings-rook-01` | `owned` / `chesscom-like` | `white-bottom` | 3 | 3 | 3 | 0 | none |
| `owned_lichess-like_white-bottom_middlegame-01` | `owned` / `lichess-like` | `white-bottom` | 30 | 30 | 30 | 0 | none |

The 8 ambiguous rows are retained as ambiguous rather than forced into a white/black guess.

## Role Classification

Role classification remains unsupported and not implemented in 12.3.

Color classifier rows keep role fields null / not measured:

- detected role: `null`
- role result: `not_measured`
- role failure reason: `classifier_not_configured`

## Boundaries

- Approved fixtures only.
- Internal/test-only only.
- No fixture image changes.
- No upload/API behavior changes.
- No public API contract changes.
- No product UI changes.
- No production-grade or real-world recognition accuracy claims.
- No role classifier implementation.

## Recommendation

Feature 12.3 supports moving forward to the next approved BLOCK 12 step, with caveats:

- Color measurement works on the approved fixture set for 159 of 167 occupied squares.
- Ambiguous rows must remain explicit in future reports.
- Role classification remains blocked/deferred for 12.4 planning and must not be implied by the color classifier.

## 12.3 Result

Feature 12.3 is complete.

BLOCK 12 closeout is complete. Role classification, upload/API integration, product UI changes, fixture changes, and production accuracy claims remain out of scope.
