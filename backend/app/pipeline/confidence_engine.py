from typing import List, Dict, Any, Tuple
from app.pipeline.preprocess import preprocess_image
from app.pipeline.layout_detection import detect_layout_regions
from app.pipeline.ocr import run_ocr
from app.pipeline.field_extraction import extract_fields
from app.pipeline.rules import validate_village_name, validate_khasra_format, validate_land_area
from app.config import settings

def process_document_pipeline(original_filepath: str) -> Tuple[str, List[Dict[str, Any]], float, str]:
    """
    Executes full AI ingestion pipeline:
    Preprocessing -> Layout Detection -> OCR -> Field Extraction -> Rules Validation & Confidence Scoring.

    Returns:
      (preprocessed_filepath, processed_fields, overall_confidence, status)
    """
    # Step 1: Preprocessing
    preprocessed_path = preprocess_image(original_filepath)

    # Step 2: Layout Detection
    regions = detect_layout_regions(preprocessed_path)

    # Step 3: OCR
    ocr_blocks = run_ocr(preprocessed_path, regions)

    # Step 4: NLP Field Extraction
    extracted_fields = extract_fields(ocr_blocks)

    # Step 5: Rules & Confidence Scoring
    total_score = 0.0
    field_count = len(extracted_fields)
    has_critical_failure = False

    for field in extracted_fields:
        fn = field["field_name"]
        fv = field["field_value"]
        score = field["confidence_score"]

        if fn == "village":
            res = validate_village_name(fv)
            if not res["valid"]:
                score *= 0.70
                has_critical_failure = True
            else:
                score = min(1.0, score * res["score"])
                field["field_value"] = res["matched_village"]

        elif fn == "khasra_number":
            valid_fmt = validate_khasra_format(fv)
            if not valid_fmt:
                score *= 0.60
                has_critical_failure = True
            else:
                score = min(1.0, score * 1.1)

        elif fn == "land_area":
            valid_area = validate_land_area(fv)
            if not valid_area:
                score *= 0.80

        field["confidence_score"] = round(score, 2)
        total_score += score

    overall_confidence = round(total_score / field_count, 2) if field_count > 0 else 0.0

    # Determine status
    if overall_confidence >= settings.CONFIDENCE_THRESHOLD_AUTO_VALIDATE and not has_critical_failure:
        status = "auto_validated"
    else:
        status = "needs_review"

    return preprocessed_path, extracted_fields, overall_confidence, status
