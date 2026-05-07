from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage
from app.detection.square_sampling import SquareRegion, derive_square_regions

SignalStatus = Literal["feasible", "ambiguous", "unsupported"]

BACKGROUND_SAMPLE_POINTS = (
    (0.18, 0.18),
    (0.82, 0.18),
    (0.18, 0.82),
    (0.82, 0.82),
)
INNER_SAMPLE_MIN = 0.28
INNER_SAMPLE_MAX = 0.72
FOREGROUND_DISTANCE_THRESHOLD = 35.0
COLOR_FEASIBLE_DISTANCE = 80.0
COLOR_AMBIGUOUS_DISTANCE = 30.0
ROLE_FEASIBLE_DISTANCE = 30.0
REQUIRED_ROLE_COUNT = 6


@dataclass(frozen=True)
class SquareSignal:
    fixture_id: str
    square: str
    expected_piece: str
    expected_color: str
    foreground_average_rgb: tuple[int, int, int] | None
    background_average_rgb: tuple[int, int, int] | None
    foreground_ratio: float | None
    max_distance: float | None
    failure_reason: str | None
    source_stage: str = "role_color_signal_audit"

    @property
    def signature(self) -> tuple[float, ...] | None:
        if (
            self.foreground_average_rgb is None
            or self.foreground_ratio is None
            or self.max_distance is None
        ):
            return None

        return (
            float(self.foreground_average_rgb[0]),
            float(self.foreground_average_rgb[1]),
            float(self.foreground_average_rgb[2]),
            self.foreground_ratio * 255,
            self.max_distance,
        )


@dataclass(frozen=True)
class FeasibilityResult:
    status: SignalStatus
    reason: str
    distance: float | None = None
    observed_groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class FixtureSignalAudit:
    fixture_id: str
    filename: str
    source: str
    style: str
    orientation: str
    occupied_square_count: int
    measured_signal_count: int
    color: FeasibilityResult
    role: FeasibilityResult
    square_signals: tuple[SquareSignal, ...]


def audit_fixture_role_color_signals(
    case: Mapping[str, Any],
    image: DecodedImage,
) -> FixtureSignalAudit:
    regions = {
        region.square: region
        for region in derive_square_regions(
            _board_bounds(case),
            str(case["orientation"]),
        )
    }
    square_signals = tuple(
        _sample_expected_piece_signal(
            fixture_id=str(case["id"]),
            image=image,
            region=regions.get(str(piece["square"])),
            piece=piece,
        )
        for piece in case.get("expected_pieces", [])
        if isinstance(piece, Mapping)
    )

    measured_signals = tuple(
        signal for signal in square_signals if signal.signature is not None
    )

    return FixtureSignalAudit(
        fixture_id=str(case["id"]),
        filename=str(case["filename"]),
        source=str(case["source"]),
        style=str(case["style"]),
        orientation=str(case["orientation"]),
        occupied_square_count=len(square_signals),
        measured_signal_count=len(measured_signals),
        color=_color_feasibility(measured_signals),
        role=_role_feasibility(measured_signals),
        square_signals=square_signals,
    )


def _sample_expected_piece_signal(
    *,
    fixture_id: str,
    image: DecodedImage,
    region: SquareRegion | None,
    piece: Mapping[str, Any],
) -> SquareSignal:
    square = str(piece.get("square", ""))
    expected_piece = str(piece.get("piece", ""))
    expected_color = str(piece.get("color", ""))

    if region is None:
        return _unavailable_signal(
            fixture_id,
            square,
            expected_piece,
            expected_color,
            "sample_unavailable",
        )

    background_samples = tuple(
        _sample_relative_pixel(image, region, x, y)
        for x, y in BACKGROUND_SAMPLE_POINTS
    )
    background = _average_pixel(background_samples)
    inner_pixels = _inner_region_pixels(image, region)

    if not inner_pixels:
        return _unavailable_signal(
            fixture_id,
            square,
            expected_piece,
            expected_color,
            "sample_unavailable",
        )

    distances = tuple(_color_distance(pixel, background) for pixel in inner_pixels)
    foreground_pixels = tuple(
        pixel
        for pixel, distance in zip(inner_pixels, distances, strict=True)
        if distance > FOREGROUND_DISTANCE_THRESHOLD
    )

    if not foreground_pixels:
        return _unavailable_signal(
            fixture_id,
            square,
            expected_piece,
            expected_color,
            "sample_unavailable",
        )

    return SquareSignal(
        fixture_id=fixture_id,
        square=square,
        expected_piece=expected_piece,
        expected_color=expected_color,
        foreground_average_rgb=_average_pixel(foreground_pixels),
        background_average_rgb=background,
        foreground_ratio=round(len(foreground_pixels) / len(inner_pixels), 4),
        max_distance=round(max(distances), 2),
        failure_reason=None,
    )


