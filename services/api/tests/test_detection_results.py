from app.detection.fen import FenGenerationFailure, FenGenerationSuccess
from app.detection.grid import (
    BoardBounds,
    BoardBoundsDetectionSuccess,
    BoardGrid,
    GridDetectionFailure,
    GridDetectionSuccess,
)
from app.detection.pieces import (
    PieceRecognitionFailure,
    PieceRecognitionSuccess,
    RecognizedPiece,
    SquareRecognition,
)
from app.detection.results import (
    DETECTION_STATUSES,
    DetectionFailure,
    DetectionMetadata,
    detection_failure_payload,
    detection_metadata_payload,
)


def test_detection_status_values_are_stable() -> None:
    assert DETECTION_STATUSES == ("placeholder", "success", "partial", "failed")


def test_standard_failure_includes_retry_guidance() -> None:
    failure = DetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
        stage="grid",
        retryable=True,
        suggestion="Use a clear, uncropped chessboard image.",
        failure_reason="board_grid_not_found",
    )

    assert failure.code == "board_grid_not_found"
    assert failure.message == "An 8x8 chessboard grid could not be found."
    assert failure.stage == "grid"
    assert failure.retryable is True
    assert failure.suggestion == "Use a clear, uncropped chessboard image."
    assert failure.failure_reason == "board_grid_not_found"


def test_standard_failure_payload_is_serializable_and_normalized() -> None:
    failure = DetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
        stage="grid",
        retryable=True,
        suggestion="Use a clear, uncropped chessboard image.",
        failure_reason="board_grid_not_found",
    )

    assert detection_failure_payload(failure) == {
        "code": "board_grid_not_found",
        "message": "An 8x8 chessboard grid could not be found.",
        "stage": "grid",
        "retryable": True,
        "suggestion": "Use a clear, uncropped chessboard image.",
        "failure_reason": "board_grid_not_found",
    }


def test_success_metadata_supports_confidence_source_and_stage() -> None:
    metadata = DetectionMetadata(
        confidence=0.75,
        source="synthetic_ppm_grid",
        stage="grid",
        status="partial",
    )

    assert metadata.confidence == 0.75
    assert metadata.source == "synthetic_ppm_grid"
    assert metadata.stage == "grid"
    assert metadata.status == "partial"


def test_success_metadata_payload_is_serializable_and_normalized() -> None:
    metadata = DetectionMetadata(
        confidence=0.75,
        source="synthetic_ppm_grid",
        stage="grid",
        status="partial",
    )

    assert detection_metadata_payload(metadata) == {
        "status": "partial",
        "confidence": 0.75,
        "source": "synthetic_ppm_grid",
        "stage": "grid",
    }


def test_grid_failure_maps_to_stable_failure_metadata() -> None:
    failure = GridDetectionFailure(
        code="board_grid_not_found",
        message="An 8x8 chessboard grid could not be found.",
    )

    assert failure.code == "board_grid_not_found"
    assert failure.stage == "grid"
    assert failure.retryable is True
    assert failure.suggestion
    assert failure.failure_reason is None


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
    assert grid_success.metadata.status == "success"
    assert piece_success.metadata.stage == "pieces"
    assert piece_success.metadata.status == "success"
    assert fen_success.metadata.stage == "fen"
    assert fen_success.metadata.status == "success"


def test_grid_bounds_output_exposes_debug_metadata() -> None:
    success = BoardBoundsDetectionSuccess(
        bounds=BoardBounds(x=4, y=8, width=64, height=64),
        confidence=0.7,
    )

    assert success.bounds == BoardBounds(x=4, y=8, width=64, height=64)
    assert success.confidence == 0.7
    assert success.source == "synthetic_ppm_board_bounds"
    assert detection_metadata_payload(success.metadata) == {
        "status": "success",
        "confidence": 0.7,
        "source": "synthetic_ppm_board_bounds",
        "stage": "grid",
    }


def test_piece_output_exposes_debug_metadata() -> None:
    piece = RecognizedPiece(color="black", role="rook", code="r")
    square = SquareRecognition(
        row=4,
        column=7,
        square="h4",
        piece=piece,
    )
    success = PieceRecognitionSuccess(squares=(square,))

    assert success.metadata.confidence == 1.0
    assert success.metadata.status == "success"
    assert success.squares[0].confidence == 1.0
    assert success.squares[0].source_stage == "piece_recognition"
    assert success.squares[0].failure_reason is None
