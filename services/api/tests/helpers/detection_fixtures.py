import json
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "detection"
MANIFEST_PATH = FIXTURE_DIR / "cases.json"


def load_detection_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_detection_cases() -> list[dict[str, Any]]:
    manifest = load_detection_manifest()
    return list(manifest["cases"])


def generate_synthetic_ppm_board(case: dict[str, Any]) -> bytes:
    synthetic = case["synthetic"]
    square_size = int(synthetic["square_size"])
    light_rgb = tuple(int(value) for value in synthetic["light_rgb"])
    dark_rgb = tuple(int(value) for value in synthetic["dark_rgb"])
    side = square_size * 8
    header = f"P6\n{side} {side}\n255\n".encode()
    pixels = bytearray()

    for y in range(side):
        for x in range(side):
            square_x = x // square_size
            square_y = y // square_size
            color = light_rgb if (square_x + square_y) % 2 == 0 else dark_rgb
            pixels.extend(color)

    return header + bytes(pixels)
