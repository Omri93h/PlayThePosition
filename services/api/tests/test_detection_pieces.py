from app.detection.pieces import (
    PieceRecognitionFailure,
    PieceRecognitionSuccess,
    SquareSample,
    format_recognized_pieces,
    recognize_pieces,
    square_name,
)


def test_recognizes_empty_square_from_synthetic_marker() -> None:
    result = recognize_pieces((SquareSample(row=0, column=0, marker="empty"),))

    assert isinstance(result, PieceRecognitionSuccess)
    assert len(result.squares) == 1
    assert result.squares[0].row == 0
    assert result.squares[0].column == 0
    assert result.squares[0].square == "a8"
    assert result.squares[0].piece is None
    assert result.squares[0].confidence == 1.0
    assert result.squares[0].source_stage == "piece_recognition"


def test_recognizes_controlled_synthetic_piece_markers() -> None:
    result = recognize_pieces(
        (
            SquareSample(row=0, column=4, marker="white_king"),
            SquareSample(row=0, column=3, marker="white_queen"),
            SquareSample(row=0, column=0, marker="white_rook"),
            SquareSample(row=0, column=2, marker="white_bishop"),
            SquareSample(row=0, column=1, marker="white_knight"),
            SquareSample(row=6, column=0, marker="white_pawn"),
            SquareSample(row=7, column=4, marker="black_king"),
            SquareSample(row=7, column=3, marker="black_queen"),
            SquareSample(row=7, column=0, marker="black_rook"),
            SquareSample(row=7, column=2, marker="black_bishop"),
            SquareSample(row=7, column=1, marker="black_knight"),
            SquareSample(row=1, column=7, marker="black_pawn"),
        )
    )

    assert isinstance(result, PieceRecognitionSuccess)
    recognized_codes = [
        square.piece.code if square.piece else None for square in result.squares
    ]

    assert recognized_codes == [
        "K",
        "Q",
        "R",
        "B",
        "N",
        "P",
        "k",
        "q",
        "r",
        "b",
        "n",
        "p",
    ]
    assert [(square.row, square.column) for square in result.squares] == [
        (0, 4),
        (0, 3),
        (0, 0),
        (0, 2),
        (0, 1),
        (6, 0),
        (7, 4),
        (7, 3),
        (7, 0),
        (7, 2),
        (7, 1),
        (1, 7),
    ]


def test_maps_row_and_column_to_algebraic_square() -> None:
    assert square_name(row=0, column=0) == "a8"
    assert square_name(row=4, column=7) == "h4"
    assert square_name(row=5, column=3) == "d3"
    assert square_name(row=7, column=7) == "h1"


def test_invalid_square_name_coordinates_raise_value_error() -> None:
    try:
        square_name(row=8, column=0)
    except ValueError as error:
        assert str(error) == "Square coordinates must be within an 8x8 board."
    else:
        raise AssertionError("Expected invalid square coordinates to raise.")


def test_formats_human_readable_debug_piece_list() -> None:
    result = recognize_pieces(
        (
            SquareSample(row=4, column=7, marker="black_rook"),
            SquareSample(row=5, column=3, marker="white_king"),
            SquareSample(row=0, column=0, marker="empty"),
        )
    )

    assert isinstance(result, PieceRecognitionSuccess)
    assert format_recognized_pieces(result.squares) == [
        "black rook at h4",
        "white king at d3",
    ]


def test_unknown_synthetic_marker_returns_structured_failure() -> None:
    result = recognize_pieces((SquareSample(row=3, column=3, marker="white_archer"),))

    assert isinstance(result, PieceRecognitionFailure)
    assert result.code == "unknown_piece_marker"
    assert result.row == 3
    assert result.column == 3
    assert result.square == "d5"
    assert result.failure_reason == "unknown_piece_marker"
    assert result.source_stage == "piece_recognition"


def test_invalid_square_coordinates_return_structured_failure() -> None:
    result = recognize_pieces((SquareSample(row=8, column=0, marker="empty"),))

    assert isinstance(result, PieceRecognitionFailure)
    assert result.code == "invalid_square"
    assert result.row == 8
    assert result.column == 0
    assert result.square is None
    assert result.failure_reason == "invalid_square"
