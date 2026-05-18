# Upload Recognition API Contract

## Status

Feature 15.1 contract, updated after Feature 15.5 internal debug inspection view.

This contract defines how uploaded image recognition is exposed behind an internal/dev gate. The default `/upload` behavior remains the existing placeholder response when the gate is absent or disabled.

## Purpose

Define a safe upload recognition API boundary before implementation.

The contract must let Play That Position eventually connect uploaded images to the internal recognition/FEN pipeline without claiming production recognition accuracy, real screenshot support, or public upload readiness before those claims are measured and approved.

## Current Runtime Baseline

Current `/upload` behavior remains unchanged by default:

- accepts PNG/JPEG uploads after existing validation
- rejects unsupported, oversized, or corrupted payloads with structured errors
- returns a placeholder FEN response on valid uploads
- logs privacy-safe upload metadata only
- does not run recognition unless `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED` is explicitly enabled
- does not expose recognition output without the internal/dev gate
- does not claim real screenshot support

Current success shape:

```json
{
  "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
  "source": "placeholder",
  "confidence": null,
  "message": "Received position.png; detection is not implemented yet."
}
```

Current validation error shape:

```json
{
  "ok": false,
  "error": {
    "code": "unsupported_file_type",
    "message": "Only PNG and JPEG images are supported."
  }
}
```

## Gate Requirement

Recognition output must not be exposed unless a later implementation provides an explicit internal/dev gate.

Required gate behavior:

- disabled by default
- configurable only for internal/dev use
- preserves the existing placeholder response while disabled
- keeps fallback behavior available when enabled
- never treats approved-fixture results as production screenshot accuracy

Feature 15.2 implements this gate as `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED`.

Only these values enable the gated path:

- `1`
- `true`
- `yes`
- `on`

## Response Compatibility Strategy

The existing top-level fields remain the compatibility baseline:

- `fen`
- `source`
- `confidence`
- `message`

Feature 15.2 adds detection metadata additively only when the internal/dev gate is enabled. Existing clients can keep reading the top-level fields.

Feature 15.3 aligns the shared TypeScript upload contract and frontend upload client with this flat top-level response shape. The frontend tolerates optional `detection` metadata but still opens the board from top-level `fen`.

Feature 15.4 adds frontend fallback handling: placeholder, partial, failed, or absent-detection upload results open the existing Edit Board workspace from top-level `fen` with manual-correction wording. Gated success results continue to open normally from top-level detected `fen`.

Feature 15.5 adds frontend-only debug inspection behind `VITE_INTERNAL_RECOGNITION_DEBUG`. This flag controls inspection visibility only. It does not enable backend recognition, change `/upload`, or make `detection` required.

## Gated Success Shape

When the gate is enabled and all required recognition stages complete safely, `/upload` returns detected FEN in the top-level `fen` field with additive detection metadata.

Example future shape:

```json
{
  "fen": "8/1b5r/2p2k2/1N1q1P2/4Q1n1/2K5/R5B1/8 b - - 0 1",
  "source": "gated_detection_orchestrator",
  "confidence": 0.91,
  "message": "Detection completed. Review the board before using it.",
  "detection": {
    "status": "success",
    "source": "gated_detection_orchestrator",
    "confidence": 0.91,
    "fen": "8/1b5r/2p2k2/1N1q1P2/4Q1n1/2K5/R5B1/8 b - - 0 1",
    "orientation": "black-bottom",
    "stages": [
      {
        "stage": "preprocess",
        "status": "success",
        "confidence": 1.0
      },
      {
        "stage": "grid",
        "status": "success",
        "confidence": 0.95
      },
      {
        "stage": "pieces",
        "status": "success",
        "confidence": 0.91
      },
      {
        "stage": "orientation",
        "status": "success",
        "confidence": 0.9
      },
      {
        "stage": "fen",
        "status": "success",
        "confidence": 0.91
      }
    ],
    "failure": null
  }
}
```

Detected FEN is allowed only when the gated path produces a safe measured result. Full-FEN fields for castling, en passant, halfmove, and fullmove may still be conservative placeholders unless later work detects them explicitly.

