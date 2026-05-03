import logging

from fastapi.testclient import TestClient

from app.main import MAX_UPLOAD_BYTES, PLACEHOLDER_FEN, app


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
