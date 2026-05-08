import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.role_color_signal_audit import audit_fixture_role_color_signals

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
REALISH_FIXTURE_IDS = {
    "owned_web_white-bottom_start-01",
    "owned_web_black-bottom_start-01",
    "owned_chesscom-like_white-bottom_kings-rook-01",
    "owned_lichess-like_white-bottom_middlegame-01",
}


def test_approved_fixture_signal_audit_measures_all_expected_pieces() -> None:
    manifest = _load_valid_manifest()
    block_12_cases = _block_12_cases(manifest)

    audits = tuple(
        audit_fixture_role_color_signals(case, _decode_case_image(case))
        for case in block_12_cases
    )

    assert len(audits) == 8
    assert sum(audit.occupied_square_count for audit in audits) == 167
    assert sum(audit.measured_signal_count for audit in audits) == 167
    assert {audit.color.status for audit in audits} == {"feasible"}
    assert {audit.role.status for audit in audits} == {
        "ambiguous",
        "unsupported",
    }


def test_realish_fixture_color_signal_is_feasible_without_role_claims() -> None:
    manifest = _load_valid_manifest()
    realish_cases = tuple(
        case for case in manifest["cases"] if case["id"] in REALISH_FIXTURE_IDS
    )

    audits = tuple(
        audit_fixture_role_color_signals(case, _decode_case_image(case))
        for case in realish_cases
    )

    assert {audit.fixture_id for audit in audits} == REALISH_FIXTURE_IDS
    assert {audit.color.status for audit in audits} == {"feasible"}
    assert all(audit.color.distance is not None for audit in audits)
    assert any(audit.role.status == "ambiguous" for audit in audits)
    assert any(audit.role.status == "unsupported" for audit in audits)


def test_sparse_fixture_role_signal_is_unsupported_for_full_role_classifier() -> None:
    manifest = _load_valid_manifest()
    case = next(
        case
        for case in manifest["cases"]
        if case["id"] == "owned_chesscom-like_white-bottom_kings-rook-01"
    )

    audit = audit_fixture_role_color_signals(case, _decode_case_image(case))

    assert audit.occupied_square_count == 3
    assert audit.measured_signal_count == 3
    assert audit.color.status == "feasible"
    assert audit.role.status == "unsupported"
    assert audit.role.reason == "insufficient_role_coverage"
    assert audit.role.observed_groups == ("king", "rook")


def test_start_position_role_signal_is_ambiguous_not_feasible() -> None:
    manifest = _load_valid_manifest()
    case = next(
        case
        for case in manifest["cases"]
        if case["id"] == "owned_web_white-bottom_start-01"
    )

    audit = audit_fixture_role_color_signals(case, _decode_case_image(case))

    assert audit.occupied_square_count == 32
    assert audit.color.status == "feasible"
    assert audit.role.status == "ambiguous"
    assert audit.role.reason == "role_signals_overlap"
    assert audit.role.distance is not None


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


def _block_12_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if not case["expected_metrics"].get("role_signal_fixture")
    )


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result
