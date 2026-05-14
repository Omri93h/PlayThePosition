from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.detection.measured_pieces import ALL_SQUARES, MeasuredPieceRow

FEN_FILES = "abcdefgh"
FEN_RANKS = "87654321"
CONSERVATIVE_CASTLING = "-"
CONSERVATIVE_EN_PASSANT = "-"
CONSERVATIVE_HALFMOVE = 0
CONSERVATIVE_FULLMOVE = 1

ActiveColor = Literal["w", "b"]

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
    "missing_white_king",
    "missing_black_king",
    "duplicate_white_king",
    "duplicate_black_king",
    "missing_side_to_move",
    "invalid_side_to_move",
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


@dataclass(frozen=True)
class FenReconstructionSuccess:
    fen: str
    placement: str
    side_to_move: ActiveColor
    castling: str = CONSERVATIVE_CASTLING
    en_passant: str = CONSERVATIVE_EN_PASSANT
    halfmove: int = CONSERVATIVE_HALFMOVE
    fullmove: int = CONSERVATIVE_FULLMOVE
    source: str = "measured_pieces"


FenReconstructionResult = FenReconstructionSuccess | FenPlacementFailure


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

    board_state = _validate_board_state(row_index)
    if isinstance(board_state, FenPlacementFailure):
        return board_state

    return FenPlacementSuccess(_render_placement(pieces_by_square))


def build_full_fen_from_measured_rows(
    rows: Sequence[MeasuredPieceRow],
    *,
    side_to_move: str | None,
) -> FenReconstructionResult:
    active_color = _validate_side_to_move(side_to_move)
    if isinstance(active_color, FenPlacementFailure):
        return active_color

    placement_result = build_fen_placement_from_measured_rows(rows)
    if isinstance(placement_result, FenPlacementFailure):
        return placement_result

    return FenReconstructionSuccess(
        fen=(
            f"{placement_result.placement} {active_color} {CONSERVATIVE_CASTLING} "
            f"{CONSERVATIVE_EN_PASSANT} {CONSERVATIVE_HALFMOVE} "
            f"{CONSERVATIVE_FULLMOVE}"
        ),
        placement=placement_result.placement,
        side_to_move=active_color,
    )


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


def _validate_side_to_move(
    side_to_move: str | None,
) -> ActiveColor | FenPlacementFailure:
    if side_to_move is None:
        return _failure(
            "missing_side_to_move",
            "Full FEN reconstruction requires explicit side-to-move metadata.",
        )

    if side_to_move in ("w", "b"):
        return side_to_move

    return _failure(
        "invalid_side_to_move",
        "Side-to-move metadata must be w or b.",
    )


def _validate_board_state(
    row_index: dict[str, MeasuredPieceRow],
) -> None | FenPlacementFailure:
    white_king_count = _king_count(row_index, "white")
    black_king_count = _king_count(row_index, "black")

    if white_king_count == 0:
        return _failure(
            "missing_white_king",
            "FEN reconstruction requires exactly one measured white king.",
        )

    if black_king_count == 0:
        return _failure(
            "missing_black_king",
            "FEN reconstruction requires exactly one measured black king.",
        )

    if white_king_count > 1:
        return _failure(
            "duplicate_white_king",
            "FEN reconstruction found multiple measured white kings.",
        )

    if black_king_count > 1:
        return _failure(
            "duplicate_black_king",
            "FEN reconstruction found multiple measured black kings.",
        )

    return None


def _king_count(row_index: dict[str, MeasuredPieceRow], color: str) -> int:
    return sum(
        1
        for row in row_index.values()
        if row.row_category == "measured_piece"
        and row.detected_role == "king"
        and row.detected_color == color
    )


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
