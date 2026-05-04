# Detection Fixture Intake Checklist

This checklist governs BLOCK 09 fixture intake. It is planning/intake guidance only; no image file may be committed until explicitly approved with metadata and licensing.

## Fixture Approval Checklist

A fixture candidate is eligible only if all of these are true:

- It is non-user.
- It is not a raw user upload.
- It is owned, generated, hand-created, public-domain, permissively licensed, or explicitly approved.
- It is a small curated single case, not a dump, dataset, or archive.
- It is a clean 2D digital board screenshot.
- The full board is visible.
- It has no rotation, perspective skew, camera artifacts, major occlusion, overlays, arrows, dialogs, or glare.
- It is desktop-first; mobile candidates are later.
- Source, style, and orientation are known.
- Expected FEN is known before commit.
- Licensing/approval note is written before commit.
- Privacy is reviewed and no personal/sensitive data is present.
- Filename follows `source_style_orientation_case.ext`.
- Metadata validator passes before tests depend on the fixture.

## First Candidate Set Proposal

Start with four images only after explicit approval in a later step:

- `synthetic_default_white-bottom_start-01.png`
- `synthetic_default_black-bottom_start-01.png`
- `lichess-like_default_white-bottom_middlegame-01.png`
- `chesscom-like_default_white-bottom_middlegame-01.png`

If external-style screenshots are not cleanly approved/licensed, replace them with owned hand-created approximations.

## Required Metadata

Every approved fixture needs:

- `id`
- `filename`
- `kind`
- `source`
- `style`
- `orientation`
- `board_bounds` if known
- `expected_pieces`
- `expected_fen`
- `expected_metrics`
- `expected_failure` when relevant
- `license.status`
- `license.note`
- `notes`

## Explicit Approval Rule

No image file may be committed until it is explicitly approved with complete metadata and licensing.
