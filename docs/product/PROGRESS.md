# Progress

## Completed

- BLOCK 00 — Foundation
- BLOCK 01 — Upload Flow
- BLOCK 02 — Analysis Board
- BLOCK 03 — Edit Mode
- BLOCK 03.5 — UX Cleanup
- BLOCK 04 — Share and Link-Out
- BLOCK 04.5 — Mobile / Layout Polish
- BLOCK 05 — Detection Engine
- BLOCK 06 — Polish and Hardening
- BLOCK 07 — Real Image Recognition Discovery
- BLOCK 08 — Real Recognition Implementation Foundation
- BLOCK 09 — Real Recognition Fixture Intake and Measurements
- BLOCK 10 — Approved Real-Ish Fixture Intake and Measurements
- BLOCK 11 — Internal Piece-Recognition Measurement Experiments

## Current

- Current focus: BLOCK 12 — Internal Role/Color Classifier Experiment, Feature 12.1 implemented / ready for review.
- BLOCK 07 is completed as discovery/experiment-only.
- BLOCK 08 is completed as foundation/measurement-gated only.
- BLOCK 09 is completed as fixture intake and measurement-only work.
- BLOCK 10 is completed as approved real-ish fixture intake and measurement-only work.
- BLOCK 11 is completed as internal/test-only piece-recognition measurement work.
- BLOCK 12 is in progress as internal/test-only role/color classifier experiment work.
- Feature 12.1 is implemented / ready for review as the role/color classifier contract.
- Feature 12.2 is planned as fixture signal audit for role/color feasibility.
- Feature 12.3 is planned as test-only color classifier experiment.
- Feature 12.4 is planned as test-only role classifier experiment.
- Feature 12.5 is planned as role/color measurement tests and report.
- Feature 12.6 is planned as closeout / next-step decision.
- Feature 11.1 is complete as BLOCK 11 definition and measurement contract.
- Feature 11.2 is complete as approved fixture expected-piece metadata audit.
- Feature 11.3 is complete as test-only square sampling / piece marker extraction experiment.
- Feature 11.4 is complete as piece-recognition measurement tests and report.
- Feature 11.5 is complete as measurement comparison, blockers, and next-step decision.
- Feature 10.1 is complete/committed as docs-only fixture source approval and candidate selection.
- Feature 10.2 is complete/committed as fixture/test tooling with four owned/generated real-ish fixtures and approved metadata.
- Feature 10.3 is complete/committed as decode/preprocess measurements on the owned/generated real-ish fixture set.
- Feature 10.4 is complete/committed as fixture-gated board-bounds measurements on the owned/generated real-ish fixture set.
- Feature 10.5 is complete as measurement comparison report and next-step decision.
- Real image recognition implementation has not started.
- MVP hardening/polish is complete.
- MVP readiness automated validation passed.
- MVP is closed.
- MVP closeout is approved.

## Completed In BLOCK 07

- 7.1 Discovery/spec and fixture strategy.
- 7.2 Detection debug/inspection UI design.
- 7.3 Real screenshot fixture pipeline.
- 7.4 Board detection experiment as synthetic/control PPM only.
- 7.5 Piece recognition experiment as synthetic/control markers only.
- 7.6 Confidence/failure UX as backend metadata standardization and docs only.
- 7.7 Integration plan for replacing scaffolded detection as docs/planning only.

## Completed In BLOCK 08

- 8.1 PNG/JPEG decode and preprocess boundary.
- 8.2 Approved fixture metadata validation.
- 8.3 Detection orchestrator behind feature gate.
- 8.4 Fixture-gated board detection path.
- 8.5 Fallback/metadata contract planning.

## MVP Readiness

- MVP release-readiness checklist is created.
- Manual validation feedback fixes are implemented.
- Final automated validation passed.
- MVP is closed.
- MVP closeout is approved.
- Closeout does not claim full production readiness or real-world screenshot detection accuracy.

## Completed In BLOCK 06

- 6.1 Loading UX
- 6.2 Error UX
- 6.3 Mobile layout
- 6.4 Observability/logs
- 6.5 Analytics events
- 6.6 Performance cleanup
- 6.7 Analysis page UX cleanup
- 6.8 Analysis page manual validation fixes

## Next

