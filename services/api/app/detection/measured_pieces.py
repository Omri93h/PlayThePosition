from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.detection.color_classifier import ColorClassificationRow
from app.detection.role_classifier import RoleClassificationRow
from app.detection.square_sampling import SquareSample

OccupancyState = Literal["empty", "occupied", "not_measured"]
RowCategory = Literal["measured_piece", "empty_square", "unsupported"]

ALL_SQUARES = frozenset(
    f"{file}{rank}" for file in "abcdefgh" for rank in "12345678"
)
BLOCKING_RESULTS = frozenset(
    {"ambiguous", "unsupported", "missing", "extra", "not_measured"}
)


class MeasuredPieceJoinError(ValueError):
    """Raised when upstream measurement rows cannot be joined safely."""


@dataclass(frozen=True)
class ConfidenceMetadata:
    square: float | None
    color: float | None
    role: float | None


@dataclass(frozen=True)
class MeasuredPieceRow:
    fixture_id: str
    square: str
    occupancy_state: OccupancyState
    detected_color: str | None
    detected_role: str | None
    row_category: RowCategory
    confidence_metadata: ConfidenceMetadata
    failure_reason: str | None
    source_stages: tuple[str, ...]


def build_measured_piece_rows(
    *,
    fixture_id: str,
    square_samples: Sequence[SquareSample],
    color_rows: Sequence[ColorClassificationRow],
    role_rows: Sequence[RoleClassificationRow],
) -> tuple[MeasuredPieceRow, ...]:
    sample_by_square = _index_by_square(
        fixture_id=fixture_id,
        rows=square_samples,
        source_name="square_sample",
    )
    color_by_square = _index_by_square(
        fixture_id=fixture_id,
        rows=color_rows,
        source_name="color_row",
    )
    role_by_square = _index_by_square(
        fixture_id=fixture_id,
        rows=role_rows,
        source_name="role_row",
    )

    if set(sample_by_square) != ALL_SQUARES:
        raise MeasuredPieceJoinError("missing_square_sample")

    return tuple(
        _build_row(
            sample=sample,
            color_row=color_by_square.get(sample.square),
            role_row=role_by_square.get(sample.square),
        )
        for sample in square_samples
    )


def _build_row(
    *,
    sample: SquareSample,
    color_row: ColorClassificationRow | None,
    role_row: RoleClassificationRow | None,
) -> MeasuredPieceRow:
    source_stages = _source_stages(sample, color_row, role_row)
    confidence_metadata = ConfidenceMetadata(
        square=sample.confidence,
        color=color_row.confidence if color_row is not None else None,
        role=role_row.confidence if role_row is not None else None,
    )
    detected_color = color_row.detected_color if color_row is not None else None
    detected_role = role_row.detected_role if role_row is not None else None

    if sample.detected_state == "not_measured":
        return _row(
            sample=sample,
            detected_color=detected_color,
            detected_role=detected_role,
            row_category="unsupported",
            confidence_metadata=confidence_metadata,
            failure_reason=sample.failure_reason or "not_measured_square",
            source_stages=source_stages,
        )

    if sample.detected_state == "empty":
        extra_reasons = _empty_square_failure_reasons(color_row, role_row)
        if extra_reasons:
            return _row(
                sample=sample,
                detected_color=detected_color,
                detected_role=detected_role,
                row_category="unsupported",
                confidence_metadata=confidence_metadata,
                failure_reason=_join_reasons(extra_reasons),
                source_stages=source_stages,
            )

        return _row(
            sample=sample,
            detected_color=None,
            detected_role=None,
            row_category="empty_square",
            confidence_metadata=confidence_metadata,
            failure_reason=None,
            source_stages=source_stages,
        )

    failure_reasons = tuple(
        reason
        for reason in (
            _color_failure_reason(color_row),
            _role_failure_reason(role_row),
        )
        if reason is not None
    )
    if failure_reasons:
        return _row(
            sample=sample,
            detected_color=detected_color,
            detected_role=detected_role,
            row_category="unsupported",
            confidence_metadata=confidence_metadata,
            failure_reason=_join_reasons(failure_reasons),
            source_stages=source_stages,
        )

    return _row(
        sample=sample,
        detected_color=detected_color,
        detected_role=detected_role,
        row_category="measured_piece",
        confidence_metadata=confidence_metadata,
        failure_reason=None,
        source_stages=source_stages,
    )


def _index_by_square(
    *,
    fixture_id: str,
    rows: Sequence[SquareSample | ColorClassificationRow | RoleClassificationRow],
    source_name: str,
) -> dict[str, SquareSample | ColorClassificationRow | RoleClassificationRow]:
    indexed: dict[
        str,
        SquareSample | ColorClassificationRow | RoleClassificationRow,
    ] = {}

    for row in rows:
        if row.fixture_id != fixture_id:
            raise MeasuredPieceJoinError(f"{source_name}_fixture_mismatch")

        if row.square in indexed:
            raise MeasuredPieceJoinError(f"duplicate_{source_name}")

        indexed[row.square] = row

    return indexed


def _empty_square_failure_reasons(
    color_row: ColorClassificationRow | None,
    role_row: RoleClassificationRow | None,
) -> tuple[str, ...]:
    reasons: list[str] = []

    if color_row is not None:
        reasons.append(_result_failure("color", color_row.color_result))

    if role_row is not None:
        reasons.append(_result_failure("role", role_row.role_result))

    return tuple(reasons)


def _color_failure_reason(row: ColorClassificationRow | None) -> str | None:
    if row is None:
        return "missing_color_row"

    if row.color_result in BLOCKING_RESULTS:
        return row.failure_reason or _result_failure("color", row.color_result)

    if row.detected_color is None:
        return "missing_color"

    return None


def _role_failure_reason(row: RoleClassificationRow | None) -> str | None:
    if row is None:
        return "missing_role_row"

    if row.role_result in BLOCKING_RESULTS:
        return row.failure_reason or _result_failure("role", row.role_result)

    if row.detected_role is None:
        return "missing_role"

    return None


def _result_failure(prefix: str, result: str) -> str:
    return f"{result}_{prefix}"


def _row(
    *,
    sample: SquareSample,
    detected_color: str | None,
    detected_role: str | None,
    row_category: RowCategory,
    confidence_metadata: ConfidenceMetadata,
    failure_reason: str | None,
    source_stages: tuple[str, ...],
) -> MeasuredPieceRow:
    return MeasuredPieceRow(
        fixture_id=sample.fixture_id,
        square=sample.square,
        occupancy_state=sample.detected_state,
        detected_color=detected_color,
        detected_role=detected_role,
        row_category=row_category,
        confidence_metadata=confidence_metadata,
        failure_reason=failure_reason,
        source_stages=source_stages,
    )


def _source_stages(
    sample: SquareSample,
    color_row: ColorClassificationRow | None,
    role_row: RoleClassificationRow | None,
) -> tuple[str, ...]:
    stages = [sample.source_stage]

    if color_row is not None:
        stages.append(color_row.source_stage)

    if role_row is not None:
        stages.append(role_row.source_stage)

    return tuple(dict.fromkeys(stages))


def _join_reasons(reasons: tuple[str, ...]) -> str:
    return ";".join(reasons)
