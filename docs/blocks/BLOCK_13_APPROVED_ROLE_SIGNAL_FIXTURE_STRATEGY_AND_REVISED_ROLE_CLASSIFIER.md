# BLOCK 13 — Approved Role-Signal Fixture Strategy and Revised Role Classifier

## Status

Planned as the current intermediate recognition block before FEN reconstruction.

BLOCK 13 must remain internal/test-only, approved-fixture-only, and measurement-only until explicitly approved otherwise.

## Purpose

Create an internal/test-only path to make role identity measurable on approved fixtures without cheating from FEN, square identity, expected metadata, filenames, starting positions, or chess rules.

BLOCK 12 proved that occupancy works on approved fixtures and color classification partially works, but role identity is not measurable yet. FEN reconstruction remains blocked because FEN needs piece roles, not only occupancy and color.

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

## Planned Features

### 13.1 BLOCK 13 definition and role-signal strategy contract
- Status: planned.
- Define the role-signal strategy, classifier boundaries, allowed signals, forbidden shortcuts, and measurement contract before any role classifier implementation.
- Keep FEN reconstruction and upload/API integration deferred.

### 13.2 Approved fixture role-signal design rules
- Status: planned.
- Define owned fixture design rules that encode role-specific visual signal without copying external site assets.
- Require all six roles, both colors, clear licensing/ownership notes, and metadata validation.
- Keep fixture additions out of scope until explicitly approved.

### 13.3 Add owned role-signal fixture set
- Status: planned.
- Add a small owned/generated approved fixture set only after explicit approval.
- Use deterministic fixture generation or owned assets only.
- Do not use raw user uploads, copied Chess.com/Lichess screenshots, unclear-license assets, or large datasets.

### 13.4 Fixture signal audit v2 for role separability
- Status: planned.
- Audit the role-signal fixture set using sampled image signal only.
- Decide whether role signals are feasible, ambiguous, or unsupported before classifier work.
- Do not infer role from expected metadata, FEN, square identity, starting position, filename, style, or chess rules.

### 13.5 Revised test-only role classifier experiment
- Status: planned.
- Implement a role classifier only if audit v2 proves role separability from sampled image signal.
- Return `unsupported`, `ambiguous`, or `not_measured` instead of guessing.
- Keep the existing color classifier separate unless a focused compatibility change is approved.

### 13.6 Role classifier measurement report and next-step decision
- Status: planned.
- Report role measurement results, combined role/color status, blockers, and whether FEN reconstruction can resume later.
- Frame results as fixture measurements, not production accuracy.

### 13.7 BLOCK 13 closeout review
- Status: planned.
- Verify all BLOCK 13 features are implemented/documented, scope stayed internal/test-only, and FEN/upload remained deferred.
- Close the block only if checks pass and next-step decision is documented.

## Strategy

BLOCK 13 should combine three steps carefully:

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

FEN reconstruction may only be reconsidered after BLOCK 13 if:

- owned role-signal fixtures are approved and metadata-valid
- all six roles and both colors are covered
- audit v2 shows role separability from sampled image signal
- role classifier measurements produce role output without forbidden shortcuts
- ambiguous and unsupported rows remain explicit
- combined role/color identity is measurable on approved fixtures
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
- No FEN reconstruction, upload behavior, public API contract, UI change, unapproved fixture image, production accuracy claim, engine, legal moves, auth, payments, external link-out, or SEO work is added.
