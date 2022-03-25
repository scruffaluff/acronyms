"""Command line interface for acronyms.

See https://docs.python.org/3/using/cmdline.html#cmdoption-m for why module is
named __main__.py.
"""


import logging
from typing import Any, Dict, Optional

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


@app.get("/")
async def root() -> Dict[str, Any]:
    """Greet user."""
    logging.debug("root path accessed")
    return {"message": "Hello World"}


@app.get("/acronyms")
async def get_acronym(
    abbreviation: Optional[str] = None,
    session: Session = Depends(models.get_db),
) -> Optional[Any]:
    """Get all matching acronyms."""
    query = session.query(Acronym.abbreviation, Acronym.expansion)

    if abbreviation is not None:
        query = query.filter(Acronym.abbreviation == abbreviation)

    return query.all()


@app.post("/acronyms")
async def post_acronym(
    acronym: AcronymBody, session: Session = Depends(models.get_db)
) -> None:
    """Insert an acronym to database."""
    acronym_ = Acronym(
        abbreviation=acronym.abbreviation, expansion=acronym.expansion
    )
    session.add(acronym_)
    session.commit()
