from app.detection.pieces import (
    PieceRecognitionFailure,
    PieceRecognitionSuccess,
    SquareSample,
    recognize_pieces,
)


def test_recognizes_empty_square_from_synthetic_marker() -> None:
    result = recognize_pieces((SquareSample(row=0, column=0, marker="empty"),))

    assert isinstance(result, PieceRecognitionSuccess)
    assert len(result.squares) == 1
    assert result.squares[0].row == 0
    assert result.squares[0].column == 0
    assert result.squares[0].piece is None


def test_recognizes_controlled_synthetic_piece_markers() -> None:
    result = recognize_pieces(
        (
            SquareSample(row=0, column=4, marker="white_king"),
            SquareSample(row=7, column=3, marker="black_queen"),
            SquareSample(row=6, column=0, marker="white_pawn"),
            SquareSample(row=1, column=7, marker="black_pawn"),
        )
    )

    assert isinstance(result, PieceRecognitionSuccess)
    recognized_codes = [
        square.piece.code if square.piece else None for square in result.squares
    ]

    assert recognized_codes == ["K", "q", "P", "p"]
    assert [(square.row, square.column) for square in result.squares] == [
        (0, 4),
        (7, 3),
        (6, 0),
        (1, 7),
    ]


def test_unknown_synthetic_marker_returns_structured_failure() -> None:
    result = recognize_pieces((SquareSample(row=3, column=3, marker="white_rook"),))

    assert isinstance(result, PieceRecognitionFailure)
    assert result.code == "unknown_piece_marker"
    assert result.row == 3
    assert result.column == 3


def test_invalid_square_coordinates_return_structured_failure() -> None:
    result = recognize_pieces((SquareSample(row=8, column=0, marker="empty"),))

    assert isinstance(result, PieceRecognitionFailure)
    assert result.code == "invalid_square"
    assert result.row == 8
    assert result.column == 0
