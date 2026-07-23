"""FastAPI application entry point for beam prediction service."""

try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None

if FastAPI:
    app = FastAPI(title="LaserSim Beam AI API")

    @app.get("/health")
    def health():
        return {"status": "ok"}
else:
    app = None
