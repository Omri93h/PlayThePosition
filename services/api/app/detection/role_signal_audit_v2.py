from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage
from app.detection.square_sampling import SquareRegion, derive_square_regions

SignalStatus = Literal["feasible", "ambiguous", "unsupported"]

SOURCE_STAGE = "role_signal_audit_v2"
REQUIRED_ROLES = ("king", "queen", "rook", "bishop", "knight", "pawn")
BACKGROUND_SAMPLE_POINTS = (
    (0.08, 0.08),
    (0.92, 0.08),
    (0.08, 0.92),
    (0.92, 0.92),
)
SIGNATURE_GRID_SIZE = 24
SIGNATURE_SAMPLE_MIN = 0.05
SIGNATURE_SAMPLE_MAX = 0.95
FOREGROUND_DISTANCE_THRESHOLD = 15.0
ROLE_SEPARATION_MARGIN_MIN = 0.10


@dataclass(frozen=True)
class RoleSignalV2Sample:
    fixture_id: str
    square: str
    expected_role: str
    expected_color: str
    signature: tuple[int, ...] | None
    failure_reason: str | None
    source_stage: str = SOURCE_STAGE


@dataclass(frozen=True)
class RolePairDistance:
    first_role: str
    second_role: str
    distance: float


@dataclass(frozen=True)
class RoleSignalSeparability:
    status: SignalStatus
    reason: str
    observed_roles: tuple[str, ...]
    minimum_margin: float | None = None
    minimum_pairwise_distance: float | None = None
    ambiguous_pairs: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class FixtureRoleSignalAuditV2:
    fixture_id: str
    filename: str
    source: str
    style: str
    orientation: str
    occupied_square_count: int
    measured_signal_count: int
    separability: RoleSignalSeparability
    pair_distances: tuple[RolePairDistance, ...]
    samples: tuple[RoleSignalV2Sample, ...]


@dataclass(frozen=True)
class AggregateRoleSignalAuditV2:
    fixture_count: int
    occupied_square_count: int
    measured_signal_count: int
    separability: RoleSignalSeparability
    pair_distances: tuple[RolePairDistance, ...]
    fixture_audits: tuple[FixtureRoleSignalAuditV2, ...]


def audit_fixture_role_signals_v2(
    case: Mapping[str, Any],
    image: DecodedImage,
) -> FixtureRoleSignalAuditV2:
    regions = {
        region.square: region
        for region in derive_square_regions(
            _board_bounds(case),
            str(case["orientation"]),
        )
    }
    samples = tuple(
        _sample_expected_piece_role_signal(
            fixture_id=str(case["id"]),
            image=image,
            region=regions.get(str(piece["square"])),
            piece=piece,
        )
        for piece in case.get("expected_pieces", [])
        if isinstance(piece, Mapping)
    )
    measured = tuple(sample for sample in samples if sample.signature is not None)

    return FixtureRoleSignalAuditV2(
        fixture_id=str(case["id"]),
        filename=str(case["filename"]),
        source=str(case["source"]),
        style=str(case["style"]),
        orientation=str(case["orientation"]),
        occupied_square_count=len(samples),
        measured_signal_count=len(measured),
        separability=_role_separability(samples),
        pair_distances=_role_pair_distances(measured),
        samples=samples,
    )


def aggregate_role_signal_audits_v2(
    fixture_audits: Sequence[FixtureRoleSignalAuditV2],
) -> AggregateRoleSignalAuditV2:
    samples = tuple(
        sample for audit in fixture_audits for sample in audit.samples
    )
    measured = tuple(sample for sample in samples if sample.signature is not None)

    return AggregateRoleSignalAuditV2(
        fixture_count=len(fixture_audits),
        occupied_square_count=len(samples),
        measured_signal_count=len(measured),
        separability=_role_separability(samples),
        pair_distances=_role_pair_distances(measured),
        fixture_audits=tuple(fixture_audits),
    )


def _sample_expected_piece_role_signal(
    *,
    fixture_id: str,
    image: DecodedImage,
    region: SquareRegion | None,
    piece: Mapping[str, Any],
) -> RoleSignalV2Sample:
    square = str(piece.get("square", ""))
    expected_role = str(piece.get("piece", ""))
    expected_color = str(piece.get("color", ""))

    if region is None:
        return _unavailable_sample(
            fixture_id,
            square,
            expected_role,
            expected_color,
            "sample_unavailable",
        )

    background_samples = tuple(
        _sample_relative_pixel(image, region, x, y)
        for x, y in BACKGROUND_SAMPLE_POINTS
    )
    background = _average_pixel(background_samples)

    return RoleSignalV2Sample(
        fixture_id=fixture_id,
        square=square,
        expected_role=expected_role,
        expected_color=expected_color,
        signature=_shape_signature(image, region, background),
        failure_reason=None,
    )


