from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from app.detection.role_color_signal_audit import FixtureSignalAudit, SquareSignal
from app.detection.square_sampling import SquareSample

ColorLabel = Literal["white", "black"]
ColorResult = Literal[
    "correct",
    "wrong",
    "missing",
    "extra",
    "not_measured",
    "unsupported",
    "ambiguous",
]

SOURCE_STAGE = "color_classifier"
MIN_MODEL_SEPARATION = 80.0
MIN_CLASSIFICATION_MARGIN = 10.0
MIN_OWNED_MARKER_RATIO = 0.1
MIN_OWNED_MARKER_MARGIN = 0.1


@dataclass(frozen=True)
class ColorReferenceModel:
    fixture_id: str
    white_signature: tuple[float, ...]
    black_signature: tuple[float, ...]
    separation: float
    source_stage: str = SOURCE_STAGE


@dataclass(frozen=True)
class ColorClassificationRow:
    fixture_id: str
    square: str
    expected_color: str | None
    detected_color: ColorLabel | None
    color_result: ColorResult
    confidence: float | None
    failure_reason: str | None
    source_stage: str = SOURCE_STAGE
    detected_role: None = None
    role_result: Literal["not_measured"] = "not_measured"
    role_failure_reason: str = "classifier_not_configured"


@dataclass(frozen=True)
class ColorClassificationSummary:
    fixture_id: str
    filename: str
    source: str
    style: str
    orientation: str
    occupied_square_count: int
    measured_color_count: int
    correct_count: int
    wrong_count: int
    missing_count: int
    extra_count: int
    not_measured_count: int
    unsupported_count: int
    ambiguous_count: int
    blocker_notes: tuple[str, ...]


@dataclass(frozen=True)
class FixtureColorClassification:
    rows: tuple[ColorClassificationRow, ...]
    summary: ColorClassificationSummary


def classify_fixture_colors(
    *,
    audit: FixtureSignalAudit,
    samples: Sequence[SquareSample],
) -> FixtureColorClassification:
    model = _build_reference_model(audit)
    sample_by_square = {sample.square: sample for sample in samples}
    rows = tuple(
        _classify_signal_color(
            signal=signal,
            sample=sample_by_square.get(signal.square),
            model=model,
        )
        for signal in audit.square_signals
    )

    return FixtureColorClassification(
        rows=rows,
        summary=_summarize(audit, rows),
    )


def _build_reference_model(
    audit: FixtureSignalAudit,
) -> ColorReferenceModel | ColorClassificationRow:
    signatures_by_color = _signatures_by_color(audit.square_signals)

    if set(signatures_by_color) != {"white", "black"}:
        return _fixture_failure(
            audit.fixture_id,
            "unsupported",
            "unsupported_fixture",
        )

    white_signature = _average_signature(signatures_by_color["white"])
    black_signature = _average_signature(signatures_by_color["black"])
    separation = _signature_distance(white_signature, black_signature)

    if separation < MIN_MODEL_SEPARATION:
        return _fixture_failure(
            audit.fixture_id,
            "ambiguous",
            "ambiguous_color",
        )

    return ColorReferenceModel(
        fixture_id=audit.fixture_id,
        white_signature=white_signature,
        black_signature=black_signature,
        separation=round(separation, 2),
    )


def _classify_signal_color(
    *,
    signal: SquareSignal,
    sample: SquareSample | None,
    model: ColorReferenceModel | ColorClassificationRow,
) -> ColorClassificationRow:
    if sample is None or sample.detected_state == "not_measured":
        return _row(signal, None, "not_measured", None, "occupancy_missing")

    if sample.detected_state == "empty":
        return _row(signal, None, "missing", None, "occupancy_missing")

    if signal.signature is None:
        return _row(signal, None, "not_measured", None, "sample_unavailable")

    marker_color = _classify_owned_marker_color(signal)
    if marker_color is not None:
        detected_color, result, confidence, failure_reason = marker_color
        if result != "correct":
            return _row(signal, detected_color, result, confidence, failure_reason)

        result: ColorResult = (
            "correct" if detected_color == signal.expected_color else "wrong"
        )
        return _row(signal, detected_color, result, confidence, None)

    if isinstance(model, ColorClassificationRow):
        return _row(
            signal,
            None,
            model.color_result,
            None,
            model.failure_reason,
        )

    white_distance = _signature_distance(signal.signature, model.white_signature)
    black_distance = _signature_distance(signal.signature, model.black_signature)
    margin = abs(white_distance - black_distance)

    if margin < MIN_CLASSIFICATION_MARGIN:
        return _row(signal, None, "ambiguous", None, "ambiguous_color")

    detected_color: ColorLabel = (
        "white" if white_distance < black_distance else "black"
    )
    result: ColorResult = (
        "correct" if detected_color == signal.expected_color else "wrong"
    )

    return _row(
        signal,
        detected_color,
        result,
        _confidence(margin, model.separation),
        None,
    )


