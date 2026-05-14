import json
from pathlib import Path

import pytest

from app.detection.color_classifier import (
    ColorClassificationRow,
    classify_fixture_colors,
)
from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.measured_pieces import (
    MeasuredPieceJoinError,
    build_measured_piece_rows,
)
from app.detection.role_classifier import (
    RoleClassificationRow,
    classify_fixture_roles,
)
from app.detection.role_color_signal_audit import audit_fixture_role_color_signals
from app.detection.role_signal_audit_v2 import audit_fixture_role_signals_v2
from app.detection.square_sampling import SquareSample, sample_fixture_squares

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
ROLE_SIGNAL_FILENAMES = {
    "owned_role-signal_white-bottom_dense-01.png",
    "owned_role-signal_black-bottom_dense-01.png",
    "owned_role-signal_white-bottom_shifted-01.png",
}


def test_measured_piece_row_from_usable_occupied_square() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_occupied_sample("a1")),
        color_rows=(_color_row("a1", "white"),),
        role_rows=(_role_row("a1", "king"),),
    )
    row = _row_for(rows, "a1")

    assert row.row_category == "measured_piece"
    assert row.occupancy_state == "occupied"
    assert row.detected_color == "white"
    assert row.detected_role == "king"
    assert row.confidence_metadata.square == 0.91
    assert row.confidence_metadata.color == 0.82
    assert row.confidence_metadata.role == 0.95
    assert row.failure_reason is None
    assert row.source_stages == (
        "square_sampling",
        "color_classifier",
        "role_classifier",
    )


def test_empty_square_row_does_not_require_color_or_role() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_empty_sample("d4")),
        color_rows=(),
        role_rows=(),
    )
    row = _row_for(rows, "d4")

    assert row.row_category == "empty_square"
    assert row.occupancy_state == "empty"
    assert row.detected_color is None
    assert row.detected_role is None
    assert row.failure_reason is None
    assert row.source_stages == ("square_sampling",)


def test_not_measured_square_becomes_unsupported() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_not_measured_sample("b2")),
        color_rows=(),
        role_rows=(),
    )
    row = _row_for(rows, "b2")

    assert row.row_category == "unsupported"
    assert row.occupancy_state == "not_measured"
    assert row.failure_reason == "invalid_board_bounds"


def test_missing_color_on_occupied_square_becomes_unsupported() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_occupied_sample("a1")),
        color_rows=(),
        role_rows=(_role_row("a1", "king"),),
    )
    row = _row_for(rows, "a1")

    assert row.row_category == "unsupported"
    assert row.detected_role == "king"
    assert row.failure_reason == "missing_color_row"


def test_missing_role_on_occupied_square_becomes_unsupported() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_occupied_sample("a1")),
        color_rows=(_color_row("a1", "white"),),
        role_rows=(),
    )
    row = _row_for(rows, "a1")

    assert row.row_category == "unsupported"
    assert row.detected_color == "white"
    assert row.failure_reason == "missing_role_row"


@pytest.mark.parametrize(
    ("color_result", "role_result", "expected_reason"),
    [
        ("ambiguous", "correct", "ambiguous_color"),
        ("unsupported", "correct", "unsupported_color"),
        ("not_measured", "correct", "not_measured_color"),
        ("correct", "ambiguous", "ambiguous_role"),
        ("correct", "unsupported", "unsupported_role"),
        ("correct", "not_measured", "not_measured_role"),
    ],
)
def test_blocking_color_or_role_results_become_unsupported(
    color_result: str,
    role_result: str,
    expected_reason: str,
) -> None:
    color = _color_row(
        "a1",
        "white",
        result=color_result,
        failure_reason=expected_reason if "color" in expected_reason else None,
    )
    role = _role_row(
        "a1",
        "king",
        result=role_result,
        failure_reason=expected_reason if "role" in expected_reason else None,
    )

    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_occupied_sample("a1")),
        color_rows=(color,),
        role_rows=(role,),
    )
    row = _row_for(rows, "a1")

    assert row.row_category == "unsupported"
    assert row.failure_reason == expected_reason


def test_wrong_classifier_results_still_preserve_measured_signal() -> None:
    rows = build_measured_piece_rows(
        fixture_id="fixture",
        square_samples=_samples(_occupied_sample("a1")),
        color_rows=(_color_row("a1", "black", result="wrong"),),
        role_rows=(_role_row("a1", "queen", result="wrong"),),
    )
    row = _row_for(rows, "a1")

    assert row.row_category == "measured_piece"
    assert row.detected_color == "black"
    assert row.detected_role == "queen"
    assert row.failure_reason is None


