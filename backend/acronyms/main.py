"""Website main module."""


from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from acronyms.routes import acronyms


app = FastAPI(redoc_url=None)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
app.include_router(acronyms.router, prefix="/api")


@app.get("/")
def read_index() -> FileResponse:
    """Fetch frontend Vue entrypoint as site root."""
    return FileResponse("dist/index.html")


@app.get("/favicon.ico")
def read_favicon() -> FileResponse:
    """Fetch site favicon."""
    return FileResponse("dist/favicon.ico")


@app.on_event("startup")
def startup() -> None:
    """Initialize configuration for web application."""
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