def _classify_owned_marker_color(
    signal: SquareSignal,
) -> tuple[ColorLabel | None, ColorResult, float | None, str | None] | None:
    white_ratio = signal.owned_white_marker_ratio
    black_ratio = signal.owned_black_marker_ratio
    if white_ratio is None or black_ratio is None:
        return None

    strongest = max(white_ratio, black_ratio)
    margin = abs(white_ratio - black_ratio)
    if strongest < MIN_OWNED_MARKER_RATIO:
        return None

    if margin < MIN_OWNED_MARKER_MARGIN:
        return None, "ambiguous", None, "ambiguous_color"

    detected_color: ColorLabel = "white" if white_ratio > black_ratio else "black"
    confidence = round(min(1.0, max(0.5, margin / strongest)), 2)
    return detected_color, "correct", confidence, None


def _summarize(
    audit: FixtureSignalAudit,
    rows: tuple[ColorClassificationRow, ...],
) -> ColorClassificationSummary:
    blocker_notes = tuple(
        sorted(
            {
                row.failure_reason
                for row in rows
                if row.failure_reason is not None
                and row.color_result != "correct"
            }
        )
    )

    return ColorClassificationSummary(
        fixture_id=audit.fixture_id,
        filename=audit.filename,
        source=audit.source,
        style=audit.style,
        orientation=audit.orientation,
        occupied_square_count=audit.occupied_square_count,
        measured_color_count=sum(row.detected_color is not None for row in rows),
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
    signal: SquareSignal,
    detected_color: ColorLabel | None,
    result: ColorResult,
    confidence: float | None,
    failure_reason: str | None,
) -> ColorClassificationRow:
    return ColorClassificationRow(
        fixture_id=signal.fixture_id,
        square=signal.square,
        expected_color=signal.expected_color or None,
        detected_color=detected_color,
        color_result=result,
        confidence=confidence,
        failure_reason=failure_reason,
    )


def _fixture_failure(
    fixture_id: str,
    result: Literal["unsupported", "ambiguous"],
    failure_reason: str,
) -> ColorClassificationRow:
    return ColorClassificationRow(
        fixture_id=fixture_id,
        square="",
        expected_color=None,
        detected_color=None,
        color_result=result,
        confidence=None,
        failure_reason=failure_reason,
    )


def _signatures_by_color(
    signals: Sequence[SquareSignal],
) -> dict[str, tuple[tuple[float, ...], ...]]:
    grouped: dict[str, list[tuple[float, ...]]] = {}

    for signal in signals:
        if signal.signature is None:
            continue

        grouped.setdefault(signal.expected_color, []).append(signal.signature)

    return {key: tuple(value) for key, value in grouped.items()}


def _average_signature(
    signatures: tuple[tuple[float, ...], ...],
) -> tuple[float, ...]:
    return tuple(
        sum(signature[index] for signature in signatures) / len(signatures)
        for index in range(len(signatures[0]))
    )


def _signature_distance(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    return sum(
        (left - right) ** 2 for left, right in zip(first, second, strict=True)
    ) ** 0.5


def _confidence(margin: float, separation: float) -> float:
    return round(min(1.0, max(0.5, margin / separation)), 2)


def _count(rows: tuple[ColorClassificationRow, ...], result: ColorResult) -> int:
    return sum(row.color_result == result for row in rows)
