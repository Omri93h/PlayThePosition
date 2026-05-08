import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.image import DecodedImage, decode_image_bytes

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
ROLE_SIGNAL_FILENAMES = {
    "owned_role-signal_white-bottom_dense-01.png",
    "owned_role-signal_black-bottom_dense-01.png",
    "owned_role-signal_white-bottom_shifted-01.png",
}
REQUIRED_ROLES = {"king", "queen", "rook", "bishop", "knight", "pawn"}
REQUIRED_COLORS = {"white", "black"}


def test_role_signal_fixtures_are_owned_generated_and_metadata_valid() -> None:
    manifest = _load_valid_manifest()
    role_signal_cases = _role_signal_cases(manifest)

    assert {case["filename"] for case in role_signal_cases} == ROLE_SIGNAL_FILENAMES
    assert {case["source"] for case in role_signal_cases} == {"owned"}
    assert {case["style"] for case in role_signal_cases} == {"role-signal"}
    assert {case["kind"] for case in role_signal_cases} == {"synthetic"}

    for case in role_signal_cases:
        metrics = case["expected_metrics"]

        assert metrics["role_signal_fixture"] is True
        assert metrics["role_signal_audit_required"] is True
        assert set(metrics["required_roles"]) == REQUIRED_ROLES
        assert set(metrics["required_colors"]) == REQUIRED_COLORS
        assert metrics["role_signal_source"] == "owned_pixel_marker"
        assert metrics["role_signal_must_not_use_metadata"] is True
        assert case["expected_failure"] is None
        assert case["license"]["status"] == "owned"
        assert "owned deterministic role-signal fixture rendering" in (
            case["license"]["note"]
        )
        assert "external assets" in case["license"]["note"]
        assert "user uploads" in case["license"]["note"]


def test_role_signal_fixtures_cover_roles_colors_and_square_colors() -> None:
    manifest = _load_valid_manifest()
    role_signal_cases = _role_signal_cases(manifest)

    for case in role_signal_cases:
        pieces = case["expected_pieces"]

        assert {piece["piece"] for piece in pieces} == REQUIRED_ROLES
        assert {piece["color"] for piece in pieces} == REQUIRED_COLORS
        assert len(pieces) == 12
        assert _square_colors(case) == {"light", "dark"}

    shifted = next(
        case
        for case in role_signal_cases
        if case["id"] == "owned_role-signal_white-bottom_shifted-01"
    )
    dense = next(
        case
        for case in role_signal_cases
        if case["id"] == "owned_role-signal_white-bottom_dense-01"
    )

    assert _role_squares(shifted) != _role_squares(dense)


def test_role_signal_fixtures_decode_as_owned_png_images() -> None:
    manifest = _load_valid_manifest()

    for case in _role_signal_cases(manifest):
        image_path = APPROVED_DIR / case["filename"]
        decoded = decode_image_bytes(
            image_path.read_bytes(),
            IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
        )

        assert isinstance(decoded, DecodedImage), case["id"]
        assert decoded.format == case["expected_metrics"]["expected_format"]
        assert decoded.width == case["expected_metrics"]["expected_width"]
        assert decoded.height == case["expected_metrics"]["expected_height"]
        assert decoded.mode == case["expected_metrics"]["expected_mode"]


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


def _role_signal_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if case["expected_metrics"].get("role_signal_fixture")
    )


def _role_squares(case: dict) -> dict[str, set[str]]:
    by_role = {role: set() for role in REQUIRED_ROLES}

    for piece in case["expected_pieces"]:
        by_role[piece["piece"]].add(piece["square"])

    return by_role


def _square_colors(case: dict) -> set[str]:
    return {
        _square_color(piece["square"], case["orientation"])
        for piece in case["expected_pieces"]
    }


def _square_color(square: str, orientation: str) -> str:
    file_index = ord(square[0]) - ord("a")
    rank = int(square[1])

    if orientation == "black-bottom":
        row = rank - 1
        column = 7 - file_index
    else:
        row = 8 - rank
        column = file_index

    return "light" if (row + column) % 2 == 0 else "dark"
