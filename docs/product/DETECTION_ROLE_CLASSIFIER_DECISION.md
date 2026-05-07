# Detection Role Classifier Decision

This report records BLOCK 12 / Feature 12.4 test-only role classifier decision.

The decision is internal/test-only and approved-fixture-only. It does not implement role classifier code, change fixtures, change `/upload`, expose product UI, or claim production recognition accuracy.

## Decision

Role classification is blocked/deferred on the current approved fixture set.

Feature 12.4 should not implement a broad role classifier because current role signals are ambiguous or unsupported:

- Starting-position fixtures contain all six roles, but sampled role signatures overlap.
- Sparse kings-plus-rook fixtures cover only king and rook, so they cannot support broad role classification.
- The owned `lichess-like` middlegame fixture contains all six roles, but role separation is low under the current signal audit.

## Allowed Signal

The only allowed role signal for this block is sampled visual signal from approved fixture images.

Allowed:

- approved fixture images
- approved `board_bounds`
- square sampling regions
- sampled square visual signatures from `docs/product/DETECTION_ROLE_COLOR_SIGNAL_AUDIT.md`

Forbidden shortcuts:

- expected metadata lookup as a classifier
- FEN inference
- square identity inference
- starting-position assumptions
- chess rules
- filename or style-based role lookup

## Current Evidence

The 12.2 signal audit found:

| Fixture group | Coverage | Role result | Reason |
| --- | --- | --- | --- |
| Synthetic starting positions | all six roles | ambiguous | role signals overlap |
| Owned web-default starting positions | all six roles | ambiguous | role signals overlap |
| Synthetic kings-plus-rook positions | king and rook only | unsupported | insufficient role coverage |
| Owned chesscom-like kings-plus-rook position | king and rook only | unsupported | insufficient role coverage |
| Owned lichess-like middlegame position | all six roles | ambiguous | low role separation |

This evidence is enough to block a broad role classifier and preserve honest `not_measured`, `unsupported`, or `ambiguous` outcomes.

## Color Classifier Separation

Feature 12.3 color classifier output remains separate from role classification.

Current color result:

- 167 approved occupied squares
- 159 correct color classifications
- 8 ambiguous color rows
- 0 wrong color rows

Color classifier success does not imply full piece identity success. Combined role/color success remains unavailable because role is not classified.

## Role Output Policy

Until a later approved role strategy changes this decision, role outputs should remain:

- detected role: `null`
- role result: `not_measured`, `unsupported`, or `ambiguous`
- role failure reason: `classifier_not_configured`, `unsupported_fixture`, `ambiguous_role`, `sample_unavailable`, or another explicit non-success reason

No row should report role `correct` or `wrong` unless a future approved classifier produces a role from image signal without forbidden shortcuts.

## Blockers

- Role signal overlaps in fixtures with all six roles.
- Sparse fixtures do not cover all six roles.
- Current fixture art may not encode enough role-specific signal for deterministic role classification.
- Any role classifier built from FEN, square identity, starting position, or expected metadata would be a measurement shortcut, not image-based classification.

## Recommendation

Feature 12.4 supports moving to Feature 12.5 as a measurement/reporting step.

Feature 12.5 should report:

- occupancy measurement from BLOCK 11
- color classifier measurement from 12.3
- role classifier blocked/deferred state from 12.4
- combined role/color success unavailable
- upload/API integration still blocked

Future role work should be explicitly replanned. Likely safe directions are:

- improve approved fixture role signals in a later approved fixture block
- create a new role classifier approach only after a plan defines measurable image signal
- keep role classification unsupported and prevent FEN reconstruction/upload integration from proceeding

## 12.4 Result

Feature 12.4 is complete as a blocked/deferred role-classifier decision.

BLOCK 12 closeout is complete. No role classifier code, fixture changes, upload/API integration, product UI changes, or production accuracy claims were added by this feature.
