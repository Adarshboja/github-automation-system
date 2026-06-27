"""FastAPI application for architectural integration."""

from __future__ import annotations

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create FastAPI app exposing operational health."""

    app = FastAPI(title="GitHub Activity Automation System")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

