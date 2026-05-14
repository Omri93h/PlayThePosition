# Blocks Index

## Execution order

1. BLOCK 00 — Foundation
2. BLOCK 01 — Upload Flow
3. BLOCK 02 — Analysis Board
4. BLOCK 03 — Edit Mode
5. BLOCK 03.5 — UX Cleanup
6. BLOCK 04 — Share and Link-Out
7. BLOCK 05 — Detection Engine
8. BLOCK 06 — Polish and Hardening
9. BLOCK 07 — Real Image Recognition Discovery
10. BLOCK 08 — Real Recognition Implementation Foundation
11. BLOCK 09 — Real Recognition Fixture Intake and Measurements
12. BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements
13. BLOCK 11 — Internal Piece-Recognition Measurement Experiments
14. BLOCK 12 — Internal Role/Color Classifier Experiment
15. BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier
16. BLOCK 14 — Recognition Orchestration + FEN Reconstruction
17. BLOCK 15 — Upload/API Integration Behind Internal Gate
18. BLOCK 16 — Board Interaction / Game Mode Fixes
19. BLOCK 17 — User-Facing Analyze Flow Polish

## Status

- BLOCK 06 is completed.
- BLOCK 07 is completed as discovery/experiment-only.
- BLOCK 08 is completed as foundation/measurement-gated only.
- BLOCK 09 is completed as fixture-intake and measurement-only work.
- BLOCK 10 is completed as approved real-ish fixture-intake and measurement-only work.
- BLOCK 11 is completed as internal/test-only piece-recognition measurement work.
- BLOCK 12 is completed as internal/test-only role/color classifier experiment work.
- BLOCK 13 is completed as internal/test-only role-signal strategy and revised role-classifier measurement work.
- BLOCK 14 is completed/accepted as internal/test-only recognition orchestration and FEN reconstruction work.
- BLOCK 15 is active for upload/API integration behind an internal gate. Feature 15.1 is implemented as docs-only contract work; runtime implementation has not started.
- BLOCK 16 is planned for board interaction and game-mode fixes.
- BLOCK 17 is planned for user-facing analyze flow polish.
- Current step is awaiting approved Feature 15.2 planning.
- BLOCK 14 must build FEN from measured outputs, not `expected_fen`; invalid measured data must return clear failure states.
- BLOCK 15 must preserve placeholder/default upload behavior unless an explicit internal/dev gate is enabled by later approved implementation.

## Rules
- Work block-by-block.
- Complete the current feature before starting the next one.
- Do not turn fixture measurements into production detection claims without explicit approval.
- Do not build upload integration, engine, legal moves, auth/accounts, payments, premium link-out, or SEO without explicit approval.
