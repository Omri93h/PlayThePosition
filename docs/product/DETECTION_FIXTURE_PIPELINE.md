# Detection Fixture Pipeline

This document defines the future real screenshot fixture pipeline for BLOCK 07 discovery. No real screenshots are added in 7.3, and this does not implement recognition or claim accuracy.

## Fixture Folder Strategy

- `services/api/tests/fixtures/detection/cases.json`
  - Active synthetic manifest used by current tests.
- `services/api/tests/fixtures/detection/cases.example.json`
  - Example metadata shape for future approved screenshots.
- `services/api/tests/fixtures/detection/approved/`
  - The only future tracked location for approved screenshot fixtures.
  - Contains an active empty `cases.json` manifest and README.
- `services/api/tests/fixtures/detection/raw/`
  - Local-only experiments. Ignored by git.
- `services/api/tests/fixtures/detection/large/`
  - Local-only large data or dataset experiments. Ignored by git.

## Approved Fixture Intake Flow

1. Confirm the fixture is needed for a specific measurement or failure case.
2. Confirm source, license, and approval status.
3. Ensure the image is small, purposeful, and free of personal/sensitive data.
4. Add the image only under `approved/`.
5. Add metadata before using the fixture in tests.
6. Keep the fixture set curated; do not add raw dumps or broad datasets.

## Metadata Requirements

Each approved fixture should include:

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

`cases.example.json` documents the intended shape. The existing `cases.json` remains the active synthetic manifest until a later feature explicitly approves real fixture integration.

## Privacy And Licensing Rules

- Do not store raw user uploads.
- Do not commit large or unclear-license screenshots.
- Do not commit screenshots from chess sites, streams, books, courses, private messages, or user submissions without explicit approval.
- Do not include sensitive personal information.
- Every approved fixture must have a licensing/approval note.

## Validation Strategy

BLOCK 08 adds a lightweight approved-fixture metadata validator. It checks:

- Required metadata fields.
- Referenced image paths resolve under `approved/`.
- Referenced image does not live under `raw/` or `large/`.
- Licensing/approval note is present.
- File size and dimensions are below approved limits when an image file exists and file validation is required.
- Expected FEN, orientation, and failure/confidence fields are present.

The active approved manifest remains empty until real screenshots are explicitly approved.

## Future Test Consumption

Future tests should:

- Keep synthetic tests fast and deterministic.
- Load approved real fixtures only from `approved/`.
- Pair every fixture with expected metadata.
- Report results as measurements, not accuracy claims.
- Keep failures recoverable through Edit Board.

## 7.3 Done Definition

- Fixture folder strategy is documented.
- Approved fixture intake rules are documented.
- `approved/` has a README but no images.
- Local raw/large/archive dumps remain ignored.
- No recognition code, dependencies, real screenshots, or user uploads are added.
