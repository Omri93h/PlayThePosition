from dataclasses import dataclass
from typing import Literal

from app.detection.orientation import BoardOrientation
from app.detection.pieces import SquareRecognition

ActiveColor = Literal["w", "b"]


@dataclass(frozen=True)
class FenMetadata:
    active_color: ActiveColor = "w"
    castling: str = "-"
    en_passant: str = "-"
    halfmove: int = 0
    fullmove: int = 1


@dataclass(frozen=True)
class FenGenerationSuccess:
    fen: str
    source: str = "structured_recognition"


@dataclass(frozen=True)
class FenGenerationFailure:
    code: str
    message: str
    row: int | None = None
    column: int | None = None


FenGenerationResult = FenGenerationSuccess | FenGenerationFailure


def generate_fen(
    squares: tuple[SquareRecognition, ...],
    orientation: BoardOrientation,
    metadata: FenMetadata | None = None,
) -> FenGenerationResult:
    metadata = metadata or FenMetadata()

    if orientation not in ("white-bottom", "black-bottom"):
        return FenGenerationFailure(
            code="unsupported_orientation",
            message="FEN generation requires white-bottom or black-bottom orientation.",
        )

    board: list[list[str | None]] = [[None for _ in range(8)] for _ in range(8)]
    seen_squares: set[tuple[int, int]] = set()

    for square in squares:
        if not _is_valid_square(square):
            return FenGenerationFailure(
                code="invalid_square",
                message="Recognized square coordinates must be within an 8x8 board.",
                row=square.row,
                column=square.column,
            )

        key = (square.row, square.column)

        if key in seen_squares:
            return FenGenerationFailure(
                code="duplicate_square",
                message="Recognized square data contains duplicate coordinates.",
                row=square.row,
                column=square.column,
            )

        seen_squares.add(key)

        if square.piece is None:
            continue

        board_row, board_column = _map_visual_square(
            row=square.row,
            column=square.column,
            orientation=orientation,
        )
        board[board_row][board_column] = square.piece.code

    placement = "/".join(_render_rank(rank) for rank in board)

    return FenGenerationSuccess(
        fen=(
            f"{placement} {metadata.active_color} {metadata.castling} "
            f"{metadata.en_passant} {metadata.halfmove} {metadata.fullmove}"
        )
    )


def _is_valid_square(square: SquareRecognition) -> bool:
    return 0 <= square.row < 8 and 0 <= square.column < 8


def _map_visual_square(
    row: int,
    column: int,
    orientation: BoardOrientation,
) -> tuple[int, int]:
    if orientation == "white-bottom":
        return row, column

    return 7 - row, 7 - column


def _render_rank(rank: list[str | None]) -> str:
    rendered = ""
    empty_count = 0

    for piece_code in rank:
        if piece_code is None:
            empty_count += 1
            continue

        if empty_count:
            rendered += str(empty_count)
            empty_count = 0

        rendered += piece_code

    if empty_count:
        rendered += str(empty_count)

    return rendered
