from dataclasses import dataclass
from typing import Literal

from app.detection.pieces import SquareRecognition

BoardOrientation = Literal["white-bottom", "black-bottom", "unknown"]


@dataclass(frozen=True)
class OrientationDetectionResult:
    orientation: BoardOrientation
    source: str = "synthetic_piece_layout"
    confidence: float | None = None
    reason: str = ""


def detect_orientation(
    squares: tuple[SquareRecognition, ...],
) -> OrientationDetectionResult:
    if not squares:
        return OrientationDetectionResult(
            orientation="unknown",
            reason="No recognized squares were provided.",
        )

    white_lower_score = 0
    black_lower_score = 0

    for square in squares:
        if not _is_valid_square(square):
            return OrientationDetectionResult(
                orientation="unknown",
                reason="Recognized square coordinates are outside the board.",
            )

        if square.piece is None:
            continue

        if square.row >= 4 and square.piece.color == "white":
            white_lower_score += 1

        if square.row >= 4 and square.piece.color == "black":
            black_lower_score += 1

    if white_lower_score > black_lower_score:
        return OrientationDetectionResult(
            orientation="white-bottom",
            confidence=_score_confidence(white_lower_score, black_lower_score),
            reason="White pieces are concentrated near visually lower rows.",
        )

    if black_lower_score > white_lower_score:
        return OrientationDetectionResult(
            orientation="black-bottom",
            confidence=_score_confidence(black_lower_score, white_lower_score),
            reason="Black pieces are concentrated near visually lower rows.",
        )

    return OrientationDetectionResult(
        orientation="unknown",
        reason="Piece layout is ambiguous for orientation.",
    )


def _is_valid_square(square: SquareRecognition) -> bool:
    return 0 <= square.row < 8 and 0 <= square.column < 8


def _score_confidence(winning_score: int, losing_score: int) -> float:
    total = winning_score + losing_score

    if total == 0:
        return 0.0

    return round((winning_score - losing_score) / total, 2)
