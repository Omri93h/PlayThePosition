# Detection Piece-Recognition Measurement Contract

This contract defines the internal/test-only measurement shape for BLOCK 11 piece-recognition experiments.

It does not implement piece recognition, change `/upload`, change public API contracts, expose UI, add fixtures, or claim production accuracy.

## Scope

The measurement contract applies only to approved fixtures under:

- `services/api/tests/fixtures/detection/approved/`
- `services/api/tests/fixtures/detection/approved/cases.json`

The contract is for comparing fixture metadata against test-only detection outputs. It is not a user-facing detection contract.

## Definitions

- Expected piece: the fixture metadata entry for a square in `expected_pieces`, including `piece` and `color`.
- Detected piece: the piece/color reported by a test-only recognizer, sampler, or extraction experiment for a square.
- Empty square: a square with no expected piece in fixture metadata, or no detected piece in a test-only output.
- Unknown / unsupported detection: a test-only recognizer could not classify a square or fixture because the input, sample, marker, or method is unsupported.
- Confidence: a numeric measurement confidence when the test-only recognizer can provide one. It is measurement metadata, not a production probability.
- Failure reason: a short structured reason explaining why a square or fixture could not be measured or classified.
- Source stage: the internal stage that produced the measurement, such as `piece_recognition`, `square_sampling`, or `fixture_marker_extraction`.

## Result Categories

Every measured square should resolve to one category:

- `correct`: expected piece/color and detected piece/color match.
- `wrong`: expected and detected are both occupied, but piece or color differs.
- `missing`: expected square is occupied, but detected output is empty or unknown.
- `extra`: expected square is empty, but detected output reports a piece.
- `not_measured`: square or fixture was skipped because the method is unsupported, blocked, or intentionally out of scope.

## Per-Square Output

Each measured square should produce:

```json
{
  "fixture_id": "owned_web_white-bottom_start-01",
  "square": "e4",
  "expected": {
    "piece": null,
    "color": null
  },
  "detected": {
    "piece": null,
    "color": null
  },
  "result": "correct",
  "confidence": 1.0,
  "failure_reason": null,
  "source_stage": "piece_recognition"
}
```

Rules:

- `expected.piece` and `expected.color` are `null` for expected-empty squares.
- `detected.piece` and `detected.color` are `null` for detected-empty or unclassified squares.
- `confidence` may be `null` when unavailable.
- `failure_reason` should be `null` for normal measured squares.
- `not_measured` rows must include a `failure_reason`.

## Per-Position Summary

Each measured fixture should produce:

```json
{
  "fixture_id": "owned_web_white-bottom_start-01",
  "filename": "owned_web_white-bottom_start-01.png",
  "source": "owned",
  "style": "web-default",
  "orientation": "white-bottom",
  "expected_occupied_count": 32,
  "detected_occupied_count": 32,
  "correct_count": 32,
  "wrong_count": 0,
  "missing_count": 0,
  "extra_count": 0,
  "not_measured_count": 0,
  "unsupported_reason": null,
  "blocker_notes": []
}
```

Rules:

- Position summaries should count only internal/test-only measurement outputs.
- `unsupported_reason` should be set when the entire fixture cannot be measured.
- `blocker_notes` should capture why a fixture or method is not ready for broader use.
- A clean summary is still not a production accuracy claim.

## Boundaries

- Internal/test-only only.
- Approved fixtures only.
- No raw user uploads.
- No new fixture images in 11.1.
- No `/upload` behavior changes.
- No public API contract changes.
- No product UI changes.
- No production-grade or real-world screenshot accuracy claims.
- No replacement of the current detection pipeline.

## Future Use

Feature 11.2 should audit whether approved fixture metadata is complete enough for this contract.

Feature 11.3 may introduce a test-only sampling or marker-extraction experiment that emits this shape.

Feature 11.4 should use this shape for measurement tests and a report.
