# Detection Role-Signal Strategy Contract

This contract defines BLOCK 13 / Feature 13.1 for the approved role-signal fixture strategy and revised role classifier.

It is docs/contract-only. It does not add fixture images, edit fixture metadata, implement classifier code, change `/upload`, change public API contracts, expose product UI, start FEN reconstruction, or claim piece identity recognition or production accuracy.

## Purpose

Make role identity measurable on approved fixtures before FEN reconstruction.

FEN reconstruction needs piece roles, not only occupancy and color. BLOCK 13 must therefore solve or clearly measure the role-signal blocker before BLOCK 14 recognition orchestration and FEN reconstruction can proceed.

## Relationship To BLOCK 12

BLOCK 12 proved:

- Occupancy works on approved fixtures: 167 / 167 sampled occupied, 0 missing, 0 extra.
- Color partially works on approved fixtures: 159 correct, 8 ambiguous, 0 wrong.
- Role remains blocked/deferred.
- Combined role/color success is unavailable.
- Piece identity is not recognized.

BLOCK 13 extends this work by defining how approved fixtures may provide measurable role signal and how a future revised role classifier may use that signal.

## Allowed Inputs

Future BLOCK 13 role-signal work may use:

- approved fixture images
- approved `board_bounds`
- square sampling regions
- sampled visual signatures from fixture pixels
- fixture metadata only for measurement comparison, not classifier decisions

Fixture metadata may answer whether a measured output is correct during tests and reports. It must not be used to choose the detected role.

## Valid Role Signal

A valid role signal must be:

- visual pixel or signature evidence that differs by role
- measurable per square
- separable across all six roles: king, queen, rook, bishop, knight, pawn
- reproducible across the owned approved role-signal fixture set
- derived from approved fixture image data, not metadata or chess knowledge

Signal can be produced by owned/generated fixture markers or owned visual role shapes, but it must remain visible in image pixels and measurable through the approved sampling/audit path.

## Forbidden Shortcuts

Role-signal work must not infer role from:

- FEN
- square identity
- starting-position assumptions
- expected metadata lookup
- filename lookup
- style lookup
- source lookup
- orientation lookup
- chess rules

These shortcuts would measure metadata knowledge, not image-based role signal.

## Output Expectations

Future role classifier rows should emit:

- `detected_role`
- `role_result`
- `confidence`
- `failure_reason`
- `source_stage`

Role result values should remain compatible with prior BLOCK 12 measurement contracts:

- `correct`
- `wrong`
- `missing`
- `extra`
- `not_measured`
- `unsupported`
- `ambiguous`

Confidence is measurement metadata only. It is not a production probability, real-world recognition claim, or user-facing accuracy score.

## Failure Reasons

Initial BLOCK 13 failure reasons may include:

- `ambiguous_role`
- `unsupported_fixture`
- `sample_unavailable`
- `role_signal_not_separable`
- `classifier_not_configured`
- `empty_square`
- `occupancy_missing`

Future features may add narrower reasons when useful, but failures should stay structured, explicit, and safe for reports.

## Non-Success Behavior

Future role-signal and classifier work must return non-success states instead of guessing.

Rules:

- Weak role signal returns `ambiguous`.
- Missing sample data returns `not_measured`.
- Unsupported fixture styles return `unsupported`.
- Empty squares do not receive roles.
- A role is `correct` or `wrong` only when a future classifier produces a role from allowed image signal.

## Later Fixture Governance

New role-signal fixtures are not added in 13.1.

Later fixture work must follow these rules:

- owned/generated fixtures only
- all six roles required
- both colors required
- deterministic generation preferred
- no copied external assets
- no raw user uploads
- no unclear-license screenshots
- metadata and license notes required
- explicit approval required before adding images
- fixture metadata validation must pass before tests depend on fixtures

Fixture design should make role signal measurable without relying on filename, style, position, FEN, or expected metadata.

## Audit V2 Gate

Feature 13.4 fixture signal audit v2 must prove role separability before 13.5 classifier work.

Audit v2 must:

- sample role signal from approved fixture image pixels
- report feasible / ambiguous / unsupported by fixture and style
- confirm all six roles are covered
- report separability thresholds or measured signal distance
- keep expected metadata only for grouping/reporting, not classifier decisions
- block classifier work if role signals remain ambiguous or unsupported

## FEN And Upload Gates

FEN reconstruction remains blocked until role identity is measurable from approved fixture image signal.

Upload/API integration remains blocked until FEN reconstruction is proven internally and explicitly approved.

## 13.1 Result

Feature 13.1 is implemented / ready for review.

BLOCK 13 remains in progress. No fixture images, fixture metadata changes, classifier code, FEN reconstruction, upload/API integration, product UI changes, or production accuracy claims were added.
