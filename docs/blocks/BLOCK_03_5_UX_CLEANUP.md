# BLOCK 03.5 — UX Cleanup

## Goal
Tighten the upload and edit-mode experience after manual validation before moving into share/link-out work.

## Depends on
BLOCK 03 — Edit Mode

## Features

### 3.5.1 Full dropzone click target
- Make the full image upload dropzone clickable.
- Keep upload limited to image files only.

### 3.5.2 Hide edit controls when edit mode is inactive
- Keep the analysis view calmer outside edit mode.
- Reveal edit-specific controls only when edit mode is active.

### 3.5.3 Visual chess piece palette
- Replace text-only piece codes with a clearer visual chess piece palette.
- Keep the palette compact and simple.

### 3.5.4 Icon-based action controls
- Use clear icons for common board/edit actions where appropriate.
- Keep accessible labels for icon controls.

### 3.5.5 Selected-square highlight
- Highlight the selected square during edit interactions.
- Keep the highlight subtle and consistent with the dark-first design direction.

### 3.5.6 Remove temporary upload/analysis demo toggle when flow allows
- Remove the local demo toggle once the upload-to-analysis flow is sufficient.
- Avoid introducing routing as part of this cleanup unless separately scoped.

### 3.5.7 Improve edit mode visual board state
- Make edit mode feel visually distinct from regular analysis.
- Clarify active edit sub-modes without cluttering the board.

## Done definition
- Upload and edit-mode controls feel clear and polished.
- Image upload remains the only supported upload type.
- Cleanup does not add share, detection, engine, account, or storage features.
