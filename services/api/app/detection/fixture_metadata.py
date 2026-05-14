from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from app.detection.image import (
    MAX_IMAGE_BYTES,
    MAX_IMAGE_HEIGHT,
    MAX_IMAGE_WIDTH,
    DecodedImage,
    decode_image_bytes,
)

ORIENTATIONS = {"white-bottom", "black-bottom", "unknown"}
SIDE_TO_MOVE_VALUES = {"w", "b"}
SUCCESS_KINDS = {"approved_manual_fixture", "hand_created", "synthetic"}
BASE_REQUIRED_CASE_FIELDS = {
    "board_bounds",
    "expected_fen",
    "expected_pieces",
    "id",
    "filename",
    "kind",
    "source",
    "style",
    "orientation",
    "license",
}
PIECE_ROLES = {"king", "queen", "rook", "bishop", "knight", "pawn"}
PIECE_COLORS = {"white", "black"}
FEN_PIECES = {
    "K": ("king", "white"),
    "Q": ("queen", "white"),
    "R": ("rook", "white"),
    "B": ("bishop", "white"),
    "N": ("knight", "white"),
    "P": ("pawn", "white"),
    "k": ("king", "black"),
    "q": ("queen", "black"),
    "r": ("rook", "black"),
    "b": ("bishop", "black"),
    "n": ("knight", "black"),
    "p": ("pawn", "black"),
}
FILES = "abcdefgh"
RANKS = "12345678"
FORBIDDEN_PATH_PARTS = {"raw", "large", "dump", "dumps", "archive", "archives"}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".rar"}
IMAGE_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


@dataclass(frozen=True)
class FixtureMetadataIssue:
    code: str
    message: str
    case_id: str | None = None


@dataclass(frozen=True)
class FixtureMetadataValidation:
    valid: bool
    issues: tuple[FixtureMetadataIssue, ...]


def validate_approved_fixture_manifest(
    manifest: dict[str, Any],
    *,
    approved_dir: Path,
    require_existing_images: bool = False,
    max_bytes: int = MAX_IMAGE_BYTES,
    max_width: int = MAX_IMAGE_WIDTH,
    max_height: int = MAX_IMAGE_HEIGHT,
) -> FixtureMetadataValidation:
    issues: list[FixtureMetadataIssue] = []

    if "version" not in manifest:
        issues.append(_issue("missing_required_field", "Manifest requires version."))
    elif not isinstance(manifest["version"], int):
        issues.append(_issue("invalid_field", "Manifest version must be an integer."))

    if "cases" not in manifest:
        issues.append(_issue("missing_required_field", "Manifest requires cases."))
        return _validation(issues)

    if not isinstance(manifest["cases"], list):
        issues.append(_issue("invalid_field", "Manifest cases must be a list."))
        return _validation(issues)

    approved_root = approved_dir.resolve()

    for case in manifest["cases"]:
        if not isinstance(case, dict):
            issues.append(
                _issue("invalid_case", "Each fixture case must be an object.")
            )
            continue

        issues.extend(
            _validate_case(
                case,
                approved_root=approved_root,
                require_existing_images=require_existing_images,
                max_bytes=max_bytes,
                max_width=max_width,
                max_height=max_height,
            )
        )

    return _validation(issues)


def _validate_case(
    case: dict[str, Any],
    *,
    approved_root: Path,
    require_existing_images: bool,
    max_bytes: int,
    max_width: int,
    max_height: int,
) -> list[FixtureMetadataIssue]:
    issues: list[FixtureMetadataIssue] = []
    case_id = case.get("id") if isinstance(case.get("id"), str) else None

    for field in sorted(BASE_REQUIRED_CASE_FIELDS):
        if field not in case:
            issues.append(
                _issue(
                    "missing_required_field",
                    f"Fixture case requires {field}.",
                    case_id,
                )
            )

    if issues:
        return issues

    for field in ("id", "filename", "kind", "source", "style", "orientation"):
        if not isinstance(case[field], str) or not case[field].strip():
            issues.append(
                _issue("invalid_field", f"Fixture {field} must be a string.", case_id)
            )

    orientation = case.get("orientation")
    if isinstance(orientation, str) and orientation not in ORIENTATIONS:
        issues.append(
            _issue(
                "invalid_orientation",
                "Fixture orientation must be white-bottom, black-bottom, or unknown.",
                case_id,
            )
        )

    kind = case.get("kind")
    if kind in SUCCESS_KINDS:
        issues.extend(_validate_side_to_move(case, case_id))

        expected_fen = case.get("expected_fen")
        if not isinstance(expected_fen, str) or not expected_fen.strip():
            issues.append(
                _issue(
                    "missing_expected_fen",
                    "Approved success fixtures require expected_fen.",
                    case_id,
                )
            )
        elif len(expected_fen.split()) != 6:
            issues.append(
                _issue(
                    "invalid_expected_fen",
                    "expected_fen must use the basic six-field FEN shape.",
                    case_id,
                )
            )
        else:
            issues.extend(_validate_expected_pieces(case, expected_fen, case_id))

    issues.extend(_validate_license(case, case_id))

    filename = case.get("filename")
    if isinstance(filename, str):
        image_path = _validated_image_path(filename, approved_root, case_id)
        if isinstance(image_path, FixtureMetadataIssue):
            issues.append(image_path)
        else:
            issues.extend(
                _validate_optional_image_file(
                    image_path,
                    case_id=case_id,
                    require_existing_images=require_existing_images,
                    max_bytes=max_bytes,
                    max_width=max_width,
                    max_height=max_height,
                )
            )

    return issues


