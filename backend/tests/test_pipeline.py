import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.pipeline.preprocess import deskew_image, denoise_and_enhance
from app.pipeline.rules import validate_village_name, validate_khasra_format, validate_land_area
from app.pipeline.confidence_engine import process_document_pipeline
from app.pipeline.field_extraction import extract_fields
import numpy as np

def test_khasra_format_validation():
    assert validate_khasra_format("142/1") == True
    assert validate_khasra_format("504") == True
    assert validate_khasra_format("88/A") == True
    assert validate_khasra_format("INVALID_KHASRA_FORMAT_!!!") == False

def test_land_area_validation():
    assert validate_land_area("1.450 Hectares") == True
    assert validate_land_area("0.05 Acres") == True
    assert validate_land_area("-5.0 Hectares") == False

def test_village_fuzzy_matching():
    res = validate_village_name("Rampur")
    assert res["valid"] == True
    assert res["matched_village"] == "Rampur"

def test_field_extraction():
    ocr_blocks = [{
        "text": "Khasra No: 142/1 Khata No: 88 Village: Rampur Tehsil: Sadar District: Bhopal Owner Name: Ramesh Chandra Sharma Land Area: 1.450 Hectares",
        "confidence": 0.90,
        "bounding_box": {"x": 0, "y": 0, "w": 100, "h": 20}
    }]
    fields = extract_fields(ocr_blocks)
    field_map = {f["field_name"]: f["field_value"] for f in fields}
    
    assert field_map.get("khasra_number") == "142/1"
    assert field_map.get("khata_number") == "88"
    assert field_map.get("owner_name") == "Ramesh Chandra Sharma"
    assert field_map.get("village") == "Rampur"
