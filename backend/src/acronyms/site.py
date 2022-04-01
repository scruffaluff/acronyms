"""Command line interface for acronyms.

See https://docs.python.org/3/using/cmdline.html#cmdoption-m for why module is
named __main__.py.
"""


from typing import Any, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from acronyms import models
from acronyms.models import Acronym


app = FastAPI()


class AcronymBody(BaseModel):
    """Post request validator for Acronym type."""

    abbreviation: str
    expansion: str


@app.delete("/api")
async def delete_acronym(
    id: int, session: Session = Depends(models.get_db)
) -> None:
    """Insert an acronym to database."""
    session.query(Acronym).filter(Acronym.id == id).delete()
    session.commit()


@app.get("/api")
async def get_acronym(
    abbreviation: Optional[str] = None,
    session: Session = Depends(models.get_db),
) -> Optional[Any]:
    """Get all matching acronyms."""
    query = session.query(Acronym.id, Acronym.abbreviation, Acronym.expansion)

    if abbreviation is not None:
        query = query.filter(Acronym.abbreviation == abbreviation)

    return query.all()


@app.post("/api")
async def post_acronym(
    acronym: AcronymBody, session: Session = Depends(models.get_db)
) -> int:
    """Insert an acronym to database."""
    acronym_ = Acronym(
        abbreviation=acronym.abbreviation, expansion=acronym.expansion
    )
    session.add(acronym_)
    return acronym_.id
