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
- BLOCK 12 — Internal Role/Color Classifier Experiment
- BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier
- BLOCK 14 — Recognition Orchestration + FEN Reconstruction

## Current

- Current focus: BLOCK 15 / Feature 15.5 internal debug inspection view is implemented / ready for review; next work is PLAN ONLY for Feature 15.6.
- Product name: Play That Position.
- Future domain/brand asset: `playthatposition.com`.
- Current development/runtime: localhost only.
- Product positioning: “Play any chess position you find online.”
- Existing Edit mode is the manual correction path after detection; future fallback wording should refer to that workspace rather than a second editor.
- BLOCK 07 is completed as discovery/experiment-only.
- BLOCK 08 is completed as foundation/measurement-gated only.
- BLOCK 09 is completed as fixture intake and measurement-only work.
- BLOCK 10 is completed as approved real-ish fixture intake and measurement-only work.
- BLOCK 11 is completed as internal/test-only piece-recognition measurement work.
- BLOCK 12 is completed as internal/test-only role/color classifier experiment work.
- BLOCK 13 is completed as internal/test-only approved role-signal fixture strategy and revised role-classifier measurement work.
- Feature 13.1 is complete as BLOCK 13 definition and role-signal strategy contract.
- Feature 13.2 is complete as approved fixture role-signal design rules.
- Feature 13.3 is complete as owned/generated role-signal fixture intake.
- Feature 13.4 is complete as fixture signal audit v2 for role separability.
- Feature 13.5 is complete as a revised test-only role classifier experiment.
- Feature 13.6 is complete as the role classifier measurement report and next-step decision.
- Feature 13.7 is complete as BLOCK 13 closeout review.
- BLOCK 14 is completed/accepted as internal/test-only, approved-fixture-only recognition orchestration and FEN reconstruction work.
- Feature 14.1 is implemented / ready for review as BLOCK 14 definition and recognition orchestration contract.
- Feature 14.2 is implemented / ready for review as the internal measured-piece model.
- Feature 14.2.5 is implemented / ready for review as the BLOCK 14 failure and FEN evaluation contract.
- Feature 14.3 is implemented / ready for review as a placement-only FEN builder from measured-piece rows.
- Feature 14.3.1 is implemented / ready for review as a role-signal color classifier repair.
- Feature 14.4 is implemented / ready for review as side-to-move and orientation handling.
- Feature 14.5 is implemented / ready for review as an invalid-board validation boundary.
- Feature 14.6 is implemented / ready for review as the recognition/FEN readiness report.
- Feature 14.7 is complete / accepted after Omri manual validation as the BLOCK 14 closeout review.
- BLOCK 15 is active as upload/API integration behind an internal gate.
- Feature 15.1 is implemented / ready for review as docs-only uploaded image recognition API contract definition.
- Feature 15.2 is implemented / ready for review as backend-only gated `/upload` recognition wiring.
- Feature 15.3 is implemented / ready for review as shared contract and frontend upload result alignment.
- Feature 15.4 is implemented / ready for review as failure fallback through the existing Edit mode / position workspace.
- Feature 15.4.1 is implemented / ready for review as Edit mode correction interaction cleanup.
- Feature 15.5 is implemented / ready for review as a frontend-only internal debug inspection view behind `VITE_INTERNAL_RECOGNITION_DEBUG`.
- Feature 12.1 is complete as the role/color classifier contract.
- Feature 12.2 is complete as fixture signal audit for role/color feasibility.
- Feature 12.3 is complete as test-only color classifier experiment.
- Feature 12.4 is complete as a blocked/deferred role classifier decision.
- Feature 12.5 is complete as role/color measurement tests and report.
- Feature 12.6 is complete as measurement comparison, blockers, and next-step decision.
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

