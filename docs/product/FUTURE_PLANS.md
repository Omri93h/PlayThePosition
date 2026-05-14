# Future Plans — Post-MVP

These remain outside the currently active BLOCK 14 planning track unless explicitly moved into scope.

Product name: Play That Position.

Future domain/brand asset: `playthatposition.com`.

Current development/runtime: localhost only.

Product positioning: “Play any chess position you find online.”

Image recognition is a means to reach the product goal: a live, editable chess position the user can review, correct, play from, copy, share, or open in an analyzer. Detection work should continue to support that positioning without treating recognition itself as the product.

## Future — Detection Accuracy

- BLOCK 07 covers discovery/planning for the path toward real screenshot recognition.
- BLOCK 08 covers the approved recognition-foundation slice only: decode/preprocess boundary, approved fixture validation, gated orchestration, fixture-gated board detection, and fallback/metadata planning.
- BLOCK 09 covers the approved fixture-intake and measurement slice only: approved non-user fixture candidate selection, first approved fixture set after explicit approval, decode/preprocess measurements, board-bounds measurements, and a next-step decision.
- BLOCK 10 covers the approved real-ish fixture measurement slice only: fixture source approval, a tiny approved non-user real-ish fixture set, decode/preprocess measurements, board-bounds measurements, and comparison against BLOCK 09 synthetic-only measurements.
- BLOCK 11 covers internal/test-only occupancy measurement against expected fixture pieces. Role/color piece recognition remains unsupported.
- BLOCK 12 covers the completed internal/test-only role/color classifier experiment using approved fixtures only. Current results show occupancy works on approved fixtures, color partially works, role remains blocked/deferred, and upload/API integration remains deferred.
- BLOCK 13 is complete as approved role-signal fixture strategy and revised role-classifier measurement work before FEN reconstruction.
- BLOCK 14 is complete/accepted for recognition orchestration and FEN reconstruction: board bounds → squares → occupancy → role/color → FEN. It remains internal/test-only and approved-fixture-only until explicitly approved otherwise.
- BLOCK 15 is planned for upload/API integration behind an internal/dev gate only after explicit BLOCK 15 planning.
- A future internal Recognition Review Studio / Detection Training Console should come after there is an internal recognition/FEN pipeline worth reviewing and before public upload launch.
- BLOCK 16 is planned for board interaction and game mode fixes.
- BLOCK 17 is planned for user-facing analyze flow polish.
- Production-grade real-world screenshot recognition accuracy remains future work until measured and explicitly approved.
- Upload integration for real recognition remains future work until explicitly approved.
- Detection debug/inspection view implementation remains unstarted until approved.

## Approved Roadmap — BLOCKS 12–17

### BLOCK 12 — Internal Role/Color Classifier Experiment

Goal: make piece recognition detect piece color and role on approved fixtures only.

- 12.1 Role/color classifier contract.
- 12.2 Fixture signal audit.
- 12.3 Color classifier experiment.
- 12.4 Role classifier experiment.
- 12.5 Role/color measurement report.
- 12.6 Closeout / next-step decision.

Gate: if role/color cannot be identified reliably on controlled fixtures, do not start FEN reconstruction or upload/API integration.

### BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier

Goal: make role identity measurable on approved fixtures before FEN reconstruction.

- 13.1 BLOCK 13 definition and role-signal strategy contract.
- 13.2 Approved fixture role-signal design rules.
- 13.3 Add owned role-signal fixture set.
- 13.4 Fixture signal audit v2 for role separability.
- 13.5 Revised test-only role classifier experiment.
- 13.6 Role classifier measurement report and next-step decision.
- 13.7 BLOCK 13 closeout review.

Gate: BLOCK 13 is complete as internal/test-only measurement work. FEN reconstruction may be planned next, but implementation must stay approved-fixture-only and internal/test-only until explicitly approved.

### BLOCK 14 — Recognition Orchestration + FEN Reconstruction

Goal: turn measured detection outputs into internal board state and FEN on approved fixtures first.

- 14.1 Recognition pipeline contract: board bounds → squares → occupancy → role/color → FEN.
- 14.2 Internal measured-piece model: combine square, occupancy, color, and role rows.
- 14.3 FEN builder from measured pieces.
- 14.4 Side-to-move and orientation handling.
- 14.5 Invalid-board and failure-state handling.
- 14.6 Approved-fixture FEN reconstruction tests and readiness report.
- 14.7 BLOCK 14 closeout review with manual validation checklist.

Gate: must generate correct FEN from measured outputs on approved fixtures before upload integration. FEN must be built from measured outputs, not fixture `expected_fen`; `expected_fen` is comparison-only. Invalid measured data must return clear failure states, not fake FEN. Upload/API integration and public UI behavior remain deferred until BLOCK 15 planning is explicitly approved.

### BLOCK 15 — Upload/API Integration Behind Internal Gate

Goal: connect uploaded image → recognition result behind an internal/dev gate.

