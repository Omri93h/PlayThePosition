import logging

from app.detection import PLACEHOLDER_FEN, DetectionResult, detect_position


def test_detection_placeholder_returns_existing_placeholder_fen() -> None:
    result = detect_position(b"fake-image-bytes")

    assert isinstance(result, DetectionResult)
    assert result.fen == PLACEHOLDER_FEN
    assert result.confidence is None


def test_detection_placeholder_includes_source_and_metadata() -> None:
    result = detect_position(b"abc")

    assert result.source == "placeholder_detection"
    assert result.metadata["status"] == "placeholder"
    assert result.metadata["input_bytes"] == "3"
    assert "real detection is not implemented" in result.metadata["message"]


def test_detection_placeholder_logs_scaffold_event(caplog) -> None:
    caplog.set_level(logging.INFO, logger="play_the_position.detection")

    detect_position(b"abc")
    record = find_event(caplog.records, "detection.placeholder")

    assert record.fields == {
        "input_bytes": 3,
        "source": "placeholder_detection",
        "stage": "pipeline",
    }


def find_event(records, event: str):
    for record in records:
        if getattr(record, "event", "") == event:
            return record

    raise AssertionError(f"Missing log event: {event}")
