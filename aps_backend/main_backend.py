"""Compatibility entry point for Docker and uvicorn.

The application now lives in `app.main`. This module keeps the historical
`uvicorn main_backend:app` command working while new code imports from `app`.
"""

import uvicorn

from app.main import app

__all__ = ["app"]


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
