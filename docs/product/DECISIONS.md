# Decisions

- Product name is Play That Position.
- Future domain/brand asset is `playthatposition.com`; current development/runtime remains localhost only until deploy/domain work is separately approved.
- Product input is image upload only for MVP.
- TXT/FEN upload is not part of current scope.
- Detection remains placeholder-only until BLOCK 05.
- Edit Mode is for correcting board positions after upload/detection.
- Manual correction fallback means using the existing Edit Mode / position workspace, not building a second editor.
- Analysis Mode with legal move dots is future work.
- Manual validation after BLOCK 03 created BLOCK 03.5 UX Cleanup before BLOCK 04.
- External analyzer link-out to Chess.com and Lichess is planned and may be premium-gated.
- Do not implement live external links until the gating decision is finalized.
- Copy FEN remains the free fallback for external analysis workflows.
- Do not implement payment or link-out before the relevant approved block.
- BLOCK 04 must account for link-out gating instead of assuming external analysis links are free.
- Do not build engine, share, accounts, or storage features before their blocks.
