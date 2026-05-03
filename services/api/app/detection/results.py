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
DetectionStatus = Literal["placeholder", "success", "partial", "failed"]
DETECTION_STATUSES: tuple[DetectionStatus, ...] = (
    "placeholder",
    "success",
    "partial",
    "failed",
)


@dataclass(frozen=True)
class DetectionMetadata:
    confidence: Confidence
    source: str
    stage: DetectionStage
    status: DetectionStatus = "success"


@dataclass(frozen=True)
class DetectionFailure:
    code: FailureCode | str
    message: str
    stage: DetectionStage
    retryable: bool
    suggestion: str
    failure_reason: str | None = None


def detection_metadata_payload(metadata: DetectionMetadata) -> dict[str, object]:
    return {
        "status": metadata.status,
        "confidence": metadata.confidence,
        "source": metadata.source,
        "stage": metadata.stage,
    }


def detection_failure_payload(failure: DetectionFailure) -> dict[str, object]:
    return {
        "code": failure.code,
        "message": failure.message,
        "stage": failure.stage,
        "retryable": failure.retryable,
        "suggestion": failure.suggestion,
        "failure_reason": failure.failure_reason,
    }
