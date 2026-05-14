import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

from app.detection.color_classifier import classify_fixture_colors
from app.detection.fen_reconstruction import (
    FenPlacementFailure,
    FenPlacementSuccess,
    FenReconstructionSuccess,
    build_fen_placement_from_measured_rows,
    build_full_fen_from_measured_rows,
)
from app.detection.fixture_metadata import (
    IMAGE_CONTENT_TYPES,
    validate_approved_fixture_manifest,
)
from app.detection.grid import BoardBounds
from app.detection.image import DecodedImage, decode_image_bytes
from app.detection.measured_pieces import (
    ConfidenceMetadata,
    MeasuredPieceRow,
    build_measured_piece_rows,
)
from app.detection.role_classifier import classify_fixture_roles
from app.detection.role_color_signal_audit import audit_fixture_role_color_signals
from app.detection.role_signal_audit_v2 import audit_fixture_role_signals_v2
from app.detection.square_sampling import SquareSample, sample_fixture_squares

APPROVED_DIR = Path(__file__).parent / "fixtures" / "detection" / "approved"
APPROVED_MANIFEST_PATH = APPROVED_DIR / "cases.json"


def test_builds_placement_from_measured_piece_rows() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e8", "black", "king"),
            _piece_row("a7", "black", "pawn"),
            _piece_row("h2", "white", "queen"),
            _piece_row("e1", "white", "king"),
        )
    )

    assert isinstance(result, FenPlacementSuccess)
    assert result.placement == "4k3/p7/8/8/8/8/7Q/4K3"


def test_maps_all_roles_and_colors_to_fen_letters() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("a8", "black", "king"),
            _piece_row("b8", "black", "queen"),
            _piece_row("c8", "black", "rook"),
            _piece_row("d8", "black", "bishop"),
            _piece_row("e8", "black", "knight"),
            _piece_row("f8", "black", "pawn"),
            _piece_row("a1", "white", "king"),
            _piece_row("b1", "white", "queen"),
            _piece_row("c1", "white", "rook"),
            _piece_row("d1", "white", "bishop"),
            _piece_row("e1", "white", "knight"),
            _piece_row("f1", "white", "pawn"),
        )
    )

    assert isinstance(result, FenPlacementSuccess)
    assert result.placement == "kqrbnp2/8/8/8/8/8/8/KQRBNP2"


def test_unsupported_row_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _unsupported_row("e4", "ambiguous_color"),
        )
    )

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "ambiguous_color"
    assert result.failure_reasons == ("ambiguous_color",)


def test_missing_role_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e4", "white", None),
        )
    )

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "missing_role"


def test_missing_color_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e4", None, "king"),
        )
    )

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "missing_color"


def test_missing_square_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(_rows()[:-1])

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "missing_square_sample"


def test_duplicate_square_blocks_placement() -> None:
    rows = tuple(row for row in _rows() if row.square != "h8") + (_empty_row("a1"),)
    result = build_fen_placement_from_measured_rows(rows)

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "duplicate_square_sample"


def test_missing_white_king_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e8", "black", "king"),
        )
    )

    _assert_failure(result, "missing_white_king")


def test_missing_black_king_blocks_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e1", "white", "king"),
        )
    )

    _assert_failure(result, "missing_black_king")


def test_duplicate_white_kings_block_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e1", "white", "king"),
            _piece_row("a1", "white", "king"),
            _piece_row("e8", "black", "king"),
        )
    )

    _assert_failure(result, "duplicate_white_king")


def test_duplicate_black_kings_block_placement() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _piece_row("e1", "white", "king"),
            _piece_row("e8", "black", "king"),
            _piece_row("a8", "black", "king"),
        )
    )

    _assert_failure(result, "duplicate_black_king")


def test_full_fen_inherits_invalid_board_failures() -> None:
    result = build_full_fen_from_measured_rows(
        _rows(
            _piece_row("e8", "black", "king"),
        ),
        side_to_move="w",
    )

    _assert_failure(result, "missing_white_king")


def test_row_level_failures_take_precedence_over_invalid_board_failures() -> None:
    result = build_fen_placement_from_measured_rows(
        _rows(
            _unsupported_row("e4", "ambiguous_color"),
        )
    )

    _assert_failure(result, "ambiguous_color")


