from dataclasses import dataclass, field

PLACEHOLDER_FEN = "8/8/8/8/8/8/8/8 w - - 0 1"


@dataclass(frozen=True)
class DetectionResult:
    fen: str
    source: str
    confidence: float | None
    metadata: dict[str, str] = field(default_factory=dict)


def detect_position(image_bytes: bytes) -> DetectionResult:
    return DetectionResult(
        fen=PLACEHOLDER_FEN,
        source="placeholder_detection",
        confidence=None,
        metadata={
            "status": "placeholder",
            "input_bytes": str(len(image_bytes)),
            "message": (
                "Detection pipeline skeleton; real detection is not implemented yet."
            ),
        },
    )
