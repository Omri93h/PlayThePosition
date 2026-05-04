from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from app.detection.image import DecodedImage, ImageDecodeFailure, decode_image_bytes
from app.detection.pipeline import PLACEHOLDER_FEN
from app.detection.results import (
    Confidence,
    DetectionFailure,
    DetectionStage,
    DetectionStatus,
)

ORCHESTRATOR_SOURCE = "gated_detection_orchestrator"


@dataclass(frozen=True)
class DetectionOrchestratorConfig:
    enabled: bool = False
    min_success_confidence: float = 0.5


@dataclass(frozen=True)
class DetectionStageOutput:
    stage: DetectionStage
    status: DetectionStatus
    source: str
    confidence: Confidence = None
    payload: Mapping[str, object] = field(default_factory=dict)
    failure: DetectionFailure | None = None


BoardBoundsHook = Callable[[DecodedImage], DetectionStageOutput]
PieceRecognitionHook = Callable[
    [DecodedImage, DetectionStageOutput],
    DetectionStageOutput,
]
OrientationHook = Callable[[DetectionStageOutput], DetectionStageOutput]
FenGenerationHook = Callable[
    [DetectionStageOutput, DetectionStageOutput],
    DetectionStageOutput,
]


@dataclass(frozen=True)
class DetectionOrchestratorHooks:
    board_bounds: BoardBoundsHook | None = None
    piece_recognition: PieceRecognitionHook | None = None
    orientation: OrientationHook | None = None
    fen_generation: FenGenerationHook | None = None


@dataclass(frozen=True)
class DetectionOrchestratorResult:
    status: DetectionStatus
    fen: str
    source: str
    confidence: Confidence
    stages: tuple[DetectionStageOutput, ...]
    failure: DetectionFailure | None = None


def run_detection_orchestrator(
    image_bytes: bytes,
    content_type: str,
    *,
    config: DetectionOrchestratorConfig | None = None,
    hooks: DetectionOrchestratorHooks | None = None,
) -> DetectionOrchestratorResult:
    config = config or DetectionOrchestratorConfig()
    hooks = hooks or DetectionOrchestratorHooks()

    if not config.enabled:
        return _placeholder_result(
            DetectionStageOutput(
                stage="pipeline",
                status="placeholder",
                source="feature_gate_disabled",
                payload={"message": "Detection orchestrator is disabled."},
            )
        )

    decoded = decode_image_bytes(image_bytes, content_type)

    if isinstance(decoded, ImageDecodeFailure):
        failure = _decode_failure(decoded)
        return _placeholder_result(
            DetectionStageOutput(
                stage="preprocess",
                status="failed",
                source=decoded.metadata.source,
                confidence=decoded.metadata.confidence,
                failure=failure,
            ),
            status="failed",
            failure=failure,
        )

    stages: list[DetectionStageOutput] = [
        DetectionStageOutput(
            stage="preprocess",
            status="success",
            source=decoded.metadata.source,
            confidence=decoded.metadata.confidence,
            payload={
                "width": decoded.width,
                "height": decoded.height,
                "format": decoded.format,
                "mode": decoded.mode,
            },
        )
    ]

    board_bounds = _run_required_stage(
        "grid",
        stages,
        hooks.board_bounds,
        decoded,
    )
    if isinstance(board_bounds, DetectionOrchestratorResult):
        return board_bounds

    pieces = _run_required_stage(
        "pieces",
        stages,
        hooks.piece_recognition,
        decoded,
        board_bounds,
    )
    if isinstance(pieces, DetectionOrchestratorResult):
        return pieces

    orientation = _run_required_stage(
        "orientation",
        stages,
        hooks.orientation,
        pieces,
    )
    if isinstance(orientation, DetectionOrchestratorResult):
        return orientation

    fen_stage = _run_required_stage(
        "fen",
        stages,
        hooks.fen_generation,
        pieces,
        orientation,
    )
    if isinstance(fen_stage, DetectionOrchestratorResult):
        return fen_stage

    fen = fen_stage.payload.get("fen")
    if not isinstance(fen, str) or not fen.strip():
        failure = _failure(
            code="fen_missing",
            message="FEN stage did not provide a safe FEN value.",
            stage="fen",
            retryable=False,
            suggestion="Check FEN generation stage output before integration.",
        )
        stages[-1] = DetectionStageOutput(
            stage="fen",
            status="failed",
            source=fen_stage.source,
            confidence=fen_stage.confidence,
            payload=fen_stage.payload,
            failure=failure,
        )
        return _placeholder_result(*stages, status="failed", failure=failure)

    if _is_low_confidence(fen_stage.confidence, config.min_success_confidence):
        failure = _failure(
            code="low_confidence",
            message="Detection result confidence is below the configured threshold.",
            stage="fen",
            retryable=True,
            suggestion="Keep placeholder fallback and review the position manually.",
        )
        return _placeholder_result(*stages, status="partial", failure=failure)

    return DetectionOrchestratorResult(
        status="success",
        fen=fen,
        source=ORCHESTRATOR_SOURCE,
        confidence=fen_stage.confidence,
        stages=tuple(stages),
    )


def _run_required_stage(
    stage: DetectionStage,
    stages: list[DetectionStageOutput],
    hook,
    *args,
) -> DetectionStageOutput | DetectionOrchestratorResult:
    if hook is None:
        failure = _failure(
            code="stage_not_configured",
            message=f"{stage} stage is not configured.",
            stage=stage,
            retryable=False,
            suggestion="Inject a stage hook before enabling this detection path.",
        )
        stage_output = DetectionStageOutput(
            stage=stage,
            status="failed",
            source=ORCHESTRATOR_SOURCE,
            failure=failure,
        )
        stages.append(stage_output)
        return _placeholder_result(*stages, status="partial", failure=failure)

    stage_output = hook(*args)
    stages.append(stage_output)

    if stage_output.status == "success":
        return stage_output

    failure = stage_output.failure or _failure(
        code="stage_failed",
        message=f"{stage} stage did not complete successfully.",
        stage=stage,
        retryable=True,
        suggestion="Use placeholder fallback and inspect detection metadata.",
    )

    return _placeholder_result(
        *stages,
        status="failed" if stage_output.status == "failed" else "partial",
        failure=failure,
    )


def _placeholder_result(
    *stages: DetectionStageOutput,
    status: DetectionStatus = "placeholder",
    failure: DetectionFailure | None = None,
) -> DetectionOrchestratorResult:
    return DetectionOrchestratorResult(
        status=status,
        fen=PLACEHOLDER_FEN,
        source="placeholder_detection",
        confidence=None,
        stages=tuple(stages),
        failure=failure,
    )


def _decode_failure(failure: ImageDecodeFailure) -> DetectionFailure:
    return _failure(
        code=failure.code,
        message=failure.message,
        stage=failure.stage,
        retryable=failure.retryable,
        suggestion=failure.suggestion,
        failure_reason=failure.failure_reason,
    )


def _failure(
    *,
    code: str,
    message: str,
    stage: DetectionStage,
    retryable: bool,
    suggestion: str,
    failure_reason: str | None = None,
) -> DetectionFailure:
    return DetectionFailure(
        code=code,
        message=message,
        stage=stage,
        retryable=retryable,
        suggestion=suggestion,
        failure_reason=failure_reason,
    )


def _is_low_confidence(confidence: Confidence, threshold: float) -> bool:
    return confidence is not None and confidence < threshold
