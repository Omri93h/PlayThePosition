import json
from pathlib import Path

from app.detection.fixture_metadata import validate_approved_fixture_manifest
from app.detection.image import MAX_IMAGE_BYTES, DecodedImage, decode_image_bytes

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def test_approved_fixture_decode_measurements_match_expected_metadata() -> None:
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
        content_type = CONTENT_TYPES[image_path.suffix.lower()]
        decoded = decode_image_bytes(image_bytes, content_type)

        assert isinstance(decoded, DecodedImage), case["id"]
        assert decoded.metadata.stage == "preprocess"
        assert decoded.metadata.status == "success"

        expected_metrics = case["expected_metrics"]
        assert expected_metrics["decode_required"] is True
        assert decoded.format == expected_metrics["expected_format"]
        assert decoded.width == expected_metrics["expected_width"]
        assert decoded.height == expected_metrics["expected_height"]
        assert decoded.mode == expected_metrics["expected_mode"]
        assert 0 < len(image_bytes) <= MAX_IMAGE_BYTES

        measurements.append(
            {
                "id": case["id"],
                "format": decoded.format,
                "width": decoded.width,
                "height": decoded.height,
                "mode": decoded.mode,
                "bytes": len(image_bytes),
                "status": decoded.metadata.status,
            }
        )

    assert len(measurements) == 4
    assert {measurement["status"] for measurement in measurements} == {"success"}