def test_builds_full_fen_only_with_explicit_side_to_move() -> None:
    result = build_full_fen_from_measured_rows(
        _rows(
            _piece_row("e8", "black", "king"),
            _piece_row("e1", "white", "king"),
        ),
        side_to_move="b",
    )

    assert isinstance(result, FenReconstructionSuccess)
    assert result.fen == "4k3/8/8/8/8/8/8/4K3 b - - 0 1"
    assert result.placement == "4k3/8/8/8/8/8/8/4K3"
    assert result.side_to_move == "b"
    assert result.castling == "-"
    assert result.en_passant == "-"
    assert result.halfmove == 0
    assert result.fullmove == 1


def test_missing_side_to_move_blocks_full_fen() -> None:
    result = build_full_fen_from_measured_rows(_rows(), side_to_move=None)

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "missing_side_to_move"


def test_invalid_side_to_move_blocks_full_fen() -> None:
    result = build_full_fen_from_measured_rows(_rows(), side_to_move="white")

    assert isinstance(result, FenPlacementFailure)
    assert result.code == "invalid_side_to_move"


def test_manifest_validation_requires_explicit_side_to_move() -> None:
    manifest = _load_manifest()
    manifest["cases"][0].pop("side_to_move")

    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is False
    assert any(issue.code == "missing_side_to_move" for issue in validation.issues)


def test_manifest_validation_rejects_invalid_side_to_move() -> None:
    manifest = _load_manifest()
    manifest["cases"][0]["side_to_move"] = "white"

    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is False
    assert any(issue.code == "invalid_side_to_move" for issue in validation.issues)


def test_approved_role_signal_fixture_placements_compare_to_expected() -> None:
    manifest = _load_valid_manifest()
    results = tuple(
        (
            _expected_placement(case),
            build_fen_placement_from_measured_rows(_build_case_rows(case)),
        )
        for case in _role_signal_cases(manifest)
    )

    successes = tuple(
        result for _, result in results if isinstance(result, FenPlacementSuccess)
    )
    failures = tuple(
        result for _, result in results if isinstance(result, FenPlacementFailure)
    )

    assert len(successes) == 3
    assert failures == ()

    placement_matches = tuple(
        result.placement == expected_placement
        for expected_placement, result in results
        if isinstance(result, FenPlacementSuccess)
    )
    assert placement_matches == (True, True, True)


def test_approved_role_signal_fixtures_build_full_fen_from_side_to_move() -> None:
    manifest = _load_valid_manifest()
    results = tuple(
        (
            case["expected_fen"],
            build_full_fen_from_measured_rows(
                _build_case_rows(case),
                side_to_move=case["side_to_move"],
            ),
        )
        for case in _role_signal_cases(manifest)
    )

    successes = tuple(
        result for _, result in results if isinstance(result, FenReconstructionSuccess)
    )
    failures = tuple(
        result for _, result in results if isinstance(result, FenPlacementFailure)
    )

    assert len(successes) == 3
    assert failures == ()
    assert tuple(result.fen == expected_fen for expected_fen, result in results) == (
        True,
        True,
        True,
    )


def test_black_bottom_measured_rows_do_not_get_transformed_again_for_fen() -> None:
    manifest = _load_valid_manifest()
    case = next(
        case
        for case in _role_signal_cases(manifest)
        if case["orientation"] == "black-bottom"
    )
    rows = _build_case_rows(case)

    result = build_full_fen_from_measured_rows(
        rows,
        side_to_move=case["side_to_move"],
    )
    double_transform_result = build_fen_placement_from_measured_rows(
        _double_transformed_rows(rows)
    )

    assert isinstance(result, FenReconstructionSuccess)
    assert result.placement == _expected_placement(case)
    assert isinstance(double_transform_result, FenPlacementSuccess)
    assert result.placement != double_transform_result.placement


def _build_case_rows(case: dict) -> tuple[MeasuredPieceRow, ...]:
    decoded = _decode_case_image(case)
    samples = _sample_case(case, decoded)
    color_classification = classify_fixture_colors(
        audit=audit_fixture_role_color_signals(case, decoded),
        samples=samples,
    )
    role_classification = classify_fixture_roles(
        audit_fixture_role_signals_v2(case, decoded)
    )

    return build_measured_piece_rows(
        fixture_id=case["id"],
        square_samples=samples,
        color_rows=color_classification.rows,
        role_rows=role_classification.rows,
    )


