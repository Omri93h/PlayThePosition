# Detection Role Classifier Experiment

Feature 13.5 adds a revised internal/test-only role classifier experiment for the owned role-signal fixtures.

This experiment is approved-fixture-only and measurement-only. It does not change fixture images, change `cases.json`, implement FEN reconstruction, change `/upload`, expose UI behavior, or claim production or general screenshot recognition.

## Purpose

Feature 13.4 audit v2 found the owned `role-signal` fixture set feasible for a revised role classifier experiment. Feature 13.5 uses the same sampled image signatures to classify role markers as one of:

- king
- queen
- rook
- bishop
- knight
- pawn

The classifier is intentionally limited to controlled role-signal fixtures. It is not a general chess-piece classifier.

## Inputs

The role classifier uses:

- approved role-signal fixture audit rows
- sampled image shape signatures from `role_signal_audit_v2`
- fixture style only to decide whether the fixture is supported

Expected metadata is used only to score the result after detection. It is not used to choose `detected_role`.

Forbidden shortcuts remain forbidden:

- FEN inference
- square identity inference
- starting-position inference
- expected metadata lookup for the detected role
- filename/source/orientation lookup for the detected role
- chess-rule inference

## Outputs

Each role classification row includes:

- `fixture_id`
- `square`
- `expected_role`
- `detected_role`
- `role_result`
- `confidence`
- `failure_reason`
- `source_stage: "role_classifier"`

Non-success behavior remains explicit:

- missing signature returns `not_measured`
- unsupported fixture style returns `unsupported`
- unclear marker shape returns `ambiguous`
- the classifier does not guess when it cannot classify

## Measured Result

Role classifier experiment result on the 13.3 role-signal fixture set:

| Metric | Result |
| --- | ---: |
| Role-signal fixtures measured | 3 |
| Occupied squares measured | 36 |
| Detected role rows | 36 |
| Correct role classifications | 36 |
| Wrong role classifications | 0 |
| Ambiguous rows | 0 |
| Unsupported rows | 0 |
| Not measured rows | 0 |

All six roles are represented in the detected output.

## Shortcut Guard

Focused tests tamper with an expected role after sampling. The classifier still returns the role indicated by the sampled marker shape, and the row is scored as `wrong` against the tampered expected metadata. This verifies that expected metadata is used for scoring, not for choosing `detected_role`.

## Legacy Fixture Handling

Legacy non-role-signal fixtures are unsupported for this classifier experiment. They are not part of the 13.5 gate and are not treated as role-recognition evidence.

## Decision

Feature 13.5 supports moving to 13.6 for a role classifier measurement report and next-step decision.

FEN reconstruction remains deferred until 13.6 reports combined role/color status and explicitly decides whether the BLOCK 13 gates are satisfied.

## Limitations

- Results apply only to three owned/generated role-signal fixtures.
- This does not prove behavior on existing legacy fixtures, real screenshots, uploads, camera photos, overlays, third-party boards, or production traffic.
- This does not generate FEN.
- This does not change `/upload`, public API behavior, or UI behavior.
- This does not claim product-ready piece identity recognition.

## 13.5 Result

Feature 13.5 is implemented / ready for review.

BLOCK 13 remains in progress. Feature 13.6 is still unimplemented and requires a separate approved plan.
