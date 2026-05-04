from io import BytesIO

from PIL import Image

from app.detection.orchestrator import (
    DetectionOrchestratorConfig,
    DetectionOrchestratorHooks,
    DetectionStageOutput,
    run_detection_orchestrator,
)
from app.detection.pipeline import PLACEHOLDER_FEN
from app.detection.results import DetectionFailure


def test_orchestrator_default_gate_is_off() -> None:
    result = run_detection_orchestrator(b"not decoded", "image/png")

    assert result.status == "placeholder"
    assert result.fen == PLACEHOLDER_FEN
    assert result.source == "placeholder_detection"
    assert result.stages[0].source == "feature_gate_disabled"


def test_disabled_gate_returns_placeholder_fallback() -> None:
    result = run_detection_orchestrator(
        make_png_bytes(),
        "image/png",
        config=DetectionOrchestratorConfig(enabled=False),
        hooks=successful_hooks(),
    )

    assert result.status == "placeholder"
    assert result.fen == PLACEHOLDER_FEN
    assert [stage.stage for stage in result.stages] == ["pipeline"]


def test_enabled_path_runs_decode_stage_before_missing_hook_fallback() -> None:
    result = run_detection_orchestrator(
        make_png_bytes(),
        "image/png",
        config=DetectionOrchestratorConfig(enabled=True),
    )

    assert result.status == "partial"
    assert result.fen == PLACEHOLDER_FEN
    assert [stage.stage for stage in result.stages] == ["preprocess", "grid"]
    assert result.stages[0].payload["width"] == 2
    assert result.stages[0].payload["format"] == "png"
    assert result.failure is not None
    assert result.failure.code == "stage_not_configured"
    assert result.failure.stage == "grid"


def test_decode_failure_returns_structured_failure() -> None:
    result = run_detection_orchestrator(
        b"not a png",
        "image/png",
        config=DetectionOrchestratorConfig(enabled=True),
    )

    assert result.status == "failed"
    assert result.fen == PLACEHOLDER_FEN
    assert result.failure is not None
    assert result.failure.code == "invalid_image_bytes"
    assert result.failure.stage == "preprocess"
    assert result.stages[0].status == "failed"


def test_downstream_failure_stops_safely_with_metadata() -> None:
    failure = DetectionFailure(
        code="board_grid_not_found",
        message="No board grid found.",
        stage="grid",
        retryable=True,
        suggestion="Use a cleaner full-board screenshot.",
        failure_reason="board_grid_not_found",
    )

    result = run_detection_orchestrator(
        make_png_bytes(),
        "image/png",
        config=DetectionOrchestratorConfig(enabled=True),
        hooks=DetectionOrchestratorHooks(
            board_bounds=lambda _image: DetectionStageOutput(
                stage="grid",
                status="failed",
                source="test_grid",
                confidence=0.1,
                failure=failure,
            )
        ),
    )

    assert result.status == "failed"
    assert result.fen == PLACEHOLDER_FEN
    assert result.failure == failure
    assert [stage.stage for stage in result.stages] == ["preprocess", "grid"]


def test_successful_injected_stage_flow_can_produce_internal_fen() -> None:
    fen = "4k3/8/8/8/8/8/8/4K3 w - - 0 1"

    result = run_detection_orchestrator(
        make_png_bytes(),
        "image/png",
        config=DetectionOrchestratorConfig(enabled=True),
        hooks=successful_hooks(fen=fen),
    )

    assert result.status == "success"
    assert result.fen == fen
    assert result.source == "gated_detection_orchestrator"
    assert result.confidence == 0.82
    assert [stage.stage for stage in result.stages] == [
        "preprocess",
        "grid",
        "pieces",
        "orientation",
        "fen",
    ]


def test_low_confidence_success_uses_placeholder_fallback() -> None:
    result = run_detection_orchestrator(
        make_png_bytes(),
        "image/png",
        config=DetectionOrchestratorConfig(
            enabled=True,
            min_success_confidence=0.9,
        ),
        hooks=successful_hooks(fen_confidence=0.2),
    )

    assert result.status == "partial"
    assert result.fen == PLACEHOLDER_FEN
    assert result.failure is not None
    assert result.failure.code == "low_confidence"


def successful_hooks(
    *,
    fen: str = "8/8/8/8/8/8/8/8 w - - 0 1",
    fen_confidence: float = 0.82,
) -> DetectionOrchestratorHooks:
    return DetectionOrchestratorHooks(
        board_bounds=lambda _image: DetectionStageOutput(
            stage="grid",
            status="success",
            source="test_grid",
            confidence=0.8,
            payload={"bounds": {"x": 0, "y": 0, "width": 2, "height": 2}},
        ),
        piece_recognition=lambda _image, _grid: DetectionStageOutput(
            stage="pieces",
            status="success",
            source="test_pieces",
            confidence=0.85,
            payload={"pieces": []},
        ),
        orientation=lambda _pieces: DetectionStageOutput(
            stage="orientation",
            status="success",
            source="test_orientation",
            confidence=0.9,
            payload={"orientation": "white-bottom"},
        ),
        fen_generation=lambda _pieces, _orientation: DetectionStageOutput(
            stage="fen",
            status="success",
            source="test_fen",
            confidence=fen_confidence,
            payload={"fen": fen},
        ),
    )


def make_png_bytes() -> bytes:
    image = Image.new("RGB", (2, 2), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
