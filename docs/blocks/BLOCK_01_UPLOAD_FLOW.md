# BLOCK 01 — Upload Flow

## Goal
Allow the user to upload a chess screenshot and send it to the backend safely.

## Depends on
BLOCK 00 — Foundation

## Features

### 1.1 Upload screen UI
- Centered dropzone.
- Click to upload.
- Drag-and-drop.
- Simple, clean layout.

### 1.2 Upload UI states
- Idle.
- Dragging.
- Loading.
- Error.
- Retry.

### 1.3 Upload API endpoint
- `POST /upload`.
- Accept image file.
- Return placeholder FEN initially.

### 1.4 Upload validation and error handling
- Reject invalid file types.
- Reject oversized files.
- Handle corrupted images.
- Return structured errors.

### 1.5 Frontend-backend upload wiring
- Send file to API.
- Handle success.
- Handle failure.
- Prepare navigation to analysis page.

## Done definition
- Valid image uploads succeed.
- Invalid uploads fail cleanly.
- Frontend states are covered.
- Tests exist for happy and failure paths.
