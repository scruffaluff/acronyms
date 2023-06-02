"""Website main module."""


from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from acronyms import auth, models
from acronyms.routes import acronyms


package = Path(__file__).parent
app = FastAPI(redoc_url=None)
app.mount(
    "/assets", StaticFiles(directory=package / "web/assets"), name="assets"
)
app.include_router(acronyms.router, prefix="/api")
auth.include_routes(app)


@app.get("/")
def read_index() -> FileResponse:
    """Fetch frontend Vue entrypoint as site root."""
    return FileResponse(package / "web/index.html")


@app.get("/favicon.ico")
def read_favicon() -> FileResponse:
    """Fetch site favicon."""
    return FileResponse(package / "web/favicon.ico")


@app.on_event("startup")
async def startup() -> None:
    """Initialize configuration for web application."""
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    await models.initialize_database()
