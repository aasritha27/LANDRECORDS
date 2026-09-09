import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="verifier") # uploader, verifier, admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filepath = Column(String(500), nullable=False)
    preprocessed_filepath = Column(String(500), nullable=True)
    status = Column(String(50), default="uploaded", index=True) 
    # Statuses: uploaded -> preprocessed -> ocr_complete -> classified -> auto_validated / needs_review -> verified
    overall_confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    land_record = relationship("LandRecord", back_populates="document", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False, index=True)
    field_value = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    bounding_box = Column(JSON, nullable=True) # {"x": 10, "y": 20, "w": 100, "h": 30}
    is_verified = Column(Boolean, default=False)
    corrected_value = Column(Text, nullable=True)
    validation_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="extracted_fields")

class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)
    khasra_number = Column(String(100), index=True, nullable=True)
    khata_number = Column(String(100), index=True, nullable=True)
    survey_number = Column(String(100), nullable=True)
    owner_name = Column(String(255), index=True, nullable=True)
    father_husband_name = Column(String(255), nullable=True)
    village = Column(String(100), index=True, nullable=True)
    tehsil = Column(String(100), index=True, nullable=True)
    district = Column(String(100), index=True, nullable=True)
    land_area = Column(String(100), nullable=True)
    land_type = Column(String(100), nullable=True) # Agricultural, Residential, Commercial
    mutation_details = Column(Text, nullable=True)
    geometry_geojson = Column(JSON, nullable=True) # GeoJSON polygon for Leaflet/GIS rendering
    status = Column(String(50), default="draft")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="land_record")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False) # upload, preprocess, ocr, field_edit, verify, reject
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
