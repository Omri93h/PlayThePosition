from dataclasses import dataclass, field

from app.logging import get_logger, log_event

PLACEHOLDER_FEN = "8/8/8/8/8/8/8/8 w - - 0 1"
logger = get_logger("detection")


@dataclass(frozen=True)
class DetectionResult:
    fen: str
    source: str
    confidence: float | None
    metadata: dict[str, str] = field(default_factory=dict)


def detect_position(image_bytes: bytes) -> DetectionResult:
    log_event(
        logger,
        "detection.placeholder",
        input_bytes=len(image_bytes),
        source="placeholder_detection",
        stage="pipeline",
    )

    return DetectionResult(
        fen=PLACEHOLDER_FEN,
        source="placeholder_detection",
        confidence=None,
        metadata={
            "status": "placeholder",
            "input_bytes": str(len(image_bytes)),
            "stage": "pipeline",
            "message": (
                "Detection pipeline skeleton; real detection is not implemented yet."
            ),
        },
    )
