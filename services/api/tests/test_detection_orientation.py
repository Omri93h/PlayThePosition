from app.detection.orientation import detect_orientation
from app.detection.pieces import RecognizedPiece, SquareRecognition

WHITE_PAWN = RecognizedPiece(color="white", role="pawn", code="P")
BLACK_PAWN = RecognizedPiece(color="black", role="pawn", code="p")
WHITE_KING = RecognizedPiece(color="white", role="king", code="K")
BLACK_QUEEN = RecognizedPiece(color="black", role="queen", code="q")


def test_detects_white_bottom_from_synthetic_piece_layout() -> None:
    result = detect_orientation(
        (
            SquareRecognition(row=6, column=0, piece=WHITE_PAWN),
            SquareRecognition(row=7, column=4, piece=WHITE_KING),
            SquareRecognition(row=1, column=3, piece=BLACK_QUEEN),
        )
    )

    assert result.orientation == "white-bottom"
    assert result.confidence is not None
    assert "White pieces" in result.reason


def test_detects_black_bottom_from_synthetic_piece_layout() -> None:
    result = detect_orientation(
        (
            SquareRecognition(row=6, column=3, piece=BLACK_QUEEN),
            SquareRecognition(row=7, column=7, piece=BLACK_PAWN),
            SquareRecognition(row=1, column=4, piece=WHITE_KING),
        )
    )

    assert result.orientation == "black-bottom"
    assert result.confidence is not None
    assert "Black pieces" in result.reason


def test_ambiguous_piece_layout_returns_unknown() -> None:
    result = detect_orientation(
        (
            SquareRecognition(row=6, column=0, piece=WHITE_PAWN),
            SquareRecognition(row=6, column=7, piece=BLACK_PAWN),
        )
    )

    assert result.orientation == "unknown"
    assert "ambiguous" in result.reason


def test_empty_piece_layout_returns_unknown_cleanly() -> None:
    result = detect_orientation(())

    assert result.orientation == "unknown"
    assert "No recognized squares" in result.reason


def test_invalid_square_coordinates_return_unknown_cleanly() -> None:
    result = detect_orientation(
        (SquareRecognition(row=8, column=0, piece=WHITE_PAWN),)
    )

    assert result.orientation == "unknown"
    assert "outside the board" in result.reason
