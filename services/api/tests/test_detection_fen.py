from app.detection.fen import FenGenerationFailure, FenGenerationSuccess, generate_fen
from app.detection.pieces import RecognizedPiece, SquareRecognition

WHITE_KING = RecognizedPiece(color="white", role="king", code="K")
BLACK_QUEEN = RecognizedPiece(color="black", role="queen", code="q")
WHITE_PAWN = RecognizedPiece(color="white", role="pawn", code="P")
BLACK_PAWN = RecognizedPiece(color="black", role="pawn", code="p")


def test_generates_fen_from_structured_white_bottom_board() -> None:
    result = generate_fen(
        (
            SquareRecognition(row=0, column=4, piece=BLACK_QUEEN),
            SquareRecognition(row=6, column=0, piece=WHITE_PAWN),
            SquareRecognition(row=7, column=4, piece=WHITE_KING),
        ),
        orientation="white-bottom",
    )

    assert isinstance(result, FenGenerationSuccess)
    assert result.fen == "4q3/8/8/8/8/8/P7/4K3 w - - 0 1"


def test_generates_fen_from_structured_black_bottom_board() -> None:
    result = generate_fen(
        (
            SquareRecognition(row=0, column=4, piece=WHITE_KING),
            SquareRecognition(row=1, column=7, piece=WHITE_PAWN),
            SquareRecognition(row=7, column=4, piece=BLACK_QUEEN),
        ),
        orientation="black-bottom",
    )

    assert isinstance(result, FenGenerationSuccess)
    assert result.fen == "3q4/8/8/8/8/8/P7/3K4 w - - 0 1"


def test_compresses_consecutive_empty_squares() -> None:
    result = generate_fen(
        (
            SquareRecognition(row=3, column=2, piece=WHITE_PAWN),
            SquareRecognition(row=3, column=5, piece=BLACK_PAWN),
        ),
        orientation="white-bottom",
    )

    assert isinstance(result, FenGenerationSuccess)
    assert result.fen == "8/8/8/2P2p2/8/8/8/8 w - - 0 1"


def test_duplicate_square_data_returns_structured_failure() -> None:
    result = generate_fen(
        (
            SquareRecognition(row=0, column=0, piece=WHITE_KING),
            SquareRecognition(row=0, column=0, piece=BLACK_QUEEN),
        ),
        orientation="white-bottom",
    )

    assert isinstance(result, FenGenerationFailure)
    assert result.code == "duplicate_square"
    assert result.row == 0
    assert result.column == 0


def test_out_of_board_square_returns_structured_failure() -> None:
    result = generate_fen(
        (SquareRecognition(row=8, column=0, piece=WHITE_KING),),
        orientation="white-bottom",
    )

    assert isinstance(result, FenGenerationFailure)
    assert result.code == "invalid_square"
    assert result.row == 8
    assert result.column == 0


def test_unknown_orientation_returns_structured_failure() -> None:
    result = generate_fen((), orientation="unknown")

    assert isinstance(result, FenGenerationFailure)
    assert result.code == "unsupported_orientation"
