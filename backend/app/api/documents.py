from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.db import get_db
from app.models.models import Document
from app.schemas.schemas import DocumentResponse, ExtractedFieldResponse, LandRecordResponse

router = APIRouter(prefix="/documents", tags=["Documents"])

def build_document_response(doc: Document) -> DocumentResponse:
    fields_resp = [ExtractedFieldResponse.model_validate(f) for f in doc.extracted_fields] if doc.extracted_fields else []
    record_resp = LandRecordResponse.model_validate(doc.land_record) if doc.land_record else None
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        original_filepath=doc.original_filepath,
        preprocessed_filepath=doc.preprocessed_filepath,
        status=doc.status,
        overall_confidence=doc.overall_confidence,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        extracted_fields=fields_resp,
        land_record=record_resp
    )

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    status: Optional[str] = Query(None, description="Filter by status: uploaded, preprocessed, auto_validated, needs_review, verified"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).options(
        selectinload(Document.extracted_fields),
        selectinload(Document.land_record)
    )
    if status:
        query = query.where(Document.status == status)
    
    query = query.order_by(Document.id.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    documents = result.scalars().all()
    return [build_document_response(d) for d in documents]

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).options(
        selectinload(Document.extracted_fields),
        selectinload(Document.land_record)
    ).where(Document.id == document_id)
    result = await db.execute(query)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return build_document_response(doc)
