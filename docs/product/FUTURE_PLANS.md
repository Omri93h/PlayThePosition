# Future Plans — Post-MVP

These remain outside the currently active BLOCK 12 / 12.1 planning step unless explicitly moved into scope.

## Future — Detection Accuracy

- BLOCK 07 covers discovery/planning for the path toward real screenshot recognition.
- BLOCK 08 covers the approved recognition-foundation slice only: decode/preprocess boundary, approved fixture validation, gated orchestration, fixture-gated board detection, and fallback/metadata planning.
- BLOCK 09 covers the approved fixture-intake and measurement slice only: approved non-user fixture candidate selection, first approved fixture set after explicit approval, decode/preprocess measurements, board-bounds measurements, and a next-step decision.
- BLOCK 10 covers the approved real-ish fixture measurement slice only: fixture source approval, a tiny approved non-user real-ish fixture set, decode/preprocess measurements, board-bounds measurements, and comparison against BLOCK 09 synthetic-only measurements.
- BLOCK 11 covers internal/test-only occupancy measurement against expected fixture pieces. Role/color piece recognition remains unsupported.
- BLOCK 12 covers the planned internal/test-only role/color classifier experiment using approved fixtures only. Upload/API integration remains deferred.
- BLOCK 13 is planned for recognition orchestration and FEN reconstruction: board bounds → squares → occupancy → role/color → FEN.
- BLOCK 14 is planned for upload/API integration behind an internal/dev gate only after approved-fixture FEN reconstruction works.
- BLOCK 15 is planned for board interaction and game mode fixes.
- BLOCK 16 is planned for user-facing analyze flow polish.
- Production-grade real-world screenshot recognition accuracy remains future work until measured and explicitly approved.
- Upload integration for real recognition remains future work until explicitly approved.
- Detection debug/inspection view implementation remains unstarted until approved.

## Approved Roadmap — BLOCKS 12–16

### BLOCK 12 — Internal Role/Color Classifier Experiment

Goal: make piece recognition detect piece color and role on approved fixtures only.

- 12.1 Role/color classifier contract.
- 12.2 Fixture signal audit.
- 12.3 Color classifier experiment.
- 12.4 Role classifier experiment.
- 12.5 Role/color measurement report.
- 12.6 Closeout / next-step decision.

Gate: if role/color cannot be identified reliably on controlled fixtures, do not start upload/API integration.

### BLOCK 13 — Recognition Orchestration + FEN Reconstruction

Goal: turn detection outputs into internal board state and FEN.

- 13.1 Recognition pipeline contract: board bounds → squares → occupancy → role/color → FEN.
- 13.2 Internal FEN builder from measured pieces.
- 13.3 Side-to-move integration.
- 13.4 Error states: missing king, duplicate kings, invalid board, unknown pieces.
- 13.5 Internal tests against approved fixtures.
- 13.6 Report: FEN reconstruction readiness.

Gate: must generate correct FEN from approved fixtures before upload integration.

### BLOCK 14 — Upload/API Integration Behind Internal Gate

Goal: connect uploaded image → recognition result behind an internal/dev gate.

- 14.1 API contract for uploaded image recognition.
- 14.2 Backend endpoint behind dev/internal flag.
- 14.3 Frontend upload flow uses backend result.
- 14.4 Failure fallback: manual board/edit mode.
- 14.5 Debug inspection view showing detected board bounds, detected pieces, confidence/failure reasons, and generated FEN.
- 14.6 Internal QA report.

Gate: if real uploaded screenshots fail badly, keep it internal and improve detection.

### BLOCK 15 — Board Interaction / Game Mode Fixes

Goal: make the board usable after loading/editing.

- 15.1 Define Play/Edit/Analyze mode behavior.
- 15.2 Allow legal piece movement in game mode.
- 15.3 Show legal moves when selecting a piece.
- 15.4 Handle captures, promotion, castling, and en passant if needed.
- 15.5 Board state sync with FEN.
- 15.6 Tests for legal move UI behavior.

Gate: user can load/edit a position and actually play from it.

### BLOCK 16 — User-Facing Analyze Flow Polish

Goal: make the core user journey feel like a real product.

- 16.1 Upload → detected board → review/edit → analyze flow.
- 16.2 Clear route/path after upload, for example `/position/:id`, not subdomain.
- 16.3 Logo click goes home/upload.
- 16.4 Fix logo/header polish.
- 16.5 Chess.com analyze link behavior.
- 16.6 Shareable result page / preview basics.

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
