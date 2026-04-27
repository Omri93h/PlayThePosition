# BLOCK 02 — Analysis Board

## Goal
Display a live chessboard from FEN after upload.

## Depends on
BLOCK 01 — Upload Flow

## Features

### 2.1 Analysis page shell
- Large board area.
- Top toolbar.
- Bottom action row.
- Responsive layout foundation.

### 2.2 Static FEN board loading
- Load board from a known static FEN.
- Confirm board library works.

### 2.3 API FEN integration
- Receive FEN from upload response.
- Load that FEN in the board.

### 2.4 Board interactions
- Drag/click moves where supported.
- Keep board responsive.

### 2.5 Board state management
- Current FEN.
- Reset.
- Flip board.
- Controlled board state.

## Done definition
- Upload can lead to an analysis board.
- Board renders reliably from FEN.
- State is controlled and testable.
