from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.detection.measured_pieces import ALL_SQUARES, MeasuredPieceRow

FEN_FILES = "abcdefgh"
FEN_RANKS = "87654321"

FailureCode = Literal[
    "unsupported_fixture",
    "missing_square_sample",
    "duplicate_square_sample",
    "conflicting_square_rows",
    "not_measured_square",
    "missing_color",
    "missing_role",
    "ambiguous_color",
    "ambiguous_role",
    "unsupported_color",
    "unsupported_role",
    "invalid_orientation",
    "fen_not_generated",
]

ROLE_TO_FEN = {
    "king": "k",
    "queen": "q",
    "rook": "r",
    "bishop": "b",
    "knight": "n",
    "pawn": "p",
}

CANONICAL_FAILURES = {
    "unsupported_fixture": "unsupported_fixture",
    "missing_square_sample": "missing_square_sample",
    "duplicate_square_sample": "duplicate_square_sample",
    "conflicting_square_rows": "conflicting_square_rows",
    "not_measured_square": "not_measured_square",
    "missing_color": "missing_color",
    "missing_color_row": "missing_color",
    "missing_role": "missing_role",
    "missing_role_row": "missing_role",
    "ambiguous_color": "ambiguous_color",
    "ambiguous_role": "ambiguous_role",
    "unsupported_color": "unsupported_color",
    "unsupported_role": "unsupported_role",
    "invalid_orientation": "invalid_orientation",
    "invalid_board_bounds": "not_measured_square",
    "sample_unavailable": "not_measured_square",
}


@dataclass(frozen=True)
class FenPlacementSuccess:
    placement: str
    source: str = "measured_pieces"


@dataclass(frozen=True)
class FenPlacementFailure:
    code: FailureCode
    message: str
    failure_reasons: tuple[str, ...]
    source: str = "measured_pieces"


FenPlacementResult = FenPlacementSuccess | FenPlacementFailure


def build_fen_placement_from_measured_rows(
    rows: Sequence[MeasuredPieceRow],
) -> FenPlacementResult:
    row_index = _index_rows(rows)
    if isinstance(row_index, FenPlacementFailure):
        return row_index

    pieces_by_square: dict[str, str] = {}
    for square in _ordered_squares():
        row = row_index[square]

        if row.row_category == "empty_square":
            continue

        if row.row_category == "unsupported":
            return _failure_for_row(row)

        if row.row_category != "measured_piece":
            return _failure(
                "fen_not_generated",
                f"Unsupported row category: {row.row_category}",
            )

        fen_letter = _fen_letter(row)
        if isinstance(fen_letter, FenPlacementFailure):
            return fen_letter

        pieces_by_square[square] = fen_letter

    return FenPlacementSuccess(_render_placement(pieces_by_square))


def _index_rows(
    rows: Sequence[MeasuredPieceRow],
) -> dict[str, MeasuredPieceRow] | FenPlacementFailure:
    if len(rows) != 64:
        return _failure(
            "missing_square_sample",
            "FEN placement reconstruction requires exactly 64 measured rows.",
        )

    fixture_ids = {row.fixture_id for row in rows}
    if len(fixture_ids) != 1:
        return _failure(
            "conflicting_square_rows",
            "Measured rows must belong to exactly one fixture.",
        )

    indexed: dict[str, MeasuredPieceRow] = {}
    for row in rows:
        if row.square not in ALL_SQUARES:
            return _failure(
                "missing_square_sample",
                f"Measured row has invalid square: {row.square}.",
            )

        if row.square in indexed:
            return _failure(
                "duplicate_square_sample",
                f"Measured rows contain duplicate square: {row.square}.",
            )

        indexed[row.square] = row

    missing = ALL_SQUARES - set(indexed)
    if missing:
        return _failure(
            "missing_square_sample",
            f"Measured rows are missing square: {sorted(missing)[0]}.",
        )

    return indexed


def _fen_letter(row: MeasuredPieceRow) -> str | FenPlacementFailure:
    if row.detected_role is None:
        return _failure("missing_role", f"Measured piece {row.square} has no role.")

    if row.detected_color is None:
        return _failure("missing_color", f"Measured piece {row.square} has no color.")

    role_letter = ROLE_TO_FEN.get(row.detected_role)
    if role_letter is None:
        return _failure(
            "unsupported_role",
            f"Measured piece {row.square} has unsupported role.",
        )

    if row.detected_color == "white":
        return role_letter.upper()

    if row.detected_color == "black":
        return role_letter

    return _failure(
        "unsupported_color",
        f"Measured piece {row.square} has unsupported color.",
    )


def _render_placement(pieces_by_square: dict[str, str]) -> str:
    ranks: list[str] = []
    for rank in FEN_RANKS:
        rendered_rank = ""
        empty_count = 0
        for file in FEN_FILES:
            piece = pieces_by_square.get(f"{file}{rank}")
            if piece is None:
                empty_count += 1
                continue

            if empty_count:
                rendered_rank += str(empty_count)
                empty_count = 0

            rendered_rank += piece

        if empty_count:
            rendered_rank += str(empty_count)

        ranks.append(rendered_rank)

    return "/".join(ranks)


def _failure_for_row(row: MeasuredPieceRow) -> FenPlacementFailure:
    reasons = _split_reasons(row.failure_reason)
    code = _canonical_code(reasons)
    return _failure(
        code,
        f"Measured row {row.square} cannot be used for FEN placement.",
        reasons,
    )


def _split_reasons(reason: str | None) -> tuple[str, ...]:
    if reason is None:
        return ("fen_not_generated",)

    return tuple(part for part in reason.split(";") if part)


def _canonical_code(reasons: tuple[str, ...]) -> FailureCode:
    for reason in reasons:
        mapped = CANONICAL_FAILURES.get(reason)
        if mapped is not None:
            return mapped

    return "fen_not_generated"


def _failure(
    code: FailureCode,
    message: str,
    failure_reasons: tuple[str, ...] | None = None,
) -> FenPlacementFailure:
    return FenPlacementFailure(
        code=code,
        message=message,
        failure_reasons=failure_reasons or (code,),
    )


def _ordered_squares() -> tuple[str, ...]:
    return tuple(f"{file}{rank}" for rank in FEN_RANKS for file in FEN_FILES)
