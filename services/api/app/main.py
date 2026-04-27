from fastapi import FastAPI

app = FastAPI(title="Play The Position API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
