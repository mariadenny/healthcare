from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="FastAPI backend for optimizing healthcare clinic appointment scheduling and patient flow.",
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning a welcoming project message."""
    return {
        "message": f"Welcome to the {settings.app_name}",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint to verify service availability."""
    return {"status": "ok"}
