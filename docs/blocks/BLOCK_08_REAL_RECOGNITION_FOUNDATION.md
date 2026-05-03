# BLOCK 08 — Real Recognition Implementation Foundation

## Status
Planned foundation block. Implementation has not started.

## Purpose
Start the safe foundation for replacing scaffolded detection with measured real-recognition building blocks.

This block is foundation/measurement-gated only. It does not approve production-grade recognition claims.

## Non-goals
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.
- No production-grade recognition accuracy claim.

## Planned features

### 8.1 PNG/JPEG decode and preprocess boundary
- Add a safe backend image decode/preprocess boundary for uploaded PNG/JPEG bytes.
- Keep behavior internal until explicitly wired.
- Do not change `/upload` behavior during planning.

### 8.2 Approved fixture metadata validation
- Add validation for approved fixture metadata before real fixture tests depend on it.
- Keep approved fixtures curated and licensed.
- Do not store raw user uploads.

### 8.3 Detection orchestrator behind feature gate
- Add an internal orchestrator that can call decode, board bounds, orientation, piece recognition, FEN generation, and confidence/failure shaping.
- Keep real-recognition execution gated and fallback-safe.

### 8.4 Fixture-gated board detection path
- Run the board detection path against approved fixtures only.
- Report measurements, not accuracy claims.
- Keep failures recoverable through Edit Board.

### 8.5 Fallback/metadata contract planning
- Plan the additive optional detection metadata contract.
- Preserve existing upload response fields.
- Require fallback behavior before user-facing detection changes.

## Guardrails
- No raw user uploads are stored.
- Approved fixtures only.
- Recognition behavior must be gated and fallback-safe.
- Edit Board remains the recovery path.
- Confidence/failure metadata is required before any user-facing recognition claims.
- Do not overclaim accuracy; report measurements only.

## Completion criteria
- Decode/preprocess boundary exists.
- Approved fixture validation path exists.
- Orchestrator is feature-gated.
- Board detection path can run on approved fixtures.
- Fallback strategy is documented and tested.
- No production-grade or real-world accuracy claim is made.
