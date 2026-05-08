import json
from dataclasses import replace
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.role_classifier import (
    SOURCE_STAGE,
    classify_fixture_roles,
)
from app.detection.role_signal_audit_v2 import audit_fixture_role_signals_v2

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
ROLE_SIGNAL_FILENAMES = {
    "owned_role-signal_white-bottom_dense-01.png",
    "owned_role-signal_black-bottom_dense-01.png",
    "owned_role-signal_white-bottom_shifted-01.png",
}
REQUIRED_ROLES = {"king", "queen", "rook", "bishop", "knight", "pawn"}


def test_role_classifier_measures_owned_role_signal_fixtures() -> None:
    manifest = _load_valid_manifest()
    classifications = tuple(
        classify_fixture_roles(
            audit_fixture_role_signals_v2(case, _decode_case_image(case))
        )
        for case in _role_signal_cases(manifest)
    )

    assert {item.summary.filename for item in classifications} == ROLE_SIGNAL_FILENAMES
    assert sum(item.summary.occupied_square_count for item in classifications) == 36
    assert sum(item.summary.measured_role_count for item in classifications) == 36
    assert sum(item.summary.correct_count for item in classifications) == 36
    assert sum(item.summary.wrong_count for item in classifications) == 0
    assert sum(item.summary.ambiguous_count for item in classifications) == 0
    assert sum(item.summary.unsupported_count for item in classifications) == 0
    assert sum(item.summary.not_measured_count for item in classifications) == 0
    assert _detected_roles(classifications) == REQUIRED_ROLES
    assert {row.source_stage for item in classifications for row in item.rows} == {
        SOURCE_STAGE
    }


def test_role_classifier_keeps_expected_metadata_as_scoring_only() -> None:
    manifest = _load_valid_manifest()
    case = next(
        case
        for case in _role_signal_cases(manifest)
        if case["id"] == "owned_role-signal_white-bottom_dense-01"
    )
    audit = audit_fixture_role_signals_v2(case, _decode_case_image(case))
    tampered_samples = tuple(
        replace(sample, expected_role="queen")
        if sample.square == "a2"
        else sample
        for sample in audit.samples
    )
    tampered_audit = replace(audit, samples=tampered_samples)

    classification = classify_fixture_roles(tampered_audit)
    row = next(row for row in classification.rows if row.square == "a2")

    assert row.detected_role == "rook"
    assert row.expected_role == "queen"
    assert row.role_result == "wrong"


def test_non_role_signal_fixture_is_unsupported() -> None:
    manifest = _load_valid_manifest()
    case = next(
        case
        for case in manifest["cases"]
        if not case["expected_metrics"].get("role_signal_fixture")
    )

    classification = classify_fixture_roles(
        audit_fixture_role_signals_v2(case, _decode_case_image(case))
    )

    assert classification.summary.unsupported_count == len(classification.rows)
    assert classification.summary.measured_role_count == 0
    assert classification.summary.blocker_notes == ("unsupported_fixture",)
    assert {row.detected_role for row in classification.rows} == {None}
    assert {row.failure_reason for row in classification.rows} == {
        "unsupported_fixture"
    }


def test_missing_signature_returns_not_measured_without_guessing() -> None:
    manifest = _load_valid_manifest()
    case = _role_signal_cases(manifest)[0]
    audit = audit_fixture_role_signals_v2(case, _decode_case_image(case))
    first_sample = audit.samples[0]
    modified_audit = replace(
        audit,
        samples=(
            replace(first_sample, signature=None, failure_reason="sample_unavailable"),
            *audit.samples[1:],
        ),
    )

    classification = classify_fixture_roles(modified_audit)
    row = next(row for row in classification.rows if row.square == first_sample.square)

    assert row.detected_role is None
    assert row.role_result == "not_measured"
    assert row.failure_reason == "sample_unavailable"


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


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result


def _detected_roles(classifications: tuple) -> set[str]:
    return {
        row.detected_role
        for classification in classifications
        for row in classification.rows
        if row.detected_role is not None
    }
