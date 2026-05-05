import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import (
    BoardBounds,
    BoardBoundsDetectionSuccess,
    detect_board_bounds_from_decoded_image,
)
from app.detection.image import DecodedImage, decode_image_bytes

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_approved_fixture_board_bounds_measurements_match_expected_metadata() -> None:
    manifest = json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8"))
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is True
    assert validation.issues == ()

    measurements = []

    for case in manifest["cases"]:
        image_path = APPROVED_DIR / case["filename"]
        image_bytes = image_path.read_bytes()
        content_type = IMAGE_CONTENT_TYPES[image_path.suffix.lower()]
        decoded = decode_image_bytes(image_bytes, content_type)

        assert isinstance(decoded, DecodedImage), case["id"]

        result = detect_board_bounds_from_decoded_image(decoded)

        assert isinstance(result, BoardBoundsDetectionSuccess), case["id"]
        assert case["expected_metrics"]["board_bounds_required"] is True
        assert result.stage == case["expected_metrics"]["expected_board_bounds_stage"]
        assert result.source == case["expected_metrics"]["expected_board_bounds_source"]
        assert (
            result.confidence
            >= case["expected_metrics"]["expected_board_bounds_confidence_min"]
        )
        assert _bounds_to_dict(result.bounds) == case["board_bounds"]

        measurements.append(
            {
                "id": case["id"],
                "detected": True,
                "bounds": _bounds_to_dict(result.bounds),
                "confidence": result.confidence,
                "stage": result.stage,
                "source": result.source,
            }
        )

    assert len(measurements) == 4
    assert {measurement["detected"] for measurement in measurements} == {True}
    assert {measurement["bounds"]["width"] for measurement in measurements} == {512}
    assert {measurement["bounds"]["height"] for measurement in measurements} == {512}


def _bounds_to_dict(bounds: BoardBounds) -> dict[str, int]:
    return {
        "x": bounds.x,
        "y": bounds.y,
        "width": bounds.width,
        "height": bounds.height,
    }
