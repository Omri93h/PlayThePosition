# Detection Integration Plan

This plan defines how Play The Position should replace scaffolded detection with real screenshot recognition later. It is planning only: no API contract change, upload behavior change, CV/ML dependency, screenshot fixture, or accuracy claim is approved by this document.

## Current Scaffolded Flow

- `/upload` validates image type, max size, and minimal PNG/JPEG signature.
- `/upload` returns the current placeholder/scaffolded FEN response:
  - `fen`
  - `source: "placeholder"`
  - `confidence: null`
  - message saying detection is not implemented yet.
- `detect_position()` exists as a placeholder pipeline boundary, but `/upload` does not route through real detection.
- Board bounds, piece recognition, orientation, FEN generation, confidence, and failure boundaries are synthetic/control-only or structured-data-only experiments.
- Real screenshot recognition implementation has not started.

## Staged Replacement Path

1. Keep scaffold fallback.
   - Placeholder FEN behavior remains the fallback until real detection is proven.
   - Upload must never fail solely because detection could not recognize the board.

2. Add backend orchestration boundary first.
   - Create a single detection orchestrator that calls preprocessing, board bounds, orientation, piece recognition, FEN generation, and confidence/failure shaping.
   - Keep it internal until fixture metrics are meaningful.

3. Keep detection metadata additive.
   - Preserve current upload response fields.
   - Add an optional `detection` object only in a later approved contract/API feature.
   - Do not remove or rename existing response fields when metadata is introduced.

4. Route approved fixtures through experiments before user-facing changes.
   - Run board bounds, orientation, piece list, FEN, confidence, and failure checks against approved fixture metadata.
   - Treat results as measurements, not public accuracy claims.

5. Add debug/details panel later.
   - The future panel should render metadata only.
   - It should use "Detection estimate", "Needs review", and "Low confidence" wording.
   - It should not display raw screenshots or crops unless explicitly approved.

6. Change user-facing behavior only after gates pass.
   - Detection must have measured fixture results, reliable fallback behavior, and clear failure messaging before `/upload` uses detected FEN for users.

## Backend Boundaries

- Image decode/preprocess boundary for approved image formats.
- Board bounds/crop boundary with confidence and failure reason.
- Orientation boundary returning `white-bottom`, `black-bottom`, or `unknown`.
- Piece recognition boundary returning square, piece, color, confidence, source stage, and failure reason.
- FEN generation boundary from structured recognized board data.
- Confidence/failure metadata boundary using stable status values:
  - `placeholder`
  - `success`
  - `partial`
  - `failed`
- Privacy-safe logging that avoids raw image data and full file contents.

## Frontend Boundaries

- Upload API client can later accept optional `detection` metadata while preserving existing upload behavior.
- Analysis state can later store detection metadata separately from the current FEN.
- Future `DetectionDetailsPanel` or equivalent receives metadata only.
- The details panel should stay secondary to the board and Edit Board correction flow.
- No frontend should depend on raw uploaded image bytes.

## Contract Strategy

- Current `/upload` response remains unchanged for now.
- A later approved feature may add optional detection metadata:
  - `detection.status`
  - `detection.board_crop`
  - `detection.orientation`
  - `detection.pieces`
  - `detection.fen`
  - `detection.failure`
- Existing fields must remain available:
  - `fen`
  - `source`
  - `confidence`
  - `message`
- Existing clients can ignore the future `detection` object and continue reading the existing fields.
- Contract changes should be additive, tested, and documented before frontend use.

### Future Optional `detection` Object

This is a docs-only future shape. BLOCK 08 / 8.5 does not add this to `/upload`, change the public API contract in code, or require frontend changes.

```json
{
  "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
  "source": "placeholder",
  "confidence": null,
  "message": "Detection is not implemented yet.",
  "detection": {
    "status": "partial",
    "source": "gated_detection_orchestrator",
    "confidence": 0.42,
    "stages": [
      {
        "stage": "preprocess",
        "status": "success",
        "confidence": 1.0
      },
      {
        "stage": "grid",
        "status": "success",
        "confidence": 0.7
      },
      {
        "stage": "piece_recognition",
        "status": "partial",
        "confidence": null
      }
    ],
    "failure": {
      "code": "stage_not_configured",
      "message": "Piece recognition is not configured for this gated path.",
      "stage": "piece_recognition",
      "retryable": false,
      "suggestion": "Review and correct the board manually with Edit Board."
    }
  }
}
```

## Fixture And Test Gates

Before changing user-facing detection behavior:

- Approved fixture metadata exists for each tested screenshot.
- Fixtures are small, curated, approved, and licensed.
- No raw user uploads are stored.
- Each fixture records expected board bounds, orientation, pieces, FEN, confidence expectations, and expected failure where relevant.
- Tests measure:
  - board crop detected yes/no plus confidence
  - orientation detected or unknown
  - piece list produced with per-piece confidence
  - generated FEN compared to expected FEN
  - failure code, stage, retryable flag, and suggestion
- Placeholder fallback is proven for failed, partial, or low-confidence detection.

## Internal Fallback Contract

These are internal orchestrator outcomes only. They do not change current `/upload` behavior and must stay behind explicit gates until a later approved integration feature.

- Disabled detection: `status: "placeholder"`, placeholder FEN, no failure object, and a `pipeline` stage/source indicating the gate is disabled.
- Decode failure: `status: "failed"`, placeholder FEN, failure at `preprocess`, and no detected FEN.
- Board bounds failure: `status: "failed"`, placeholder FEN, failure at `grid`, and a board/grid failure reason.
- Downstream missing stages: `status: "partial"`, placeholder FEN, `stage_not_configured`, and the missing stage name.
- Low confidence: `status: "partial"`, placeholder FEN, `low_confidence`, and the stage/confidence that failed the threshold.
- Complete gated success: `status: "success"`, `source: "gated_detection_orchestrator"` or equivalent internal gated source, and detected FEN only when all injected/gated stages complete safely and pass confidence requirements.

## Rollback And Fallback

- Keep the existing Edit Mode / Edit Board position workspace as the primary recovery path.
- Never block upload solely because detection fails.
- Keep a feature/config gate around any real detection path.
- For low-confidence results, use "Needs review" and keep correction obvious.
- If detection fails, return safe fallback behavior and structured metadata only after the optional metadata contract is approved.
- If a rollout causes trust or stability problems, disable the real detection path and keep placeholder/scaffold behavior.

## Risks

- PNG/JPEG decode/preprocess exists internally but is not wired into `/upload`.
- Approved real screenshot fixtures have not been added yet.
- Upload currently bypasses `detect_position()`.
- Screenshot styles vary heavily across sites, themes, devices, and board/piece styles.
- Accuracy can be overclaimed if user-facing wording is not strict.
- Poor detection can hurt trust more than honest scaffolded behavior.

## 7.7 Done Definition

- Current scaffolded flow is documented.
- Staged replacement path is documented.
- Backend/frontend boundaries are documented.
- Fixture gates and fallback strategy are documented.
- No code, tests, API contracts, upload behavior, dependencies, screenshots, or recognition implementation are changed.

## 8.5 Done Definition

- Internal fallback outcomes are documented for disabled, failed, partial, low-confidence, and gated success paths.
- Future optional detection metadata is documented as additive and not returned by `/upload` yet.
- Existing response fields remain the compatibility baseline: `fen`, `source`, `confidence`, and `message`.
- No public API contract, upload behavior, frontend code, screenshots, fixtures, dependencies, or recognition implementation are changed.