def _validate_side_to_move(
    case: dict[str, Any],
    case_id: str | None,
) -> list[FixtureMetadataIssue]:
    side_to_move = case.get("side_to_move")

    if side_to_move is None:
        return [
            _issue(
                "missing_side_to_move",
                "Approved success fixtures require explicit side_to_move metadata.",
                case_id,
            )
        ]

    if side_to_move not in SIDE_TO_MOVE_VALUES:
        return [
            _issue(
                "invalid_side_to_move",
                "Fixture side_to_move must be w or b.",
                case_id,
            )
        ]

    return []


def _validate_expected_pieces(
    case: dict[str, Any],
    expected_fen: str,
    case_id: str | None,
) -> list[FixtureMetadataIssue]:
    issues: list[FixtureMetadataIssue] = []
    expected_pieces = case.get("expected_pieces")

    if not isinstance(expected_pieces, list):
        return [
            _issue(
                "invalid_expected_pieces",
                "expected_pieces must be a list.",
                case_id,
            )
        ]

    fen_placement = _parse_fen_piece_placement(expected_fen, case_id)
    if isinstance(fen_placement, FixtureMetadataIssue):
        return [fen_placement]

    metadata_pieces: dict[str, tuple[str, str]] = {}
    seen_squares: set[str] = set()

    for piece in expected_pieces:
        if not isinstance(piece, dict):
            issues.append(
                _issue(
                    "invalid_expected_piece",
                    "Each expected piece must be an object.",
                    case_id,
                )
            )
            continue

        square = piece.get("square")
        role = piece.get("piece")
        color = piece.get("color")

        if not isinstance(square, str) or not _is_valid_square(square):
            issues.append(
                _issue(
                    "invalid_expected_piece_square",
                    "Expected piece square must be a valid algebraic square.",
                    case_id,
                )
            )
            continue

        if square in seen_squares:
            issues.append(
                _issue(
                    "duplicate_expected_piece_square",
                    "Expected pieces must not contain duplicate squares.",
                    case_id,
                )
            )
            continue

        seen_squares.add(square)

        if role not in PIECE_ROLES:
            issues.append(
                _issue(
                    "invalid_expected_piece_role",
                    "Expected piece role must be king, queen, rook, bishop, "
                    "knight, or pawn.",
                    case_id,
                )
            )

        if color not in PIECE_COLORS:
            issues.append(
                _issue(
                    "invalid_expected_piece_color",
                    "Expected piece color must be white or black.",
                    case_id,
                )
            )

        if role in PIECE_ROLES and color in PIECE_COLORS:
            metadata_pieces[square] = (role, color)

    if issues:
        return issues

    if metadata_pieces != fen_placement:
        return [
            _issue(
                "expected_pieces_fen_mismatch",
                "expected_pieces must match occupied squares and piece "
                "colors/roles in expected_fen.",
                case_id,
            )
        ]

    return []


