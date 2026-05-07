from dataclasses import dataclass
from typing import Literal

from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage

FILES = "abcdefgh"
SOURCE_STAGE = "square_sampling"
SUPPORTED_ORIENTATIONS = {"white-bottom", "black-bottom"}

DetectedState = Literal["empty", "occupied", "not_measured"]

INNER_SAMPLE_MIN = 0.28
INNER_SAMPLE_MAX = 0.72
BACKGROUND_SAMPLE_POINTS = (
    (0.18, 0.18),
    (0.82, 0.18),
    (0.18, 0.82),
    (0.82, 0.82),
)
OCCUPIED_DISTANCE_THRESHOLD = 35.0
OCCUPIED_RATIO_THRESHOLD = 0.02
OCCUPIED_MAX_DISTANCE_THRESHOLD = 60.0


@dataclass(frozen=True)
class SquareRegion:
    square: str
    row: int
    column: int
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class SquareSample:
    fixture_id: str
    square: str
    row: int
    column: int
    detected_state: DetectedState
    detected_piece: str | None
    detected_color: str | None
    confidence: float | None
    failure_reason: str | None
    source_stage: str = SOURCE_STAGE


def sample_fixture_squares(
    *,
    fixture_id: str,
    image: DecodedImage,
    board_bounds: BoardBounds,
    orientation: str,
) -> tuple[SquareSample, ...]:
    regions = derive_square_regions(board_bounds, orientation)
    unsupported_reason = _unsupported_reason(image, board_bounds, orientation)

    if unsupported_reason is not None:
        return tuple(
            _not_measured_sample(fixture_id, region, unsupported_reason)
            for region in regions
        )

    return tuple(_sample_square(fixture_id, image, region) for region in regions)


def derive_square_regions(
    board_bounds: BoardBounds,
    orientation: str,
) -> tuple[SquareRegion, ...]:
    square_width = board_bounds.width // 8 if board_bounds.width > 0 else 0
    square_height = board_bounds.height // 8 if board_bounds.height > 0 else 0

    return tuple(
        SquareRegion(
            square=_square_for_visual_cell(row, column, orientation),
            row=row,
            column=column,
            x=board_bounds.x + (column * square_width),
            y=board_bounds.y + (row * square_height),
            width=square_width,
            height=square_height,
        )
        for row in range(8)
        for column in range(8)
    )


def _sample_square(
    fixture_id: str,
    image: DecodedImage,
    region: SquareRegion,
) -> SquareSample:
    background_samples = tuple(
        _sample_relative_pixel(image, region, x, y)
        for x, y in BACKGROUND_SAMPLE_POINTS
    )
    background = _average_pixel(background_samples)
    inner_pixels = _inner_region_pixels(image, region)

    if not inner_pixels:
        return _not_measured_sample(fixture_id, region, "empty_sample_region")

    distances = tuple(_color_distance(pixel, background) for pixel in inner_pixels)
    changed_ratio = sum(
        distance > OCCUPIED_DISTANCE_THRESHOLD for distance in distances
    ) / len(distances)
    max_distance = max(distances)
    is_occupied = (
        changed_ratio >= OCCUPIED_RATIO_THRESHOLD
        and max_distance >= OCCUPIED_MAX_DISTANCE_THRESHOLD
    )

    return SquareSample(
        fixture_id=fixture_id,
        square=region.square,
        row=region.row,
        column=region.column,
        detected_state="occupied" if is_occupied else "empty",
        detected_piece=None,
        detected_color=None,
        confidence=_confidence(changed_ratio, max_distance, is_occupied),
        failure_reason=None,
    )


def _unsupported_reason(
    image: DecodedImage,
    board_bounds: BoardBounds,
    orientation: str,
) -> str | None:
    if orientation not in SUPPORTED_ORIENTATIONS:
        return "unsupported_orientation"

    if board_bounds.width <= 0 or board_bounds.height <= 0:
        return "invalid_board_bounds"

    if board_bounds.width % 8 != 0 or board_bounds.height % 8 != 0:
        return "invalid_board_bounds"

    if board_bounds.x < 0 or board_bounds.y < 0:
        return "invalid_board_bounds"

    if board_bounds.x + board_bounds.width > image.width:
        return "board_bounds_outside_image"

    if board_bounds.y + board_bounds.height > image.height:
        return "board_bounds_outside_image"

    return None


def _not_measured_sample(
    fixture_id: str,
    region: SquareRegion,
    failure_reason: str,
) -> SquareSample:
    return SquareSample(
        fixture_id=fixture_id,
        square=region.square,
        row=region.row,
        column=region.column,
        detected_state="not_measured",
        detected_piece=None,
        detected_color=None,
        confidence=None,
        failure_reason=failure_reason,
    )


def _square_for_visual_cell(row: int, column: int, orientation: str) -> str:
    if orientation == "black-bottom":
        return f"{FILES[7 - column]}{row + 1}"

    return f"{FILES[column]}{8 - row}"


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


def _confidence(
    changed_ratio: float,
    max_distance: float,
    is_occupied: bool,
) -> float:
    if is_occupied:
        return round(min(1.0, max(0.5, max_distance / 255)), 2)

    return round(max(0.5, 1.0 - changed_ratio), 2)
