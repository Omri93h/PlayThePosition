import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.square_sampling import (
    SOURCE_STAGE,
    derive_square_regions,
    sample_fixture_squares,
)

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_square_regions_are_derived_from_board_bounds_and_orientation() -> None:
    bounds = BoardBounds(x=16, y=24, width=320, height=320)

    white_regions = derive_square_regions(bounds, "white-bottom")
    black_regions = derive_square_regions(bounds, "black-bottom")

    assert len(white_regions) == 64
    assert white_regions[0].square == "a8"
    assert white_regions[-1].square == "h1"
    assert white_regions[0].x == 16
    assert white_regions[0].y == 24
    assert white_regions[0].width == 40
    assert white_regions[0].height == 40
    assert black_regions[0].square == "h1"
    assert black_regions[-1].square == "a8"


def test_approved_fixtures_can_be_sampled_into_contract_rows() -> None:
    manifest = _load_valid_manifest()

    for case in manifest["cases"]:
        decoded = _decode_case_image(case)
        samples = sample_fixture_squares(
            fixture_id=case["id"],
            image=decoded,
            board_bounds=_board_bounds(case),
            orientation=case["orientation"],
        )
        expected_occupied = {piece["square"] for piece in case["expected_pieces"]}
        sampled_by_square = {sample.square: sample for sample in samples}

        assert len(samples) == 64
        assert set(sampled_by_square) == _all_squares()
        assert {sample.source_stage for sample in samples} == {SOURCE_STAGE}
        assert {sample.failure_reason for sample in samples} == {None}
        assert {sample.fixture_id for sample in samples} == {case["id"]}
        assert {
            sample.square
            for sample in samples
            if sample.detected_state == "occupied"
        } == expected_occupied
        assert {
            sample.square for sample in samples if sample.detected_state == "empty"
        } == _all_squares() - expected_occupied

        first_sample = samples[0]
        assert first_sample.detected_piece is None
        assert first_sample.detected_color is None
        assert first_sample.confidence is not None


def test_invalid_bounds_return_not_measured_samples_without_crashing() -> None:
    manifest = _load_valid_manifest()
    case = manifest["cases"][0]
    decoded = _decode_case_image(case)

    samples = sample_fixture_squares(
        fixture_id=case["id"],
        image=decoded,
        board_bounds=BoardBounds(x=0, y=0, width=511, height=512),
        orientation=case["orientation"],
    )

    assert len(samples) == 64
    assert {sample.detected_state for sample in samples} == {"not_measured"}
    assert {sample.confidence for sample in samples} == {None}
    assert {sample.failure_reason for sample in samples} == {"invalid_board_bounds"}


def test_unsupported_orientation_returns_not_measured_samples() -> None:
    manifest = _load_valid_manifest()
    case = manifest["cases"][0]
    decoded = _decode_case_image(case)

    samples = sample_fixture_squares(
        fixture_id=case["id"],
        image=decoded,
        board_bounds=_board_bounds(case),
        orientation="unknown",
    )

    assert len(samples) == 64
    assert {sample.detected_state for sample in samples} == {"not_measured"}
    assert {sample.failure_reason for sample in samples} == {"unsupported_orientation"}


def _load_valid_manifest() -> dict:
    manifest = json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8"))
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is True
    assert validation.issues == ()

    return manifest


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result


def _board_bounds(case: dict) -> BoardBounds:
    bounds = case["board_bounds"]

    return BoardBounds(
        x=bounds["x"],
        y=bounds["y"],
        width=bounds["width"],
        height=bounds["height"],
    )


def _all_squares() -> set[str]:
    return {f"{file}{rank}" for file in "abcdefgh" for rank in "12345678"}
