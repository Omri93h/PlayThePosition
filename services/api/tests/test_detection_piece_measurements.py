import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.piece_measurements import (
    ROLE_COLOR_NOT_SUPPORTED,
    measure_fixture_piece_samples,
)
from app.detection.square_sampling import SquareSample, sample_fixture_squares

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_approved_fixture_samples_convert_to_measurement_rows() -> None:
    manifest = _load_valid_manifest()
    measurements = []

    for case in _block_12_cases(manifest):
        measurement = measure_fixture_piece_samples(
            case,
            _sample_case(case),
        )
        measurements.append(measurement.summary)

        assert len(measurement.rows) == 64
        assert {row.fixture_id for row in measurement.rows} == {case["id"]}
        assert {row.source_stage for row in measurement.rows} == {"square_sampling"}
        assert {
            row.square
            for row in measurement.rows
            if row.result_category == "not_measured"
        } == {piece["square"] for piece in case["expected_pieces"]}
        assert {
            row.failure_reason
            for row in measurement.rows
            if row.result_category == "not_measured"
        } == {ROLE_COLOR_NOT_SUPPORTED}

    aggregate = _aggregate_summaries(measurements)

    assert aggregate["fixture_count"] == 8
    assert aggregate["total_squares"] == 512
    assert aggregate["expected_occupied_count"] == 167
    assert aggregate["sampled_occupied_count"] == 167
    assert aggregate["empty_square_correct_count"] == 345
    assert aggregate["occupancy_matched_occupied_count"] == 167
    assert aggregate["missing_count"] == 0
    assert aggregate["extra_count"] == 0
    assert aggregate["role_color_unsupported_count"] == 167


def test_measurement_categories_cover_empty_missing_extra_and_unsupported() -> None:
    case = _measurement_case()
    samples = (
        _sample("a1", "empty"),
        _sample("a2", "occupied"),
        _sample("b1", "empty"),
        _sample("b2", "occupied"),
        _sample("h8", "not_measured", failure_reason="unsupported_orientation"),
    )

    measurement = measure_fixture_piece_samples(case, samples)
    rows = {row.square: row for row in measurement.rows}

    assert rows["a1"].result_category == "correct"
    assert rows["a2"].result_category == "not_measured"
    assert rows["a2"].failure_reason == ROLE_COLOR_NOT_SUPPORTED
    assert rows["b1"].result_category == "missing"
    assert rows["b2"].result_category == "extra"
    assert rows["h8"].result_category == "not_measured"
    assert rows["h8"].failure_reason == "unsupported_orientation"

    assert measurement.summary.correct_count == 1
    assert measurement.summary.missing_count == 1
    assert measurement.summary.extra_count == 1
    assert measurement.summary.not_measured_count == 2
    assert measurement.summary.role_color_unsupported_count == 1
    assert measurement.summary.blocker_notes == (
        "role/color recognition is not supported by square sampling",
    )


def test_not_measured_samples_remain_safe_without_piece_identity_claims() -> None:
    case = _measurement_case()
    samples = (_sample("a2", "not_measured", failure_reason="invalid_board_bounds"),)

    measurement = measure_fixture_piece_samples(case, samples)
    row = measurement.rows[0]

    assert row.result_category == "not_measured"
    assert row.expected_piece == "pawn"
    assert row.expected_color == "white"
    assert row.detected_piece is None
    assert row.detected_color is None
    assert row.failure_reason == "invalid_board_bounds"
    assert measurement.summary.role_color_unsupported_count == 0


def _load_valid_manifest() -> dict:
    manifest = json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8"))
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is True
    assert validation.issues == ()

    return manifest


def _block_12_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if not case["expected_metrics"].get("role_signal_fixture")
    )


def _sample_case(case: dict) -> tuple[SquareSample, ...]:
    decoded = _decode_case_image(case)

    return sample_fixture_squares(
        fixture_id=case["id"],
        image=decoded,
        board_bounds=_board_bounds(case),
        orientation=case["orientation"],
    )


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result


def _board_bounds(case: dict) -> BoardBounds:
    bounds = case["board_bounds"]

    return BoardBounds(
        x=bounds["x"],
        y=bounds["y"],
        width=bounds["width"],
        height=bounds["height"],
    )


def _aggregate_summaries(summaries: list) -> dict[str, int]:
    return {
        "fixture_count": len(summaries),
        "total_squares": sum(summary.total_squares for summary in summaries),
        "expected_occupied_count": sum(
            summary.expected_occupied_count for summary in summaries
        ),
        "sampled_occupied_count": sum(
            summary.sampled_occupied_count for summary in summaries
        ),
        "empty_square_correct_count": sum(
            summary.empty_square_correct_count for summary in summaries
        ),
        "occupancy_matched_occupied_count": sum(
            summary.occupancy_matched_occupied_count for summary in summaries
        ),
        "missing_count": sum(summary.missing_count for summary in summaries),
        "extra_count": sum(summary.extra_count for summary in summaries),
        "role_color_unsupported_count": sum(
            summary.role_color_unsupported_count for summary in summaries
        ),
    }


def _measurement_case() -> dict:
    return {
        "id": "test-fixture",
        "filename": "test-fixture.png",
        "source": "test",
        "style": "test",
        "orientation": "white-bottom",
        "expected_pieces": [
            {"square": "a2", "piece": "pawn", "color": "white"},
            {"square": "b1", "piece": "knight", "color": "white"},
        ],
    }


def _sample(
    square: str,
    detected_state: str,
    *,
    failure_reason: str | None = None,
) -> SquareSample:
    return SquareSample(
        fixture_id="test-fixture",
        square=square,
        row=0,
        column=0,
        detected_state=detected_state,
        detected_piece=None,
        detected_color=None,
        confidence=None if detected_state == "not_measured" else 0.8,
        failure_reason=failure_reason,
    )
