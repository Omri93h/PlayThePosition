# Detection BLOCK 13 Role Classifier Measurement Report

Feature 13.6 records the BLOCK 13 role classifier measurement result and the next-step decision after the revised test-only role classifier experiment.

This report is internal/test-only, approved-fixture-only, and measurement-only. It does not change fixtures, implement FEN reconstruction, change `/upload`, expose product UI behavior, or claim production or general screenshot recognition.

## BLOCK 13 Summary

BLOCK 13 was created because BLOCK 12 proved occupancy measurement worked on approved fixtures and color classification partially worked, but role identity remained blocked.

Completed BLOCK 13 work through Feature 13.5:

- 13.1 documented the role-signal strategy contract and forbidden shortcuts.
- 13.2 documented approved role-signal fixture design rules.
- 13.3 added three owned/generated `role-signal` fixtures with deterministic fixture tooling and approved metadata.
- 13.4 added audit v2 and found the owned `role-signal` fixtures separable from sampled image signal.
- 13.5 added the revised test-only role classifier and measured role output on the owned `role-signal` fixtures.

## 13.4 Audit V2 Result

Audit v2 measured whether role identity was separable from sampled fixture pixels before classifier work.

| Metric | Result |
| --- | ---: |
| Role-signal fixtures audited | 3 |
| Expected occupied squares | 36 |
| Measured role-signal samples | 36 |
| Roles observed | 6 |
| Minimum separation margin | 0.1406 |
| Ambiguous role pairs | 0 |
| Aggregate status | feasible |

The audit used approved fixture pixels, approved `board_bounds`, derived square regions, and sampled shape signatures. Expected metadata was used for grouping/scoring only, not for classifier decisions.

## 13.5 Role Classifier Result

The revised role classifier measured only occupied squares in the three owned/generated `role-signal` fixtures.

| Metric | Result |
| --- | ---: |
| Role-signal fixtures measured | 3 |
| Occupied role-signal squares | 36 |
| Correct role classifications | 36 |
| Wrong role classifications | 0 |
| Ambiguous rows | 0 |
| Unsupported rows | 0 |
| Not measured rows | 0 |

All six roles are represented in the measured output:

- king
- queen
- rook
- bishop
- knight
- pawn

Focused tests verify expected metadata remains scoring-only by tampering with an expected role after sampling and confirming `detected_role` still follows the sampled marker shape.

## Boundaries

The successful role result applies only to the three owned/generated role-signal fixtures:

- `owned_role-signal_white-bottom_dense-01.png`
- `owned_role-signal_black-bottom_dense-01.png`
- `owned_role-signal_white-bottom_shifted-01.png`

This does not prove role classification on:

- legacy synthetic fixtures
- real-ish fixtures
- real screenshots
- uploads
- camera photos
- third-party board screenshots
- overlays or annotated boards
- production traffic

The classifier is still an internal test-only experiment over controlled fixture markers. It is not a general chess-piece recognizer.

## Role, Color, FEN, And Upload Separation

- Role classification: measurable on the owned role-signal fixture set only.
- Color classification: remains separate and unchanged from BLOCK 12.
- Combined role/color identity: can be considered for a later internal orchestration step, but this report does not implement it.
- FEN reconstruction: not started in 13.6.
- Upload/API integration: deferred and unchanged.
- Product UI behavior: unchanged.

FEN reconstruction should not start inside Feature 13.6. It can be reconsidered only after BLOCK 13 closeout confirms the BLOCK 13 role gates, source-of-truth docs, and remaining role/color integration assumptions are clean.

## Decision

Feature 13.6 supported moving to BLOCK 13 closeout review.

After closeout, the next technical direction may reconsider BLOCK 14 — Recognition Orchestration + FEN Reconstruction as an internal/test-only approved-fixture step. That future work must still avoid upload/API integration until internal FEN reconstruction is explicitly approved and measured.

Upload/API integration remains deferred.

## 13.6 Result

Feature 13.6 is implemented / ready for review.

BLOCK 13 closeout review is complete. BLOCK 13 is closed as internal/test-only, approved-fixture-only measurement work.