def test_duplicate_upstream_rows_fail_clearly() -> None:
    with pytest.raises(MeasuredPieceJoinError, match="duplicate_color_row"):
        build_measured_piece_rows(
            fixture_id="fixture",
            square_samples=_samples(_occupied_sample("a1")),
            color_rows=(
                _color_row("a1", "white"),
                _color_row("a1", "white"),
            ),
            role_rows=(_role_row("a1", "king"),),
        )


def test_missing_square_sample_fails_clearly() -> None:
    with pytest.raises(MeasuredPieceJoinError, match="missing_square_sample"):
        build_measured_piece_rows(
            fixture_id="fixture",
            square_samples=(_occupied_sample("a1"),),
            color_rows=(_color_row("a1", "white"),),
            role_rows=(_role_row("a1", "king"),),
        )


def test_approved_role_signal_fixtures_join_without_building_fen() -> None:
    manifest = _load_valid_manifest()
    all_rows = tuple(
        row
        for case in _role_signal_cases(manifest)
        for row in _build_case_rows(case)
    )

    assert len(all_rows) == 64 * len(ROLE_SIGNAL_FILENAMES)
    assert sum(row.row_category == "measured_piece" for row in all_rows) == 35
    assert sum(row.row_category == "empty_square" for row in all_rows) == 156
    assert sum(row.row_category == "unsupported" for row in all_rows) == 1
    assert sum(row.occupancy_state == "occupied" for row in all_rows) == 36
    assert {
        row.failure_reason
        for row in all_rows
        if row.row_category == "unsupported"
    } == {"ambiguous_color"}


def _build_case_rows(case: dict):
    decoded = _decode_case_image(case)
    samples = _sample_case(case, decoded)
    color_classification = classify_fixture_colors(
        audit=audit_fixture_role_color_signals(case, decoded),
        samples=samples,
    )
    role_classification = classify_fixture_roles(
        audit_fixture_role_signals_v2(case, decoded)
    )

    return build_measured_piece_rows(
        fixture_id=case["id"],
        square_samples=samples,
        color_rows=color_classification.rows,
        role_rows=role_classification.rows,
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


def _role_signal_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if case["expected_metrics"].get("role_signal_fixture")
    )


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


def _samples(*overrides: SquareSample) -> tuple[SquareSample, ...]:
    overrides_by_square = {sample.square: sample for sample in overrides}

    return tuple(
        overrides_by_square.get(square, _empty_sample(square))
        for square in _all_squares()
    )


def _occupied_sample(square: str) -> SquareSample:
    return SquareSample(
        fixture_id="fixture",
        square=square,
        row=0,
        column=0,
        detected_state="occupied",
        detected_piece=None,
        detected_color=None,
        confidence=0.91,
        failure_reason=None,
    )


def _empty_sample(square: str) -> SquareSample:
    return SquareSample(
        fixture_id="fixture",
        square=square,
        row=0,
        column=0,
        detected_state="empty",
        detected_piece=None,
        detected_color=None,
        confidence=0.88,
        failure_reason=None,
    )


def _not_measured_sample(square: str) -> SquareSample:
    return SquareSample(
        fixture_id="fixture",
        square=square,
        row=0,
        column=0,
        detected_state="not_measured",
        detected_piece=None,
        detected_color=None,
        confidence=None,
        failure_reason="invalid_board_bounds",
    )


def _color_row(
    square: str,
    detected_color: str | None,
    *,
    result: str = "correct",
    failure_reason: str | None = None,
) -> ColorClassificationRow:
    return ColorClassificationRow(
        fixture_id="fixture",
        square=square,
        expected_color=None,
        detected_color=detected_color,
        color_result=result,
        confidence=0.82 if detected_color is not None else None,
        failure_reason=failure_reason,
    )


def _role_row(
    square: str,
    detected_role: str | None,
    *,
    result: str = "correct",
    failure_reason: str | None = None,
) -> RoleClassificationRow:
    return RoleClassificationRow(
        fixture_id="fixture",
        square=square,
        expected_role=None,
        detected_role=detected_role,
        role_result=result,
        confidence=0.95 if detected_role is not None else None,
        failure_reason=failure_reason,
    )


def _row_for(rows: tuple, square: str):
    return next(row for row in rows if row.square == square)


def _all_squares() -> tuple[str, ...]:
    return tuple(f"{file}{rank}" for file in "abcdefgh" for rank in "12345678")
