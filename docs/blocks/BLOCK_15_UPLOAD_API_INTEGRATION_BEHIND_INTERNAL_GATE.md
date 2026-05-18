# BLOCK 15 — Upload/API Integration Behind Internal Gate

## Status

Active. Features 15.1, 15.2, 15.3, 15.4, and 15.4.1 are implemented / ready for review.

BLOCK 15 must keep recognition behavior behind an explicit internal/dev gate until later features approve and implement runtime wiring. The current default upload behavior remains the existing placeholder response.

## Purpose

Connect uploaded image recognition to the existing product flow behind an internal/dev gate, while preserving safe placeholder behavior by default.

BLOCK 14 produced an internal/test-only FEN reconstruction path for approved role-signal fixtures. BLOCK 15 defines and then wires the upload/API boundary carefully so fixture-backed readiness is not overclaimed as production screenshot recognition.

## Non-goals

- No public production recognition accuracy claim.
- No real screenshot support claim.
- No ungated recognition response.
- No raw user-upload storage.
- No second editor or replacement for the existing Edit mode / position workspace.
- No broad chess legality validation.
- No engine or Stockfish work.
- No auth, accounts, payments, premium gating, saved collections, or SEO.
- No branding, logo, route, deploy, or public launch work.

## Planned Features

### 15.1 Uploaded image recognition API contract behind internal gate
- Status: implemented / ready for review as docs-only contract work.
- Contract location: `docs/product/UPLOAD_RECOGNITION_API_CONTRACT.md`.
- Defines the gated upload recognition response shape.
- Defines the default disabled/placeholder behavior that must remain safe and non-claiming.
- Defines success, failure, partial, and fallback semantics for later endpoint wiring.
- Defines privacy-safe logging expectations.
- Defines how BLOCK 14 FEN output may be consumed later without using fixture expectations as source data.
- Does not edit runtime API, frontend code, shared contract code, tests, or product behavior.

### 15.2 Backend endpoint behind dev/internal flag
- Status: implemented / ready for review.
- Wire `/upload` to the internal detection orchestrator only when an explicit internal/dev gate is enabled.
- Preserve current placeholder response when the gate is disabled.
- Preserve upload validation behavior and privacy-safe logging.
- Return detected FEN only on gated safe success.
- Return placeholder fallback plus structured detection metadata for failed, partial, disabled, or low-confidence gated results.
- Uses `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED`, disabled by default, with only explicit truthy values enabling the path.

### 15.3 Frontend upload flow uses backend result
- Status: implemented / ready for review.
- Teach the frontend upload client to handle the approved upload recognition contract.
- Align shared upload contract code with the backend response shape where appropriate.
- Preserve current upload UX when detection is disabled or falls back.
- Open the existing editable position workspace with the returned safe FEN.
- Keep detection metadata secondary and review-oriented.
- Does not add debug/inspection UI or public recognition claims.

### 15.4 Failure fallback through existing Edit mode / position workspace
- Status: implemented / ready for review.
- Make recognition failures and low-confidence results recoverable through the existing Edit mode / position workspace.
- Do not build a second editor.
- Use honest wording such as needs review, detection unavailable, or manual correction.
- Frontend fallback classification opens placeholder, partial, failed, or absent-detection upload results in Edit Board from the top-level `fen`.
- Gated success results still open normally from the top-level detected `fen`.

### 15.4.1 Edit correction interaction cleanup
- Status: implemented / ready for review.
- Keeps Edit mode framed as correction/editing only, not Play-style selected-piece interaction.
- Uses active placement piece wording for palette-driven correction.
- Keeps existing board-piece drag as free correction drag in Edit mode.
- Keeps Play mode selected-piece rings, legal moves, play undo/redo, and move history deferred to BLOCK 16.

### 15.5 Debug inspection view
- Status: planned.
- Add an internal/debug-only inspection view for detected board bounds, detected pieces, confidence, failure reasons, stages, and generated FEN.
- Keep it internal until explicitly approved otherwise.
- Do not expose raw uploaded image storage or public QA tooling.

### 15.6 Internal QA report
- Status: planned.
- Summarize gated upload recognition behavior, fallback behavior, failures, and known blockers.
- Keep claims internal until measured and approved.
- Prepare a block closeout review and manual validation checklist.

## Contract Boundary

Feature 15.1 is documented in `docs/product/UPLOAD_RECOGNITION_API_CONTRACT.md`.

The contract keeps these rules central:

- Default `/upload` behavior remains placeholder and non-claiming unless a later feature implements gated recognition.
- Recognition output must be behind an internal/dev gate.
- Detected FEN may be returned only when all required gated stages complete safely.
- Failed, partial, disabled, or low-confidence recognition must preserve safe fallback behavior.
- Detection metadata must be additive and compatible with the current product flow.
- Upload validation errors remain structured errors.
- Raw image bytes, file contents, and screenshots must not be logged.

## BLOCK 14 Consumption Rules

Later BLOCK 15 implementation may consume BLOCK 14 output only through measured/orchestrated recognition results.

It must not:

- use fixture `expected_fen` to build, choose, or recover FEN
- use fixture `expected_pieces` as classifier, builder, or runtime source data
- infer production screenshot accuracy from approved fixture results
- expose full-FEN placeholder fields as detected castling, en-passant, halfmove, or fullmove truth
- bypass invalid-board failures

## Success Gates

BLOCK 15 may close only if:

- upload recognition remains disabled/placeholder by default
- gated recognition can be enabled only through an explicit internal/dev flag
- `/upload` returns safe fallback behavior for failed, partial, disabled, or low-confidence recognition
- detected FEN is returned only from safe measured outputs
- frontend behavior remains compatible with fallback states
- the existing Edit mode / position workspace is the manual correction path
- docs and UI avoid production accuracy, real screenshot support, and public upload-readiness claims
- automated checks and a BLOCK 15 closeout/manual validation checklist are complete

## Failure Gates

BLOCK 15 must not move to public/user-facing recognition claims if:

- recognition is enabled by default
- failed recognition blocks upload without a manual correction path
- detected FEN can be faked or inferred from fixture expectation data
- response shape breaks the existing upload flow without an approved migration
- privacy-safe logging boundaries are missing
- docs imply production-grade accuracy or real screenshot support

## Completion Criteria

- Feature 15.1 contract is documented.
- Backend gated upload wiring is implemented and tested in a later approved feature.
- Frontend upload handling is updated and tested in a later approved feature.
- Fallback through the existing editable position workspace is implemented and tested.
- Internal/debug inspection remains gated.
- Internal QA report and closeout checklist are complete.
- No public production recognition, real screenshot support, engine, legal moves, auth, payments, saved collections, or SEO work is added.
