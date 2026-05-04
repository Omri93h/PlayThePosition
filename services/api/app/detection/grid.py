from dataclasses import dataclass, field

from app.detection.image import DecodedImage
from app.detection.results import DetectionMetadata, DetectionStage

RgbPixel = tuple[int, int, int]


@dataclass(frozen=True)
class PreprocessedImage:
    width: int
    height: int
    pixels: tuple[RgbPixel, ...]


@dataclass(frozen=True)
class GridSquare:
    row: int
    column: int
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class BoardGrid:
    rows: int
    columns: int
    squares: tuple[GridSquare, ...]


@dataclass(frozen=True)
class BoardBounds:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class GridDetectionSuccess:
    grid: BoardGrid
    source: str = "synthetic_ppm_grid"
    metadata: DetectionMetadata = field(
        default_factory=lambda: DetectionMetadata(
            confidence=0.75,
            source="synthetic_ppm_grid",
            stage="grid",
        )
    )


@dataclass(frozen=True)
class GridDetectionFailure:
    code: str
    message: str
    stage: DetectionStage = "grid"
    retryable: bool = True
    suggestion: str = "Use a clear, uncropped chessboard image."
    failure_reason: str | None = None


@dataclass(frozen=True)
class BoardBoundsDetectionSuccess:
    bounds: BoardBounds
    confidence: float
    source: str = "synthetic_ppm_board_bounds"
    stage: DetectionStage = "grid"

    @property
    def metadata(self) -> DetectionMetadata:
        return DetectionMetadata(
            confidence=self.confidence,
            source=self.source,
            stage=self.stage,
        )


GridDetectionResult = GridDetectionSuccess | GridDetectionFailure
BoardBoundsDetectionResult = BoardBoundsDetectionSuccess | GridDetectionFailure
PreprocessResult = PreprocessedImage | GridDetectionFailure


def preprocess_image_bytes(image_bytes: bytes) -> PreprocessResult:
    if not image_bytes:
        return GridDetectionFailure(
            code="empty_image",
            message="Image payload is empty.",
            stage="preprocess",
            suggestion="Upload a non-empty image file.",
            failure_reason="empty_image",
        )

    return _parse_ppm(image_bytes)


def detect_board_grid(image_bytes: bytes) -> GridDetectionResult:
    image = preprocess_image_bytes(image_bytes)

    if isinstance(image, GridDetectionFailure):
        return image

    return detect_grid_from_image(image)


def detect_board_bounds(image_bytes: bytes) -> BoardBoundsDetectionResult:
    image = preprocess_image_bytes(image_bytes)

    if isinstance(image, GridDetectionFailure):
        return image

    return detect_board_bounds_from_image(image)


def detect_board_bounds_from_image(
    image: PreprocessedImage,
    *,
    source: str = "synthetic_ppm_board_bounds",
) -> BoardBoundsDetectionResult:
    max_square_size = min(image.width, image.height) // 8

    for square_size in range(max_square_size, 1, -1):
        side = square_size * 8

        for y in range(0, image.height - side + 1):
            for x in range(0, image.width - side + 1):
                if _region_has_checkerboard(image, x, y, square_size):
                    return BoardBoundsDetectionSuccess(
                        bounds=BoardBounds(x=x, y=y, width=side, height=side),
                        confidence=0.7,
                        source=source,
                    )

    return _grid_not_found()


def detect_board_bounds_from_decoded_image(
    image: DecodedImage,
) -> BoardBoundsDetectionResult:
    preprocessed = decoded_image_to_preprocessed_image(image)

    return detect_board_bounds_from_image(
        preprocessed,
        source="fixture_gated_decoded_board_bounds",
    )


def decoded_image_to_preprocessed_image(image: DecodedImage) -> PreprocessedImage:
    pixels = tuple(
        tuple(image.pixels[index : index + image.channels][:3])
        for index in range(0, len(image.pixels), image.channels)
    )

    return PreprocessedImage(
        width=image.width,
        height=image.height,
        pixels=pixels,
    )


def detect_grid_from_image(image: PreprocessedImage) -> GridDetectionResult:
    if image.width <= 0 or image.height <= 0:
        return _grid_not_found()

    if image.width != image.height or image.width % 8 != 0:
        return _grid_not_found()

    square_size = image.width // 8

    if not _region_has_checkerboard(image, 0, 0, square_size):
        return _grid_not_found()

    squares = tuple(
        GridSquare(
            row=row,
            column=column,
            x=column * square_size,
            y=row * square_size,
            width=square_size,
            height=square_size,
        )
        for row in range(8)
        for column in range(8)
    )

    return GridDetectionSuccess(grid=BoardGrid(rows=8, columns=8, squares=squares))


