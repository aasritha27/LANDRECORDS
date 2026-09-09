from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

# Extracted Field Schemas
class ExtractedFieldBase(BaseModel):
    field_name: str
    field_value: Optional[str] = None
    confidence_score: float = 0.0
    bounding_box: Optional[Dict[str, Any]] = None
    is_verified: bool = False
    corrected_value: Optional[str] = None
    validation_notes: Optional[str] = None

class ExtractedFieldCreate(ExtractedFieldBase):
    pass

class ExtractedFieldResponse(ExtractedFieldBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Land Record Schemas
class LandRecordBase(BaseModel):
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    survey_number: Optional[str] = None
    owner_name: Optional[str] = None
    father_husband_name: Optional[str] = None
    village: Optional[str] = None
    tehsil: Optional[str] = None
    district: Optional[str] = None
    land_area: Optional[str] = None
    land_type: Optional[str] = None
    mutation_details: Optional[str] = None
    geometry_geojson: Optional[Dict[str, Any]] = None
    status: str = "draft"

class LandRecordResponse(LandRecordBase):
    id: int
    document_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    status: str
    overall_confidence: float = 0.0

class DocumentCreate(DocumentBase):
    original_filepath: str

class DocumentResponse(DocumentBase):
    id: int
    original_filepath: str
    preprocessed_filepath: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    extracted_fields: List[ExtractedFieldResponse] = []
    land_record: Optional[LandRecordResponse] = None

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    document_id: int
    user_id: Optional[int] = None
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Verification / Field Edit Request
class FieldUpdateItem(BaseModel):
    field_id: int
    corrected_value: str
    validation_notes: Optional[str] = None

class DocumentVerifyRequest(BaseModel):
    updates: List[FieldUpdateItem]
    approve: bool = True
