from fastapi.testclient import TestClient

from app.main import SHARED_POSITIONS, app


def test_share_stores_fen_and_returns_id_and_path() -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()

    response = client.post(
        "/share",
        json={"fen": "8/8/8/8/8/8/8/8 w - - 0 1"},
    )

    body = response.json()

    assert response.status_code == 200
    assert body["fen"] == "8/8/8/8/8/8/8/8 w - - 0 1"
    assert body["source"] == "share"
    assert isinstance(body["id"], str)
    assert len(body["id"]) > 0
    assert body["path"] == f"/share/{body['id']}"


def test_share_loads_saved_fen_by_id() -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()

    created = client.post(
        "/share",
        json={"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
    ).json()

    response = client.get(f"/share/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "source": "share",
    }


def test_share_unknown_id_returns_structured_404() -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()

    response = client.get("/share/missing")

    assert response.status_code == 404
    assert response.json() == {
        "ok": False,
        "error": {
            "code": "share_not_found",
            "message": "Shared position was not found.",
        },
    }
