from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from app.detection.square_sampling import SquareSample

FILES = "abcdefgh"
RANKS = "12345678"
ROLE_COLOR_NOT_SUPPORTED = "role_color_not_supported"

MeasurementCategory = Literal["correct", "wrong", "missing", "extra", "not_measured"]


@dataclass(frozen=True)
class PieceMeasurementRow:
    fixture_id: str
    square: str
    expected_piece: str | None
    expected_color: str | None
    detected_piece: str | None
    detected_color: str | None
    result_category: MeasurementCategory
    confidence: float | None
    failure_reason: str | None
    source_stage: str


@dataclass(frozen=True)
class PieceMeasurementSummary:
    fixture_id: str
    filename: str
    source: str
    style: str
    orientation: str
    total_squares: int
    expected_occupied_count: int
    sampled_occupied_count: int
    empty_square_correct_count: int
    occupancy_matched_occupied_count: int
    correct_count: int
    wrong_count: int
    missing_count: int
    extra_count: int
    not_measured_count: int
    role_color_unsupported_count: int
    blocker_notes: tuple[str, ...]


@dataclass(frozen=True)
class FixturePieceMeasurement:
    rows: tuple[PieceMeasurementRow, ...]
    summary: PieceMeasurementSummary


def measure_fixture_piece_samples(
    case: Mapping[str, Any],
    samples: Sequence[SquareSample],
) -> FixturePieceMeasurement:
    expected_by_square = _expected_pieces_by_square(case)
    rows = tuple(
        _measure_square(
            fixture_id=str(case["id"]),
            expected=expected_by_square.get(sample.square),
            sample=sample,
        )
        for sample in samples
    )

    return FixturePieceMeasurement(
        rows=rows,
        summary=_summarize_fixture(case, rows, expected_by_square),
    )


def _measure_square(
    *,
    fixture_id: str,
    expected: Mapping[str, str] | None,
    sample: SquareSample,
) -> PieceMeasurementRow:
    expected_piece = expected["piece"] if expected else None
    expected_color = expected["color"] if expected else None

    if sample.detected_state == "not_measured":
        return PieceMeasurementRow(
            fixture_id=fixture_id,
            square=sample.square,
            expected_piece=expected_piece,
            expected_color=expected_color,
            detected_piece=sample.detected_piece,
            detected_color=sample.detected_color,
            result_category="not_measured",
            confidence=sample.confidence,
            failure_reason=sample.failure_reason or "square_not_measured",
            source_stage=sample.source_stage,
        )

    if expected is None and sample.detected_state == "empty":
        return PieceMeasurementRow(
            fixture_id=fixture_id,
            square=sample.square,
            expected_piece=None,
            expected_color=None,
            detected_piece=None,
            detected_color=None,
            result_category="correct",
            confidence=sample.confidence,
            failure_reason=None,
            source_stage=sample.source_stage,
        )

    if expected is not None and sample.detected_state == "empty":
        return PieceMeasurementRow(
            fixture_id=fixture_id,
            square=sample.square,
            expected_piece=expected_piece,
            expected_color=expected_color,
            detected_piece=None,
            detected_color=None,
            result_category="missing",
            confidence=sample.confidence,
            failure_reason=None,
            source_stage=sample.source_stage,
        )

    if expected is None and sample.detected_state == "occupied":
        return PieceMeasurementRow(
            fixture_id=fixture_id,
            square=sample.square,
            expected_piece=None,
            expected_color=None,
            detected_piece=sample.detected_piece,
            detected_color=sample.detected_color,
            result_category="extra",
            confidence=sample.confidence,
            failure_reason=None,
            source_stage=sample.source_stage,
        )

    return PieceMeasurementRow(
        fixture_id=fixture_id,
        square=sample.square,
        expected_piece=expected_piece,
        expected_color=expected_color,
        detected_piece=sample.detected_piece,
        detected_color=sample.detected_color,
        result_category="not_measured",
        confidence=sample.confidence,
        failure_reason=ROLE_COLOR_NOT_SUPPORTED,
        source_stage=sample.source_stage,
    )


def _summarize_fixture(
    case: Mapping[str, Any],
    rows: tuple[PieceMeasurementRow, ...],
    expected_by_square: Mapping[str, Mapping[str, str]],
) -> PieceMeasurementSummary:
    sampled_occupied_count = sum(
        1 for row in rows if _sampled_occupied_without_role(row)
    )
    role_color_unsupported_count = sum(
        row.failure_reason == ROLE_COLOR_NOT_SUPPORTED for row in rows
    )
    blocker_notes = (
        ("role/color recognition is not supported by square sampling",)
        if role_color_unsupported_count
        else ()
    )

    return PieceMeasurementSummary(
        fixture_id=str(case["id"]),
        filename=str(case["filename"]),
        source=str(case["source"]),
        style=str(case["style"]),
        orientation=str(case["orientation"]),
        total_squares=len(rows),
        expected_occupied_count=len(expected_by_square),
        sampled_occupied_count=sampled_occupied_count,
        empty_square_correct_count=sum(
            row.result_category == "correct" for row in rows
        ),
        occupancy_matched_occupied_count=role_color_unsupported_count,
        correct_count=sum(row.result_category == "correct" for row in rows),
        wrong_count=sum(row.result_category == "wrong" for row in rows),
        missing_count=sum(row.result_category == "missing" for row in rows),
        extra_count=sum(row.result_category == "extra" for row in rows),
        not_measured_count=sum(
            row.result_category == "not_measured" for row in rows
        ),
        role_color_unsupported_count=role_color_unsupported_count,
        blocker_notes=blocker_notes,
    )


def _sampled_occupied_without_role(row: PieceMeasurementRow) -> bool:
    return (
        row.result_category in {"extra", "not_measured"}
        and row.confidence is not None
        and row.failure_reason != "square_not_measured"
    )


def _expected_pieces_by_square(
    case: Mapping[str, Any],
) -> dict[str, Mapping[str, str]]:
    return {
        str(piece["square"]): piece
        for piece in case.get("expected_pieces", [])
        if str(piece.get("square")) in _all_squares()
    }


def _all_squares() -> set[str]:
    return {f"{file}{rank}" for file in FILES for rank in RANKS}
