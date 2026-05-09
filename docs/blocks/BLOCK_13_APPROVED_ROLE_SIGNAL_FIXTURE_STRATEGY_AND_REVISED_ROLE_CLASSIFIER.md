# BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier

## Status

Completed as internal/test-only, approved-fixture-only role-signal and role-classifier measurement work.

BLOCK 13 remained internal/test-only, approved-fixture-only, and measurement-only. It did not start FEN reconstruction, upload/API integration, product UI behavior, or production/general screenshot recognition.

## Purpose

Create an internal/test-only path to make role identity measurable on approved fixtures without cheating from FEN, square identity, expected metadata, filenames, starting positions, or chess rules.

BLOCK 12 proved that occupancy works on approved fixtures and color classification partially works, but role identity was not measurable yet. FEN reconstruction remained blocked because FEN needs piece roles, not only occupancy and color. BLOCK 13 measures role identity on owned role-signal fixtures only before any FEN reconstruction work can be reconsidered.

## Non-goals

- No FEN reconstruction.
- No upload integration.
- No public API changes.
- No product UI changes.
- No production-grade recognition claim.
- No real-world screenshot accuracy claim.
- No raw user uploads.
- No unapproved fixture images.
- No fixture image changes outside a later explicitly approved role-signal fixture feature.
- No template matching, broad image-feature classifier, CV/ML dependency, or heavy recognition stack unless a later approved plan changes direction.
- No engine or Stockfish work.
- No legal move display or legal move validation.
- No auth or user accounts.
- No payments, premium gating, or subscriptions.
- No external Chess.com/Lichess link-out.
- No SEO or distribution work.

## Features

### 13.1 BLOCK 13 definition and role-signal strategy contract
- Status: implemented / ready for review.
- Defines the role-signal strategy, classifier boundaries, allowed signals, forbidden shortcuts, and measurement contract in `docs/product/DETECTION_ROLE_SIGNAL_STRATEGY_CONTRACT.md`.
- Keep FEN reconstruction and upload/API integration deferred.

### 13.2 Approved fixture role-signal design rules
- Status: implemented / ready for review.
- Defines owned fixture design rules in `docs/product/DETECTION_ROLE_SIGNAL_FIXTURE_DESIGN_RULES.md`.
- Requires role-specific visual signal for all six roles, both colors, clear licensing/ownership notes, and metadata validation.
- Keeps fixture images, manifest updates, generator tooling, and classifier code out of scope until explicitly approved.
- Keep fixture additions out of scope until explicitly approved.

### 13.3 Add owned role-signal fixture set
- Status: implemented / ready for review.
- Adds three owned/generated role-signal fixtures under `services/api/tests/fixtures/detection/approved/`.
- Adds deterministic fixture tooling in `tooling/scripts/generate_role_signal_detection_fixtures.py`.
- Updates `cases.json` additively with role-signal fixture metadata, owned license notes, expected pieces, expected FEN, and role-signal audit metrics.
- Does not alter existing approved fixture images, implement audit v2, implement role classifier code, start FEN reconstruction, or start upload/API integration.

### 13.4 Fixture signal audit v2 for role separability
- Status: implemented / ready for review.
- Adds audit v2 in `services/api/app/detection/role_signal_audit_v2.py`.
- Audits only the three owned `role-signal` fixtures for the 13.5 gate.
- Measures sampled image shape signatures only; expected metadata is used for grouping/scoring, not classifier decisions.
- Documents results in `docs/product/DETECTION_ROLE_SIGNAL_AUDIT_V2.md`: 3 fixtures, 36 occupied squares, 36 measured role-signal samples, all six roles observed, aggregate status feasible, minimum separation margin 0.1406, and no ambiguous role pairs.
- Does not implement role classifier code, infer role from forbidden shortcuts, start FEN reconstruction, start upload/API integration, or claim production recognition.

