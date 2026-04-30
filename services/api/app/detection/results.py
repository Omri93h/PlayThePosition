from dataclasses import dataclass
from typing import Literal

DetectionStage = Literal[
    "preprocess",
    "grid",
    "pieces",
    "orientation",
    "fen",
    "pipeline",
]
FailureCode = Literal[
    "empty_image",
    "invalid_image_bytes",
    "unsupported_image_format",
    "board_grid_not_found",
    "invalid_square",
    "unknown_piece_marker",
    "duplicate_square",
    "unsupported_orientation",
    "placeholder_detection",
]
Confidence = float | None


@dataclass(frozen=True)
class DetectionMetadata:
    confidence: Confidence
    source: str
    stage: DetectionStage


@dataclass(frozen=True)
class DetectionFailure:
    code: FailureCode | str
    message: str
    stage: DetectionStage
    retryable: bool
    suggestion: str
