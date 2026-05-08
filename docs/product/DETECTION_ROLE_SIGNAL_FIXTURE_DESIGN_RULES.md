# Detection Role-Signal Fixture Design Rules

Feature 13.2 defines the design rules for future owned role-signal fixtures. It does not add images, edit fixture metadata, implement generator tooling, implement classifier code, start FEN reconstruction, start upload/API integration, or claim piece identity recognition.

## Purpose

BLOCK 12 showed that approved fixtures support occupancy measurement and partial color classification, but role identity remains blocked. BLOCK 13 can only move toward a revised role classifier after fixtures contain visual role signals that are measurable from pixels.

These rules define how future owned role-signal fixtures must be designed before Feature 13.3 adds any images or metadata.

## Role Marker Goals

- Each chess role must have a distinct visual signal.
- The signal must be visible in the fixture pixels, not only described in metadata.
- The signal must be measurable through square sampling and the future audit v2 path.
- The signal must not depend on board square, FEN, expected metadata, filename, source, style, orientation, starting position, or chess rules.
- Weak or ambiguous signal must remain measurable as `ambiguous`, `unsupported`, or `not_measured`; fixtures must not encourage silent guessing.

## Six-Role Marker Rules

Future role-signal fixtures must provide owned marker or shape language for all six roles:

- king
- queen
- rook
- bishop
- knight
- pawn

Marker differences must survive the current square-sampling resolution. Avoid role markers that differ only by tiny details near square edges, very thin strokes, anti-aliased specks, or details likely to disappear when sampled from an inner square region.

Prefer centered or inner-square signal so audit v2 can sample it consistently. Role differences should be present in the main sampled piece/marker area, not only in a corner, border, label, board coordinate, or decorative chrome.

## Color Compatibility

Role markers must preserve the strong white/black separation used by the existing internal color classifier.

- Role marker design must not erase, invert, or hide the color signal.
- Both colors should use the same role-shape logic with color-specific foreground signal.
- Role-specific shapes should remain distinguishable for both white and black pieces.
- Color signal must not be encoded by square color, filename, metadata, source, style, or orientation.

Color compatibility does not imply full piece identity recognition. A fixture can support color measurement while role measurement remains blocked.

## Required Coverage

The future approved role-signal fixture set must include:

- all six roles
- both colors
- multiple board locations
- light and dark board squares where relevant
- at least one dense position that covers all roles
- optional sparse/control positions only as supplemental coverage

Sparse positions are useful for debugging, but they are not sufficient to prove role separability across the full role set.

## Ownership And License Rules

Future role-signal fixtures must be legally safe and controlled.

- Use owned/generated fixtures only.
- Do not copy Chess.com, Lichess, other site screenshots, site UI, or piece assets.
- Do not use raw user uploads.
- Do not use unclear-license screenshots, dumps, archives, datasets, social posts, streams, books, courses, private chats, or third-party game screenshots.
- Prefer deterministic generation so fixture output can be reproduced.
- Record `license.status` and `license.note` before commit.
- Add images only in a later explicitly approved fixture-addition feature.

## Metadata Rules

Future manifest entries for role-signal fixtures must include:

- `id`
- `filename`
- `kind`
- `source`
- `style`
- `orientation`
- `board_bounds`
- `expected_pieces` with `square`, `piece`, and `color`
- `expected_fen` for measurement comparison only
- `expected_metrics` for role-signal audit expectations
- `expected_failure` when relevant
- `license.status`
- `license.note`
- `notes` explaining the fixture purpose

`expected_fen`, `expected_pieces`, and metadata may be used to score measurements. They must not be used by a classifier to decide a role.

## Deterministic Generation Rules

Feature 13.3 should add generator tooling only if explicitly approved. When that happens, generated fixtures should use stable dimensions, board bounds, palettes, marker placement, and output paths.

Generation must not depend on system randomness. If any seed is used, it must be fixed and documented. Fixture output should be reproducible from repository-owned tooling.

## Forbidden Encodings

Role signal must not be encoded by:

- square identity
- metadata or FEN alone
- filename, source, style, or orientation
- starting-position inference
- chess rules
- board coordinates
- hidden labels or off-board UI

The fixture design must not claim production recognition, general screenshot support, real-world screenshot accuracy, FEN reconstruction readiness, upload integration readiness, or piece identity recognition.

## Audit-Readiness Checklist

Before future fixtures can support role classifier work, audit v2 should be able to inspect sampled image signal and report whether each fixture/style is feasible, ambiguous, or unsupported.

A future fixture set should be considered audit-ready only if:

- role markers are visible in sampled inner-square pixels
- all six roles are present
- both colors are present
- role markers remain distinguishable on light and dark squares where relevant
- color signal remains separable
- metadata validates before tests depend on the fixture
- every ambiguous or unsupported signal can be reported honestly

## 13.2 Result

Feature 13.2 is implemented / ready for review as docs/design-rules only.

No fixture images were added. `cases.json` was not changed. No generator tooling, classifier code, FEN reconstruction, upload/API integration, UI behavior, production recognition claim, or piece identity recognition claim was added.
