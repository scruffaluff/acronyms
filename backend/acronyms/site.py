"""Website main module."""


from typing import Dict, List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import decorator, FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from acronyms import models
from acronyms.schemas import AcronymBody
from acronyms.models import Acronym, AcronymColumn
from acronyms.settings import Settings


settings = Settings()
app = FastAPI(redoc_url=None)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


@app.delete("/api/acronym/{id}")
async def delete_acronym(
    id: int = Path(description="Identifier of acronym to remove", ge=0),
    session: Session = Depends(models.get_db),
) -> Dict[str, bool]:
    """Insert an acronym to database."""
    session.query(Acronym).filter(Acronym.id == id).delete()
    session.commit()
    return {"ok": True}


@app.get("/api/acronym")
@decorator.cache(expire=60)
async def get_acronym(
    response: Response,
    id: Optional[int] = None,
    # TODO: Allow searching by partial match.
    abbreviation: Optional[str] = None,
    phrase: Optional[str] = None,
    limit: int = Query(
        default=settings.page_size,
        description="Maximum number of acronyms to return",
        gt=0,
        le=50,
    ),
    offset: int = Query(default=0, ge=0),
    order: Optional[AcronymColumn] = None,
    session: Session = Depends(models.get_db),
) -> Union[Acronym, List[Acronym], None]:
    """Get all matching acronyms."""
    query = session.query(Acronym)
    if id is not None:
        return query.get(id)

    if abbreviation is None and phrase is None:
        query_ = query
    elif abbreviation is None:
        query_ = query.filter(Acronym.phrase.contains(phrase))
    elif phrase is None:
        query_ = query.filter(Acronym.abbreviation.contains(abbreviation))
    else:
        query_ = query.filter(
            sqlalchemy.or_(
                Acronym.abbreviation.contains(abbreviation),
                Acronym.phrase.contains(phrase),
            )
        )

    response.headers["X-Total-Count"] = str(query_.count())
    return query_.order_by(order).offset(offset).limit(limit).all()


@app.post("/api/acronym")
async def post_acronym(
    acronym: AcronymBody, session: Session = Depends(models.get_db)
) -> int:
    """Insert an acronym to database."""
    acronym_ = Acronym(abbreviation=acronym.abbreviation, phrase=acronym.phrase)

    try:
        session.add(acronym_)
        session.commit()
    except IntegrityError as exception:
        raise HTTPException(status_code=400, detail=str(exception))
    return acronym_.id


@app.put("/api/acronym/{id}")
async def put_acronym(
    id: int,
    body: AcronymBody,
    session: Session = Depends(models.get_db),
) -> Dict[str, bool]:
    """Get all matching acronyms."""
    acronym = session.query(Acronym).filter(Acronym.id == id)

    try:
        acronym.update(body.dict())
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate acronym request")
    return {"ok": True}


@app.get("/")
def read_index() -> FileResponse:
    """Fetch frontend Vue entrypoint as site root."""
    return FileResponse("dist/index.html")


@app.get("/favicon.ico")
def read_favicon() -> FileResponse:
    """Fetch site favicon."""
    return FileResponse("dist/favicon.ico")


@app.on_event("startup")
async def startup() -> None:
    """Initialize configuration for web application."""
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
