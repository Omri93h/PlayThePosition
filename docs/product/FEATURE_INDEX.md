# Feature Index

## BLOCK 00 — Foundation

- 0.1 Monorepo bootstrap
- 0.2 Frontend setup
- 0.3 Backend setup
- 0.4 Contracts setup
- 0.5 Testing setup
- 0.6 Quality tooling setup

## BLOCK 01 — Upload Flow

- 1.1 Upload screen UI
- 1.2 Upload UI states
- 1.3 Upload API endpoint
- 1.4 Upload validation and error handling
- 1.5 Frontend-backend upload wiring

## BLOCK 02 — Analysis Board

- 2.1 Analysis page shell
- 2.2 Static FEN board loading
- 2.3 API FEN integration
- 2.4 Board interactions
- 2.5 Board state management

## BLOCK 03 — Edit Mode

- 3.1 Edit mode toggle
- 3.2 Free piece movement
- 3.3 Remove pieces
- 3.4 Add pieces
- 3.5 Undo/redo
- 3.6 Board metadata editing

## BLOCK 03.5 — UX Cleanup

- 3.5.1 Full dropzone click target
- 3.5.2 Hide edit controls when edit mode is inactive
- 3.5.3 Visual chess piece palette
- 3.5.4 Icon-based action controls
- 3.5.5 Selected-square highlight
- 3.5.6 Remove temporary upload/analysis demo toggle when flow allows
- 3.5.7 Improve edit mode visual board state

## BLOCK 04 — Share and Link-Out

- 4.1 Copy FEN
- 4.2 Chess.com / Lichess analyzer link planning
- 4.3 Share link backend
- 4.4 Public position page
- 4.5 Share UI

## BLOCK 04.5 — Mobile / Layout Polish

- 4.5.1 Mobile-first analysis controls polish
- 4.5.2 Board and action controls polish

## BLOCK 05 — Detection Engine

- 5.1 Detection pipeline skeleton
- 5.2 Board grid detection
- 5.3 Piece recognition
- 5.4 Orientation detection
- 5.5 FEN generation
- 5.6 Detection confidence and failure handling
- 5.7 Test dataset

## BLOCK 06 — Polish and Hardening

- 6.1 Loading UX
- 6.2 Error UX
- 6.3 Mobile layout
- 6.4 Observability/logs
- 6.5 Analytics events
- 6.6 Performance cleanup
- 6.7 Analysis page UX cleanup
- 6.8 Analysis page manual validation fixes

## BLOCK 07 — Real Image Recognition Discovery

- Status: complete.
- 7.1 Discovery/spec and fixture strategy — complete
- 7.2 Detection debug/inspection UI design — complete
- 7.3 Real screenshot fixture pipeline — complete
- 7.4 Board detection experiment — complete
- 7.5 Piece recognition experiment — complete
- 7.6 Confidence/failure UX — complete
- 7.7 Integration plan for replacing scaffolded detection — complete

## BLOCK 08 — Real Recognition Implementation Foundation

- Status: complete.
- 8.1 PNG/JPEG decode and preprocess boundary — complete
- 8.2 Approved fixture metadata validation — complete
- 8.3 Detection orchestrator behind feature gate — complete
- 8.4 Fixture-gated board detection path — complete
- 8.5 Fallback/metadata contract planning — complete

## BLOCK 09 — Real Recognition Fixture Intake and Measurements

- Status: complete.
- 9.1 Approved fixture intake checklist and first candidate selection — complete
- 9.2 Add first approved non-user fixture set — complete
- 9.3 Run decode/preprocess measurements on approved fixtures — complete
- 9.4 Run fixture-gated board-bounds measurements — complete
- 9.5 Measurement report and next-step decision — complete

## BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements

- Status: complete.
- 10.1 Fixture source approval and candidate selection — complete
- 10.2 Add first approved real-ish non-user fixture set — complete
- 10.3 Run decode/preprocess measurements on real-ish fixtures — complete
- 10.4 Run board-bounds measurements on real-ish fixtures — complete
- 10.5 Measurement comparison report and next-step decision — complete

## BLOCK 11 — Internal Piece-Recognition Measurement Experiments

- Status: planned.
- 11.1 BLOCK 11 definition and measurement contract — implemented / ready for review
- 11.2 Approved fixture expected-piece metadata audit — implemented / ready for review
- 11.3 Test-only square sampling / piece marker extraction experiment — implemented / ready for review
- 11.4 Piece-recognition measurement tests and report — planned
- 11.5 Measurement comparison, blockers, and next-step decision — planned