def _color_feasibility(signals: tuple[SquareSignal, ...]) -> FeasibilityResult:
    by_color = _signals_by(signals, "expected_color")

    if set(by_color) != {"white", "black"}:
        return FeasibilityResult(
            status="unsupported",
            reason="requires_both_colors",
            observed_groups=tuple(sorted(by_color)),
        )

    white = _average_signature(by_color["white"])
    black = _average_signature(by_color["black"])
    distance = round(_signature_distance(white, black), 2)

    if distance >= COLOR_FEASIBLE_DISTANCE:
        return FeasibilityResult(
            status="feasible",
            reason="white_black_signal_separable",
            distance=distance,
            observed_groups=("black", "white"),
        )

    if distance >= COLOR_AMBIGUOUS_DISTANCE:
        return FeasibilityResult(
            status="ambiguous",
            reason="white_black_signal_low_separation",
            distance=distance,
            observed_groups=("black", "white"),
        )

    return FeasibilityResult(
        status="unsupported",
        reason="white_black_signal_not_separable",
        distance=distance,
        observed_groups=("black", "white"),
    )


def _role_feasibility(signals: tuple[SquareSignal, ...]) -> FeasibilityResult:
    by_role = _signals_by(signals, "expected_piece")
    observed_roles = tuple(sorted(by_role))

    if len(by_role) < REQUIRED_ROLE_COUNT:
        return FeasibilityResult(
            status="unsupported",
            reason="insufficient_role_coverage",
            observed_groups=observed_roles,
        )

    role_signatures = {
        role: _average_signature(role_signals)
        for role, role_signals in by_role.items()
    }
    min_distance = _minimum_pairwise_distance(tuple(role_signatures.values()))

    if min_distance >= ROLE_FEASIBLE_DISTANCE:
        return FeasibilityResult(
            status="feasible",
            reason="role_signals_separable",
            distance=round(min_distance, 2),
            observed_groups=observed_roles,
        )

    return FeasibilityResult(
        status="ambiguous",
        reason="role_signals_overlap",
        distance=round(min_distance, 2),
        observed_groups=observed_roles,
    )


def _signals_by(
    signals: tuple[SquareSignal, ...],
    field: Literal["expected_color", "expected_piece"],
) -> dict[str, tuple[SquareSignal, ...]]:
    grouped: dict[str, list[SquareSignal]] = {}

    for signal in signals:
        if signal.signature is None:
            continue

        group = getattr(signal, field)
        grouped.setdefault(group, []).append(signal)

    return {key: tuple(value) for key, value in grouped.items()}


def _average_signature(signals: tuple[SquareSignal, ...]) -> tuple[float, ...]:
    signatures = tuple(signal.signature for signal in signals)
    valid_signatures = tuple(
        signature for signature in signatures if signature is not None
    )

    return tuple(
        sum(signature[index] for signature in valid_signatures)
        / len(valid_signatures)
        for index in range(len(valid_signatures[0]))
    )


def _minimum_pairwise_distance(signatures: tuple[tuple[float, ...], ...]) -> float:
    distances = tuple(
        _signature_distance(first, second)
        for index, first in enumerate(signatures)
        for second in signatures[index + 1 :]
    )

    return min(distances) if distances else 0.0


def _signature_distance(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    return sum(
        (left - right) ** 2 for left, right in zip(first, second, strict=True)
    ) ** 0.5


def _unavailable_signal(
    fixture_id: str,
    square: str,
    expected_piece: str,
    expected_color: str,
    failure_reason: str,
) -> SquareSignal:
    return SquareSignal(
        fixture_id=fixture_id,
        square=square,
        expected_piece=expected_piece,
        expected_color=expected_color,
        foreground_average_rgb=None,
        background_average_rgb=None,
        foreground_ratio=None,
        max_distance=None,
        failure_reason=failure_reason,
    )


def _board_bounds(case: Mapping[str, Any]) -> BoardBounds:
    bounds = case["board_bounds"]

    return BoardBounds(
        x=int(bounds["x"]),
        y=int(bounds["y"]),
        width=int(bounds["width"]),
        height=int(bounds["height"]),
    )


def _sample_relative_pixel(
    image: DecodedImage,
    region: SquareRegion,
    x_ratio: float,
    y_ratio: float,
) -> tuple[int, int, int]:
    x = min(region.x + region.width - 1, region.x + int(region.width * x_ratio))
    y = min(region.y + region.height - 1, region.y + int(region.height * y_ratio))

    return image.pixel_at(x, y)[:3]


def _inner_region_pixels(
    image: DecodedImage,
    region: SquareRegion,
) -> tuple[tuple[int, int, int], ...]:
    step = max(1, min(region.width, region.height) // 12)
    x_start = region.x + int(region.width * INNER_SAMPLE_MIN)
    x_end = region.x + int(region.width * INNER_SAMPLE_MAX)
    y_start = region.y + int(region.height * INNER_SAMPLE_MIN)
    y_end = region.y + int(region.height * INNER_SAMPLE_MAX)

    return tuple(
        image.pixel_at(x, y)[:3]
        for y in range(y_start, y_end, step)
        for x in range(x_start, x_end, step)
    )


def _average_pixel(pixels: tuple[tuple[int, int, int], ...]) -> tuple[int, int, int]:
    return tuple(
        sum(pixel[index] for pixel in pixels) // len(pixels) for index in range(3)
    )


def _color_distance(
    first: tuple[int, int, int],
    second: tuple[int, int, int],
) -> float:
    return sum(
        (left - right) ** 2 for left, right in zip(first, second, strict=True)
    ) ** 0.5
