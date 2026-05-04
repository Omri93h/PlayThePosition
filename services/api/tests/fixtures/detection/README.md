# Detection Fixtures

This directory holds lightweight metadata for detection tests. Current fixtures are synthetic and generated in test code. Do not commit generated binary images for these cases.

## Folder Strategy

- `cases.json` is the active synthetic manifest used by current tests.
- `cases.example.json` documents the future approved-fixture metadata shape.
- `approved/` is the only future tracked location for approved screenshot fixtures.
- `approved/cases.json` is the active approved-fixture manifest.
  It is intentionally empty until screenshots are explicitly approved.
- `raw/`, `large/`, and archive dumps are local-only and ignored by git.
- Do not commit real screenshot images outside `approved/`.

## Naming

Use:

```text
source_style_orientation_case.ext
```

Example:

```text
lichess-like_default_white-bottom_start-01.png
```

Use concise values for:

- `source`: `synthetic`, `chesscom-like`, `lichess-like`, or another approved source label.
- `style`: `default`, `green`, `brown`, `minimal`, or another concise style label.
- `orientation`: `white-bottom`, `black-bottom`, or `unknown`.
- `case`: short scenario plus sequence, such as `start-01`, `middlegame-01`, or `noboard-01`.

## Approval And Licensing

- Prefer synthetic or hand-created fixtures first.
- Real screenshots may be added only as a small curated set after approval.
- Use screenshots that are owned, licensed, public-domain, generated with approval, or explicitly permitted.
- Include a licensing/approval note for every fixture.
- Do not add copyrighted screenshots from chess sites, streams, books, courses, or user submissions without explicit approval.
- Do not store raw user-uploaded screenshots unless explicitly approved.

## Metadata Expectations

Every fixture should include metadata for:

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
- `expected_failure` when the case should fail
- `license`
- `notes`

See `cases.example.json` for the future approved-fixture metadata shape. The existing `cases.json` remains the active synthetic test manifest.

`approved/cases.json` must pass the approved fixture metadata validator before future tests depend on approved screenshots.

Approved success cases require:

- `id`
- `filename`
- `kind`
- `source`
- `style`
- `orientation`: `white-bottom`, `black-bottom`, or `unknown`
- `expected_fen`
- `license.status`
- `license.note`

The validator rejects absolute paths, parent traversal, `raw/`, `large/`, dump/archive paths, and archive files.

## Acceptable Fixture Sources

- Synthetic fixtures generated in test code.
- Hand-created board images where all assets are owned or approved.
- Public-domain or permissively licensed images with a clear source note.
- Small manually approved screenshots only when licensing and privacy are clear.

## Unacceptable Fixture Sources

- Raw user uploads.
- Unapproved screenshots from chess sites, streams, books, courses, or private messages.
- Large raw datasets, archive dumps, or unclear-license images.
- Images with sensitive personal information.

## Local Experiments

Put experimental local/raw data under ignored `raw/` or `large/` folders. Do not commit those files.

Do not place approved fixtures in `raw/` or `large/`; use `approved/` only after explicit approval.