def _load_valid_manifest() -> dict:
    manifest = _load_manifest()
    validation = validate_approved_fixture_manifest(
        manifest,
        approved_dir=APPROVED_DIR,
        require_existing_images=True,
    )

    assert validation.valid is True
    assert validation.issues == ()

    return manifest


def _load_manifest() -> dict:
    return deepcopy(json.loads(APPROVED_MANIFEST_PATH.read_text(encoding="utf-8")))


def _role_signal_cases(manifest: dict) -> tuple[dict, ...]:
    return tuple(
        case
        for case in manifest["cases"]
        if case["expected_metrics"].get("role_signal_fixture")
    )


def _expected_placement(case: dict) -> str:
    return case["expected_fen"].split()[0]


def _decode_case_image(case: dict) -> DecodedImage:
    image_path = APPROVED_DIR / case["filename"]
    result = decode_image_bytes(
        image_path.read_bytes(),
        IMAGE_CONTENT_TYPES[image_path.suffix.lower()],
    )

    assert isinstance(result, DecodedImage)

    return result


def _sample_case(case: dict, decoded: DecodedImage) -> tuple[SquareSample, ...]:
    bounds = case["board_bounds"]

    return sample_fixture_squares(
        fixture_id=case["id"],
        image=decoded,
        board_bounds=BoardBounds(
            x=bounds["x"],
            y=bounds["y"],
            width=bounds["width"],
            height=bounds["height"],
        ),
        orientation=case["orientation"],
    )


def _rows(*overrides: MeasuredPieceRow) -> tuple[MeasuredPieceRow, ...]:
    overrides_by_square = {row.square: row for row in overrides}

    return tuple(
        overrides_by_square.get(square, _empty_row(square))
        for square in _all_squares()
    )


def _piece_row(
    square: str,
    color: str | None,
    role: str | None,
) -> MeasuredPieceRow:
    return MeasuredPieceRow(
        fixture_id="fixture",
        square=square,
        occupancy_state="occupied",
        detected_color=color,
        detected_role=role,
        row_category="measured_piece",
        confidence_metadata=ConfidenceMetadata(square=0.9, color=0.8, role=0.95),
        failure_reason=None,
        source_stages=("square_sampling", "color_classifier", "role_classifier"),
    )


def _empty_row(square: str) -> MeasuredPieceRow:
    return MeasuredPieceRow(
        fixture_id="fixture",
        square=square,
        occupancy_state="empty",
        detected_color=None,
        detected_role=None,
        row_category="empty_square",
        confidence_metadata=ConfidenceMetadata(square=0.9, color=None, role=None),
        failure_reason=None,
        source_stages=("square_sampling",),
    )


def _unsupported_row(square: str, failure_reason: str) -> MeasuredPieceRow:
    return MeasuredPieceRow(
        fixture_id="fixture",
        square=square,
        occupancy_state="occupied",
        detected_color=None,
        detected_role=None,
        row_category="unsupported",
        confidence_metadata=ConfidenceMetadata(square=0.9, color=None, role=None),
        failure_reason=failure_reason,
        source_stages=("square_sampling", "color_classifier", "role_classifier"),
    )


def _assert_failure(result: object, code: str) -> None:
    assert isinstance(result, FenPlacementFailure)
    assert result.code == code
    assert result.failure_reasons == (code,)


def _double_transformed_rows(
    rows: tuple[MeasuredPieceRow, ...],
) -> tuple[MeasuredPieceRow, ...]:
    return tuple(replace(row, square=_flipped_square(row.square)) for row in rows)


def _flipped_square(square: str) -> str:
    file_index = "abcdefgh".index(square[0])
    rank_index = "12345678".index(square[1])
    return f"{'abcdefgh'[7 - file_index]}{'12345678'[7 - rank_index]}"


def _all_squares() -> tuple[str, ...]:
    return tuple(f"{file}{rank}" for file in "abcdefgh" for rank in "12345678")
