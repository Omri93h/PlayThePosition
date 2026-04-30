from dataclasses import dataclass, field
from typing import Literal

from app.detection.results import DetectionMetadata, DetectionStage

PieceColor = Literal["white", "black"]
PieceRole = Literal["king", "queen", "pawn"]
PieceCode = Literal["K", "Q", "P", "q", "p"]
SyntheticMarker = Literal[
    "empty",
    "white_king",
    "black_queen",
    "white_pawn",
    "black_pawn",
]


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
    stage: DetectionStage = "pieces"
    retryable: bool = True
    suggestion: str = "Use supported synthetic piece markers."


PieceRecognitionResult = PieceRecognitionSuccess | PieceRecognitionFailure

SYNTHETIC_MARKERS: dict[SyntheticMarker, RecognizedPiece | None] = {
    "empty": None,
    "white_king": RecognizedPiece(color="white", role="king", code="K"),
    "black_queen": RecognizedPiece(color="black", role="queen", code="q"),
    "white_pawn": RecognizedPiece(color="white", role="pawn", code="P"),
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
            )

        piece = SYNTHETIC_MARKERS.get(sample.marker)

        if sample.marker not in SYNTHETIC_MARKERS:
            return PieceRecognitionFailure(
                code="unknown_piece_marker",
                message="Synthetic piece marker could not be classified.",
                row=sample.row,
                column=sample.column,
            )

        recognized_squares.append(
            SquareRecognition(
                row=sample.row,
                column=sample.column,
                piece=piece,
            )
        )

    return PieceRecognitionSuccess(squares=tuple(recognized_squares))


def _is_valid_square(sample: SquareSample) -> bool:
    return 0 <= sample.row < 8 and 0 <= sample.column < 8
