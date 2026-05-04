from io import BytesIO

from PIL import Image

from app.detection.image import DecodedImage, ImageDecodeFailure, decode_image_bytes


def test_valid_png_decodes_to_rgb_image() -> None:
    result = decode_image_bytes(
        make_image_bytes("PNG", mode="RGB", color=(10, 20, 30)),
        "image/png",
    )

    assert isinstance(result, DecodedImage)
    assert result.width == 2
    assert result.height == 3
    assert result.format == "png"
    assert result.mode == "RGB"
    assert result.channels == 3
    assert result.pixel_at(0, 0) == (10, 20, 30)
    assert result.metadata.stage == "preprocess"
    assert result.metadata.status == "success"


def test_valid_jpeg_decodes_to_rgb_image() -> None:
    result = decode_image_bytes(
        make_image_bytes("JPEG", mode="RGB", color=(200, 180, 90)),
        "image/jpeg",
    )

    assert isinstance(result, DecodedImage)
    assert result.width == 2
    assert result.height == 3
    assert result.format == "jpeg"
    assert result.mode == "RGB"
    assert len(result.pixels) == result.width * result.height * 3


def test_rgba_png_preserves_alpha_channel() -> None:
    result = decode_image_bytes(
        make_image_bytes("PNG", mode="RGBA", color=(10, 20, 30, 128)),
        "image/png",
    )

    assert isinstance(result, DecodedImage)
    assert result.mode == "RGBA"
    assert result.channels == 4
    assert result.pixel_at(1, 2) == (10, 20, 30, 128)


def test_empty_image_bytes_fail_cleanly() -> None:
    result = decode_image_bytes(b"", "image/png")

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "empty_image"
    assert result.failure_reason == "empty_image"
    assert result.metadata.status == "failed"


def test_malformed_image_bytes_fail_cleanly() -> None:
    result = decode_image_bytes(b"\x89PNG\r\n\x1a\nnot a complete png", "image/png")

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "invalid_image_bytes"
    assert result.failure_reason == "malformed_or_truncated_image"


def test_unsupported_content_type_fails_cleanly() -> None:
    result = decode_image_bytes(b"not a webp", "image/webp")

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "unsupported_image_format"
    assert result.failure_reason == "unsupported_image_format"


def test_mime_signature_mismatch_fails_cleanly() -> None:
    result = decode_image_bytes(
        make_image_bytes("JPEG", mode="RGB", color=(1, 2, 3)),
        "image/png",
    )

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "mime_signature_mismatch"
    assert result.failure_reason == "mime_signature_mismatch"


def test_excessive_byte_size_fails_before_decode() -> None:
    result = decode_image_bytes(
        make_image_bytes("PNG", mode="RGB", color=(1, 2, 3)),
        "image/png",
        max_bytes=4,
    )

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "image_too_large"
    assert result.failure_reason == "excessive_byte_size"


def test_oversized_dimensions_fail_cleanly() -> None:
    result = decode_image_bytes(
        make_image_bytes("PNG", mode="RGB", color=(1, 2, 3), size=(3, 3)),
        "image/png",
        max_width=2,
        max_height=2,
    )

    assert isinstance(result, ImageDecodeFailure)
    assert result.code == "image_dimensions_too_large"
    assert result.failure_reason == "oversized_dimensions"


def test_pixel_accessor_rejects_out_of_bounds_coordinates() -> None:
    result = decode_image_bytes(
        make_image_bytes("PNG", mode="RGB", color=(10, 20, 30)),
        "image/png",
    )

    assert isinstance(result, DecodedImage)

    try:
        result.pixel_at(2, 0)
    except ValueError as error:
        assert str(error) == "Pixel coordinates must be inside the image bounds."
    else:
        raise AssertionError("Expected out-of-bounds pixel access to fail.")


def make_image_bytes(
    image_format: str,
    *,
    mode: str,
    color,
    size: tuple[int, int] = (2, 3),
) -> bytes:
    image = Image.new(mode, size, color=color)

    if image_format == "JPEG" and image.mode != "RGB":
        image = image.convert("RGB")

    buffer = BytesIO()
    image.save(buffer, format=image_format)

    return buffer.getvalue()
