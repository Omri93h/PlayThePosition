# Detection Role-Signal Audit V2

Feature 13.4 adds an internal/test-only audit for the owned role-signal fixtures added in 13.3.

This audit is approved-fixture-only and measurement-only. It does not implement a role classifier, change fixture images, change `cases.json`, start FEN reconstruction, start upload/API integration, expose UI behavior, or claim production or real-world screenshot accuracy.

## Purpose

BLOCK 12 showed that occupancy works on approved fixtures and color classification partially works, but role identity was blocked because the previous fixture signals were ambiguous or unsupported.

Audit v2 checks whether the new owned `role-signal` fixtures make role identity separable from sampled fixture pixels before any revised role classifier is implemented.

## Fixture Set

Audit v2 gates only approved fixtures where `expected_metrics.role_signal_fixture == true`:

| Fixture | Orientation | Occupied squares | Result |
| --- | --- | ---: | --- |
| `owned_role-signal_white-bottom_dense-01` | `white-bottom` | 12 | feasible |
| `owned_role-signal_black-bottom_dense-01` | `black-bottom` | 12 | feasible |
| `owned_role-signal_white-bottom_shifted-01` | `white-bottom` | 12 | feasible |

Legacy synthetic and real-ish fixtures may remain useful as comparison context, but they do not block the 13.5 gate.

## What Is Measured

Audit v2 measures role-signal separability from sampled image pixels:

- approved fixture image pixels
- approved `board_bounds`
- derived square regions
- sampled shape signatures from each expected occupied square

Expected metadata is used only to group and score measured samples by known role. It is not used as a classifier decision, and it must not be used by future classifier work to choose a detected role.

Audit v2 compares all six roles:

- king
- queen
- rook
- bishop
- knight
- pawn

## Method

For each expected occupied square, audit v2 builds a shape signature from a fixed 24 by 24 grid sampled inside the square. Each grid point records whether the sampled pixel differs from the local square background by the configured foreground threshold.

Role separability is feasible when:

- all six roles are observed
- every expected occupied square has a measured signature
- each role has enough samples for comparison
- every sample's nearest same-role signal is separated from its nearest other-role signal by the configured margin
- no role pair is ambiguous

Weak signal returns `ambiguous`; missing coverage or samples returns `unsupported`.

## Results

Aggregate role-signal audit v2 result:

| Metric | Result |
| --- | ---: |
| Role-signal fixtures audited | 3 |
| Expected occupied squares | 36 |
| Measured role-signal samples | 36 |
| Roles observed | 6 |
| Minimum separation margin | 0.1406 |
| Minimum pairwise role distance | 0.1406 |
| Ambiguous role pairs | 0 |
| Aggregate status | feasible |

Closest measured role pairs:

| Role pair | Distance |
| --- | ---: |
| bishop / knight | 0.1406 |
| knight / pawn | 0.1441 |
| king / bishop | 0.1701 |
| queen / rook | 0.1736 |
| bishop / pawn | 0.1910 |

## Decision

Audit v2 finds the owned role-signal fixture set feasible for a revised internal/test-only role classifier experiment.

Feature 13.5 may proceed only within the approved BLOCK 13 boundaries:

- approved fixtures only
- internal/test-only
- sampled image signal only
- no FEN, square identity, filename, starting-position, expected-metadata, or chess-rule shortcuts
- explicit `ambiguous`, `unsupported`, or `not_measured` outcomes instead of guesses

## Limitations

- Results apply only to the three owned/generated role-signal fixtures.
- This does not prove role recognition on existing legacy fixtures, real screenshots, uploads, camera photos, overlays, third-party boards, or production traffic.
- This does not implement a role classifier.
- This does not produce FEN.
- This does not change `/upload`, public API behavior, or UI behavior.
- This does not claim piece identity recognition works for users.

## 13.4 Result

Feature 13.4 is implemented / ready for review.

BLOCK 13 closeout review is complete. Feature 13.5 is implemented in `docs/product/DETECTION_ROLE_CLASSIFIER_EXPERIMENT.md`, and BLOCK 13 is closed as internal/test-only, approved-fixture-only measurement work.
