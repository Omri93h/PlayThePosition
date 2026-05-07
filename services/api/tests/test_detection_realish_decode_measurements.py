import json
from pathlib import Path

from app.detection.fixture_metadata import validate_approved_fixture_manifest
from app.detection.image import MAX_IMAGE_BYTES, DecodedImage, decode_image_bytes

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
REALISH_FIXTURE_FILENAMES = {
    "owned_web_white-bottom_start-01.png",
    "owned_web_black-bottom_start-01.png",
    "owned_chesscom-like_white-bottom_kings-rook-01.png",
    "owned_lichess-like_white-bottom_middlegame-01.png",
}
CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def test_realish_fixture_decode_measurements_match_expected_metadata() -> None:
    manifest = json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8"))
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is True
    assert validation.issues == ()

    realish_cases = [case for case in manifest["cases"] if case["source"] == "owned"]

    assert {case["filename"] for case in realish_cases} == REALISH_FIXTURE_FILENAMES

    measurements = []

    for case in realish_cases:
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
    assert {measurement["format"] for measurement in measurements} == {"png"}
    assert {measurement["width"] for measurement in measurements} == {512}
    assert {measurement["height"] for measurement in measurements} == {512}
    assert {measurement["mode"] for measurement in measurements} == {"RGB"}
