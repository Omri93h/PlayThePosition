import json
from pathlib import Path

from app.detection.color_classifier import (
    SOURCE_STAGE,
    classify_fixture_colors,
)
from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.role_color_signal_audit import (
    SquareSignal,
    audit_fixture_role_color_signals,
)
from app.detection.square_sampling import SquareSample, sample_fixture_squares

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_approved_fixture_colors_classify_without_role_classification() -> None:
    manifest = _load_valid_manifest()
    results = tuple(_classify_case(case) for case in _block_12_cases(manifest))
    summaries = tuple(result.summary for result in results)

    assert len(results) == 8
    assert sum(summary.occupied_square_count for summary in summaries) == 167
    assert sum(summary.measured_color_count for summary in summaries) == 159
    assert sum(summary.correct_count for summary in summaries) == 159
    assert sum(summary.wrong_count for summary in summaries) == 0
    assert sum(summary.missing_count for summary in summaries) == 0
    assert sum(summary.extra_count for summary in summaries) == 0
    assert sum(summary.not_measured_count for summary in summaries) == 0
    assert sum(summary.unsupported_count for summary in summaries) == 0
    assert sum(summary.ambiguous_count for summary in summaries) == 8

    all_rows = tuple(row for result in results for row in result.rows)
    assert {row.source_stage for row in all_rows} == {SOURCE_STAGE}
    assert {row.role_result for row in all_rows} == {"not_measured"}
    assert {row.detected_role for row in all_rows} == {None}
    assert {row.role_failure_reason for row in all_rows} == {
        "classifier_not_configured"
    }


def test_detected_colors_match_expected_fixture_metadata() -> None:
    manifest = _load_valid_manifest()

    for case in _block_12_cases(manifest):
        result = _classify_case(case)
        expected_by_square = {
            piece["square"]: piece["color"] for piece in case["expected_pieces"]
        }

        assert len(result.rows) == len(expected_by_square)

        for row in result.rows:
            assert row.expected_color == expected_by_square[row.square]

            if row.color_result == "correct":
                assert row.detected_color == expected_by_square[row.square]
                assert row.confidence is not None
                assert row.failure_reason is None
            else:
                assert row.detected_color is None
                assert row.color_result == "ambiguous"
                assert row.confidence is None
                assert row.failure_reason == "ambiguous_color"


def test_role_signal_fixture_colors_classify_from_owned_marker_pixels() -> None:
    manifest = _load_valid_manifest()
    results = tuple(_classify_case(case) for case in _role_signal_cases(manifest))
    summaries = tuple(result.summary for result in results)

    assert len(results) == 3
    assert sum(summary.occupied_square_count for summary in summaries) == 36
    assert sum(summary.measured_color_count for summary in summaries) == 36
    assert sum(summary.correct_count for summary in summaries) == 36
    assert sum(summary.wrong_count for summary in summaries) == 0
    assert sum(summary.missing_count for summary in summaries) == 0
    assert sum(summary.extra_count for summary in summaries) == 0
    assert sum(summary.not_measured_count for summary in summaries) == 0
    assert sum(summary.unsupported_count for summary in summaries) == 0
    assert sum(summary.ambiguous_count for summary in summaries) == 0

    for case, result in zip(_role_signal_cases(manifest), results, strict=True):
        expected_by_square = {
            piece["square"]: piece["color"] for piece in case["expected_pieces"]
        }

        assert len(result.rows) == len(expected_by_square)
        for row in result.rows:
            assert row.detected_color == expected_by_square[row.square]
            assert row.color_result == "correct"
            assert row.failure_reason is None


def test_empty_or_missing_occupancy_samples_do_not_guess_color() -> None:
    manifest = _load_valid_manifest()
    case = manifest["cases"][0]
    decoded = _decode_case_image(case)
    audit = audit_fixture_role_color_signals(case, decoded)
    samples = tuple(
        SquareSample(
            fixture_id=sample.fixture_id,
            square=sample.square,
            row=sample.row,
            column=sample.column,
            detected_state="empty",
            detected_piece=None,
            detected_color=None,
            confidence=sample.confidence,
            failure_reason=None,
        )
        for sample in _sample_case(case, decoded)
    )

    result = classify_fixture_colors(audit=audit, samples=samples)

    assert {row.detected_color for row in result.rows} == {None}
    assert {row.color_result for row in result.rows} == {"missing"}
    assert {row.failure_reason for row in result.rows} == {"occupancy_missing"}


def test_ambiguous_color_signal_does_not_guess() -> None:
    signals = (
        _signal("a1", "white", (100, 100, 100), 0.2, 50),
        _signal("a2", "black", (103, 103, 103), 0.2, 52),
    )
    audit = _audit_with_signals(signals)
    samples = tuple(
        SquareSample(
            fixture_id="ambiguous_fixture",
            square=signal.square,
            row=0,
            column=0,
            detected_state="occupied",
            detected_piece=None,
            detected_color=None,
            confidence=0.8,
            failure_reason=None,
        )
        for signal in signals
    )

    result = classify_fixture_colors(audit=audit, samples=samples)

    assert {row.detected_color for row in result.rows} == {None}
    assert {row.color_result for row in result.rows} == {"ambiguous"}
    assert {row.failure_reason for row in result.rows} == {"ambiguous_color"}


def test_missing_signal_returns_not_measured_without_guessing() -> None:
    signal = SquareSignal(
        fixture_id="missing_signal_fixture",
        square="a1",
        expected_piece="king",
        expected_color="white",
        foreground_average_rgb=None,
        background_average_rgb=None,
        foreground_ratio=None,
        max_distance=None,
        failure_reason="sample_unavailable",
    )
    audit = _audit_with_signals((signal,))
    sample = SquareSample(
        fixture_id="missing_signal_fixture",
        square="a1",
        row=0,
        column=0,
        detected_state="occupied",
        detected_piece=None,
        detected_color=None,
        confidence=0.8,
        failure_reason=None,
    )

    result = classify_fixture_colors(audit=audit, samples=(sample,))

    assert len(result.rows) == 1
    assert result.rows[0].detected_color is None
    assert result.rows[0].color_result == "not_measured"
    assert result.rows[0].failure_reason == "sample_unavailable"


def _classify_case(case: dict):
    decoded = _decode_case_image(case)
    audit = audit_fixture_role_color_signals(case, decoded)

    return classify_fixture_colors(
        audit=audit,
        samples=_sample_case(case, decoded),
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


def _block_12_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if not case["expected_metrics"].get("role_signal_fixture")
    )


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


def _signal(
    square: str,
    color: str,
    foreground: tuple[int, int, int],
    foreground_ratio: float,
    max_distance: float,
) -> SquareSignal:
    return SquareSignal(
        fixture_id="ambiguous_fixture",
        square=square,
        expected_piece="king",
        expected_color=color,
        foreground_average_rgb=foreground,
        background_average_rgb=(0, 0, 0),
        foreground_ratio=foreground_ratio,
        max_distance=max_distance,
        failure_reason=None,
    )


def _audit_with_signals(signals: tuple[SquareSignal, ...]):
    return type(
        "FixtureSignalAuditStub",
        (),
        {
            "fixture_id": signals[0].fixture_id,
            "filename": "fixture.png",
            "source": "test",
            "style": "test",
            "orientation": "white-bottom",
            "occupied_square_count": len(signals),
            "measured_signal_count": sum(
                signal.signature is not None for signal in signals
            ),
            "square_signals": signals,
        },
    )()