- Plan Feature 15.6 — Internal QA report — only if explicitly approved.
- Keep BLOCK 14 results internal/test-only and approved-fixture-only until later work is approved.
- Keep Feature 15.5 debug inspection frontend-only, upload-derived, and hidden unless `VITE_INTERNAL_RECOGNITION_DEBUG` is explicitly enabled.
- Do not implement the BLOCK 15 internal QA report until Feature 15.6 planning is approved.
- Do not rename UI/header/logo/web metadata, package names, routes, manifests, deploy config, or runtime identifiers until a separate approved rename task.
- Approved roadmap after BLOCK 13 currently runs through BLOCK 17. BLOCK 14 is complete/accepted and remains internal/test-only until later work is approved.
- Keep BLOCK 11 internal/test-only.
- Keep production-grade recognition, engine, legal moves, accounts, payments, external link-out, and SEO deferred unless explicitly moved into scope.
- Keep upload integration and production-grade recognition deferred until explicitly approved.

## Completed In BLOCK 11

- 11.1 BLOCK 11 definition and measurement contract.
- 11.2 Approved fixture expected-piece metadata audit.
- 11.3 Test-only square sampling / piece marker extraction experiment.
- 11.4 Piece-recognition measurement tests and report.
- 11.5 Measurement comparison, blockers, and next-step decision.

## Completed In BLOCK 12

- 12.1 Role/color classifier contract.
- 12.2 Fixture signal audit for role/color feasibility.
- 12.3 Test-only color classifier experiment.
- 12.4 Test-only role classifier experiment as blocked/deferred.
- 12.5 Role/color measurement tests and report.
- 12.6 Measurement comparison, blockers, and next-step decision.

## Planned Roadmap After BLOCK 12

- BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier.
- BLOCK 14 — Recognition Orchestration + FEN Reconstruction.
- BLOCK 15 — Upload/API Integration Behind Internal Gate.
- BLOCK 16 — Board Interaction / Game Mode Fixes.
- BLOCK 17 — User-Facing Analyze Flow Polish.

## Completed In BLOCK 13

- 13.1 BLOCK 13 definition and role-signal strategy contract.
- 13.2 Approved fixture role-signal design rules.
- 13.3 Add owned role-signal fixture set.
- 13.4 Fixture signal audit v2 for role separability.
- 13.5 Revised test-only role classifier experiment.
- 13.6 Role classifier measurement report and next-step decision.
- 13.7 BLOCK 13 closeout review.

## Completed In BLOCK 14

- 14.1 BLOCK 14 definition and recognition orchestration contract — implemented / ready for review.
- 14.2 Internal measured-piece model: combine square, occupancy, color, and role rows — implemented / ready for review.
- 14.2.5 BLOCK 14 failure and FEN evaluation contract — implemented / ready for review.
- 14.3 FEN builder from measured pieces — implemented / ready for review.
- 14.3.1 Role-signal color classifier repair — implemented / ready for review.
- 14.4 Side-to-move and orientation handling — implemented / ready for review.
- 14.5 Invalid-board and failure-state handling — implemented / ready for review.
- 14.6 Approved-fixture FEN reconstruction tests and readiness report — implemented / ready for review.
- 14.7 BLOCK 14 closeout review with manual validation checklist — complete / accepted after Omri manual validation.

## Active In BLOCK 15

