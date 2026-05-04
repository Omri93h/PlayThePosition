from io import BytesIO
from pathlib import Path

from PIL import Image

from app.detection.fixture_metadata import validate_approved_fixture_manifest
from app.detection.grid import (
    BoardBoundsDetectionSuccess,
    GridDetectionFailure,
    GridDetectionSuccess,
    detect_board_bounds,
    detect_board_bounds_from_decoded_image,
    detect_board_grid,
    preprocess_image_bytes,
)
from app.detection.image import DecodedImage, decode_image_bytes


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


def test_approved_fixture_metadata_gates_decoded_board_detection(
    tmp_path: Path,
) -> None:
    approved_dir = tmp_path / "approved"
    approved_dir.mkdir()
    image_path = approved_dir / "synthetic_default_white-bottom_full-01.png"
    image_path.write_bytes(make_board_image_bytes("PNG", square_size=8))
    manifest = {
        "version": 1,
        "cases": [approved_fixture_case(filename=image_path.name)],
    }
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=approved_dir,
        require_existing_images=True,
    )

    assert validation.valid is True

    decoded = decode_image_bytes(image_path.read_bytes(), "image/png")
    assert isinstance(decoded, DecodedImage)

    result = detect_board_bounds_from_decoded_image(decoded)

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 0
    assert result.bounds.y == 0
    assert result.bounds.width == 64
    assert result.bounds.height == 64
    assert result.source == "fixture_gated_decoded_board_bounds"
    assert result.metadata.stage == "grid"


def test_decoded_full_board_png_returns_full_bounds() -> None:
    decoded = decode_image_bytes(
        make_board_image_bytes("PNG", square_size=8),
        "image/png",
    )
    assert isinstance(decoded, DecodedImage)

    result = detect_board_bounds_from_decoded_image(decoded)

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 0
    assert result.bounds.y == 0
    assert result.bounds.width == 64
    assert result.bounds.height == 64
    assert result.confidence == 0.7


def test_decoded_inset_board_png_returns_expected_bounds() -> None:
    decoded = decode_image_bytes(
        make_board_image_bytes("PNG", square_size=8, margin=10),
        "image/png",
    )
    assert isinstance(decoded, DecodedImage)

    result = detect_board_bounds_from_decoded_image(decoded)

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 10
    assert result.bounds.y == 10
    assert result.bounds.width == 64
    assert result.bounds.height == 64


def test_decoded_inset_board_jpeg_returns_expected_bounds() -> None:
    decoded = decode_image_bytes(
        make_board_image_bytes("JPEG", square_size=12, margin=12),
        "image/jpeg",
    )
    assert isinstance(decoded, DecodedImage)

    result = detect_board_bounds_from_decoded_image(decoded)

    assert isinstance(result, BoardBoundsDetectionSuccess)
    assert result.bounds.x == 12
    assert result.bounds.y == 12
    assert result.bounds.width == 96
    assert result.bounds.height == 96


def test_decoded_non_board_image_returns_board_not_found() -> None:
    decoded = decode_image_bytes(make_solid_image_bytes("PNG"), "image/png")
    assert isinstance(decoded, DecodedImage)

    result = detect_board_bounds_from_decoded_image(decoded)

    assert isinstance(result, GridDetectionFailure)
    assert result.code == "board_grid_not_found"
    assert result.stage == "grid"
    assert result.failure_reason == "board_grid_not_found"


def test_invalid_fixture_metadata_prevents_detection_from_running(
    tmp_path: Path,
) -> None:
    approved_dir = tmp_path / "approved"
    approved_dir.mkdir()
    manifest = {
        "version": 1,
        "cases": [
            approved_fixture_case(
                filename="../synthetic_default_white-bottom_full-01.png",
            )
        ],
    }
    detection_ran = False

    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=approved_dir,
    )

    if validation.valid:
        detection_ran = True

    assert validation.valid is False
    assert detection_ran is False


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


def approved_fixture_case(filename: str) -> dict:
    return {
        "id": "synthetic_default_white-bottom_full-01",
        "filename": filename,
        "kind": "approved_manual_fixture",
        "source": "synthetic",
        "style": "default",
        "orientation": "white-bottom",
        "board_bounds": {"x": 0, "y": 0, "width": 64, "height": 64},
        "expected_pieces": [],
        "expected_fen": "8/8/8/8/8/8/8/8 w - - 0 1",
        "expected_metrics": {
            "board_crop_detected": True,
            "orientation_detected": "white-bottom",
            "piece_list_required": False,
            "fen_match_required": False,
            "failure_reason_required": False,
        },
        "license": {
            "status": "approved",
            "note": "Generated temporary test image; not committed.",
        },
        "notes": "Runtime-only fixture metadata.",
    }


def make_board_image_bytes(
    image_format: str,
    *,
    square_size: int,
    margin: int = 0,
) -> bytes:
    light = (230, 238, 218)
    dark = (42, 86, 55)
    background = (14, 16, 15)
    board_side = square_size * 8
    image_side = board_side + margin * 2
    image = Image.new("RGB", (image_side, image_side), color=background)
    pixels = image.load()

    for y in range(margin, margin + board_side):
        for x in range(margin, margin + board_side):
            board_x = x - margin
            board_y = y - margin
            square_x = board_x // square_size
            square_y = board_y // square_size
            pixels[x, y] = light if (square_x + square_y) % 2 == 0 else dark

    buffer = BytesIO()
    save_kwargs = {"quality": 100, "subsampling": 0} if image_format == "JPEG" else {}
    image.save(buffer, format=image_format, **save_kwargs)
    return buffer.getvalue()


def make_solid_image_bytes(image_format: str) -> bytes:
    image = Image.new("RGB", (64, 64), color=(120, 120, 120))
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()