- Review Feature 12.1 — Role/color classifier contract.
- Next planned feature is 12.2 — Fixture signal audit for role/color feasibility.
- Keep BLOCK 12 internal/test-only and approved-fixture-only.
- Approved roadmap after BLOCK 12 runs through BLOCK 16: recognition orchestration/FEN reconstruction, internally gated upload/API integration, board interaction/game mode fixes, and user-facing analyze flow polish.
- Keep BLOCK 11 internal/test-only.
- Keep production-grade recognition, engine, legal moves, accounts, payments, external link-out, and SEO deferred unless explicitly moved into scope.
- Keep upload integration and production-grade recognition deferred until explicitly approved.

## Completed In BLOCK 11

- 11.1 BLOCK 11 definition and measurement contract.
- 11.2 Approved fixture expected-piece metadata audit.
- 11.3 Test-only square sampling / piece marker extraction experiment.
- 11.4 Piece-recognition measurement tests and report.
- 11.5 Measurement comparison, blockers, and next-step decision.

## Planned In BLOCK 12

- 12.1 Role/color classifier contract — implemented / ready for review.
- 12.2 Fixture signal audit for role/color feasibility — planned.
- 12.3 Test-only color classifier experiment — planned.
- 12.4 Test-only role classifier experiment — planned.
- 12.5 Role/color measurement tests and report — planned.
- 12.6 Closeout / next-step decision — planned.

## Planned Roadmap After BLOCK 12

- BLOCK 13 — Recognition Orchestration + FEN Reconstruction.
- BLOCK 14 — Upload/API Integration Behind Internal Gate.
- BLOCK 15 — Board Interaction / Game Mode Fixes.
- BLOCK 16 — User-Facing Analyze Flow Polish.

## Completed In BLOCK 10

- 10.1 Fixture source approval and candidate selection — complete/committed.
- 10.2 Add first approved real-ish non-user fixture set — complete/committed.
- 10.3 Run decode/preprocess measurements on real-ish fixtures — complete/committed.
- 10.4 Run board-bounds measurements on real-ish fixtures — complete/committed.
- 10.5 Measurement comparison report and next-step decision — complete.

## Completed In BLOCK 09

- 9.1 Approved fixture intake checklist and first candidate selection.
- 9.2 Add first approved non-user fixture set.
- 9.3 Run decode/preprocess measurements on approved fixtures.
- 9.4 Run fixture-gated board-bounds measurements.
- 9.5 Measurement report and next-step decision.

## Known MVP Limitations

- Detection is scaffolded/synthetic and is not real-world screenshot accurate yet.
- Real recognition implementation is not started.
- Upload integration for real recognition is not started.
- PNG/JPEG decode/preprocess exists internally but is not wired into upload.
- Decode/preprocess measurements are complete for the approved synthetic fixture set.
- Fixture-gated board-bounds measurements are complete for the approved synthetic fixture set.
- BLOCK 09 measurement report is complete and recommends adding a small approved non-synthetic or real-ish fixture set before upload integration.
- BLOCK 10 has added a tiny owned/generated real-ish fixture set for future measurement.
- Decode/preprocess measurements are complete for the approved real-ish fixture set.
- Fixture-gated board-bounds measurements are complete for the approved real-ish fixture set.
- Detection orchestrator exists internally behind an explicit disabled-by-default gate and is not wired into upload.
- Fixture-gated board bounds detection exists internally for generated test images and is not wired into upload.
- Future optional detection metadata contract is documented only; `/upload` does not return it yet.
- Approved synthetic non-user fixture images and owned/generated real-ish fixture images have been added; approved real screenshot fixtures have not been added.
- Production-grade recognition accuracy work remains deferred.
- Upload integration remains deferred.
- Public API changes for real recognition remain deferred.
- No engine or Stockfish analysis.
- No legal move validation.
- No auth or user accounts.
- No payments, subscriptions, or premium gating.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.
- BLOCK 10 measurement comparison and next-step decision are complete.
- BLOCK 10 is complete as approved real-ish fixture-intake and measurement-only work.
- Recommended next technical direction after BLOCK 10 is a future piece-recognition measurement/experiment block using approved fixtures only.
- BLOCK 11 piece-recognition measurement currently measures occupancy only; role/color recognition remains unsupported and not measured.
- BLOCK 11 measurement comparison recommends a future internal/test-only role/color classifier experiment block before any upload/API integration.
- BLOCK 11 is complete as internal/test-only measurement work.
- BLOCK 12 is in progress to explore role/color classification internally against approved fixtures only.
- BLOCK 12 role/color classifier contract is documented; classifier implementation has not started.

## Later / Deferred

- Keep post-MVP items deferred until explicitly moved into scope.
