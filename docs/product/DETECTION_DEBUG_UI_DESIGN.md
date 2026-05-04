# Detection Debug UI Design

This design covers a future inspection/debug view for screenshot recognition results. It is for making detection understandable and debuggable without overclaiming accuracy. It does not implement UI, real recognition, or raw image display.

## Purpose

- Show what the detection pipeline estimated.
- Help users and developers understand uncertain or failed results.
- Keep Edit Board as the recovery path.
- Avoid wording that suggests production-grade accuracy.

## Placement

- Future placement: analysis page near the board/actions area.
- Hidden by default behind a compact "Detection details" toggle.
- Optional auto-open for low-confidence or failed detection cases only if later approved.
- The panel should feel secondary to the board and correction workflow.

## User-facing Wording

Use:

- "Detection estimate"
- "What we detected"
- "Needs review"
- "Low confidence"

Avoid:

- "confirmed"
- "accurate"
- "recognized perfectly"
- any wording that implies real-world screenshot accuracy is solved.

## Data To Show

- Detection status: `placeholder`, `success`, `partial`, or `failed`.
- Board crop status, confidence, and bounds when available.
- Orientation and confidence.
- Recognized pieces list, for example:
  - black rook at h4
  - white king at d3
- Per-piece confidence.
- Generated FEN and confidence.
- Failure reason, stage, retry guidance, and suggestion.

## Privacy

- Do not show raw uploaded image or crop previews unless explicitly approved later.
- Do not store raw uploaded screenshots.
- The future panel should receive metadata only, not raw image bytes.

## Confidence And Failure Wording

- Use "Detection estimate" for normal results, including successful future detection.
- Use "Needs review" when confidence is partial or some squares/stages are uncertain.
- Use "Low confidence" for weak board, orientation, piece, or FEN estimates.
- Failed detection should show the failed stage, failure reason, and a short suggestion such as trying a cleaner full-board screenshot.
- Avoid "confirmed", "accurate", "recognized perfectly", or any wording that implies real-world screenshot accuracy is solved.
- Do not show raw uploaded screenshots or crop previews unless explicitly approved later.
- The current upload response is not changed by 7.6; detection metadata remains internal/scaffolded until a later approved integration feature.

## UX States

### Placeholder / Scaffolded
- Explain that detection is still scaffolded or unavailable.
- Keep the message honest and short.
- Offer Edit Board as the correction path.

### Success
- Show board crop detected, orientation, generated FEN, and recognized pieces.
- Still label the result as an estimate.

### Partial
- Show what was detected and what was uncertain.
- Highlight low-confidence pieces or missing board/orientation data.
- Encourage review/correction in Edit Board.

### Failed
- Show the failed stage and friendly suggestion.
- Keep technical detail secondary.
- Do not block manual correction if a board can still be opened.

## Future Backend Response Shape

Keep the current upload response stable until implementation is explicitly approved. A later implementation may add an optional `detection` object:

The staged backend/frontend integration plan is documented in `docs/product/DETECTION_INTEGRATION_PLAN.md`.

Frontend implementation notes for that later work:

- Store detection metadata separately from the editable/current FEN so user corrections remain authoritative.
- Keep Detection details as secondary UI; the board and Edit Board recovery path stay primary.
- Treat missing `detection` metadata as normal until the optional contract is approved and shipped.
- Use "Detection estimate", "Needs review", and "Low confidence" for uncertain results.
- Do not show raw uploaded images or crop previews unless explicitly approved later.

```json
{
  "fen": "4k3/8/8/8/7r/3K4/8/8 w - - 0 1",
  "source": "detected",
  "confidence": 0.76,
  "message": "Detection estimate created. Please review the board.",
  "detection": {
    "status": "partial",
    "board_crop": {
      "detected": true,
      "confidence": 0.91,
      "bounds": { "x": 124, "y": 88, "width": 512, "height": 512 }
    },
    "orientation": {
      "value": "white-bottom",
      "confidence": 0.84
    },
    "pieces": [
      {
        "square": "h4",
        "piece": "rook",
        "color": "black",
        "confidence": 0.82,
        "source_stage": "piece_recognition",
        "failure_reason": null
      },
      {
        "square": "d3",
        "piece": "king",
        "color": "white",
        "confidence": 0.79,
        "source_stage": "piece_recognition",
        "failure_reason": null
      }
    ],
    "fen": {
      "value": "4k3/8/8/8/7r/3K4/8/8 w - - 0 1",
      "confidence": 0.76
    },
    "failure": null
  }
}
```

Failure example:

```json
{
  "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
  "source": "placeholder",
  "confidence": null,
  "message": "Detection could not find a board. You can still set up the position manually.",
  "detection": {
    "status": "failed",
    "board_crop": {
      "detected": false,
      "confidence": 0.18,
      "bounds": null
    },
    "orientation": {
      "value": "unknown",
      "confidence": null
    },
    "pieces": [],
    "fen": null,
    "failure": {
      "code": "board_grid_not_found",
      "message": "Could not find a clear chessboard grid.",
      "stage": "grid",
      "retryable": true,
      "suggestion": "Try a clean 2D board screenshot with the full board visible."
    }
  }
}
```

## Future Frontend Boundaries

- `DetectionDetailsPanel` or equivalent.
- Receives detection metadata only.
- Does not receive raw image bytes.
- Does not fetch extra detection data by itself unless later approved.
- Renders compact summary first, expandable details second.
- Keeps the board and Edit Board workflow primary.

## Mock / Scaffold Guidance

- For now, keep this as docs/design only.
- Do not add mocked UI in app code yet.
- Do not expose debug controls in production UI yet.
- Future tests should use metadata-only fixtures and avoid raw screenshots.

## 7.2 Done Definition

- Debug/inspection placement and states are documented.
- Future data contract needs are documented.
- Privacy rules are explicit.
- Sample payloads are short and metadata-only.
- No UI code, backend contract code, recognition implementation, dependencies, or fixture images are added.