- 15.1 API contract for uploaded image recognition.
- 15.2 Backend endpoint behind dev/internal flag.
- 15.3 Frontend upload flow uses backend result.
- 15.4 Failure fallback: use the existing Edit mode / position workspace for manual correction; do not build a second editor.
- 15.5 Debug inspection view showing detected board bounds, detected pieces, confidence/failure reasons, and generated FEN.
- 15.6 Internal QA report.

Gate: if real uploaded screenshots fail badly, keep it internal and improve detection.

### Future Internal Tooling — Recognition Review Studio / Detection Training Console

Purpose: create an internal/admin-only tool for reviewing recognition results and collecting corrected labeled examples.

This is not ML training at first and is not immediate active work. The initial goal is review, correction, labeling, QA data collection, and clearer failure analysis. Actual training or model improvement may come later only after enough labeled samples exist and data/privacy rules are defined.

Future capabilities:

- Upload chess screenshots and non-chess screenshots.
- Show detection result:
  - board found / not found
  - detected board bounds
  - detected pieces
  - generated FEN if available
  - confidence/failure reasons
- Allow Omri to mark:
  - correct result
  - wrong board crop
  - wrong piece
  - wrong color
  - missing piece
  - extra piece
  - not a chessboard
  - unusable screenshot
- Save corrected labels as internal dataset samples.

Placement and guardrails:

- Future internal tooling block only.
- Does not interrupt the active roadmap block.
- Should come after an internal recognition/FEN pipeline exists and is worth reviewing.
- Should come before public upload launch.
- Should complement the existing Edit mode / position workspace, not replace it with a second editor.
- Must remain internal/admin-only until privacy, storage, retention, consent, and dataset rules are defined.
- Must not claim production accuracy or public recognition readiness.

### BLOCK 16 — Board Interaction / Game Mode Fixes

Goal: make the board usable after loading/editing.

- 16.1 Define Play/Edit/Analyze mode behavior.
- 16.2 Allow legal piece movement in game mode.
- 16.3 Show legal moves when selecting a piece.
- 16.4 Handle captures, promotion, castling, and en passant if needed.
- 16.5 Board state sync with FEN.
- 16.6 Tests for legal move UI behavior.

Gate: user can load/edit a position and actually play from it.

### BLOCK 17 — User-Facing Analyze Flow Polish

Goal: make the core user journey feel like a real product.

- 17.1 Upload → detected board → review/edit → analyze flow.
- 17.2 Clear route/path after upload, for example `/position/:id`, not subdomain.
- 17.3 Logo click goes home/upload.
- 17.4 Fix logo/header polish.
- 17.5 Chess.com analyze link behavior.
- 17.6 Shareable result page / preview basics.

Gate: user can upload, fix mistakes, move pieces, analyze, and share.

## Phase 2 — Accounts and Saved Work

- User accounts.
- Save positions.
- Private collections.
- Public collections.
- Collection sharing.

## Phase 3 — Engine Analysis

- Analysis mode with legal move dots.
- Play mode legal moves should select a piece on first click or press.
- The selected square should receive a stroke/highlight.
- Legal destination squares should be shown for the selected piece.
- Clicking or pressing the same selected square should cancel selection.
- Clicking or pressing a legal destination should move the selected piece.
- Future implementation should use frontend chess rules such as `chess.js` or an equivalent approved library.
- Validate side-to-move legality for positions where check state constrains whose turn it can be.
- Engine bar / Stockfish.
- Best move.
- Candidate lines.
- Engine settings.

## Phase 3.5 — User Settings and Customization

- Board colors.
- Theme.
- Light/dark mode.
- Maybe piece style.
- Other visual preferences later.

## Future — UI Polish Backlog

- Side-to-move, Flip, and Reset must be visually aligned in the same row in Play mode.
- Rename UI/header/logo/web metadata from Play The Position to Play That Position in a later approved branding/UI task.
- Update favicon/app icon/social preview assets only in a later approved asset task.
- Keep package names, repo paths, routes, manifests, and runtime/deploy config unchanged until a separate approved technical rename/deploy task.

## Phase 4 — SEO and Growth

- Footer/trust/legal/launch pages:
  - About.
  - How It Works.
  - FAQ.
  - Privacy Policy.
  - Terms of Use.
  - Contact.
- Homepage demo video/GIF.
- Feedback popup.
- Public indexed position pages.
- Programmatic SEO pages.
- Puzzle/position collections.
- Share previews for social platforms.
- Growth loops around chess communities.

## Phase 5 — Monetization

- Ads and compliance pages.
- Premium-gated external analysis links to Chess.com and Lichess.
- Finalize whether external analyzer link-out is free, premium, or partially gated.
- Keep Copy FEN as the free fallback if live external analyzer links are gated.
- Pro tier.
- Unlimited analysis or saves.
- Advanced edit/detection tools.
- Premium engine features.

## Later — Native and Mobile Apps

- Future mobile app.
- Native iOS app.
- Native Android app.
- Mobile-specific workflows beyond the responsive MVP web app.

## Rule

Do not implement future plans unless explicitly moved into an approved block/feature.

## Explicitly Deferred

- Monetization.
- Login.
- Subscriptions.
- Ads.
- SEO pages.
- Public launch.
- Heavy Stockfish engine work.
- Broad branding redesign.
