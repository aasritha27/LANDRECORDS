from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.db import get_db
from app.models.models import LandRecord
from app.schemas.schemas import LandRecordResponse

router = APIRouter(prefix="/records", tags=["Land Records"])

@router.get("/", response_model=List[LandRecordResponse])
async def search_land_records(
    village: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    khasra_number: Optional[str] = Query(None),
    owner_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(LandRecord)
    if village:
        query = query.where(LandRecord.village.ilike(f"%{village}%"))
    if district:
        query = query.where(LandRecord.district.ilike(f"%{district}%"))
    if khasra_number:
        query = query.where(LandRecord.khasra_number.ilike(f"%{khasra_number}%"))
    if owner_name:
        query = query.where(LandRecord.owner_name.ilike(f"%{owner_name}%"))

    res = await db.execute(query)
    records = res.scalars().all()
    return records
