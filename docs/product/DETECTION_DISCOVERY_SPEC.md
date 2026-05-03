# Detection Discovery Spec

This spec defines the first discovery target for moving from scaffolded/synthetic detection toward real screenshot-to-board recognition. It does not claim production-grade accuracy, and it does not approve storing raw user uploads.

## First Supported Screenshot Target

Start with the narrowest useful target:

- Clean 2D digital chessboard screenshots.
- Full board visible.
- No rotation or perspective skew.
- No major occlusion from dialogs, arrows, highlights, hands, camera glare, or overlays.
- Desktop screenshots first.
- Mobile screenshots later, after desktop fixtures and metrics are stable.

## Initial Source / Style Targets

- Chess.com-like web board.
- Lichess-like web board.
- Simple/default board colors.
- Simple/default piece styles.

These are style targets for discovery. They are not permission to copy brand assets or commit copyrighted screenshots.

## Non-goals

- No production-grade accuracy claim.
- No camera/photo/skewed-board support yet.
- No engine, Stockfish, legal move validation, or legal move display.
- No auth, accounts, payments, premium gating, or external link-out.
- No raw user-upload storage.

## Fixture Policy

- Prefer synthetic and hand-created fixtures first.
- Add small manually approved fixtures only when they have clear licensing/approval.
- Do not store raw user-uploaded screenshots unless explicitly approved.
- Do not commit large datasets, unclear-license screenshots, archive dumps, or copyrighted images.
- Every fixture must include a licensing/approval note.
- Every fixture must include expected metadata before being used for measurement.

## Fixture Naming

Use:

```text
source_style_orientation_case.ext
```

Example:

```text
lichess_default_white-bottom_start-01.png
```

Recommended values:

- `source`: `chesscom-like`, `lichess-like`, `synthetic`, or another approved source label.
- `style`: `default`, `green`, `brown`, `minimal`, or another concise style label.
- `orientation`: `white-bottom`, `black-bottom`, or `unknown`.
- `case`: concise case name plus sequence, such as `start-01`, `middlegame-01`, or `noboard-01`.

## Fixture Metadata Schema

Each fixture metadata entry should include:

- `id`
- `filename`
- `kind`: `synthetic`, `hand_created`, `approved_manual_fixture`, or `failure_case`
- `source`
- `style`
- `orientation`
- `board_bounds` if known: `x`, `y`, `width`, `height`
- `expected_pieces`: square, piece, color, and optional confidence note
- `expected_fen`
- `license`: status and note
- `expected_metrics`
- `expected_failure` when the case should fail
- `notes`

## Success Metrics

Measure each approved fixture with:

- Board crop detected: yes/no plus confidence.
- Orientation detected: `white-bottom`, `black-bottom`, or `unknown`.
- Piece list produced with per-piece confidence.
- FEN generated and compared to expected FEN.
- Failure reason reported when detection cannot proceed.

Confidence should be explicit and easy to inspect. A low-confidence result is acceptable if the failure path remains honest and recoverable through Edit Board.

## Debug / Inspection Output

Human-readable output should be simple:

```text
black rook at h4
white king at d3
```

Structured output should use JSON-style records:

```json
{
  "square": "h4",
  "piece": "rook",
  "color": "black",
  "confidence": 0.82,
  "source_stage": "piece_recognition",
  "failure_reason": null
}
```

Unknown or failed squares should be explicit:

```json
{
  "square": "d3",
  "piece": null,
  "color": null,
  "confidence": 0.31,
  "source_stage": "piece_recognition",
  "failure_reason": "low_confidence"
}
```

## Privacy / Safety Rules

- Do not store raw user uploads.
- Do not commit large or unclear-license screenshots.
- Do not add copyrighted screenshots from chess sites, streams, books, courses, or user submissions without explicit approval.
- Keep local experiments under ignored raw/large fixture folders.
- Approved fixtures only.

## 7.1 Done Definition

- First supported screenshot target is documented.
- Fixture policy, naming, and metadata expectations are documented.
- Success metrics are documented.
- Debug/inspection output shape is documented.
- No recognition implementation, dependencies, real screenshots, or user uploads are added.
