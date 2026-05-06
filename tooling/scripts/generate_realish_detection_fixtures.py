"""Generate owned real-ish detection fixtures for backend tests.

This script is fixture tooling only. It renders simple owned chessboard images
with deterministic board colors and glyph-like piece markers. It does not use
or copy Chess.com, Lichess, or other third-party screenshot assets.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8
REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_FIXTURE_DIR = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "detection" / "approved"
)

PIECE_NAMES = {
    "k": "king",
    "q": "queen",
    "r": "rook",
    "b": "bishop",
    "n": "knight",
    "p": "pawn",
}


@dataclass(frozen=True)
class FixtureSpec:
    filename: str
    fen: str
    orientation: str
    style: str


@dataclass(frozen=True)
class StyleSpec:
    light: tuple[int, int, int]
    dark: tuple[int, int, int]
    border: tuple[int, int, int]
    white_piece_fill: tuple[int, int, int]
    white_piece_stroke: tuple[int, int, int]
    black_piece_fill: tuple[int, int, int]
    black_piece_stroke: tuple[int, int, int]


STYLES = {
    "web-default": StyleSpec(
        light=(231, 238, 219),
        dark=(78, 124, 92),
        border=(32, 43, 38),
        white_piece_fill=(250, 249, 241),
        white_piece_stroke=(48, 57, 52),
        black_piece_fill=(30, 34, 33),
        black_piece_stroke=(220, 224, 214),
    ),
    "chesscom-like": StyleSpec(
        light=(235, 232, 208),
        dark=(105, 145, 82),
        border=(38, 52, 33),
        white_piece_fill=(250, 248, 237),
        white_piece_stroke=(53, 60, 47),
        black_piece_fill=(31, 35, 29),
        black_piece_stroke=(219, 226, 209),
    ),
    "lichess-like": StyleSpec(
        light=(221, 212, 195),
        dark=(136, 111, 88),
        border=(52, 43, 36),
        white_piece_fill=(247, 246, 238),
        white_piece_stroke=(55, 48, 43),
        black_piece_fill=(28, 26, 24),
        black_piece_stroke=(223, 215, 201),
    ),
}

FIXTURES = (
    FixtureSpec(
        filename="owned_web_white-bottom_start-01.png",
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1",
        orientation="white-bottom",
        style="web-default",
    ),
    FixtureSpec(
        filename="owned_web_black-bottom_start-01.png",
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1",
        orientation="black-bottom",
        style="web-default",
    ),
    FixtureSpec(
        filename="owned_chesscom-like_white-bottom_kings-rook-01.png",
        fen="4k3/8/8/8/7r/3K4/8/8 w - - 0 1",
        orientation="white-bottom",
        style="chesscom-like",
    ),
    FixtureSpec(
        filename="owned_lichess-like_white-bottom_middlegame-01.png",
        fen="r2q1rk1/pp2bppp/2n1bn2/2pp4/3P4/2PBPN2/PP1BPPP1/R2Q1RK1 w - - 0 1",
        orientation="white-bottom",
        style="lichess-like",
    ),
)


def main() -> None:
    APPROVED_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    for fixture in FIXTURES:
        image = render_fixture(fixture)
        image.save(APPROVED_FIXTURE_DIR / fixture.filename, format="PNG")


def render_fixture(fixture: FixtureSpec) -> Image.Image:
    style = STYLES[fixture.style]
    image = Image.new("RGB", (BOARD_SIZE, BOARD_SIZE), style.border)
    draw = ImageDraw.Draw(image)
    pieces = parse_fen_pieces(fixture.fen)

    for visual_row in range(8):
        for visual_col in range(8):
            x = visual_col * SQUARE_SIZE
            y = visual_row * SQUARE_SIZE
            fill = style.light if (visual_row + visual_col) % 2 == 0 else style.dark
            draw.rectangle(
                (x, y, x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1),
                fill=fill,
            )

            square = square_for_visual_cell(
                visual_row,
                visual_col,
                fixture.orientation,
            )
            piece = pieces.get(square)
            if piece:
                draw_piece_marker(draw, x, y, piece, style)

    return image


def parse_fen_pieces(fen: str) -> dict[str, str]:
    placement = fen.split()[0]
    pieces: dict[str, str] = {}

    for rank_index, rank_text in enumerate(placement.split("/")):
        rank = 8 - rank_index
        file_index = 0

        for char in rank_text:
            if char.isdigit():
                file_index += int(char)
                continue

            file_name = chr(ord("a") + file_index)
            pieces[f"{file_name}{rank}"] = char
            file_index += 1

    return pieces


def square_for_visual_cell(row: int, column: int, orientation: str) -> str:
    if orientation == "white-bottom":
        file_name = chr(ord("a") + column)
        rank = 8 - row
        return f"{file_name}{rank}"

    if orientation == "black-bottom":
        file_name = chr(ord("h") - column)
        rank = row + 1
        return f"{file_name}{rank}"

    raise ValueError(f"Unsupported orientation: {orientation}")


def draw_piece_marker(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    piece: str,
    style: StyleSpec,
) -> None:
    is_white = piece.isupper()
    fill = style.white_piece_fill if is_white else style.black_piece_fill
    stroke = style.white_piece_stroke if is_white else style.black_piece_stroke
    label = piece.upper()

    inset = 10
    center_x = x + SQUARE_SIZE // 2
    center_y = y + SQUARE_SIZE // 2
    circle_box = (
        x + inset,
        y + inset,
        x + SQUARE_SIZE - inset,
        y + SQUARE_SIZE - inset,
    )

    draw.ellipse(circle_box, fill=fill, outline=stroke, width=3)
    draw_symbol(draw, center_x, center_y, label, stroke)


def draw_symbol(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    label: str,
    fill: tuple[int, int, int],
) -> None:
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        (center_x - text_width // 2, center_y - text_height // 2),
        label,
        fill=fill,
        font=font,
    )

    role = PIECE_NAMES[label.lower()]
    if role == "king":
        draw.line((center_x, center_y - 18, center_x, center_y + 18), fill=fill, width=3)
        draw.line(
            (center_x - 12, center_y - 7, center_x + 12, center_y - 7),
            fill=fill,
            width=3,
        )
    elif role == "queen":
        draw.polygon(
            (
                (center_x - 16, center_y + 12),
                (center_x - 8, center_y - 15),
                (center_x, center_y + 8),
                (center_x + 8, center_y - 15),
                (center_x + 16, center_y + 12),
            ),
            outline=fill,
        )
    elif role == "rook":
        draw.rectangle(
            (center_x - 15, center_y - 13, center_x + 15, center_y + 15),
            outline=fill,
            width=3,
        )
    elif role == "bishop":
        draw.ellipse(
            (center_x - 14, center_y - 17, center_x + 14, center_y + 17),
            outline=fill,
            width=3,
        )
    elif role == "knight":
        draw.line(
            (
                center_x - 12,
                center_y + 15,
                center_x + 10,
                center_y + 5,
                center_x - 2,
                center_y - 15,
            ),
            fill=fill,
            width=4,
        )
    elif role == "pawn":
        draw.ellipse(
            (center_x - 10, center_y - 15, center_x + 10, center_y + 5),
            outline=fill,
            width=3,
        )
        draw.line(
            (center_x - 13, center_y + 14, center_x + 13, center_y + 14),
            fill=fill,
            width=3,
        )


if __name__ == "__main__":
    main()
