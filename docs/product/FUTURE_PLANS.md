# Future Plans — Post-MVP

These remain outside completed BLOCK 11 internal/test-only measurement work unless explicitly moved into scope.

## Future — Detection Accuracy

- BLOCK 07 covers discovery/planning for the path toward real screenshot recognition.
- BLOCK 08 covers the approved recognition-foundation slice only: decode/preprocess boundary, approved fixture validation, gated orchestration, fixture-gated board detection, and fallback/metadata planning.
- BLOCK 09 covers the approved fixture-intake and measurement slice only: approved non-user fixture candidate selection, first approved fixture set after explicit approval, decode/preprocess measurements, board-bounds measurements, and a next-step decision.
- BLOCK 10 covers the approved real-ish fixture measurement slice only: fixture source approval, a tiny approved non-user real-ish fixture set, decode/preprocess measurements, board-bounds measurements, and comparison against BLOCK 09 synthetic-only measurements.
- BLOCK 11 covers internal/test-only occupancy measurement against expected fixture pieces. Role/color piece recognition remains unsupported.
- After BLOCK 11, the next recognition work should move toward an internal/test-only role/color classifier experiment block using approved fixtures only, likely as a future BLOCK 12, only after explicit approval.
- Production-grade real-world screenshot recognition accuracy remains future work until measured and explicitly approved.
- Upload integration for real recognition remains future work until explicitly approved.
- Detection debug/inspection view implementation remains unstarted until approved.

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
