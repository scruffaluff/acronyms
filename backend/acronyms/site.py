"""Command line interface for acronyms.

See https://docs.python.org/3/using/cmdline.html#cmdoption-m for why module is
named __main__.py.
"""


from typing import Dict, List, Optional, Union

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from acronyms import models
from acronyms.models import Acronym, AcronymColumn


app = FastAPI(redoc_url=None)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


class AcronymBody(BaseModel):
    """Post request validator for Acronym type."""

    abbreviation: str
    description: Optional[str]
    phrase: str


@app.get("/")
def read_index() -> FileResponse:
    """Fetch frontend Vue entrypoint as site root."""
    return FileResponse("dist/index.html")


@app.get("/favicon.ico")
def read_favicon() -> FileResponse:
    """Fetch site favicon."""
    return FileResponse("dist/favicon.ico")


@app.delete("/api/{id}")
async def delete_acronym(
    id: int, session: Session = Depends(models.get_db)
) -> Dict[str, bool]:
    """Insert an acronym to database."""
    session.query(Acronym).filter(Acronym.id == id).delete()
    session.commit()
    return {"ok": True}


@app.get("/api")
async def get_acronym(
    id: Optional[int] = None,
    abbreviation: Optional[str] = None,
    phrase: Optional[str] = None,
    limit: int = Query(default=10, gt=0, le=50),
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
        query_ = query.filter(Acronym.phrase == phrase)
    elif phrase is None:
        query_ = query.filter(Acronym.abbreviation == abbreviation)
    else:
        query_ = query.filter(
            Acronym.abbreviation == abbreviation, Acronym.phrase == phrase
        )

    return query_.order_by(order).offset(offset).limit(limit).all()


@app.post("/api")
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


@app.put("/api/{id}")
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
