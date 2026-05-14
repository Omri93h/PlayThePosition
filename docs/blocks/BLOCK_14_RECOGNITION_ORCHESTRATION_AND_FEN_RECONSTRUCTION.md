# BLOCK 14 — Recognition Orchestration + FEN Reconstruction

## Status

Complete / accepted after Omri manual validation.

BLOCK 14 must remain approved-fixture-only and internal/test-only until explicitly approved otherwise. It does not start upload/API integration, public UI behavior, real screenshot support, or production accuracy claims.

## Purpose

Turn measured detection outputs into an internal board state and FEN string for approved fixtures.

BLOCK 13 proved role identity is measurable on the owned role-signal fixture set. BLOCK 14 should combine board bounds, square mapping, occupancy, color, role, side-to-move, and orientation into a safe internal FEN reconstruction path.

The FEN must be built from measured outputs. Fixture `expected_fen` is allowed only as test comparison data, never as a reconstruction shortcut.

## Non-goals

- No upload/API integration.
- No public API changes.
- No product UI changes.
- No real screenshot support claim.
- No production-grade recognition claim.
- No raw user uploads.
- No new fixtures or fixture image changes.
- No CV/ML dependency.
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.

## Planned Features

### 14.1 BLOCK 14 definition and recognition orchestration contract
- Status: implemented / ready for review.
- Contract location: `docs/product/DETECTION_RECOGNITION_ORCHESTRATION_CONTRACT.md`.
- Defines the internal recognition pipeline contract: board bounds -> squares -> occupancy -> color -> role -> measured board state -> FEN.
- Defines which upstream outputs are required and which failure states block FEN.
- Confirms `expected_fen` is comparison-only and must not be used to reconstruct FEN.
- Documents the side-to-move source as an explicit 14.4 gap when it is not available outside `expected_fen`.

### 14.2 Internal measured-piece model: combine square, occupancy, color, and role rows
- Status: implemented / ready for review.
- Defines and implements an internal measured-piece representation in `services/api/app/detection/measured_pieces.py`.
- Combines square sampling, color classifier rows, and role classifier rows by fixture and square.
- Preserves source stages, confidence metadata, and failure reasons.
- Keeps unsupported, ambiguous, and not-measured states explicit.
- Does not build FEN.

### 14.2.5 BLOCK 14 failure and FEN evaluation contract
- Status: implemented / ready for review.
- Contract location: `docs/product/DETECTION_FEN_RECONSTRUCTION_EVALUATION_CONTRACT.md`.
- Defines canonical BLOCK 14 failure codes before FEN builder work.
- Defines FEN evaluation/report shape.
- Confirms side to move must come from explicit fixture/test metadata, not `expected_fen`.
- Documents that full six-field FEN comparison is blocked until 14.4 defines side-to-move truth.
- Allows 14.3 to build/compare placement-only FEN if approved.

### 14.3 FEN builder from measured pieces
- Status: implemented / ready for review.
- Implements a placement-only builder in `services/api/app/detection/fen_reconstruction.py`.
- Builds the FEN placement field from measured-piece rows only.
- Emits piece letters from measured role and measured color only.
- Returns structured failure instead of fake or partial placement when required data is missing.
- After 14.3.1 repair, all three owned role-signal fixtures generate placement and match `expected_fen.split()[0]`.
- Full six-field FEN is handled separately in 14.4 and requires explicit side-to-move truth.

### 14.3.1 Role-signal color classifier repair
- Status: implemented / ready for review.
- Repairs owned role-signal color classification by measuring owned marker palette pixels from sampled image data.
- Keeps non-role-signal color classifier behavior unchanged.
- Does not use `expected_fen`, `expected_pieces`, square, fixture id, filename, or style to choose detected colors.
- Result: all three role-signal fixtures classify 36 / 36 occupied-square colors correctly, with 0 wrong and 0 ambiguous.
- Result: all three role-signal fixture placements generate and match `expected_fen.split()[0]`.

### 14.4 Side-to-move and orientation handling
- Status: implemented / ready for review.
- Adds explicit `side_to_move` metadata to approved success fixtures outside `expected_fen`.
- Keeps placement-only reconstruction available.
- Adds guarded full six-field FEN reconstruction only when explicit side-to-move is supplied.
- Uses conservative non-detected FEN placeholders: castling `-`, en passant `-`, halfmove `0`, and fullmove `1`.
- Documents and tests that measured rows already use canonical algebraic squares, so FEN reconstruction must not apply a second orientation transform.
- Confirms black-bottom fixtures require no different FEN behavior after upstream orientation-aware square mapping.

