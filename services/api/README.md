# services/api

Backend API for Play The Position.

Stack:

- Python
- FastAPI
- Pytest
- Ruff

Current scope:

- FastAPI foundation with `GET /health` only.
- No upload endpoint, image processing, detection, database, auth, share links, or frontend integration yet.

Commands:

- `python -m pytest`
- `python -m ruff check .`
- `python -m uvicorn app.main:app --reload`
