# BLOCK 05 — Detection Engine

## Goal
Replace mock detection with a real, testable screenshot-to-FEN pipeline.

## Depends on
BLOCK 04 — Share and Link-Out

## Features

### 5.1 Detection pipeline skeleton
- Image preprocessing stage.
- Board detection stage.
- Piece detection stage.
- FEN generation stage.
- Structured failure outputs.

### 5.2 Board grid detection
- Find board region.
- Normalize perspective.
- Split into 8x8 grid.

### 5.3 Piece recognition
- Classify piece per square.
- Empty square detection.

### 5.4 Orientation detection
- Determine board orientation.
- Correct FEN ordering.

### 5.5 FEN generation
- Generate valid FEN.
- Validate FEN before returning.

### 5.6 Detection confidence and failure handling
- Confidence score.
- Failure reason.
- Retry suggestions.

### 5.7 Test dataset
- Sample screenshots.
- Expected FEN outputs.
- Regression tests.

## Done definition
- Real screenshots produce usable FEN often enough for MVP.
- Failures are explicit.
- Detection is testable and debuggable.
