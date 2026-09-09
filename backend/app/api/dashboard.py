from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db import get_db
from app.models.models import Document

router = APIRouter(prefix="/dashboard", tags=["Dashboard Analytics"])

@router.get("/stats")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    # Total count
    t_res = await db.execute(select(func.count(Document.id)))
    total_docs = t_res.scalar() or 0

    # Auto validated count
    av_res = await db.execute(select(func.count(Document.id)).where(Document.status.in_(["auto_validated", "verified"])))
    auto_validated = av_res.scalar() or 0

    # Needs review count
    nr_res = await db.execute(select(func.count(Document.id)).where(Document.status == "needs_review"))
    needs_review = nr_res.scalar() or 0

    # Average confidence
    conf_res = await db.execute(select(func.avg(Document.overall_confidence)))
    avg_conf = conf_res.scalar() or 0.0

    return {
        "total_documents": total_docs,
        "auto_validated": auto_validated,
        "needs_review": needs_review,
        "avg_confidence": round(float(avg_conf), 2),
        "pass_rate_percentage": round((auto_validated / total_docs * 100), 1) if total_docs > 0 else 0.0
    }
