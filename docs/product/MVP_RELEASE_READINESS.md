# MVP Release Readiness

This checklist is for deciding whether the MVP can be formally closed out. It does not mark the MVP complete by itself.

## Closeout Status

- MVP closeout is approved.
- Final automated validation passed.
- Manual validation was limited/skipped after the final header/play-controls polish.
- This closeout does not claim full production readiness.
- This closeout does not claim real-world screenshot detection accuracy.

## Core MVP Flow Checklist

- [ ] Upload an image from the upload screen.
- [ ] Receive the scaffolded detection result without claiming real-world accuracy.
- [ ] Open the analysis board after upload.
- [ ] Edit the board position.
- [ ] Add pieces.
- [ ] Remove pieces.
- [ ] Move pieces.
- [ ] Change side to move.
- [ ] Reset the board.
- [ ] Flip the board.
- [ ] Copy the current FEN.
- [ ] Create an internal share link.
- [ ] Open a public share page and load the shared position.
- [ ] Validate mobile layout sanity for upload, loading, analysis, edit controls, share, and public share states.

## Automated Checks Before MVP Closeout

- [x] `pnpm --filter web test`
- [x] `pnpm --filter web build`
- [x] `pnpm --filter e2e test`
- [x] `pnpm -r --if-present lint`
- [x] From `services/api`: `./.venv/bin/python -m pytest`
- [x] From `services/api`: `./.venv/bin/python -m ruff check .`
- [x] `git diff --check`
- [x] `git status --short`

## Manual Validation Checklist

- [ ] Upload success feels clear and smooth.
- [ ] Upload validation and network errors are understandable and recoverable.
- [ ] Loading overlay does not imply real detection accuracy.
- [ ] Analysis board is readable on desktop and mobile.
- [ ] Edit Board / Play mode is understandable.
- [ ] Add, remove, move, undo, redo, reset, and flip behave predictably.
- [ ] Side-to-move control is understandable.
- [ ] Copy FEN and internal Share are distinct and usable.
- [ ] Public share error states are understandable.
- [ ] No future-only UI is exposed as available now.

## Manual Validation Fix Pass

- [ ] Revalidate header Upload opens the file picker from analysis and preserves the current board when canceled.
- [ ] Revalidate piece palette color mapping places selected white pieces as white and selected black pieces as black.
- [ ] Revalidate delete tool removes the clicked piece.
- [ ] Revalidate Reset and Flip behave as simple actions without persistent active state.
- [ ] Revalidate share opens a modal without auto-copying.
- [ ] Revalidate share modal readonly link and FEN fields copy their full values.
- [ ] Revalidate black and white piece palette visuals stay clear and selection uses ring/stroke only.
- [ ] Revalidate standalone main FEN action is removed and FEN copy remains available in the Share modal.
- [ ] Revalidate Edit Board mode shows edit tools/pieces as the primary controls.
- [ ] Revalidate header action says New Image and still opens the file picker directly.
- [ ] Revalidate Play mode groups Side to move with Flip and Reset in a compact responsive row.

## Known Limitations

- Detection is scaffolded/synthetic and is not real-world screenshot accurate yet.
- No Stockfish or engine analysis.
- No legal move validation.
- No auth or user accounts.
- No payments, subscriptions, or premium gating.
- No external Chess.com/Lichess link-out.
- No saved collections.

## Release Blockers

- [ ] Any failing required automated check.
- [ ] Any critical upload, analysis board, edit, copy FEN, internal share, or public share flow failure.
- [ ] Any UI copy that claims real-world screenshot detection accuracy.
- [ ] Any accidental exposure of future-only engine, auth, payment, premium, or external link-out features.
- [ ] Any mobile layout issue that blocks core MVP flow usage.

## Deferred Future Work

- Real-world screenshot detection accuracy.
- Engine analysis, Stockfish, legal move dots, and side-to-move legality validation.
- User accounts, saved positions, and collections.
- Payments, premium plans, and gating.
- External Chess.com/Lichess analyzer link-out.
- SEO/growth pages and native/mobile apps.
