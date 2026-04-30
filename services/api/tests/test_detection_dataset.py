from pathlib import Path

from tests.helpers.detection_fixtures import (
    FIXTURE_DIR,
    generate_synthetic_ppm_board,
    load_detection_cases,
    load_detection_manifest,
)

REQUIRED_CASE_FIELDS = {
    "id",
    "kind",
    "description",
    "generator",
    "expected",
    "synthetic",
}
REQUIRED_EXPECTED_FIELDS = {"fen", "orientation"}


def test_detection_dataset_metadata_loads() -> None:
    manifest = load_detection_manifest()

    assert manifest["version"] == 1
    assert len(manifest["cases"]) >= 1


def test_detection_dataset_cases_include_required_fields() -> None:
    cases = load_detection_cases()

    for case in cases:
        assert REQUIRED_CASE_FIELDS <= case.keys()
        assert REQUIRED_EXPECTED_FIELDS <= case["expected"].keys()
        assert case["kind"] == "synthetic"
        assert case["expected"]["fen"]
        assert case["expected"]["orientation"] in {
            "white-bottom",
            "black-bottom",
            "unknown",
        }


def test_synthetic_fixture_generation_is_deterministic() -> None:
    case = load_detection_cases()[0]

    first_image = generate_synthetic_ppm_board(case)
    second_image = generate_synthetic_ppm_board(case)

    assert first_image == second_image
    assert first_image.startswith(b"P6\n")


def test_detection_dataset_does_not_require_binary_fixtures() -> None:
    binary_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".ppm"}
    binary_files = [
        path
        for path in Path(FIXTURE_DIR).iterdir()
        if path.is_file() and path.suffix.lower() in binary_suffixes
    ]

    assert binary_files == []
