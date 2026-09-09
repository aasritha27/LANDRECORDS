from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db import get_db
from app.models.models import Document, ExtractedField, LandRecord, AuditLog
from app.schemas.schemas import DocumentVerifyRequest, DocumentResponse, ExtractedFieldResponse, LandRecordResponse

router = APIRouter(prefix="/review", tags=["Review & Verification"])

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

@router.post("/{document_id}/verify", response_model=DocumentResponse)
async def verify_and_approve_document(
    document_id: int,
    payload: DocumentVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).options(
        selectinload(Document.extracted_fields),
        selectinload(Document.land_record)
    ).where(Document.id == document_id)
    res = await db.execute(query)
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Apply field updates
    field_map = {}
    for update_item in payload.updates:
        f_query = select(ExtractedField).where(
            ExtractedField.id == update_item.field_id,
            ExtractedField.document_id == document_id
        )
        f_res = await db.execute(f_query)
        field_obj = f_res.scalar_one_or_none()

        if field_obj:
            old_val = field_obj.field_value
            new_val = update_item.corrected_value

            field_obj.corrected_value = new_val
            field_obj.is_verified = True
            field_obj.validation_notes = update_item.validation_notes

            field_map[field_obj.field_name] = new_val

            if old_val != new_val:
                audit = AuditLog(
                    document_id=document_id,
                    action="field_edit",
                    field_name=field_obj.field_name,
                    old_value=old_val,
                    new_value=new_val
                )
                db.add(audit)

    # Update Document Status
    doc.status = "verified" if payload.approve else "needs_review"
    
    # Update Canonical Land Record
    lr_query = select(LandRecord).where(LandRecord.document_id == document_id)
    lr_res = await db.execute(lr_query)
    land_rec = lr_res.scalar_one_or_none()

    if land_rec:
        if "khasra_number" in field_map: land_rec.khasra_number = field_map["khasra_number"]
        if "khata_number" in field_map: land_rec.khata_number = field_map["khata_number"]
        if "owner_name" in field_map: land_rec.owner_name = field_map["owner_name"]
        if "village" in field_map: land_rec.village = field_map["village"]
        if "tehsil" in field_map: land_rec.tehsil = field_map["tehsil"]
        if "district" in field_map: land_rec.district = field_map["district"]
        if "land_area" in field_map: land_rec.land_area = field_map["land_area"]
        land_rec.status = "canonical_verified" if payload.approve else "draft"

    audit_final = AuditLog(
        document_id=document_id,
        action="verify_approve" if payload.approve else "update_fields",
        new_value=f"Status changed to {doc.status}"
    )
    db.add(audit_final)

    await db.commit()

    # Re-fetch eager loaded doc
    refreshed_res = await db.execute(query)
    refreshed_doc = refreshed_res.scalar_one()
    return build_document_response(refreshed_doc)
