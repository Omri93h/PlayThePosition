import json
from pathlib import Path

from app.detection.color_classifier import classify_fixture_colors
from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.piece_measurements import measure_fixture_piece_samples
from app.detection.role_color_signal_audit import audit_fixture_role_color_signals
from app.detection.square_sampling import SquareSample, sample_fixture_squares

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_combined_role_color_measurement_report_totals_are_current() -> None:
    manifest = _load_valid_manifest()
    occupancy_summaries = []
    color_summaries = []
    color_rows = []

    for case in manifest["cases"]:
        decoded = _decode_case_image(case)
        samples = _sample_case(case, decoded)
        audit = audit_fixture_role_color_signals(case, decoded)
        color_measurement = classify_fixture_colors(audit=audit, samples=samples)

        occupancy_summaries.append(
            measure_fixture_piece_samples(case, samples).summary
        )
        color_summaries.append(color_measurement.summary)
        color_rows.extend(color_measurement.rows)

    assert len(manifest["cases"]) == 8

    assert sum(summary.total_squares for summary in occupancy_summaries) == 512
    assert (
        sum(
            summary.expected_occupied_count
            for summary in occupancy_summaries
        )
        == 167
    )
    assert (
        sum(summary.sampled_occupied_count for summary in occupancy_summaries)
        == 167
    )
    assert (
        sum(
            summary.empty_square_correct_count
            for summary in occupancy_summaries
        )
        == 345
    )
    assert sum(summary.missing_count for summary in occupancy_summaries) == 0
    assert sum(summary.extra_count for summary in occupancy_summaries) == 0

    assert sum(summary.occupied_square_count for summary in color_summaries) == 167
    assert sum(summary.measured_color_count for summary in color_summaries) == 159
    assert sum(summary.correct_count for summary in color_summaries) == 159
    assert sum(summary.ambiguous_count for summary in color_summaries) == 8
    assert sum(summary.wrong_count for summary in color_summaries) == 0

    assert {row.detected_role for row in color_rows} == {None}
    assert {row.role_result for row in color_rows} == {"not_measured"}
    assert {row.role_failure_reason for row in color_rows} == {
        "classifier_not_configured"
    }
    assert _combined_role_color_success_count(color_rows) == 0


def _combined_role_color_success_count(rows: list) -> int:
    return sum(
        row.color_result == "correct" and row.role_result == "correct"
        for row in rows
    )


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


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result


def _sample_case(case: dict, decoded: DecodedImage) -> tuple[SquareSample, ...]:
    bounds = case["board_bounds"]

    return sample_fixture_squares(
        fixture_id=case["id"],
        image=decoded,
        board_bounds=BoardBounds(
            x=bounds["x"],
            y=bounds["y"],
            width=bounds["width"],
            height=bounds["height"],
        ),
        orientation=case["orientation"],
    )
