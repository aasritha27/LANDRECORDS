from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import os
import shutil
import uuid
from app.db import get_db
from app.models.models import Document, ExtractedField, LandRecord, AuditLog
from app.schemas.schemas import DocumentResponse, ExtractedFieldResponse, LandRecordResponse
from app.config import settings
from app.pipeline.confidence_engine import process_document_pipeline

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf", ".tiff", ".bmp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}"
        )

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Execute AI Digitization Pipeline
    preprocessed_path, extracted_fields, overall_conf, pipeline_status = process_document_pipeline(filepath)

    doc = Document(
        filename=file.filename,
        original_filepath=filepath,
        preprocessed_filepath=preprocessed_path,
        status=pipeline_status,
        overall_confidence=overall_conf
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Save Extracted Fields
    saved_field_objs = []
    field_dict = {}
    for ef in extracted_fields:
        field_row = ExtractedField(
            document_id=doc.id,
            field_name=ef["field_name"],
            field_value=ef["field_value"],
            confidence_score=ef["confidence_score"],
            bounding_box=ef["bounding_box"]
        )
        db.add(field_row)
        saved_field_objs.append(field_row)
        field_dict[ef["field_name"]] = ef["field_value"]

    # Create Initial LandRecord draft
    land_rec = LandRecord(
        document_id=doc.id,
        khasra_number=field_dict.get("khasra_number"),
        khata_number=field_dict.get("khata_number"),
        survey_number=field_dict.get("survey_number"),
        owner_name=field_dict.get("owner_name"),
        father_husband_name=field_dict.get("father_husband_name"),
        village=field_dict.get("village"),
        tehsil=field_dict.get("tehsil"),
        district=field_dict.get("district"),
        land_area=field_dict.get("land_area"),
        land_type=field_dict.get("land_type"),
        mutation_details=field_dict.get("mutation_details"),
        status="auto_validated" if pipeline_status == "auto_validated" else "draft",
        geometry_geojson={
          "type": "Polygon",
          "coordinates": [[[77.4126, 23.2599], [77.4150, 23.2599], [77.4150, 23.2620], [77.4126, 23.2620], [77.4126, 23.2599]]]
        }
    )
    db.add(land_rec)

    # Audit log
    audit = AuditLog(
        document_id=doc.id,
        action="ingest_and_process",
        new_value=f"Status: {pipeline_status}, Confidence: {overall_conf}"
    )
    db.add(audit)

    await db.commit()

    # Query eagerly with selectinload to prevent MissingGreenlet in Async Pydantic serialization
    q = select(Document).options(
        selectinload(Document.extracted_fields),
        selectinload(Document.land_record)
    ).where(Document.id == doc.id)
    res = await db.execute(q)
    full_doc = res.scalar_one()

    # Build Pydantic response explicitly to avoid async ORM lazy load errors
    fields_resp = [ExtractedFieldResponse.model_validate(f) for f in full_doc.extracted_fields]
    record_resp = LandRecordResponse.model_validate(full_doc.land_record) if full_doc.land_record else None

    return DocumentResponse(
        id=full_doc.id,
        filename=full_doc.filename,
        original_filepath=full_doc.original_filepath,
        preprocessed_filepath=full_doc.preprocessed_filepath,
        status=full_doc.status,
        overall_confidence=full_doc.overall_confidence,
        created_at=full_doc.created_at,
        updated_at=full_doc.updated_at,
        extracted_fields=fields_resp,
        land_record=record_resp
    )
