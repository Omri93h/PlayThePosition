from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.detection import PLACEHOLDER_FEN
from app.logging import get_logger, log_event

app = FastAPI(title="Play The Position API")
logger = get_logger("api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

ALLOWED_UPLOAD_TYPES = {"image/jpeg", "image/png"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SHARED_POSITIONS: dict[str, "SharedPosition"] = {}


class SharePositionRequest(BaseModel):
    fen: str = Field(min_length=1)


class SharedPosition(BaseModel):
    id: str
    fen: str
    source: str = "share"


class SharePositionResponse(BaseModel):
    id: str
    path: str
    fen: str
    source: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=None)
async def upload_position(
    file: Annotated[UploadFile, File()],
) -> dict[str, object] | JSONResponse:
    file_bytes = await file.read()
    validation_error = validate_upload(file, file_bytes)

    if validation_error is not None:
        return validation_error

    log_event(
        logger,
        "upload.succeeded",
        content_type=file.content_type or "application/octet-stream",
        file_size=len(file_bytes),
        source="placeholder",
        fen_length=len(PLACEHOLDER_FEN),
    )

    return {
        "fen": PLACEHOLDER_FEN,
        "source": "placeholder",
        "confidence": None,
        "message": (
            f"Received {file.filename or 'uploaded file'}; detection is not "
            "implemented yet."
        ),
    }


@app.post("/share", response_model=SharePositionResponse)
def create_share(payload: SharePositionRequest) -> SharePositionResponse:
    share_id = uuid4().hex
    position = SharedPosition(id=share_id, fen=payload.fen)
    SHARED_POSITIONS[share_id] = position

    log_event(
        logger,
        "share.created",
        share_id=share_id,
        fen_length=len(payload.fen),
        source=position.source,
    )

    return SharePositionResponse(
        id=share_id,
        path=f"/share/{share_id}",
        fen=position.fen,
        source=position.source,
    )


@app.get("/share/{share_id}", response_model=None)
def get_share(share_id: str) -> SharedPosition | JSONResponse:
    position = SHARED_POSITIONS.get(share_id)

    if position is None:
        log_event(logger, "share.not_found", share_id=share_id)
        return share_error(
            404,
            "share_not_found",
            "Shared position was not found.",
        )

    log_event(
        logger,
        "share.loaded",
        share_id=share_id,
        fen_length=len(position.fen),
        source=position.source,
    )

    return position


def validate_upload(file: UploadFile, file_bytes: bytes) -> JSONResponse | None:
    content_type = file.content_type or "application/octet-stream"

    if content_type not in ALLOWED_UPLOAD_TYPES:
        log_upload_validation_failure(
            code="unsupported_file_type",
            content_type=content_type,
            file_size=len(file_bytes),
        )
        return upload_error(
            415,
            "unsupported_file_type",
            "Only PNG and JPEG images are supported.",
        )

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        log_upload_validation_failure(
            code="file_too_large",
            content_type=content_type,
            file_size=len(file_bytes),
        )
        return upload_error(
            413,
            "file_too_large",
            "Uploaded image exceeds the maximum size limit.",
        )

    if not has_valid_image_signature(content_type, file_bytes):
        log_upload_validation_failure(
            code="invalid_image_payload",
            content_type=content_type,
            file_size=len(file_bytes),
        )
        return upload_error(
            400,
            "invalid_image_payload",
            "Uploaded file does not appear to be a valid image.",
        )

    return None


def has_valid_image_signature(content_type: str, file_bytes: bytes) -> bool:
    if content_type == "image/png":
        return file_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    if content_type == "image/jpeg":
        return file_bytes.startswith(b"\xff\xd8\xff")

    return False


def log_upload_validation_failure(
    *,
    code: str,
    content_type: str,
    file_size: int,
) -> None:
    log_event(
        logger,
        "upload.validation_failed",
        code=code,
        content_type=content_type,
        file_size=file_size,
    )


def upload_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )


def share_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
    )