def _region_has_checkerboard(
    image: PreprocessedImage,
    x_offset: int,
    y_offset: int,
    square_size: int,
) -> bool:
    sampled_pixels = _sample_square_points(
        image,
        square_size,
        x_offset=x_offset,
        y_offset=y_offset,
    )

    if len(sampled_pixels) < 64:
        return False

    light_pixels = [
        pixel
        for row, column, pixel in sampled_pixels
        if (row + column) % 2 == 0
    ]
    dark_pixels = [
        pixel
        for row, column, pixel in sampled_pixels
        if (row + column) % 2 == 1
    ]
    light_average = _average_color(light_pixels)
    dark_average = _average_color(dark_pixels)

    if _color_distance(light_average, dark_average) < 35:
        return False

    if not _pixels_are_consistent(light_pixels, light_average):
        return False

    return _pixels_are_consistent(dark_pixels, dark_average)


def _parse_ppm(image_bytes: bytes) -> PreprocessResult:
    try:
        magic, index = _read_header_token(image_bytes, 0)
        width_token, index = _read_header_token(image_bytes, index)
        height_token, index = _read_header_token(image_bytes, index)
        max_value_token, index = _read_header_token(image_bytes, index)
    except ValueError:
        return _invalid_image()

    if magic != b"P6":
        return GridDetectionFailure(
            code="unsupported_image_format",
            message="Only binary PPM test images are supported by this boundary.",
            stage="preprocess",
            suggestion="Use a supported image format for this detection boundary.",
            failure_reason="unsupported_image_format",
        )

    try:
        width = int(width_token)
        height = int(height_token)
        max_value = int(max_value_token)
    except ValueError:
        return _invalid_image()

    if width <= 0 or height <= 0 or max_value != 255:
        return _invalid_image()

    pixel_start = _skip_single_whitespace(image_bytes, index)
    expected_length = width * height * 3
    pixel_bytes = image_bytes[pixel_start : pixel_start + expected_length]

    if len(pixel_bytes) != expected_length:
        return _invalid_image()

    pixels = tuple(
        (pixel_bytes[index], pixel_bytes[index + 1], pixel_bytes[index + 2])
        for index in range(0, expected_length, 3)
    )

    return PreprocessedImage(width=width, height=height, pixels=pixels)


def _read_header_token(image_bytes: bytes, start_index: int) -> tuple[bytes, int]:
    index = start_index

    while index < len(image_bytes):
        byte = image_bytes[index]

        if byte in b" \t\r\n":
            index += 1
            continue

        if byte == ord("#"):
            while index < len(image_bytes) and image_bytes[index] not in b"\r\n":
                index += 1
            continue

        break

    token_start = index

    while index < len(image_bytes) and image_bytes[index] not in b" \t\r\n":
        index += 1

    if token_start == index:
        raise ValueError("Missing PPM token.")

    return image_bytes[token_start:index], index


def _skip_single_whitespace(image_bytes: bytes, index: int) -> int:
    if index < len(image_bytes) and image_bytes[index] in b" \t\r\n":
        return index + 1

    return index


def _sample_square_points(
    image: PreprocessedImage,
    square_size: int,
    *,
    x_offset: int = 0,
    y_offset: int = 0,
) -> list[tuple[int, int, RgbPixel]]:
    samples: list[tuple[int, int, RgbPixel]] = []
    local_offsets = sorted(
        {
            0,
            square_size // 2,
            square_size - 1,
        }
    )

    for row in range(8):
        for column in range(8):
            for local_y in local_offsets:
                for local_x in local_offsets:
                    x = x_offset + column * square_size + local_x
                    y = y_offset + row * square_size + local_y

                    if x >= image.width or y >= image.height:
                        continue

                    samples.append((row, column, image.pixels[y * image.width + x]))

    return samples


def _average_color(pixels: list[RgbPixel]) -> RgbPixel:
    red = sum(pixel[0] for pixel in pixels) // len(pixels)
    green = sum(pixel[1] for pixel in pixels) // len(pixels)
    blue = sum(pixel[2] for pixel in pixels) // len(pixels)

    return (red, green, blue)


def _pixels_are_consistent(pixels: list[RgbPixel], average: RgbPixel) -> bool:
    return all(_color_distance(pixel, average) <= 30 for pixel in pixels)


def _color_distance(first: RgbPixel, second: RgbPixel) -> int:
    return sum(abs(first[index] - second[index]) for index in range(3))


def _invalid_image() -> GridDetectionFailure:
    return GridDetectionFailure(
        code="invalid_image_bytes",
        message="Image payload could not be preprocessed.",
        stage="preprocess",
        suggestion="Upload a valid image payload.",
        failure_reason="invalid_image_bytes",
    )


def _grid_not_found() -> GridDetectionFailure:
    return GridDetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
        failure_reason="board_grid_not_found",
    )
