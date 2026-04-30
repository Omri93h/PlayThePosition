from app.detection.fen import FenGenerationFailure, FenGenerationSuccess
from app.detection.grid import BoardGrid, GridDetectionFailure, GridDetectionSuccess
from app.detection.pieces import PieceRecognitionFailure, PieceRecognitionSuccess
from app.detection.results import DetectionFailure, DetectionMetadata


def test_standard_failure_includes_retry_guidance() -> None:
    failure = DetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
        stage="grid",
        retryable=True,
        suggestion="Use a clear, uncropped chessboard image.",
    )

    assert failure.code == "board_grid_not_found"
    assert failure.message == "An 8x8 chessboard grid could not be found."
    assert failure.stage == "grid"
    assert failure.retryable is True
    assert failure.suggestion == "Use a clear, uncropped chessboard image."


def test_success_metadata_supports_confidence_source_and_stage() -> None:
    metadata = DetectionMetadata(
        confidence=0.75,
        source="synthetic_ppm_grid",
        stage="grid",
    )

    assert metadata.confidence == 0.75
    assert metadata.source == "synthetic_ppm_grid"
    assert metadata.stage == "grid"


def test_grid_failure_maps_to_stable_failure_metadata() -> None:
    failure = GridDetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
    )

    assert failure.code == "board_grid_not_found"
    assert failure.stage == "grid"
    assert failure.retryable is True
    assert failure.suggestion


def test_piece_failure_maps_to_stable_failure_metadata() -> None:
    failure = PieceRecognitionFailure(
        code="unknown_piece_marker",
        message="Synthetic piece marker could not be classified.",
    )

    assert failure.code == "unknown_piece_marker"
    assert failure.stage == "pieces"
    assert failure.retryable is True
    assert failure.suggestion


def test_fen_failure_maps_to_stable_failure_metadata() -> None:
    failure = FenGenerationFailure(
        code="duplicate_square",
        message="Recognized square data contains duplicate coordinates.",
    )

    assert failure.code == "duplicate_square"
    assert failure.stage == "fen"
    assert failure.retryable is False
    assert failure.suggestion


def test_detection_successes_include_metadata() -> None:
    grid_success = GridDetectionSuccess(grid=BoardGrid(rows=8, columns=8, squares=()))
    piece_success = PieceRecognitionSuccess(squares=())
    fen_success = FenGenerationSuccess(fen="8/8/8/8/8/8/8/8 w - - 0 1")

    assert grid_success.metadata.stage == "grid"
    assert piece_success.metadata.stage == "pieces"
    assert fen_success.metadata.stage == "fen"
