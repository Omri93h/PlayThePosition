import logging

import pytest
from fastapi.testclient import TestClient

from app.detection.orchestrator import DetectionOrchestratorResult, DetectionStageOutput
from app.detection.results import DetectionFailure
from app.main import (
    INTERNAL_RECOGNITION_ENABLED_ENV,
    MAX_UPLOAD_BYTES,
    PLACEHOLDER_FEN,
    app,
)


@pytest.fixture(autouse=True)
def disable_internal_recognition_by_default(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_RECOGNITION_ENABLED_ENV, raising=False)


def test_upload_accepts_valid_png_and_returns_placeholder_fen() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": PLACEHOLDER_FEN,
        "source": "placeholder",
        "confidence": None,
        "message": "Received position.png; detection is not implemented yet.",
    }


def test_upload_disabled_gate_preserves_placeholder_response(monkeypatch) -> None:
    monkeypatch.delenv(INTERNAL_RECOGNITION_ENABLED_ENV, raising=False)
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": PLACEHOLDER_FEN,
        "source": "placeholder",
        "confidence": None,
        "message": "Received position.png; detection is not implemented yet.",
    }


def test_upload_non_truthy_gate_preserves_placeholder_response(monkeypatch) -> None:
    monkeypatch.setenv(INTERNAL_RECOGNITION_ENABLED_ENV, "false")
    monkeypatch.setattr(
        "app.main.run_upload_recognition",
        lambda _bytes, _content_type: (_ for _ in ()).throw(
            AssertionError("Recognition runner should not run.")
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": PLACEHOLDER_FEN,
        "source": "placeholder",
        "confidence": None,
        "message": "Received position.png; detection is not implemented yet.",
    }


def test_upload_success_logs_privacy_safe_metadata(caplog) -> None:
    client = TestClient(app)
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    record = find_event(caplog.records, "upload.succeeded")

    assert response.status_code == 200
    assert record.fields == {
        "content_type": "image/png",
        "file_size": 24,
        "source": "placeholder",
        "fen_length": len(PLACEHOLDER_FEN),
    }


def test_upload_enabled_gate_returns_detected_fen_with_metadata(
    monkeypatch,
) -> None:
    fen = "4k3/8/8/8/8/8/8/4K3 b - - 0 1"

    monkeypatch.setenv(INTERNAL_RECOGNITION_ENABLED_ENV, "true")
    monkeypatch.setattr(
        "app.main.run_upload_recognition",
        lambda _bytes, _content_type: DetectionOrchestratorResult(
            status="success",
            fen=fen,
            source="gated_detection_orchestrator",
            confidence=0.91,
            stages=(
                DetectionStageOutput(
                    stage="preprocess",
                    status="success",
                    source="test_preprocess",
                    confidence=1.0,
                ),
                DetectionStageOutput(
                    stage="orientation",
                    status="success",
                    source="test_orientation",
                    confidence=0.9,
                    payload={"orientation": "black-bottom"},
                ),
                DetectionStageOutput(
                    stage="fen",
                    status="success",
                    source="test_fen",
                    confidence=0.91,
                    payload={"fen": fen},
                ),
            ),
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fen"] == fen
    assert payload["source"] == "gated_detection_orchestrator"
    assert payload["confidence"] == 0.91
    assert payload["message"] == (
        "Detection completed. Review the board before using it."
    )
    assert payload["detection"]["status"] == "success"
    assert payload["detection"]["fen"] == fen
    assert payload["detection"]["orientation"] == "black-bottom"
    assert payload["detection"]["failure"] is None


def test_upload_enabled_gate_falls_back_with_structured_metadata(
    monkeypatch,
) -> None:
    failure = DetectionFailure(
        code="stage_not_configured",
        message="pieces stage is not configured.",
        stage="pieces",
        retryable=False,
        suggestion="Review and correct the board manually.",
    )

    monkeypatch.setenv(INTERNAL_RECOGNITION_ENABLED_ENV, "yes")
    monkeypatch.setattr(
        "app.main.run_upload_recognition",
        lambda _bytes, _content_type: DetectionOrchestratorResult(
            status="partial",
            fen=PLACEHOLDER_FEN,
            source="placeholder_detection",
            confidence=None,
            stages=(
                DetectionStageOutput(
                    stage="pieces",
                    status="failed",
                    source="gated_detection_orchestrator",
                    failure=failure,
                ),
            ),
            failure=failure,
        ),
    )
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fen"] == PLACEHOLDER_FEN
    assert payload["source"] == "placeholder"
    assert payload["confidence"] is None
    assert payload["detection"]["status"] == "partial"
    assert payload["detection"]["fen"] is None
    assert payload["detection"]["failure"]["code"] == "stage_not_configured"
    assert payload["detection"]["stages"][0]["failure"]["stage"] == "pieces"


def test_upload_enabled_gate_logs_privacy_safe_metadata(
    caplog,
    monkeypatch,
) -> None:
    failure = DetectionFailure(
        code="low_confidence",
        message="Detection result confidence is below the configured threshold.",
        stage="fen",
        retryable=True,
        suggestion="Review and correct the board manually.",
    )

    monkeypatch.setenv(INTERNAL_RECOGNITION_ENABLED_ENV, "on")
    monkeypatch.setattr(
        "app.main.run_upload_recognition",
        lambda _bytes, _content_type: DetectionOrchestratorResult(
            status="partial",
            fen=PLACEHOLDER_FEN,
            source="placeholder_detection",
            confidence=None,
            stages=(),
            failure=failure,
        ),
    )
    client = TestClient(app)
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    response = client.post(
        "/upload",
        files={
            "file": (
                "position.png",
                b"\x89PNG\r\n\x1a\nfake image bytes",
                "image/png",
            )
        },
    )

    record = find_event(caplog.records, "upload.succeeded")

    assert response.status_code == 200
    assert record.fields == {
        "content_type": "image/png",
        "file_size": 24,
        "source": "placeholder",
        "recognition_status": "partial",
        "fen_length": len(PLACEHOLDER_FEN),
        "confidence": None,
        "stage": "fen",
        "failure_code": "low_confidence",
        "retryable": True,
    }


def test_upload_accepts_valid_jpeg_and_returns_placeholder_fen() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={"file": ("position.jpg", b"\xff\xd8\xfffake image bytes", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["fen"] == PLACEHOLDER_FEN
    assert response.json()["source"] == "placeholder"


def test_upload_rejects_unsupported_content_type() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={"file": ("position.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json() == {
        "ok": False,
        "error": {
            "code": "unsupported_file_type",
            "message": "Only PNG and JPEG images are supported.",
        },
    }


def test_upload_validation_failure_logs_privacy_safe_metadata(caplog) -> None:
    client = TestClient(app)
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    response = client.post(
        "/upload",
        files={"file": ("position.txt", b"not an image", "text/plain")},
    )

    record = find_event(caplog.records, "upload.validation_failed")

    assert response.status_code == 415
    assert record.fields == {
        "code": "unsupported_file_type",
        "content_type": "text/plain",
        "file_size": 12,
    }


def test_upload_rejects_oversized_file() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={
            "file": (
                "large.png",
                b"\x89PNG\r\n\x1a\n" + b"x" * MAX_UPLOAD_BYTES,
                "image/png",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "file_too_large"


def test_upload_rejects_corrupted_image_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={"file": ("broken.png", b"not really a png", "image/png")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_payload"


def find_event(records, event: str):
    for record in records:
        if getattr(record, "event", "") == event:
            return record

    raise AssertionError(f"Missing log event: {event}")
