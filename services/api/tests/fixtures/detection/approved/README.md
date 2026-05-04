# Approved Detection Fixtures

This folder is reserved for future approved screenshot fixtures.

No images are added in 7.3 or 8.2.

`cases.json` is the active approved-fixture manifest. It is valid and empty until screenshots are explicitly approved.

## Rules For Future Images

- Add screenshots here only after explicit approval.
- Do not add raw user uploads.
- Do not add large datasets, archive dumps, or unclear-license images.
- Do not add screenshots from chess sites, streams, books, courses, private messages, or user submissions without explicit approval.
- Keep each fixture small and purposeful.
- Include expected metadata before using a fixture in tests.
- Ensure the metadata validator passes before future tests depend on an approved screenshot.

## Required Metadata

Each future approved fixture must include:

- source and style
- orientation
- board bounds if known
- expected pieces
- expected FEN
- expected success/failure metrics
- licensing/approval note
- privacy note when relevant

Use `../cases.example.json` as the metadata shape reference. The active synthetic test manifest remains `../cases.json`.

Approved success cases must include:

- `id`
- `filename`
- `kind`
- `source`
- `style`
- `orientation`
- `expected_fen`
- `license.status`
- `license.note`

Paths must stay under this `approved/` directory and must not use parent traversal, `raw/`, `large/`, dump/archive folders, or archive files.

## Privacy / Licensing Checklist

- The image is owned, public-domain, permissively licensed, generated with approval, or explicitly permitted.
- The image contains no sensitive personal information.
- The image is not a raw user upload.
- The image is not part of a large or uncurated dataset.
- The metadata includes a clear approval/licensing note.
