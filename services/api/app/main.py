from typing import Annotated

from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="Play The Position API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
def upload_position(file: Annotated[UploadFile, File()]) -> dict[str, object]:
    return {
        "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
        "source": "placeholder",
        "confidence": None,
        "message": (
            f"Received {file.filename or 'uploaded file'}; detection is not "
            "implemented yet."
        ),
    }
