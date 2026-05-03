from dataclasses import dataclass, field
from typing import Literal

from app.detection.results import DetectionMetadata, DetectionStage

PieceColor = Literal["white", "black"]
PieceRole = Literal["king", "queen", "rook", "bishop", "knight", "pawn"]
PieceCode = Literal[
    "K",
    "Q",
    "R",
    "B",
    "N",
    "P",
    "k",
    "q",
    "r",
    "b",
    "n",
    "p",
]
SyntheticMarker = Literal[
    "empty",
    "white_king",
    "white_queen",
    "white_rook",
    "white_bishop",
    "white_knight",
    "white_pawn",
    "black_king",
    "black_queen",
    "black_rook",
    "black_bishop",
    "black_knight",
    "black_pawn",
]
SOURCE_STAGE = "piece_recognition"


@dataclass(frozen=True)
class SquareSample:
    row: int
    column: int
    marker: str


@dataclass(frozen=True)
class RecognizedPiece:
    color: PieceColor
    role: PieceRole
    code: PieceCode


@dataclass(frozen=True)
class SquareRecognition:
    row: int
    column: int
    piece: RecognizedPiece | None
    square: str = ""
    confidence: float = 1.0
    source_stage: str = SOURCE_STAGE
    failure_reason: str | None = None
    source: str = "synthetic_marker"


@dataclass(frozen=True)
class PieceRecognitionSuccess:
    squares: tuple[SquareRecognition, ...]
    source: str = "synthetic_marker_recognition"
    metadata: DetectionMetadata = field(
        default_factory=lambda: DetectionMetadata(
            confidence=1.0,
            source="synthetic_marker_recognition",
            stage="pieces",
        )
    )


@dataclass(frozen=True)
class PieceRecognitionFailure:
    code: str
    message: str
    row: int | None = None
    column: int | None = None
    square: str | None = None
    failure_reason: str | None = None
    source_stage: str = SOURCE_STAGE
    stage: DetectionStage = "pieces"
    retryable: bool = True
    suggestion: str = "Use supported synthetic piece markers."


PieceRecognitionResult = PieceRecognitionSuccess | PieceRecognitionFailure

SYNTHETIC_MARKERS: dict[SyntheticMarker, RecognizedPiece | None] = {
    "empty": None,
    "white_king": RecognizedPiece(color="white", role="king", code="K"),
    "white_queen": RecognizedPiece(color="white", role="queen", code="Q"),
    "white_rook": RecognizedPiece(color="white", role="rook", code="R"),
    "white_bishop": RecognizedPiece(color="white", role="bishop", code="B"),
    "white_knight": RecognizedPiece(color="white", role="knight", code="N"),
    "white_pawn": RecognizedPiece(color="white", role="pawn", code="P"),
    "black_king": RecognizedPiece(color="black", role="king", code="k"),
    "black_queen": RecognizedPiece(color="black", role="queen", code="q"),
    "black_rook": RecognizedPiece(color="black", role="rook", code="r"),
    "black_bishop": RecognizedPiece(color="black", role="bishop", code="b"),
    "black_knight": RecognizedPiece(color="black", role="knight", code="n"),
    "black_pawn": RecognizedPiece(color="black", role="pawn", code="p"),
}


def recognize_pieces(samples: tuple[SquareSample, ...]) -> PieceRecognitionResult:
    recognized_squares: list[SquareRecognition] = []

    for sample in samples:
        if not _is_valid_square(sample):
            return PieceRecognitionFailure(
                code="invalid_square",
                message="Square sample coordinates must be within an 8x8 board.",
                row=sample.row,
                column=sample.column,
                failure_reason="invalid_square",
            )

        piece = SYNTHETIC_MARKERS.get(sample.marker)
        square = square_name(sample.row, sample.column)

        if sample.marker not in SYNTHETIC_MARKERS:
            return PieceRecognitionFailure(
                code="unknown_piece_marker",
                message="Synthetic piece marker could not be classified.",
                row=sample.row,
                column=sample.column,
                square=square,
                failure_reason="unknown_piece_marker",
            )

        recognized_squares.append(
            SquareRecognition(
                row=sample.row,
                column=sample.column,
                piece=piece,
                square=square,
                confidence=1.0,
            )
        )

    return PieceRecognitionSuccess(squares=tuple(recognized_squares))


def square_name(row: int, column: int) -> str:
    if not 0 <= row < 8 or not 0 <= column < 8:
        raise ValueError("Square coordinates must be within an 8x8 board.")

    file_name = chr(ord("a") + column)
    rank = 8 - row

    return f"{file_name}{rank}"


def format_recognized_pieces(squares: tuple[SquareRecognition, ...]) -> list[str]:
    return [
        f"{square.piece.color} {square.piece.role} at {square.square}"
        for square in squares
        if square.piece is not None
    ]


def _is_valid_square(sample: SquareSample) -> bool:
    return 0 <= sample.row < 8 and 0 <= sample.column < 8
