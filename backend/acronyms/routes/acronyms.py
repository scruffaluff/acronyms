"""Acronyms REST API endpoints."""


from typing import cast, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from fastapi_cache import decorator, FastAPICache
import sqlalchemy
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from acronyms import models, settings
from acronyms.models import Acronym, AcronymColumn
from acronyms.schemas import AcronymBody


router = APIRouter()


@router.delete("/acronym/{id}")
async def delete_acronym(
    id: int = Path(description="Identifier of acronym to remove", ge=0),
    session: AsyncSession = Depends(models.get_session),
) -> Dict[str, bool]:
    """Insert an acronym to database."""
    statement = sqlalchemy.select(Acronym).where(Acronym.id == id)
    try:
        acronym = (await session.execute(statement)).scalar_one()
    except NoResultFound as exception:
        raise HTTPException(status_code=400, detail=str(exception))

    await session.delete(acronym)
    await session.commit()
    await FastAPICache.clear(namespace="acronyms")
    return {"ok": True}


@router.get("/acronym")
@decorator.cache(expire=60, namespace="acronyms")
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
    session: AsyncSession = Depends(models.get_session),
) -> Union[Acronym, List[Acronym], None]:
    """Get all matching acronyms."""
    if id is not None:
        return await session.get(Acronym, id)

    table = sqlalchemy.select(Acronym)
    if abbreviation is None and phrase is None:
        query = table
    elif abbreviation is None:
        query = table.where(Acronym.phrase.contains(phrase))
    elif phrase is None:
        query = table.where(Acronym.abbreviation.contains(abbreviation))
    else:
        query = table.where(
            sqlalchemy.or_(
                Acronym.abbreviation.contains(abbreviation),
                Acronym.phrase.contains(phrase),
            )
        )

    count = await session.execute(
        query.with_only_columns(sqlalchemy.func.count(Acronym.id))
    )
    response.headers["X-Total-Count"] = str(count.scalar_one())
    result = await session.execute(
        query.order_by(order).offset(offset).limit(limit)
    )
    return result.scalars().all()


@router.post("/acronym")
async def post_acronym(
    acronym: AcronymBody, session: AsyncSession = Depends(models.get_session)
) -> int:
    """Insert an acronym to database."""
    acronym_ = Acronym(abbreviation=acronym.abbreviation, phrase=acronym.phrase)

    try:
        session.add(acronym_)
        await session.commit()
        await FastAPICache.clear(namespace="acronyms")

        # Id is not None since session committed the acronym.
        return cast(int, acronym_.id)
    except IntegrityError as exception:
        raise HTTPException(status_code=400, detail=str(exception))


@router.put("/acronym/{id}")
async def put_acronym(
    id: int,
    body: AcronymBody,
    session: AsyncSession = Depends(models.get_session),
) -> Dict[str, bool]:
    """Get all matching acronyms."""
    try:
        statement = (
            sqlalchemy.update(Acronym)
            .where(Acronym.id == id)
            .values(**body.dict())
        )
        await session.execute(statement)

        await session.commit()
        await FastAPICache.clear(namespace="acronyms")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Duplicate acronym request")
    return {"ok": True}
