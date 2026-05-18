# Current Focus

Current Block/Area:
BLOCK 15 — Upload/API Integration Behind Internal Gate

Current Feature:
Feature 15.5 — Debug inspection view

Current Step:
Feature 15.4.1 is implemented / ready for review. Awaiting approved PLAN ONLY work for Feature 15.5.

Rules:
- Do not start Feature 15.5 implementation without an approved Feature 15.5 plan.
- Do not edit frontend, shared contract code, tests, or fixtures unless a later approved Feature 15.5+ scope explicitly allows it.
- Keep `/upload` placeholder/default behavior when `PLAYTHATPOSITION_INTERNAL_RECOGNITION_ENABLED` is absent or disabled.
- Keep Feature 15.4 fallback behavior: placeholder, partial, failed, or absent detection opens the existing Edit Board workspace from top-level `fen`.
- Keep Feature 15.4.1 correction boundary: Edit mode is correction-only; Play mode selected-piece/legal-move behavior remains deferred.
- Keep BLOCK 14 results internal/test-only and approved-fixture-only until explicitly approved otherwise.
- Do not add CV/ML dependencies yet.
- Do not claim real-world screenshot detection accuracy.
- Do not expose recognition output without an explicit internal/dev gate.
- Do not claim public upload/API/UI readiness.
- Do not add or modify fixture images.
- Do not start engine, legal moves, auth/accounts, payments, link-out, or SEO.
