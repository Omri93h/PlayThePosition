import logging

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


def test_share_creation_logs_metadata_without_full_fen(caplog) -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    response = client.post("/share", json={"fen": fen})
    body = response.json()
    record = find_event(caplog.records, "share.created")

    assert response.status_code == 200
    assert record.fields == {
        "share_id": body["id"],
        "fen_length": len(fen),
        "source": "share",
    }
    assert fen not in record.getMessage()


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


def test_share_load_success_logs_metadata_without_full_fen(caplog) -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    fen = "8/8/8/8/8/8/8/8 w - - 0 1"
    created = client.post("/share", json={"fen": fen}).json()
    response = client.get(f"/share/{created['id']}")
    record = find_event(caplog.records, "share.loaded")

    assert response.status_code == 200
    assert record.fields == {
        "share_id": created["id"],
        "fen_length": len(fen),
        "source": "share",
    }
    assert fen not in record.getMessage()


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


def test_share_not_found_logs_share_id(caplog) -> None:
    client = TestClient(app)
    SHARED_POSITIONS.clear()
    caplog.set_level(logging.INFO, logger="play_the_position.api")

    response = client.get("/share/missing")
    record = find_event(caplog.records, "share.not_found")

    assert response.status_code == 404
    assert record.fields == {"share_id": "missing"}


def find_event(records, event: str):
    for record in records:
        if getattr(record, "event", "") == event:
            return record

    raise AssertionError(f"Missing log event: {event}")
