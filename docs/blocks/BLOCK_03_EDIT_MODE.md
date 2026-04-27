# BLOCK 03 — Edit Mode

## Goal
Allow users to manually correct imperfect detection results.

## Depends on
BLOCK 02 — Analysis Board

## Features

### 3.1 Edit mode toggle
- Enter/exit edit mode.
- Clear visual indication when active.

### 3.2 Free piece movement
- Move any piece to any square.
- No legality enforcement in edit mode.

### 3.3 Remove pieces
- Delete piece from square.
- Simple interaction.

### 3.4 Add pieces
- Piece palette.
- Place selected piece on board.

### 3.5 Undo/redo
- Undo edit actions.
- Redo edit actions.

### 3.6 Board metadata editing
- Side to move.
- Board orientation.
- Castling rights can be postponed if needed.

## Done definition
- User can fix any incorrect board manually.
- Edit mode is obvious.
- Updated board state produces valid FEN.
