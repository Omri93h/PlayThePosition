# BLOCK 05 — Detection Engine

## Goal
Build a testable detection-engine scaffold that can grow into real screenshot-to-FEN detection later.

This block currently delivers synthetic/scaffolded detection boundaries only. Real-world screenshot detection accuracy is deferred to future work.

## Depends on
BLOCK 04 — Share and Link-Out

## Features

### 5.1 Detection pipeline skeleton
- Placeholder pipeline stage.
- Shared placeholder FEN result.
- Structured metadata for future upload integration.

### 5.2 Board grid detection
- Synthetic image/grid boundary.
- Deterministic 8x8 grid detection for controlled fixtures.
- Structured grid failures.

### 5.3 Piece recognition
- Synthetic piece recognition boundary.
- Controlled marker classification only.
- Empty square detection.

### 5.4 Orientation detection
- Synthetic orientation boundary.
- Deterministic `white-bottom`, `black-bottom`, and `unknown` outputs.

### 5.5 FEN generation
- Structured-data-to-FEN generation.
- Orientation-aware board placement.
- Safe default FEN metadata.

### 5.6 Detection confidence and failure handling
- Shared confidence metadata.
- Stable failure codes and messages.
- Retryable flags and suggestions.

### 5.7 Test dataset
- Lightweight synthetic dataset manifest.
- Synthetic fixture generator.
- Expected FEN/orientation metadata.
- Documentation for adding a small curated real screenshot set later.

## Done definition
- Detection boundaries are synthetic/scaffolded and clearly documented as not real-world ready.
- Grid, piece, orientation, FEN, confidence/failure, and dataset boundaries are testable.
- Lightweight synthetic fixtures and expected metadata exist without large binary assets.
- Real-world screenshot detection accuracy remains deferred to future work.
