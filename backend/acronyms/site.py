"""Command line interface for acronyms.

See https://docs.python.org/3/using/cmdline.html#cmdoption-m for why module is
named __main__.py.
"""


from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from acronyms import models
from acronyms.models import Acronym


app = FastAPI()
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


class AcronymBody(BaseModel):
    """Post request validator for Acronym type."""

    abbreviation: str
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
    abbreviation: Optional[str] = None,
    phrase: Optional[str] = None,
    id: Optional[int] = None,
    session: Session = Depends(models.get_db),
) -> Optional[Any]:
    """Get all matching acronyms."""
    query = session.query(Acronym)

    if id is not None:
        return query.get(id)
    if abbreviation is not None:
        query = query.filter(Acronym.abbreviation == abbreviation)

    return query.all()


@app.post("/api")
async def post_acronym(
    acronym: AcronymBody, session: Session = Depends(models.get_db)
) -> int:
    """Insert an acronym to database."""
    acronym_ = Acronym(abbreviation=acronym.abbreviation, phrase=acronym.phrase)
    session.add(acronym_)
    session.commit()
    return acronym_.id


@app.put("/api/{id}")
async def put_acronym(
    id: int,
    body: AcronymBody,
    session: Session = Depends(models.get_db),
) -> Dict[str, bool]:
    """Get all matching acronyms."""
    acronym = session.query(Acronym).filter(Acronym.id == id)
    acronym.update(body.dict())

    session.commit()
    return {"ok": True}
