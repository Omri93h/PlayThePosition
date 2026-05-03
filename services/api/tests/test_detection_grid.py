from app.detection.grid import (
    BoardBoundsDetectionSuccess,
    GridDetectionFailure,
    GridDetectionSuccess,
    detect_board_bounds,
    detect_board_grid,
    preprocess_image_bytes,
)


def test_empty_image_bytes_fail_cleanly() -> None:
    result = preprocess_image_bytes(b"")

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "empty_image"


def test_invalid_image_bytes_fail_cleanly() -> None:
    result = preprocess_image_bytes(b"not an image")

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "invalid_image_bytes"


def test_synthetic_board_image_returns_structured_grid() -> None:
    result = detect_board_grid(make_synthetic_board_ppm(square_size=6))

    assert isinstance(result, GridDetectionSuccess)
    assert result.grid.rows == 8
    assert result.grid.columns == 8
    assert len(result.grid.squares) == 64
    assert result.grid.squares[0].row == 0
    assert result.grid.squares[0].column == 0
    assert result.grid.squares[0].width == 6
    assert result.grid.squares[-1].row == 7
    assert result.grid.squares[-1].column == 7


def test_non_board_image_fails_cleanly() -> None:
    result = detect_board_grid(make_solid_ppm(width=48, height=48))

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "board_grid_not_found"


def test_full_board_synthetic_ppm_returns_full_image_bounds() -> None:
    result = detect_board_bounds(make_synthetic_board_ppm(square_size=6))

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 0
    assert result.bounds.y == 0
    assert result.bounds.width == 48
    assert result.bounds.height == 48
    assert result.confidence == 0.7
    assert result.source == "synthetic_ppm_board_bounds"
    assert result.stage == "grid"


def test_inset_synthetic_board_returns_expected_bounds() -> None:
    result = detect_board_bounds(
        make_inset_synthetic_board_ppm(square_size=6, margin=8),
    )

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 8
    assert result.bounds.y == 8
    assert result.bounds.width == 48
    assert result.bounds.height == 48


def test_solid_non_board_image_fails_bounds_detection_cleanly() -> None:
    result = detect_board_bounds(make_solid_ppm(width=64, height=64))

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "board_grid_not_found"
    assert result.stage == "grid"
    assert result.retryable is True


def test_empty_image_bytes_fail_bounds_detection_cleanly() -> None:
    result = detect_board_bounds(b"")

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "empty_image"
    assert result.stage == "preprocess"


def test_invalid_image_bytes_fail_bounds_detection_cleanly() -> None:
    result = detect_board_bounds(b"not an image")

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "invalid_image_bytes"
    assert result.stage == "preprocess"


def make_synthetic_board_ppm(square_size: int) -> bytes:
    light = (178, 207, 162)
    dark = (67, 118, 88)
    side = square_size * 8

    return make_ppm(
        width=side,
        height=side,
        pixel_for=lambda x, y: (
            light if ((x // square_size) + (y // square_size)) % 2 == 0 else dark
        ),
    )


def make_inset_synthetic_board_ppm(square_size: int, margin: int) -> bytes:
    light = (178, 207, 162)
    dark = (67, 118, 88)
    background = (28, 32, 31)
    board_side = square_size * 8
    image_side = board_side + margin * 2

    def pixel_for(x, y):
        board_x = x - margin
        board_y = y - margin

        if not (0 <= board_x < board_side and 0 <= board_y < board_side):
            return background

        square_x = board_x // square_size
        square_y = board_y // square_size

        return light if (square_x + square_y) % 2 == 0 else dark

    return make_ppm(width=image_side, height=image_side, pixel_for=pixel_for)


def make_solid_ppm(width: int, height: int) -> bytes:
    return make_ppm(
        width=width,
        height=height,
        pixel_for=lambda _x, _y: (120, 120, 120),
    )


def make_ppm(
    width: int,
    height: int,
    pixel_for,
) -> bytes:
    header = f"P6\n{width} {height}\n255\n".encode()
    pixels = bytearray()

    for y in range(height):
        for x in range(width):
            pixels.extend(pixel_for(x, y))

    return header + bytes(pixels)
