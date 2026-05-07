import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.detection.fixture_metadata import validate_approved_fixture_manifest

APPROVED_DIR = (
    Path(__file__).parent / "fixtures" / "detection" / "approved"
)
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_approved_manifest_with_committed_images_is_valid() -> None:
    manifest = json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8"))

    result = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert manifest["version"] == 1
    assert {case["filename"] for case in manifest["cases"]} == {
        "synthetic_default_white-bottom_start-01.png",
        "synthetic_default_black-bottom_start-01.png",
        "synthetic_default_white-bottom_kings-rook-01.png",
        "synthetic_default_black-bottom_kings-rook-01.png",
        "owned_web_white-bottom_start-01.png",
        "owned_web_black-bottom_start-01.png",
        "owned_chesscom-like_white-bottom_kings-rook-01.png",
        "owned_lichess-like_white-bottom_middlegame-01.png",
    }
    assert result.valid is True
    assert result.issues == ()


def test_valid_success_metadata_passes_without_requiring_image_file() -> None:
    manifest = {"version": 1, "cases": [valid_success_case()]}

    result = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
    )

    assert result.valid is True


def test_missing_required_field_fails_clearly() -> None:
    case = valid_success_case()
    del case["source"]

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert issue_codes(result) == {"missing_required_field"}


def test_invalid_orientation_fails() -> None:
    case = valid_success_case()
    case["orientation"] = "sideways"

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "invalid_orientation" in issue_codes(result)


def test_absolute_path_fails() -> None:
    case = valid_success_case(filename="/tmp/fixture.png")

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "invalid_path" in issue_codes(result)


def test_parent_traversal_path_fails() -> None:
    case = valid_success_case(filename="../fixture.png")

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "invalid_path" in issue_codes(result)


def test_raw_large_archive_and_dump_paths_fail() -> None:
    filenames = [
        "raw/fixture.png",
        "large/fixture.png",
        "archives/fixture.png",
        "dumps/fixture.png",
        "approved-fixtures.zip",
    ]

    for filename in filenames:
        case = valid_success_case(filename=filename)
        result = validate_approved_fixture_manifest(
            {"version": 1, "cases": [case]},
            approved_dir=APPROVED_DIR,
        )
        assert "forbidden_path" in issue_codes(result)


def test_missing_license_status_or_note_fails() -> None:
    case = valid_success_case()
    case["license"] = {"status": "", "note": ""}

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert issue_codes(result) == {"missing_license"}


def test_missing_expected_fen_for_success_case_fails() -> None:
    case = valid_success_case()
    case["expected_fen"] = ""

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "missing_expected_fen" in issue_codes(result)


def test_missing_expected_pieces_fails() -> None:
    case = valid_success_case()
    del case["expected_pieces"]

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "missing_required_field" in issue_codes(result)


def test_invalid_expected_piece_square_fails() -> None:
    case = valid_success_case()
    case["expected_pieces"][0]["square"] = "i9"

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "invalid_expected_piece_square" in issue_codes(result)


def test_invalid_expected_piece_role_or_color_fails() -> None:
    case = valid_success_case()
    case["expected_pieces"][0]["piece"] = "archer"
    case["expected_pieces"][1]["color"] = "green"

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert issue_codes(result) == {
        "invalid_expected_piece_color",
        "invalid_expected_piece_role",
    }


def test_duplicate_expected_piece_square_fails() -> None:
    case = valid_success_case()
    case["expected_pieces"][1]["square"] = case["expected_pieces"][0]["square"]

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "duplicate_expected_piece_square" in issue_codes(result)


def test_expected_pieces_must_match_expected_fen_occupied_squares() -> None:
    case = valid_success_case()
    case["expected_pieces"] = case["expected_pieces"][:1]

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "expected_pieces_fen_mismatch" in issue_codes(result)


def test_expected_piece_role_and_color_must_match_expected_fen() -> None:
    case = valid_success_case()
    case["expected_pieces"][0]["color"] = "black"

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "expected_pieces_fen_mismatch" in issue_codes(result)


def test_invalid_fen_piece_placement_fails() -> None:
    case = valid_success_case()
    case["expected_fen"] = "9/8/8/8/8/8/8/4K3 w - - 0 1"

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [case]},
        approved_dir=APPROVED_DIR,
    )

    assert "invalid_expected_fen" in issue_codes(result)


def test_existing_temporary_image_file_is_decoded_when_required(
    tmp_path: Path,
) -> None:
    approved_dir = tmp_path / "approved"
    approved_dir.mkdir()
    fixture_path = approved_dir / "synthetic_default_white-bottom_start-01.png"
    fixture_path.write_bytes(make_png_bytes())

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [valid_success_case(filename=fixture_path.name)]},
        approved_dir=approved_dir,
        require_existing_images=True,
    )

    assert result.valid is True


def test_missing_image_file_fails_when_existing_files_required(
    tmp_path: Path,
) -> None:
    approved_dir = tmp_path / "approved"
    approved_dir.mkdir()

    result = validate_approved_fixture_manifest(
        {"version": 1, "cases": [valid_success_case()]},
        approved_dir=approved_dir,
        require_existing_images=True,
    )

    assert "missing_image_file" in issue_codes(result)


def valid_success_case(
    *,
    filename: str = "lichess-like_default_white-bottom_start-01.png",
) -> dict:
    return {
        "id": "lichess-like_default_white-bottom_start-01",
        "filename": filename,
        "kind": "approved_manual_fixture",
        "source": "lichess-like",
        "style": "default",
        "orientation": "white-bottom",
        "board_bounds": {"x": 0, "y": 0, "width": 512, "height": 512},
        "expected_pieces": [
            {"square": "e1", "piece": "king", "color": "white"},
            {"square": "e8", "piece": "king", "color": "black"},
        ],
        "expected_fen": "4k3/8/8/8/8/8/8/4K3 w - - 0 1",
        "expected_metrics": {
            "board_crop_detected": True,
            "orientation_detected": "white-bottom",
            "piece_list_required": True,
            "fen_match_required": True,
            "failure_reason_required": False,
        },
        "license": {
            "status": "approved",
            "note": "Test metadata only; no real screenshot is committed.",
        },
        "notes": "Metadata-only test case.",
    }


def issue_codes(result) -> set[str]:
    return {issue.code for issue in result.issues}


def make_png_bytes() -> bytes:
    image = Image.new("RGB", (2, 2), color=(10, 20, 30))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
