from dataclasses import dataclass
from io import BytesIO
from typing import Literal

from PIL import Image, ImageOps, UnidentifiedImageError

from app.detection.results import DetectionMetadata, DetectionStage

ImageFormat = Literal["png", "jpeg"]
ImageMode = Literal["RGB", "RGBA"]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
SUPPORTED_CONTENT_TYPES: dict[str, ImageFormat] = {
    "image/png": "png",
    "image/jpeg": "jpeg",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
SOURCE = "pillow_decode_preprocess"


@dataclass(frozen=True)
class DecodedImage:
    width: int
    height: int
    format: ImageFormat
    mode: ImageMode
    pixels: bytes
    metadata: DetectionMetadata

    @property
    def channels(self) -> int:
        return 4 if self.mode == "RGBA" else 3

    def pixel_at(self, x: int, y: int) -> tuple[int, ...]:
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise ValueError("Pixel coordinates must be inside the image bounds.")

        start = (y * self.width + x) * self.channels
        end = start + self.channels

        return tuple(self.pixels[start:end])


@dataclass(frozen=True)
class ImageDecodeFailure:
    code: str
    message: str
    stage: DetectionStage = "preprocess"
    retryable: bool = True
    suggestion: str = "Upload a valid PNG or JPEG image."
    failure_reason: str | None = None
    metadata: DetectionMetadata = DetectionMetadata(
        confidence=None,
        source=SOURCE,
        stage="preprocess",
        status="failed",
    )


ImageDecodeResult = DecodedImage | ImageDecodeFailure


def decode_image_bytes(
    image_bytes: bytes,
    content_type: str,
    *,
    max_bytes: int = MAX_IMAGE_BYTES,
    max_width: int = MAX_IMAGE_WIDTH,
    max_height: int = MAX_IMAGE_HEIGHT,
) -> ImageDecodeResult:
    if not image_bytes:
        return _failure(
            code="empty_image",
            message="Image payload is empty.",
            suggestion="Upload a non-empty PNG or JPEG image.",
            failure_reason="empty_image",
        )

    if len(image_bytes) > max_bytes:
        return _failure(
            code="image_too_large",
            message="Image payload exceeds the detection decode byte limit.",
            suggestion="Use a smaller image file.",
            failure_reason="excessive_byte_size",
        )

    normalized_content_type = _normalize_content_type(content_type)
    expected_format = SUPPORTED_CONTENT_TYPES.get(normalized_content_type)

    if expected_format is None:
        return _failure(
            code="unsupported_image_format",
            message="Only PNG and JPEG images are supported by this boundary.",
            suggestion="Use a PNG or JPEG image.",
            failure_reason="unsupported_image_format",
        )

    detected_format = detect_image_format(image_bytes)

    if detected_format is None:
        return _failure(
            code="invalid_image_bytes",
            message="Image bytes do not match a supported PNG or JPEG signature.",
            suggestion="Upload a valid PNG or JPEG image.",
            failure_reason="invalid_image_signature",
        )

    if detected_format != expected_format:
        return _failure(
            code="mime_signature_mismatch",
            message="Image MIME type does not match the file signature.",
            suggestion="Upload an image whose file type matches its content.",
            failure_reason="mime_signature_mismatch",
        )

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image = ImageOps.exif_transpose(image)
            width, height = image.size

            if width > max_width or height > max_height:
                return _failure(
                    code="image_dimensions_too_large",
                    message="Image dimensions exceed the detection decode limit.",
                    suggestion="Use a smaller board screenshot.",
                    failure_reason="oversized_dimensions",
                )

            mode = _target_mode(image)
            normalized_image = image.convert(mode)
            pixels = normalized_image.tobytes()
    except (Image.DecompressionBombError, OSError, UnidentifiedImageError, ValueError):
        return _failure(
            code="invalid_image_bytes",
            message="Image payload could not be decoded.",
            suggestion="Upload a valid, non-corrupted PNG or JPEG image.",
            failure_reason="malformed_or_truncated_image",
        )

    return DecodedImage(
        width=width,
        height=height,
        format=detected_format,
        mode=mode,
        pixels=pixels,
        metadata=DetectionMetadata(
            confidence=1.0,
            source=SOURCE,
            stage="preprocess",
        ),
    )


def detect_image_format(image_bytes: bytes) -> ImageFormat | None:
    if image_bytes.startswith(PNG_SIGNATURE):
        return "png"

    if image_bytes.startswith(JPEG_SIGNATURE):
        return "jpeg"

    return None


def _target_mode(image: Image.Image) -> ImageMode:
    if "A" in image.getbands():
        return "RGBA"

    return "RGB"


def _normalize_content_type(content_type: str) -> str:
    return content_type.split(";", 1)[0].strip().lower()


def _failure(
    *,
    code: str,
    message: str,
    suggestion: str,
    failure_reason: str,
) -> ImageDecodeFailure:
    return ImageDecodeFailure(
        code=code,
        message=message,
        suggestion=suggestion,
        failure_reason=failure_reason,
    )
