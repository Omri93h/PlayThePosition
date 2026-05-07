# Detection BLOCK 12 Measurement Comparison

This report records BLOCK 12 / Feature 12.6 measurement comparison, blockers, and next-step decision.

BLOCK 12 remains internal/test-only and approved-fixture-only. This report does not mark BLOCK 12 complete, start BLOCK 13, change `/upload`, change public API contracts, change product UI, add or modify fixtures, or claim production or real-world screenshot accuracy.

## Feature Summary

- 12.1 Role/color classifier contract exists in `docs/product/DETECTION_ROLE_COLOR_CLASSIFIER_CONTRACT.md`.
- 12.2 Fixture signal audit exists in `docs/product/DETECTION_ROLE_COLOR_SIGNAL_AUDIT.md`.
- 12.3 Color classifier experiment exists in `docs/product/DETECTION_COLOR_CLASSIFIER_EXPERIMENT.md`.
- 12.4 Role classifier decision exists in `docs/product/DETECTION_ROLE_CLASSIFIER_DECISION.md`.
- 12.5 Combined role/color measurement report exists in `docs/product/DETECTION_ROLE_COLOR_MEASUREMENT_REPORT.md`.

## Current Measurement Result

Occupancy:

- Expected occupied squares sampled as occupied: 167 / 167
- Missing count: 0
- Extra count: 0

Color:

- Correct color classifications: 159
- Ambiguous color rows: 8
- Wrong color classifications: 0

Role:

- Role classification: blocked/deferred
- Detected role: unavailable
- Combined role/color success: unavailable

## What Is Working

Occupancy measurement works on the approved fixture set. Approved fixture squares can be sampled and compared against expected occupied squares.

Color classification partially works on approved fixtures. The current color classifier records 159 correct white/black classifications and preserves 8 ambiguous rows without guessing.

## What Remains Blocked

Role classification is not implemented and remains blocked. Current approved fixture role signals are ambiguous or unsupported, so role results must remain `not_measured`, `unsupported`, or `ambiguous`.

Piece identity is not recognized. Full piece identity requires both color and role to be measured from image signal.

BLOCK 13 FEN reconstruction remains blocked. FEN reconstruction needs piece roles, not only occupancy and color.

Upload/API integration remains blocked. Current work is fixture-only, cannot produce complete detected FEN, and is not wired into `/upload` or public API behavior.

## Boundary Summary

| Area | Current status | Decision |
| --- | --- | --- |
| Board-bound detection | measured in earlier fixture-gated work | available only as internal measurement context |
| Square mapping | measured in BLOCK 11 from approved `board_bounds` | approved-fixture-only |
| Occupancy | measured in BLOCK 11 | working on approved fixtures |
| Color | measured in BLOCK 12 | partial success with explicit ambiguity |
| Role | blocked/deferred | no role classifier success |
| Piece identity | unavailable | not recognized |
| FEN reconstruction | blocked | do not start BLOCK 13 until role identity is measurable or roadmap is replanned |
| Upload/API integration | blocked | do not start upload integration |

## Blockers

- Role signals overlap in fixtures with all six roles.
- Sparse fixtures do not cover enough roles for broad role classification.
- Color measurement alone cannot create piece identity.
- Combined role/color success is unavailable.
- FEN reconstruction from detected pieces is unavailable.
- Upload/API integration would overrun the current evidence.

## Decision

Feature 12.6 records that BLOCK 12 should proceed to closeout review, but BLOCK 12 should not be marked complete by this report alone.

The next safest technical step is not the current BLOCK 13 FEN reconstruction plan. Before BLOCK 13 begins, the roadmap should be revised or an intermediate approved block should improve the role signal problem. Safe next directions include:

- improve approved fixture role signals
- revise the role classifier approach around measurable image signal
- create a dedicated role-fixture or marker strategy block

Upload/API integration remains deferred until complete piece identity can be measured and FEN reconstruction is proven internally.

## 12.6 Result

Feature 12.6 is complete.

BLOCK 12 closeout is complete as internal/test-only, approved-fixture-only measurement work. No BLOCK 13 work, upload/API integration, product UI change, fixture change, role classifier implementation, or production accuracy claim was added.
