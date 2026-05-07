# Detection Role/Color Classifier Contract

This contract defines BLOCK 12 / Feature 12.1 for internal, test-only role/color classifier experiments.

It is measurement-only. It does not implement classifier code, change `/upload`, change public API contracts, expose product UI, add or modify fixtures, or claim production recognition accuracy.

## Scope

The contract applies only to approved fixtures under:

- `services/api/tests/fixtures/detection/approved/`
- `services/api/tests/fixtures/detection/approved/cases.json`

BLOCK 12 classifiers must remain:

- approved-fixture-only
- internal/test-only
- measurement-only
- separate from upload/API behavior
- separate from product UI

## Relationship To BLOCK 11

BLOCK 11 measured occupancy only:

- empty
- occupied
- not_measured

BLOCK 12 extends BLOCK 11 occupancy rows with role/color classifier fields. It does not replace BLOCK 11 sampling, board bounds, square mapping, or fixture metadata validation.

Unsupported, unavailable, or ambiguous classifier outputs must stay honest as `not_measured`, `unsupported`, or `ambiguous`. They must not become silent guesses.

## Inputs

Each classifier measurement row should receive:

- `fixture_id`
- `filename`
- `source`
- `style`
- `orientation`
- approved `board_bounds`
- `square`
- occupancy sample state: `empty`, `occupied`, or `not_measured`
- expected piece role from fixture `expected_pieces`, or `null`
- expected piece color from fixture `expected_pieces`, or `null`
- sampled pixel or square signature metadata when available

The role/color classifiers should only classify occupied squares. Empty squares and missing occupancy samples should return structured non-success outcomes.

## Outputs

Each role/color classifier measurement row should emit:

- detected color or `null`
- detected role or `null`
- separate color result
- separate role result
- combined role/color result
- color classifier confidence when available
- role classifier confidence when available
- combined confidence when useful
- failure reason when unavailable, unsupported, or ambiguous
- source stage

Example shape:

```json
{
  "fixture_id": "owned_web_white-bottom_start-01",
  "square": "e1",
  "expected": {
    "piece": "king",
    "color": "white"
  },
  "detected": {
    "piece": "king",
    "color": "white"
  },
  "color_result": "correct",
  "role_result": "correct",
  "combined_result": "correct",
  "color_confidence": 0.92,
  "role_confidence": 0.88,
  "failure_reason": null,
  "source_stage": "role_color_classifier"
}
```

## Result Categories

Role/color classifier result fields may use:

- `correct`: expected and detected values match.
- `wrong`: a classifier returns a value, but it does not match expected metadata.
- `missing`: the square is expected occupied, but occupancy or classifier output is missing.
- `extra`: the square is expected empty, but a classifier reports a role or color.
- `not_measured`: measurement did not run or intentionally skipped this square.
- `unsupported`: the fixture, sample, or classifier method is not supported.
- `ambiguous`: the classifier found conflicting or low-separation signal and must not guess.

`wrong` should only be used when a classifier actually returns an incorrect role or color. Unsupported role/color work should use `not_measured` or `unsupported`, not `wrong`.

## Confidence Rules

Confidence is measurement metadata only. It is not a production probability and must not be described as user-facing recognition accuracy.

Rules:

- Use `null` when a classifier is unsupported or did not run.
- Use `null` when sample data is unavailable.
- Low-confidence or ambiguous samples must not guess.
- Confidence may be tracked separately for color and role.
- Combined confidence may be omitted or set to the lower useful classifier confidence.

## Failure Reasons

Supported failure reasons for initial BLOCK 12 reporting:

- `unsupported_fixture`
- `ambiguous_color`
- `ambiguous_role`
- `empty_square`
- `occupancy_missing`
- `sample_unavailable`
- `classifier_not_configured`

Future features may add more specific reasons, but they should remain short, structured, and safe for reports.

## Color And Role Separation

Color and role classification must be measured separately.

Rules:

- Color classification can pass while role classification is `not_measured`.
- Role classification can pass while color classification is `not_measured`.
- Combined role/color success requires both role and color to match expected metadata.
- Combined role/color failure should preserve the separate color and role outcomes.
- A classifier should never infer role/color from expected FEN or board position.

## Deferred

The following remain deferred and out of scope for 12.1:

- upload/API integration
- product UI usage
- production accuracy claims
- real screenshot recognition claims
- public API changes
- new fixtures or fixture image edits
- CV/ML dependencies

## Future Use

Feature 12.2 should audit whether approved fixtures contain enough role/color signal to use this contract.

Feature 12.3 should use this contract for a test-only color classifier experiment if signal is sufficient.

Feature 12.4 should use this contract for a test-only role classifier experiment if signal is sufficient.

Feature 12.5 should report measured role/color outcomes separately from occupancy and avoid any production accuracy claim.