## Gated Fallback Shape

When the gate is enabled but recognition is disabled, incomplete, failed, unsafe, or below the success threshold, `/upload` preserves safe fallback behavior.

Example future partial/failure shape:

```json
{
  "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
  "source": "placeholder",
  "confidence": null,
  "message": "Detection needs review. Open the editable board and correct the position manually.",
  "detection": {
    "status": "partial",
    "source": "gated_detection_orchestrator",
    "confidence": 0.42,
    "fen": null,
    "orientation": "unknown",
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
        "stage": "pieces",
        "status": "partial",
        "confidence": 0.42
      }
    ],
    "failure": {
      "code": "low_confidence",
      "message": "Detection result confidence is below the configured threshold.",
      "stage": "pieces",
      "retryable": true,
      "suggestion": "Review and correct the board manually in the existing position workspace."
    }
  }
}
```

Fallback rules:

- upload validation failures still return HTTP errors
- recognition failures should not imply the uploaded image is invalid
- failed recognition must not emit fake detected FEN
- low-confidence results must not replace the board without review semantics
- the existing Edit mode / position workspace is the correction path
- the frontend must not use `detection.fen` as the board source for fallback states

## Status Values

Detection metadata should use the existing internal status vocabulary unless a later feature changes it deliberately:

- `placeholder`
- `success`
- `partial`
- `failed`

The top-level `source` should remain `placeholder` for fallback responses and use an internal gated source such as `gated_detection_orchestrator` only for safe gated success.

## Failure Semantics

Future implementation should preserve structured failures with:

- `code`
- `message`
- `stage`
- `retryable`
- `suggestion`
- optional `failure_reason`

Required recognition failure families include:

- disabled gate / placeholder path
- decode or preprocess failure
- board/grid not found
- missing stage configuration
- piece recognition failure or low confidence
- orientation failure or unknown orientation
- FEN generation failure
- invalid-board failures inherited from BLOCK 14

Invalid board state, missing required measured data, missing side-to-move, invalid side-to-move, and duplicate/missing kings must block detected FEN output.

## Privacy-Safe Logging

Allowed upload/recognition log fields:

- event name
- content type
- file size
- source
- status
- stage
- failure code
- retryable flag
- confidence summary
- FEN length

Forbidden log fields:

- raw image bytes
- base64 image data
- full file contents
- screenshots or crops
- user-provided filenames when not needed for debugging
- fixture `expected_fen` or `expected_pieces` as runtime source data

## BLOCK 14 Consumption Boundary

Later BLOCK 15 implementation may consume BLOCK 14 output only as measured recognition output.

Allowed:

- use measured rows and FEN reconstruction results produced by the internal pipeline
- use explicit side-to-move only when supplied by an approved runtime/test source
- return structured failure when required measured data is unsafe
- compare generated FEN to expectations only in tests/reports

Forbidden:

- parse `expected_fen` as runtime source truth
- use `expected_pieces` as classifier or builder input
- infer side to move from fixture expected FEN
- bypass missing/duplicate king failures
- claim full-FEN placeholder fields are detected truth
- claim approved role-signal fixture readiness is production screenshot accuracy

## Frontend Compatibility Expectations

Frontend work should:

- keep accepting the current placeholder response while the gate is disabled
- treat detected results as needing user review
- open the existing editable position workspace with the returned safe FEN
- show fallback/review language when detection is partial or failed
- keep debug details secondary and internal until explicitly approved
- render debug inspection only for upload-derived views when `VITE_INTERNAL_RECOGNITION_DEBUG` is explicitly enabled
- show FEN lengths in debug inspection instead of raw FEN dumps or raw metadata blobs
- avoid claims that real screenshots are supported or production accurate

The frontend should not depend on raw uploaded image bytes, screenshots, crops, or fixture expectations.

## Tests Expected For Later Implementation

Feature 15.2 backend tests cover:

