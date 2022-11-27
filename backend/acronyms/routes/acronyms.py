"""Acronyms REST API endpoints."""


from typing import Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from acronyms import models, settings
from acronyms.models import Acronym, AcronymColumn
from acronyms.schemas import AcronymBody


router = APIRouter()


@router.delete("/acronym/{id}")
async def delete_acronym(
    id: int = Path(description="Identifier of acronym to remove", ge=0),
    session: Session = Depends(models.get_db),
) -> Dict[str, bool]:
    """Insert an acronym to database."""
    session.query(Acronym).filter(Acronym.id == id).delete()
    session.commit()
    return {"ok": True}


@router.get("/acronym")
async def get_acronym(
    response: Response,
    id: Optional[int] = None,
    abbreviation: Optional[str] = None,
    phrase: Optional[str] = None,
    limit: int = Query(
        default=settings.settings().page_size,
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


@router.post("/acronym")
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


@router.put("/acronym/{id}")
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