### 14.5 Invalid-board and failure-state handling
- Status: implemented / ready for review.
- Blocks placement-only and full six-field FEN reconstruction for missing white king, missing black king, duplicate white kings, and duplicate black kings.
- Preserves existing row/data failures for missing role/color, unsupported role/color, unsupported fixture, ambiguous data, not-measured rows, and missing/duplicate square rows.
- Keeps side-to-move validation from 14.4 separate and first for full-FEN requests.
- Does not add check/checkmate, impossible-history, castling-rights, en-passant, halfmove/fullmove, engine, or broader legality validation.
- Returns clear failure reasons rather than generated FEN.

### 14.6 Approved-fixture FEN reconstruction tests and readiness report
- Status: implemented / ready for review.
- Adds a durable readiness report at `docs/product/DETECTION_BLOCK_14_FEN_RECONSTRUCTION_READINESS_REPORT.md`.
- Adds a test-only readiness summary assertion for the approved role-signal fixture path.
- Confirms approved role-signal fixtures generate placement and guarded full FEN from measured rows plus explicit `side_to_move` metadata.
- Frames results as approved-fixture internal measurements only.
- Keep upload/API integration and public behavior deferred.

### 14.7 BLOCK 14 closeout review with manual validation checklist
- Status: complete / accepted after Omri manual validation.
- Closeout review location: `docs/product/DETECTION_BLOCK_14_CLOSEOUT_REVIEW.md`.
- Verify all BLOCK 14 features are implemented/documented, checks pass, and scope stayed internal/test-only.
- Include a block-specific manual validation checklist for Omri before final acceptance.

## Orchestration Contract

Feature 14.1 is documented in `docs/product/DETECTION_RECOGNITION_ORCHESTRATION_CONTRACT.md`.

BLOCK 14 should combine:

- approved fixture metadata
- approved `board_bounds`
- orientation-aware square mapping from `square_sampling.py`
- occupancy from square sampling
- color rows from the internal color classifier
- role rows from the internal role classifier
- side-to-move from approved fixture metadata or a test-only input contract

The internal measured-piece model should include:

- fixture id
- square
- occupancy state
- detected color
- detected role
- result categories for occupancy/color/role
- confidence metadata where available
- failure reasons
- source stages

## FEN Rules

FEN placement must be generated from measured rows only:

- white pieces use uppercase FEN letters
- black pieces use lowercase FEN letters
- empty runs are counted rank by rank
- ranks are emitted from rank 8 to rank 1
- files are emitted from file `a` to file `h`
- side-to-move is explicit
- castling, en passant, halfmove, and fullmove are conservative placeholders in 14.4, not detected game-state truth

`expected_fen` may be used only to assert expected test output. It must not be read by the FEN builder or recognition orchestrator as source data for detected pieces.

## Failure Rules

Invalid data should return clear failure states, not fake FEN.

Required failure cases:

- missing white king
- missing black king
- duplicate white kings
- duplicate black kings
- unknown occupied piece
- missing role
- missing color
- unsupported fixture
- ambiguous role or color
- not-measured required square
- invalid side-to-move
- invalid orientation

## Success Gates

BLOCK 14 may close only if:

- FEN reconstruction is generated from measured outputs, not `expected_fen`
- approved role-signal fixtures reconstruct expected FEN internally
- white-bottom and black-bottom orientation handling is tested
- side-to-move handling is explicit
- invalid-board failures are structured and tested
- upload/API integration remains deferred
- public UI behavior remains unchanged
- docs do not claim real screenshot support or production accuracy

## Failure Gates

BLOCK 14 must not move toward upload/API integration if:

- generated FEN depends on `expected_fen`
- role/color/occupancy outputs are missing or ambiguous for required squares
- invalid boards produce fake FEN
- orientation mapping is not proven
- side-to-move is implicit or guessed
- tests only cover one narrow happy path
- docs overclaim beyond approved fixtures

## Completion Criteria

- BLOCK 14 recognition orchestration contract is documented.
- Internal measured-piece model is implemented and tested.
- FEN builder from measured pieces is implemented and tested.
- Side-to-move and orientation handling are implemented and tested.
- Invalid-board failure states are implemented and tested.
- Approved-fixture FEN reconstruction tests and readiness report are complete.
- BLOCK 14 closeout review and manual validation checklist are complete.
- No upload/API behavior, public API contract, UI change, fixture image change, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