def _parse_fen_piece_placement(
    expected_fen: str,
    case_id: str | None,
) -> dict[str, tuple[str, str]] | FixtureMetadataIssue:
    placement = expected_fen.split()[0]
    ranks = placement.split("/")

    if len(ranks) != 8:
        return _issue(
            "invalid_expected_fen",
            "expected_fen piece placement must contain 8 ranks.",
            case_id,
        )

    pieces: dict[str, tuple[str, str]] = {}

    for rank_index, rank_text in enumerate(ranks):
        file_index = 0
        board_rank = 8 - rank_index

        for char in rank_text:
            if char.isdigit():
                empty_count = int(char)
                if empty_count < 1 or empty_count > 8:
                    return _issue(
                        "invalid_expected_fen",
                        "expected_fen empty-square counts must be 1 through 8.",
                        case_id,
                    )
                file_index += empty_count
                continue

            piece = FEN_PIECES.get(char)
            if piece is None:
                return _issue(
                    "invalid_expected_fen",
                    "expected_fen contains an unsupported piece code.",
                    case_id,
                )

            if file_index >= 8:
                return _issue(
                    "invalid_expected_fen",
                    "expected_fen rank contains more than 8 squares.",
                    case_id,
                )

            square = f"{FILES[file_index]}{board_rank}"
            pieces[square] = piece
            file_index += 1

        if file_index != 8:
            return _issue(
                "invalid_expected_fen",
                "expected_fen ranks must each contain exactly 8 squares.",
                case_id,
            )

    return pieces


def _is_valid_square(square: str) -> bool:
    return len(square) == 2 and square[0] in FILES and square[1] in RANKS


def _validate_license(
    case: dict[str, Any],
    case_id: str | None,
) -> list[FixtureMetadataIssue]:
    license_data = case.get("license")

    if not isinstance(license_data, dict):
        return [
            _issue(
                "missing_license",
                "Fixture license must include status and note.",
                case_id,
            )
        ]

    issues: list[FixtureMetadataIssue] = []
    for field in ("status", "note"):
        value = license_data.get(field)
        if not isinstance(value, str) or not value.strip():
            issues.append(
                _issue(
                    "missing_license",
                    f"Fixture license requires non-empty {field}.",
                    case_id,
                )
            )

    return issues


def _validated_image_path(
    filename: str,
    approved_root: Path,
    case_id: str | None,
) -> Path | FixtureMetadataIssue:
    if not filename.strip():
        return _issue("invalid_path", "Fixture filename must not be empty.", case_id)

    if "\\" in filename or ":" in filename:
        return _issue(
            "invalid_path",
            "Fixture filename must be a relative path.",
            case_id,
        )

    path = PurePosixPath(filename)

    if path.is_absolute():
        return _issue("invalid_path", "Fixture filename must not be absolute.", case_id)

    if ".." in path.parts:
        return _issue(
            "invalid_path",
            "Fixture filename must not contain parent traversal.",
            case_id,
        )

    lower_parts = {part.lower() for part in path.parts}
    if lower_parts & FORBIDDEN_PATH_PARTS:
        return _issue(
            "forbidden_path",
            "Fixture filename must not use raw, large, dump, or archive paths.",
            case_id,
        )

    full_suffix = "".join(path.suffixes).lower()
    if full_suffix in ARCHIVE_SUFFIXES or path.suffix.lower() in ARCHIVE_SUFFIXES:
        return _issue(
            "forbidden_path",
            "Fixture filename must not be an archive.",
            case_id,
        )

    resolved = (approved_root / Path(*path.parts)).resolve()

    if not _is_under_directory(resolved, approved_root):
        return _issue(
            "invalid_path",
            "Fixture filename must resolve under the approved fixture directory.",
            case_id,
        )

    return resolved


def _validate_optional_image_file(
    image_path: Path,
    *,
    case_id: str | None,
    require_existing_images: bool,
    max_bytes: int,
    max_width: int,
    max_height: int,
) -> list[FixtureMetadataIssue]:
    if not image_path.exists():
        if require_existing_images:
            return [
                _issue(
                    "missing_image_file",
                    "Fixture image file does not exist.",
                    case_id,
                )
            ]
        return []

    if not image_path.is_file():
        return [_issue("invalid_path", "Fixture image path must be a file.", case_id)]

    content_type = IMAGE_CONTENT_TYPES.get(image_path.suffix.lower())
    if content_type is None:
        return [
            _issue(
                "unsupported_image_format",
                "Fixture image must be a PNG or JPEG file.",
                case_id,
            )
        ]

    image_bytes = image_path.read_bytes()
    result = decode_image_bytes(
        image_bytes,
        content_type,
        max_bytes=max_bytes,
        max_width=max_width,
        max_height=max_height,
    )

    if isinstance(result, DecodedImage):
        return []

    return [
        _issue(
            result.code,
            result.message,
            case_id,
        )
    ]


def _is_under_directory(path: Path, directory: Path) -> bool:
    return path == directory or directory in path.parents


def _validation(
    issues: list[FixtureMetadataIssue],
) -> FixtureMetadataValidation:
    return FixtureMetadataValidation(valid=not issues, issues=tuple(issues))


def _issue(
    code: str,
    message: str,
    case_id: str | None = None,
) -> FixtureMetadataIssue:
    return FixtureMetadataIssue(code=code, message=message, case_id=case_id)
