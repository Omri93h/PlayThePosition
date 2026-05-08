import json
from pathlib import Path

from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.role_signal_audit_v2 import (
    ROLE_SEPARATION_MARGIN_MIN,
    SOURCE_STAGE,
    aggregate_role_signal_audits_v2,
    audit_fixture_role_signals_v2,
)

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"
ROLE_SIGNAL_FILENAMES = {
    "owned_role-signal_white-bottom_dense-01.png",
    "owned_role-signal_black-bottom_dense-01.png",
    "owned_role-signal_white-bottom_shifted-01.png",
}
REQUIRED_ROLES = ("king", "queen", "rook", "bishop", "knight", "pawn")


def test_role_signal_audit_v2_measures_only_role_signal_gate_fixtures() -> None:
    manifest = _load_valid_manifest()
    role_signal_cases = _role_signal_cases(manifest)

    audits = tuple(
        audit_fixture_role_signals_v2(case, _decode_case_image(case))
        for case in role_signal_cases
    )

    assert {audit.filename for audit in audits} == ROLE_SIGNAL_FILENAMES
    assert {audit.source_stage for audit in _all_samples(audits)} == {SOURCE_STAGE}
    assert {audit.style for audit in audits} == {"role-signal"}
    assert {audit.source for audit in audits} == {"owned"}
    assert len(audits) == 3


def test_role_signal_audit_v2_reports_per_fixture_role_separability() -> None:
    manifest = _load_valid_manifest()

    for case in _role_signal_cases(manifest):
        audit = audit_fixture_role_signals_v2(case, _decode_case_image(case))

        assert audit.occupied_square_count == 12
        assert audit.measured_signal_count == 12
        assert audit.separability.status == "feasible"
        assert audit.separability.reason == "role_signals_separable"
        assert audit.separability.observed_roles == REQUIRED_ROLES
        assert audit.separability.ambiguous_pairs == ()
        assert audit.separability.minimum_margin is not None
        assert audit.separability.minimum_margin >= ROLE_SEPARATION_MARGIN_MIN
        assert audit.separability.minimum_pairwise_distance is not None
        assert len(audit.pair_distances) == 15
        assert {sample.failure_reason for sample in audit.samples} == {None}
        assert {sample.signature is not None for sample in audit.samples} == {True}


def test_role_signal_audit_v2_reports_aggregate_gate_result() -> None:
    manifest = _load_valid_manifest()
    audits = tuple(
        audit_fixture_role_signals_v2(case, _decode_case_image(case))
        for case in _role_signal_cases(manifest)
    )

    aggregate = aggregate_role_signal_audits_v2(audits)

    assert aggregate.fixture_count == 3
    assert aggregate.occupied_square_count == 36
    assert aggregate.measured_signal_count == 36
    assert aggregate.separability.status == "feasible"
    assert aggregate.separability.reason == "role_signals_separable"
    assert aggregate.separability.observed_roles == REQUIRED_ROLES
    assert aggregate.separability.ambiguous_pairs == ()
    assert aggregate.separability.minimum_margin is not None
    assert aggregate.separability.minimum_margin >= ROLE_SEPARATION_MARGIN_MIN
    assert aggregate.separability.minimum_pairwise_distance is not None
    assert len(aggregate.pair_distances) == 15


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


def _all_samples(audits: tuple) -> tuple:
    return tuple(sample for audit in audits for sample in audit.samples)