- gate disabled returns the current placeholder response
- gate enabled safe success returns detected FEN and additive metadata
- gate enabled partial/failure returns placeholder fallback and structured metadata
- upload validation errors remain unchanged
- privacy-safe logs do not include raw image data

Invalid-board and unsafe FEN failures should continue to be covered through BLOCK 14 and future integrated recognition tests as the runtime recognition stages become more complete.

Feature 15.3 frontend tests cover:

- current placeholder response still opens the editable board
- gated success response opens the editable board with detected FEN
- partial/failure metadata keeps manual correction available
- analytics/logging payloads stay privacy-safe
- UI wording avoids production or real screenshot accuracy claims

Feature 15.5 frontend tests cover:

- debug inspection is hidden when `VITE_INTERNAL_RECOGNITION_DEBUG` is absent or disabled
- debug inspection appears for upload-derived views when the flag is explicitly enabled
- absent detection metadata shows a terse internal debug message only behind the flag
- safe detection metadata fields are shown without raw image, crop, base64, file, or metadata blob exposure
- fallback and success upload behavior continue to use top-level `fen`

## Non-Production Caveats

- Runtime recognition exposure is internal/dev gated and disabled by default.
- Current recognition/FEN readiness is approved-fixture/internal/test-only.
- Real screenshots are not supported by this contract.
- Production recognition accuracy is not claimed.
- Public upload/API/UI readiness is not claimed.
- Broad chess legality validation is not included.
- Engine analysis is out of scope.
- Auth, payments, SEO, saved collections, and public launch work are out of scope.

## 15.1 Done Definition

- BLOCK 15 block plan exists.
- Upload recognition API contract exists.
- Gated behavior and default disabled/placeholder behavior are documented.
- BLOCK 14 consumption boundaries are documented.
- Future backend/frontend test expectations are documented.
- Source-of-truth docs pointed to Feature 15.2 planning next before 15.2 implementation began.
- No runtime API, frontend, shared contract, tests, fixtures, or product behavior are changed.

## 15.2 Done Definition

- `/upload` preserves exact placeholder behavior when the gate is absent or disabled.
- `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED` gates backend recognition wiring.
- Gated success can return detected top-level FEN through a backend test-controlled runner.
- Gated partial/failure returns placeholder fallback plus additive detection metadata.
- Recognition failure does not turn a valid upload into an HTTP error.
- Privacy-safe upload logging is preserved.
- Frontend and shared contract code remain unchanged.

## 15.3 Done Definition

- Shared TypeScript upload contract represents the backend flat response shape.
- Shared contract includes optional additive detection metadata.
- Frontend upload client uses the shared response type.
- Placeholder responses without `detection` still open the editable position workspace.
- Gated success responses with `detection` still open from top-level `fen`.
- Existing safe analytics remain limited to source, FEN length, and confidence availability.
- No debug/inspection UI, public recognition claim, real screenshot support claim, or production accuracy claim is added.

## 15.4 Done Definition

- Placeholder, partial, failed, or absent-detection upload results open the existing Edit Board workspace.
- Gated success upload results open normally without being forced into Edit mode.
- Frontend board state uses top-level `fen`, not `detection.fen`.
- Manual-correction wording avoids production or real screenshot recognition claims.

## 15.4.1 Done Definition

- Edit mode reads as a correction workspace with active placement piece wording.
- Existing click/tap placement, delete mode, edit undo/redo, and correction drag remain intact.
- Play mode selected-piece rings, legal moves, play undo/redo, and move history remain deferred.

## 15.5 Done Definition

- Frontend-only internal debug inspection is controlled by `VITE_INTERNAL_RECOGNITION_DEBUG`.
- Only explicit truthy values `1`, `true`, `yes`, and `on` enable the panel.
- The panel renders only for upload-derived views.
- The panel shows safe metadata: status, source, confidence, orientation, stages, failure summary, top-level FEN length, and detection FEN presence/length.
- The panel does not show raw image bytes, base64, screenshots, crops, full uploaded file data, raw metadata blobs, or production-style recognition claims.
- Upload fallback and success behavior remain unchanged.