- 15.1 Uploaded image recognition API contract behind internal gate — implemented / ready for review as docs-only contract work.
- 15.2 Backend endpoint behind dev/internal flag — implemented / ready for review.
- 15.3 Shared contract and frontend upload result alignment — implemented / ready for review.
- 15.4 Failure fallback through existing Edit mode / position workspace — implemented / ready for review.
- 15.4.1 Edit correction interaction cleanup — implemented / ready for review.
- 15.5 Debug inspection view — implemented / ready for review.
- 15.6 Internal QA report — planned.

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
- Public upload integration for real recognition is not started; internal/dev-gated upload recognition wiring exists behind `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED`.
- PNG/JPEG decode/preprocess exists internally but is not wired into upload.
- Decode/preprocess measurements are complete for the approved synthetic fixture set.
- Fixture-gated board-bounds measurements are complete for the approved synthetic fixture set.
- BLOCK 09 measurement report is complete and recommends adding a small approved non-synthetic or real-ish fixture set before upload integration.
- BLOCK 10 has added a tiny owned/generated real-ish fixture set for future measurement.
- Decode/preprocess measurements are complete for the approved real-ish fixture set.
- Fixture-gated board-bounds measurements are complete for the approved real-ish fixture set.
- Detection orchestrator exists internally behind an explicit disabled-by-default gate and is wired into upload only when `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED` is explicitly enabled.
- Fixture-gated board bounds detection exists internally for generated test images and is not wired into upload.
- Optional detection metadata is implemented behind the internal/dev upload recognition gate and remains absent from default placeholder responses.
- Frontend debug inspection for upload-derived detection metadata is implemented behind `VITE_INTERNAL_RECOGNITION_DEBUG` and remains hidden by default.
- Approved synthetic non-user fixture images and owned/generated real-ish fixture images have been added; approved real screenshot fixtures have not been added.
- Production-grade recognition accuracy work remains deferred.
- Public/product-facing upload recognition claims remain deferred.
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
- BLOCK 12 is complete as internal/test-only role/color classification measurement work against approved fixtures only.
- BLOCK 12 role/color classifier contract is documented.
- BLOCK 12 fixture signal audit is complete: color signal is feasible for a test-only color classifier experiment; role signal remains ambiguous or unsupported.
- BLOCK 12 test-only color classifier experiment is complete: 159 of 167 approved occupied squares classify correctly, with 8 ambiguous rows kept explicit.
- BLOCK 12 role classifier decision is complete: role classification is blocked/deferred on current approved fixtures because role signals are ambiguous or unsupported.
- BLOCK 12 role/color measurement report is complete: occupancy and color are measured on approved fixtures, role remains blocked/deferred, combined role/color success is unavailable, and FEN/upload integration remain blocked.
- BLOCK 12 measurement comparison is complete: occupancy works on approved fixtures, color partially works with 159 correct and 8 ambiguous rows, role remains blocked/deferred, piece identity is not recognized, and FEN/upload integration remain blocked.
- Recommended next technical direction after BLOCK 12 is BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier.
- FEN reconstruction remains internal/test-only until explicitly approved.
- BLOCK 13 owned/generated role-signal fixtures are added, audit v2 finds their role signals separable on approved fixtures, and the test-only role classifier measures 36 / 36 correct role classifications on those controlled fixtures. BLOCK 13 is complete as internal/test-only, approved-fixture-only measurement work. Role identity is still not recognized in product behavior, and FEN/upload remain deferred.
- BLOCK 14 builds FEN from measured outputs only. Fixture `expected_fen` is comparison-only, invalid data returns clear failures, Feature 15.4 adds fallback-to-Edit-mode handling, and Feature 15.5 adds frontend-only internal debug inspection hidden behind `VITE_INTERNAL_RECOGNITION_DEBUG`.
- BLOCK 14 placement-only FEN builder is implemented. After the 14.3.1 role-signal color repair, all three owned role-signal fixtures classify 36 / 36 occupied-square colors correctly and all three generated placements match `expected_fen.split()[0]`. Feature 14.4 adds explicit `side_to_move` fixture metadata and guarded full-FEN reconstruction with conservative placeholder fields for approved fixture tests only. Feature 14.5 blocks placement and full FEN for missing or duplicate white/black kings without adding broad legality validation. Feature 14.6 adds the BLOCK 14 recognition/FEN readiness report and a test-only readiness summary for the approved role-signal path. Feature 14.7 adds BLOCK 14 closeout review and manual validation checklist. BLOCK 14 is complete/accepted as approved-fixture-only internal measurement, not a product accuracy claim.
- BLOCK 15 has backend gated upload recognition wiring and aligned frontend/shared upload result types. Feature 15.1 defines the upload recognition API contract behind an internal/dev gate. Feature 15.2 preserves current `/upload` placeholder/default behavior when `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED` is absent or disabled, and adds additive backend detection metadata only for the enabled internal/dev path. Feature 15.3 aligns shared contract and frontend upload result handling without adding production recognition claims. Feature 15.4 sends placeholder, partial, failed, or absent-detection upload results into the existing Edit Board workspace using top-level `fen` only. Feature 15.4.1 keeps Edit mode correction-focused and leaves Play mode selected-piece/legal-move behavior to BLOCK 16. Feature 15.5 adds frontend-only internal debug inspection for upload-derived detection metadata.

## Later / Deferred

- Keep post-MVP items deferred until explicitly moved into scope.
