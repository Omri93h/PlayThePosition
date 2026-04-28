# BLOCK 04 — Share and Link-Out

## Goal
Make the position useful outside the app.

## Depends on
BLOCK 03 — Edit Mode

## Features

### 4.1 Copy FEN
- One-click copy.
- Success/error state.
- Free fallback for external analysis workflows.

### 4.2 Chess.com / Lichess analyzer link planning
- External analyzer link-out is planned.
- Link-out may be premium-gated.
- Do not add payment, auth, or enforcement in this block unless explicitly approved later.
- Do not implement live external links until the gating decision is finalized.

### 4.3 Share link backend
- Save minimal position state.
- Return unique share URL.

### 4.4 Public position page
- Load position from share URL.
- Render board from saved FEN.

### 4.5 Share UI
- Copy share link.
- Share button state.
- Clean success feedback.

## Done definition
- User can copy FEN.
- External analyzer link-out direction is documented without premature payment/auth work.
- User can share a working position link.