def _role_separability(
    samples: tuple[RoleSignalV2Sample, ...],
) -> RoleSignalSeparability:
    measured = tuple(sample for sample in samples if sample.signature is not None)
    observed_roles = _observed_roles(measured)

    if len(measured) != len(samples):
        return RoleSignalSeparability(
            status="unsupported",
            reason="sample_unavailable",
            observed_roles=observed_roles,
        )

    missing_roles = tuple(role for role in REQUIRED_ROLES if role not in observed_roles)
    if missing_roles:
        return RoleSignalSeparability(
            status="unsupported",
            reason="insufficient_role_coverage",
            observed_roles=observed_roles,
        )

    if any(len(_samples_for_role(measured, role)) < 2 for role in REQUIRED_ROLES):
        return RoleSignalSeparability(
            status="unsupported",
            reason="insufficient_role_samples",
            observed_roles=observed_roles,
        )

    margins: list[float] = []
    ambiguous_pairs: set[tuple[str, str]] = set()
    for sample in measured:
        nearest_same = _nearest_distance(sample, measured, same_role=True)
        nearest_other = _nearest_distance(sample, measured, same_role=False)
        margin = nearest_other - nearest_same
        margins.append(margin)

        if margin < ROLE_SEPARATION_MARGIN_MIN:
            other_role = _nearest_other_role(sample, measured)
            ambiguous_pairs.add(tuple(sorted((sample.expected_role, other_role))))

    pair_distances = _role_pair_distances(measured)
    minimum_margin = round(min(margins), 4) if margins else None
    minimum_pairwise_distance = (
        round(min(pair.distance for pair in pair_distances), 4)
        if pair_distances
        else None
    )

    if minimum_margin is not None and minimum_margin >= ROLE_SEPARATION_MARGIN_MIN:
        return RoleSignalSeparability(
            status="feasible",
            reason="role_signals_separable",
            observed_roles=observed_roles,
            minimum_margin=minimum_margin,
            minimum_pairwise_distance=minimum_pairwise_distance,
        )

    return RoleSignalSeparability(
        status="ambiguous",
        reason="role_signals_overlap",
        observed_roles=observed_roles,
        minimum_margin=minimum_margin,
        minimum_pairwise_distance=minimum_pairwise_distance,
        ambiguous_pairs=tuple(sorted(ambiguous_pairs)),
    )


def _role_pair_distances(
    samples: tuple[RoleSignalV2Sample, ...],
) -> tuple[RolePairDistance, ...]:
    distances: list[RolePairDistance] = []

    for first_index, first_role in enumerate(REQUIRED_ROLES):
        for second_role in REQUIRED_ROLES[first_index + 1 :]:
            first_samples = _samples_for_role(samples, first_role)
            second_samples = _samples_for_role(samples, second_role)

            if not first_samples or not second_samples:
                continue

            distance = min(
                _signature_distance(first.signature, second.signature)
                for first in first_samples
                for second in second_samples
                if first.signature is not None and second.signature is not None
            )
            distances.append(
                RolePairDistance(
                    first_role=first_role,
                    second_role=second_role,
                    distance=round(distance, 4),
                )
            )

    return tuple(distances)


def _shape_signature(
    image: DecodedImage,
    region: SquareRegion,
    background: tuple[float, float, float],
) -> tuple[int, ...]:
    span = SIGNATURE_SAMPLE_MAX - SIGNATURE_SAMPLE_MIN

    return tuple(
        int(
            _color_distance(
                _sample_relative_pixel(
                    image,
                    region,
                    SIGNATURE_SAMPLE_MIN
                    + (span * ((column + 0.5) / SIGNATURE_GRID_SIZE)),
                    SIGNATURE_SAMPLE_MIN
                    + (span * ((row + 0.5) / SIGNATURE_GRID_SIZE)),
                ),
                background,
            )
            > FOREGROUND_DISTANCE_THRESHOLD
        )
        for row in range(SIGNATURE_GRID_SIZE)
        for column in range(SIGNATURE_GRID_SIZE)
    )


def _samples_for_role(
    samples: tuple[RoleSignalV2Sample, ...],
    role: str,
) -> tuple[RoleSignalV2Sample, ...]:
    return tuple(sample for sample in samples if sample.expected_role == role)


def _nearest_distance(
    sample: RoleSignalV2Sample,
    samples: tuple[RoleSignalV2Sample, ...],
    *,
    same_role: bool,
) -> float:
    distances = tuple(
        _signature_distance(sample.signature, other.signature)
        for other in samples
        if other is not sample
        and other.signature is not None
        and sample.signature is not None
        and (other.expected_role == sample.expected_role) is same_role
    )

    return min(distances) if distances else 0.0


def _nearest_other_role(
    sample: RoleSignalV2Sample,
    samples: tuple[RoleSignalV2Sample, ...],
) -> str:
    nearest = min(
        (
            (
                _signature_distance(sample.signature, other.signature),
                other.expected_role,
            )
            for other in samples
            if other.signature is not None
            and sample.signature is not None
            and other.expected_role != sample.expected_role
        ),
        key=lambda item: item[0],
    )

    return nearest[1]


def _observed_roles(samples: tuple[RoleSignalV2Sample, ...]) -> tuple[str, ...]:
    sample_roles = {sample.expected_role for sample in samples}

    return tuple(role for role in REQUIRED_ROLES if role in sample_roles)


def _signature_distance(
    first: tuple[int, ...] | None,
    second: tuple[int, ...] | None,
) -> float:
    if first is None or second is None:
        return 0.0

    return sum(left != right for left, right in zip(first, second, strict=True)) / len(
        first
    )


def _unavailable_sample(
    fixture_id: str,
    square: str,
    expected_role: str,
    expected_color: str,
    failure_reason: str,
) -> RoleSignalV2Sample:
    return RoleSignalV2Sample(
        fixture_id=fixture_id,
        square=square,
        expected_role=expected_role,
        expected_color=expected_color,
        signature=None,
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


def _average_pixel(
    pixels: tuple[tuple[int, int, int], ...],
) -> tuple[float, float, float]:
    return tuple(
        sum(pixel[index] for pixel in pixels) / len(pixels) for index in range(3)
    )


def _color_distance(
    first: tuple[int, int, int],
    second: tuple[float, float, float],
) -> float:
    return sum(
        (left - right) ** 2 for left, right in zip(first, second, strict=True)
    ) ** 0.5
