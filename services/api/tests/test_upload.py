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
