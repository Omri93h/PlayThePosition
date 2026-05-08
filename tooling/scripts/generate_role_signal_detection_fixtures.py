"""Generate owned role-signal detection fixtures for backend tests.

This script is fixture tooling only. It renders deterministic chessboard images
with owned geometric role markers. It does not use or copy Chess.com, Lichess,
other third-party piece assets, screenshots, fonts, or user uploads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[2]
    for site_packages in (repo_root / "services" / "api" / ".venv").glob(
        "lib/python*/site-packages"
    ):
        sys.path.insert(0, str(site_packages))
    from PIL import Image, ImageDraw


BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8
REPO_ROOT = Path(__file__).resolve().parents[2]
APPROVED_FIXTURE_DIR = (
    REPO_ROOT / "services" / "api" / "tests" / "fixtures" / "detection" / "approved"
)

ROLE_CODES = {
    "king": "k",
    "queen": "q",
    "rook": "r",
    "bishop": "b",
    "knight": "n",
    "pawn": "p",
}


@dataclass(frozen=True)
class FixtureSpec:
    filename: str
    fen: str
    orientation: str
    pieces: dict[str, tuple[str, str]]
    purpose: str


@dataclass(frozen=True)
class StyleSpec:
    light: tuple[int, int, int]
    dark: tuple[int, int, int]
    white_fill: tuple[int, int, int]
    white_outline: tuple[int, int, int]
    black_fill: tuple[int, int, int]
    black_outline: tuple[int, int, int]


ROLE_SIGNAL_STYLE = StyleSpec(
    light=(232, 238, 220),
    dark=(75, 123, 93),
    white_fill=(248, 247, 235),
    white_outline=(42, 52, 47),
    black_fill=(27, 32, 30),
    black_outline=(222, 226, 214),
)

DENSE_PIECES = {
    "a2": ("rook", "white"),
    "b5": ("knight", "white"),
    "c3": ("king", "white"),
    "e4": ("queen", "white"),
    "f5": ("pawn", "white"),
    "g2": ("bishop", "white"),
    "b7": ("bishop", "black"),
    "c6": ("pawn", "black"),
    "d5": ("queen", "black"),
    "f6": ("king", "black"),
    "g4": ("knight", "black"),
    "h7": ("rook", "black"),
}

SHIFTED_PIECES = {
    "a7": ("knight", "white"),
    "b6": ("queen", "white"),
    "d4": ("rook", "white"),
    "e5": ("pawn", "white"),
    "f1": ("bishop", "white"),
    "h2": ("king", "white"),
    "a3": ("king", "black"),
    "b4": ("pawn", "black"),
    "c8": ("rook", "black"),
    "e2": ("knight", "black"),
    "g6": ("queen", "black"),
    "h5": ("bishop", "black"),
}

FIXTURES = (
    FixtureSpec(
        filename="owned_role-signal_white-bottom_dense-01.png",
        fen="8/1b5r/2p2k2/1N1q1P2/4Q1n1/2K5/R5B1/8 w - - 0 1",
        orientation="white-bottom",
        pieces=DENSE_PIECES,
        purpose="Baseline dense role-signal fixture covering all six roles and both colors.",
    ),
    FixtureSpec(
        filename="owned_role-signal_black-bottom_dense-01.png",
        fen="8/1b5r/2p2k2/1N1q1P2/4Q1n1/2K5/R5B1/8 w - - 0 1",
        orientation="black-bottom",
        pieces=DENSE_PIECES,
        purpose="Dense role-signal fixture with black-bottom orientation.",
    ),
    FixtureSpec(
        filename="owned_role-signal_white-bottom_shifted-01.png",
        fen="2r5/N7/1Q4q1/4P2b/1p1R4/k7/4n2K/5B2 w - - 0 1",
        orientation="white-bottom",
        pieces=SHIFTED_PIECES,
        purpose="Shifted role-signal fixture moving roles across different squares.",
    ),
)


def main() -> None:
    APPROVED_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    for fixture in FIXTURES:
        image = render_fixture(fixture)
        image.save(APPROVED_FIXTURE_DIR / fixture.filename, format="PNG")


def render_fixture(fixture: FixtureSpec) -> Image.Image:
    image = Image.new("RGB", (BOARD_SIZE, BOARD_SIZE), ROLE_SIGNAL_STYLE.light)
    draw = ImageDraw.Draw(image)

    for visual_row in range(8):
        for visual_col in range(8):
            x = visual_col * SQUARE_SIZE
            y = visual_row * SQUARE_SIZE
            fill = (
                ROLE_SIGNAL_STYLE.light
                if (visual_row + visual_col) % 2 == 0
                else ROLE_SIGNAL_STYLE.dark
            )
            draw.rectangle(
                (x, y, x + SQUARE_SIZE - 1, y + SQUARE_SIZE - 1),
                fill=fill,
            )

            square = square_for_visual_cell(
                visual_row,
                visual_col,
                fixture.orientation,
            )
            piece = fixture.pieces.get(square)
            if piece is not None:
                draw_role_marker(draw, x, y, role=piece[0], color=piece[1])

    return image


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


def draw_role_marker(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    *,
    role: str,
    color: str,
) -> None:
    fill = (
        ROLE_SIGNAL_STYLE.white_fill
        if color == "white"
        else ROLE_SIGNAL_STYLE.black_fill
    )
    outline = (
        ROLE_SIGNAL_STYLE.white_outline
        if color == "white"
        else ROLE_SIGNAL_STYLE.black_outline
    )
    cx = x + SQUARE_SIZE // 2
    cy = y + SQUARE_SIZE // 2

    if role == "king":
        draw.rounded_rectangle((cx - 8, cy - 24, cx + 8, cy + 24), radius=4, fill=fill)
        draw.rounded_rectangle((cx - 24, cy - 8, cx + 24, cy + 8), radius=4, fill=fill)
        draw.line((cx, cy - 27, cx, cy + 27), fill=outline, width=3)
        draw.line((cx - 27, cy, cx + 27, cy), fill=outline, width=3)
        draw.rectangle((cx - 4, cy - 28, cx + 4, cy - 20), fill=outline)
    elif role == "queen":
        points = (
            (cx - 26, cy + 18),
            (cx - 17, cy - 18),
            (cx - 7, cy + 2),
            (cx, cy - 24),
            (cx + 7, cy + 2),
            (cx + 17, cy - 18),
            (cx + 26, cy + 18),
        )
        draw.polygon(points, fill=fill)
        draw.line((*points, points[0]), fill=outline, width=4)
        draw.rectangle((cx - 22, cy + 14, cx + 22, cy + 23), fill=fill)
        draw.rectangle((cx - 22, cy + 14, cx + 22, cy + 23), outline=outline, width=3)
    elif role == "rook":
        draw.rectangle((cx - 23, cy - 20, cx + 23, cy + 22), fill=fill)
        draw.rectangle((cx - 23, cy - 20, cx + 23, cy + 22), outline=outline, width=4)
        for offset in (-16, 0, 16):
            draw.rectangle((cx + offset - 5, cy - 27, cx + offset + 5, cy - 16), fill=fill)
            draw.rectangle(
                (cx + offset - 5, cy - 27, cx + offset + 5, cy - 16),
                outline=outline,
                width=2,
            )
        draw.rectangle((cx - 14, cy - 8, cx + 14, cy + 8), fill=outline)
    elif role == "bishop":
        draw.ellipse((cx - 16, cy - 28, cx + 16, cy + 26), fill=fill)
        draw.ellipse((cx - 16, cy - 28, cx + 16, cy + 26), outline=outline, width=4)
        draw.polygon(
            ((cx, cy - 30), (cx - 18, cy - 4), (cx + 18, cy - 4)),
            fill=fill,
        )
        draw.line(
            ((cx, cy - 30), (cx - 18, cy - 4), (cx + 18, cy - 4), (cx, cy - 30)),
            fill=outline,
            width=3,
        )
        draw.line((cx - 7, cy - 16, cx + 10, cy + 10), fill=outline, width=4)
    elif role == "knight":
        points = (
            (cx - 22, cy + 24),
            (cx - 10, cy - 24),
            (cx + 17, cy - 18),
            (cx + 8, cy - 2),
            (cx + 21, cy + 5),
            (cx + 3, cy + 24),
        )
        draw.polygon(points, fill=fill)
        draw.line((*points, points[0]), fill=outline, width=4)
        draw.rectangle((cx - 5, cy - 13, cx + 3, cy - 5), fill=outline)
    elif role == "pawn":
        draw.ellipse((cx - 14, cy - 26, cx + 14, cy + 2), fill=fill)
        draw.ellipse((cx - 14, cy - 26, cx + 14, cy + 2), outline=outline, width=4)
        draw.rounded_rectangle((cx - 18, cy - 1, cx + 18, cy + 27), radius=8, fill=fill)
        draw.rounded_rectangle(
            (cx - 18, cy - 1, cx + 18, cy + 27),
            radius=8,
            outline=outline,
            width=4,
        )
        draw.rectangle((cx - 24, cy + 20, cx + 24, cy + 28), fill=fill)
        draw.rectangle((cx - 24, cy + 20, cx + 24, cy + 28), outline=outline, width=3)
    else:
        raise ValueError(f"Unsupported role: {role}")


if __name__ == "__main__":
    main()