### 13.5 Revised test-only role classifier experiment
- Status: implemented / ready for review.
- Adds the internal/test-only classifier in `services/api/app/detection/role_classifier.py`.
- Classifies only occupied squares in approved role-signal fixtures using sampled image signatures from audit v2.
- Keeps expected metadata scoring-only; focused tests tamper with expected role metadata and confirm `detected_role` still follows the sampled marker shape.
- Documents results in `docs/product/DETECTION_ROLE_CLASSIFIER_EXPERIMENT.md`: 3 fixtures, 36 occupied squares, 36 detected role rows, 36 correct role classifications, 0 wrong, 0 ambiguous, 0 unsupported, and 0 not measured.
- Keeps the color classifier separate and unchanged.
- Does not change fixtures, start FEN reconstruction, start upload/API integration, expose UI behavior, or claim production/general screenshot recognition.

### 13.6 Role classifier measurement report and next-step decision
- Status: implemented / ready for review.
- Documents the BLOCK 13 measurement decision in `docs/product/DETECTION_BLOCK_13_ROLE_CLASSIFIER_MEASUREMENT_REPORT.md`.
- Reports the 13.4 audit v2 result: 3 owned role-signal fixtures, 36 measured role-signal samples, all six roles observed, aggregate status feasible, minimum separation margin 0.1406, and no ambiguous role pairs.
- Reports the 13.5 role classifier result: 3 role-signal fixtures, 36 occupied role-signal squares, 36 correct role classifications, 0 wrong, 0 ambiguous, 0 unsupported, and 0 not measured.
- Keeps results limited to owned/generated role-signal fixtures only.
- Keeps the color classifier separate and unchanged.
- Records that FEN reconstruction should not start inside 13.6 and can be reconsidered only after BLOCK 13 closeout confirms the gates and docs are clean.
- Keeps upload/API integration deferred.

### 13.7 BLOCK 13 closeout review
- Status: complete.
- Verified all BLOCK 13 features are implemented/documented, scope stayed internal/test-only, and FEN/upload remained deferred.
- Verified the owned role-signal fixture set, audit v2, role classifier result, and 13.6 measurement report.
- Closed BLOCK 13 as approved-fixture-only measurement work and set the next state to BLOCK 14 planning only.

## Strategy

BLOCK 13 combined three steps carefully:

- Improve approved fixture role markers/signals first.
- Generate a small owned approved role-signal fixture set designed for role separability.
- Revise the role classifier only after audit v2 proves roles are separable from sampled image signal.

Allowed role signals:

- approved fixture images
- approved `board_bounds`
- square sampling regions
- sampled visual signatures from fixture pixels

Forbidden shortcuts:

- expected metadata lookup as a classifier
- FEN inference
- square identity inference
- starting-position assumptions
- chess rules
- filename, source, style, or orientation lookup

Template matching, broad image-feature classifiers, CV/ML dependencies, or production-recognition approaches are out of scope unless a later approved plan explicitly changes direction.

## Success Gates

FEN reconstruction may be planned next as an internal/test-only approved-fixture step because BLOCK 13 closeout confirms:

- owned role-signal fixtures are approved and metadata-valid
- all six roles and both colors are covered
- audit v2 shows role separability from sampled image signal
- role classifier measurements produce role output without forbidden shortcuts
- ambiguous and unsupported rows remain explicit
- role results are limited to owned/generated role-signal fixtures only
- existing color classifier work remains separate and unchanged
- reports avoid production or real-world accuracy claims

## Failure Gates

FEN reconstruction must remain blocked if:

- role signals remain ambiguous or unsupported
- role output depends on FEN, square identity, expected metadata, filename, source, style, starting position, or chess rules
- role classification only works on sparse or narrow fixture cases
- combined role/color identity remains unavailable
- upload/API integration would require unproven recognition behavior

## Completion Criteria

- BLOCK 13 role-signal strategy contract is documented.
- Approved fixture role-signal design rules are documented.
- Owned role-signal fixtures are added only after explicit approval, or the block records why fixture addition is blocked.
- Fixture signal audit v2 is documented.
- Revised role classifier experiment is measured or clearly blocked.
- Role classifier measurement report and next-step decision are documented.
- BLOCK 13 closeout review is complete.
- No FEN reconstruction, upload behavior, public API contract, UI change, unapproved fixture image, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
