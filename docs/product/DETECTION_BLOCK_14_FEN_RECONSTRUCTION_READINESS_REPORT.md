# Detection BLOCK 14 FEN Reconstruction Readiness Report

Feature 14.6 records the current BLOCK 14 recognition/FEN readiness state after Features 14.1 through 14.5.

This report is internal/test-only and approved-fixture-only. It does not change upload/API behavior, expose product UI behavior, claim real screenshot support, or claim production recognition accuracy.

## BLOCK 14 Summary

Completed BLOCK 14 work through Feature 14.5:

- 14.1 documented the recognition orchestration contract.
- 14.2 implemented measured-piece rows that combine square, occupancy, color, and role outputs.
- 14.2.5 documented canonical FEN failure and evaluation rules.
- 14.3 implemented placement-only FEN reconstruction from measured rows.
- 14.3.1 repaired role-signal color classification for the owned role-signal fixtures.
- 14.4 added explicit `side_to_move` metadata, guarded full-FEN reconstruction, and orientation tests.
- 14.5 added the invalid-board validation boundary for missing or duplicate kings.

## Readiness Result

The current ready path is limited to the three owned/generated `role-signal` fixtures.

| Metric | Result |
| --- | ---: |
| Approved manifest cases | 11 |
| Role-signal fixtures covered | 3 |
| White-bottom role-signal fixtures | 2 |
| Black-bottom role-signal fixtures | 1 |
| Measured rows covered | 192 |
| Measured pieces covered | 36 |
| Empty squares covered | 156 |
| Unsupported rows in role-signal readiness path | 0 |
| Placement FEN generations | 3 / 3 |
| Placement matches against `expected_fen.split()[0]` | 3 / 3 |
| Guarded full-FEN generations | 3 / 3 |
| Full-FEN matches against `expected_fen` | 3 / 3 |

`expected_fen` is used only as comparison output in tests and this report. It is not used to choose detected pieces, side to move, orientation, or recovery behavior.

`expected_pieces` remains scoring/test truth only. It must not be used as classifier, builder, or readiness-reporting input.

## What Is Ready

- Measured-piece rows can represent all 64 squares for the approved role-signal fixture set.
- Placement-only FEN can be generated from measured rows for the approved role-signal fixture set.
- Guarded full six-field FEN can be generated for the approved role-signal fixture set when explicit `side_to_move` metadata exists.
- White-bottom and black-bottom role-signal fixtures are covered.
- Invalid measured rows return structured failures instead of fake FEN.

## What Is Guarded

- Full six-field FEN generation requires explicit `side_to_move` metadata outside `expected_fen`.
- Missing or invalid `side_to_move` blocks full-FEN reconstruction.
- Missing white king, missing black king, duplicate white kings, and duplicate black kings block placement-only and full-FEN reconstruction.
- Row/data failures keep precedence before board-state validation.
- FEN reconstruction does not apply a second board transform because measured rows already use canonical algebraic squares.

## Full-FEN Placeholder Boundary

Full FEN currently uses these conservative fields:

- castling: `-`
- en passant: `-`
- halfmove: `0`
- fullmove: `1`

These values are placeholders only. They are not detected game-state truth.

## Orientation Boundary

Orientation handling happens before FEN reconstruction. Square sampling produces canonical algebraic squares for measured rows.

Therefore, black-bottom fixtures require no special FEN behavior once measured rows are built. FEN reconstruction must not flip or rotate rows again.

## Known Blockers

- Non-role-signal approved fixtures remain outside the current FEN-ready path because current role classification is unsupported for them.
- Real screenshots are not supported.
- Upload/API integration is not started.
- Public UI behavior is unchanged.
- Production recognition accuracy is not claimed.
- Broad chess legality validation is not implemented.
- Check/checkmate legality, impossible move history, castling-rights detection, en-passant detection, halfmove/fullmove truth, and engine analysis remain out of scope.

## Test Coverage

Feature 14.6 adds a test-only readiness summary assertion in `services/api/tests/test_detection_fen_reconstruction.py`.

That test verifies:

- role-signal fixture coverage is present
- both orientations are represented
- explicit side-to-move metadata exists and is the full-FEN source
- role-signal fixtures generate placement FEN
- role-signal fixtures generate guarded full FEN
- generated placement/full FEN compare successfully against fixture expectations
- the full-FEN placeholder fields remain `- - 0 1`
- the measured row totals match the current approved role-signal fixture set

Existing 14.5 tests continue to cover invalid-board guard behavior.

## Decision

Feature 14.6 supports moving to Feature 14.7, the BLOCK 14 closeout review with a manual validation checklist.

BLOCK 14 must remain internal/test-only and approved-fixture-only until closeout review is complete and a later feature explicitly approves upload/API integration.
