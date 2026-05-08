from dataclasses import dataclass
from typing import Literal

from app.detection.role_signal_audit_v2 import (
    FixtureRoleSignalAuditV2,
    RoleSignalV2Sample,
)

RoleLabel = Literal["king", "queen", "rook", "bishop", "knight", "pawn"]
RoleResult = Literal[
    "correct",
    "wrong",
    "missing",
    "extra",
    "not_measured",
    "unsupported",
    "ambiguous",
]

SOURCE_STAGE = "role_classifier"
SUPPORTED_STYLE = "role-signal"


@dataclass(frozen=True)
class RoleClassificationRow:
    fixture_id: str
    square: str
    expected_role: str | None
    detected_role: RoleLabel | None
    role_result: RoleResult
    confidence: float | None
    failure_reason: str | None
    source_stage: str = SOURCE_STAGE


@dataclass(frozen=True)
class RoleClassificationSummary:
    fixture_id: str
    filename: str
    source: str
    style: str
    orientation: str
    occupied_square_count: int
    measured_role_count: int
    correct_count: int
    wrong_count: int
    missing_count: int
    extra_count: int
    not_measured_count: int
    unsupported_count: int
    ambiguous_count: int
    blocker_notes: tuple[str, ...]


@dataclass(frozen=True)
class FixtureRoleClassification:
    rows: tuple[RoleClassificationRow, ...]
    summary: RoleClassificationSummary


@dataclass(frozen=True)
class ShapeFeatures:
    foreground_count: int
    top_count: int
    middle_count: int
    bottom_count: int
    row_max: int
    column_max: int
    horizontal_symmetry_delta: int
    min_column: int
    max_column: int
    min_row: int
    max_row: int


def classify_fixture_roles(
    audit: FixtureRoleSignalAuditV2,
) -> FixtureRoleClassification:
    fixture_failure = _fixture_failure_reason(audit)
    rows = tuple(
        _classify_sample_role(sample, fixture_failure)
        for sample in audit.samples
    )

    return FixtureRoleClassification(
        rows=rows,
        summary=_summarize(audit, rows),
    )


def _fixture_failure_reason(audit: FixtureRoleSignalAuditV2) -> str | None:
    if audit.style != SUPPORTED_STYLE:
        return "unsupported_fixture"

    if audit.separability.status == "unsupported":
        return audit.separability.reason

    if audit.separability.status == "ambiguous":
        return "ambiguous_role"

    return None


def _classify_sample_role(
    sample: RoleSignalV2Sample,
    fixture_failure: str | None,
) -> RoleClassificationRow:
    if fixture_failure == "unsupported_fixture":
        return _row(sample, None, "unsupported", None, fixture_failure)

    if fixture_failure is not None:
        return _row(sample, None, "ambiguous", None, fixture_failure)

    if sample.signature is None:
        return _row(sample, None, "not_measured", None, "sample_unavailable")

    features = _shape_features(sample.signature)
    if features is None:
        return _row(sample, None, "ambiguous", None, "ambiguous_role")

    detected_role = _detect_role_from_features(features)
    if detected_role is None:
        return _row(sample, None, "ambiguous", None, "ambiguous_role")

    result: RoleResult = (
        "correct" if detected_role == sample.expected_role else "wrong"
    )

    return _row(
        sample,
        detected_role,
        result,
        _confidence(features),
        None,
    )


def _detect_role_from_features(features: ShapeFeatures) -> RoleLabel | None:
    if features.foreground_count >= 360 and features.top_count >= 70:
        return "rook"

    if features.row_max >= 24 or features.min_column == 0:
        return "queen"

    if features.bottom_count >= 100:
        return "pawn"

    if features.horizontal_symmetry_delta >= 24:
        return "knight"

    if features.max_column - features.min_column <= 15:
        return "bishop"

    if features.column_max >= 23 and features.row_max >= 22:
        return "king"

    return None


def _shape_features(signature: tuple[int, ...]) -> ShapeFeatures | None:
    side = int(len(signature) ** 0.5)
    if side <= 0 or side * side != len(signature):
        return None

    rows = [
        sum(signature[row * side : (row + 1) * side])
        for row in range(side)
    ]
    columns = [
        sum(signature[column::side])
        for column in range(side)
    ]
    active_rows = tuple(index for index, count in enumerate(rows) if count)
    active_columns = tuple(index for index, count in enumerate(columns) if count)

    if not active_rows or not active_columns:
        return None

    third = side // 4
    top_count = sum(rows[:third])
    bottom_count = sum(rows[-third:])
    middle_count = sum(rows[third:-third])

    return ShapeFeatures(
        foreground_count=sum(signature),
        top_count=top_count,
        middle_count=middle_count,
        bottom_count=bottom_count,
        row_max=max(rows),
        column_max=max(columns),
        horizontal_symmetry_delta=sum(
            abs(columns[index] - columns[(side - 1) - index])
            for index in range(side // 2)
        ),
        min_column=min(active_columns),
        max_column=max(active_columns),
        min_row=min(active_rows),
        max_row=max(active_rows),
    )


def _summarize(
    audit: FixtureRoleSignalAuditV2,
    rows: tuple[RoleClassificationRow, ...],
) -> RoleClassificationSummary:
    blocker_notes = tuple(
        sorted(
            {
                row.failure_reason
                for row in rows
                if row.failure_reason is not None
                and row.role_result != "correct"
            }
        )
    )

    return RoleClassificationSummary(
        fixture_id=audit.fixture_id,
        filename=audit.filename,
        source=audit.source,
        style=audit.style,
        orientation=audit.orientation,
        occupied_square_count=audit.occupied_square_count,
        measured_role_count=sum(row.detected_role is not None for row in rows),
        correct_count=_count(rows, "correct"),
        wrong_count=_count(rows, "wrong"),
        missing_count=_count(rows, "missing"),
        extra_count=_count(rows, "extra"),
        not_measured_count=_count(rows, "not_measured"),
        unsupported_count=_count(rows, "unsupported"),
        ambiguous_count=_count(rows, "ambiguous"),
        blocker_notes=blocker_notes,
    )


def _row(
    sample: RoleSignalV2Sample,
    detected_role: RoleLabel | None,
    result: RoleResult,
    confidence: float | None,
    failure_reason: str | None,
) -> RoleClassificationRow:
    return RoleClassificationRow(
        fixture_id=sample.fixture_id,
        square=sample.square,
        expected_role=sample.expected_role or None,
        detected_role=detected_role,
        role_result=result,
        confidence=confidence,
        failure_reason=failure_reason,
    )


def _confidence(features: ShapeFeatures) -> float:
    return round(
        min(
            1.0,
            max(
                0.5,
                features.foreground_count / 400,
            ),
        ),
        2,
    )


def _count(rows: tuple[RoleClassificationRow, ...], result: RoleResult) -> int:
    return sum(row.role_result == result for row in rows)
