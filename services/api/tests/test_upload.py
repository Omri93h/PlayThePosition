from fastapi.testclient import TestClient

from app.main import app


def test_upload_returns_placeholder_fen_response() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload",
        files={"file": ("position.png", b"fake image bytes", "image/png")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
        "source": "placeholder",
        "confidence": None,
        "message": "Received position.png; detection is not implemented yet.",
    }
