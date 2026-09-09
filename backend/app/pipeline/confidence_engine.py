from typing import List, Dict, Any, Tuple
from app.pipeline.preprocess import preprocess_image
from app.pipeline.layout_detection import detect_layout_regions
from app.pipeline.ocr import run_ocr
from app.pipeline.field_extraction import extract_fields
from app.pipeline.rules import validate_village_name, validate_khasra_format, validate_land_area
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Minimum number of critical fields required before we trust the extraction at all
MIN_FIELDS_FOR_CONFIDENCE = 2

# Critical fields — if ANY of these are missing, cap confidence
CRITICAL_FIELDS = {"owner_name", "khasra_number", "village"}


def process_document_pipeline(original_filepath: str) -> Tuple[str, List[Dict[str, Any]], float, str]:
    """
    Executes full AI ingestion pipeline:
    Preprocessing → Layout Detection → OCR → Field Extraction → Rules Validation & Confidence Scoring.

    Returns:
      (preprocessed_filepath, processed_fields, overall_confidence, status)
    """
    # Step 1: Preprocessing (deskew, enhance, binarize)
    preprocessed_path = preprocess_image(original_filepath)
    logger.info(f"Preprocessed image saved: {preprocessed_path}")

    # Step 2: Layout Detection
    regions = detect_layout_regions(preprocessed_path)

    # Step 3: OCR (real confidence from Tesseract/EasyOCR)
    ocr_blocks = run_ocr(preprocessed_path, regions)
    logger.info(f"OCR returned {len(ocr_blocks)} text blocks")

    # Step 4: NLP Field Extraction
    extracted_fields = extract_fields(ocr_blocks)
    field_count = len(extracted_fields)
    logger.info(f"Extracted {field_count} fields: {[f['field_name'] for f in extracted_fields]}")

    # Step 5: Rules & Confidence Scoring
    total_score = 0.0
    has_critical_failure = False

    for field in extracted_fields:
        fn = field["field_name"]
        fv = field["field_value"]
        score = field["confidence_score"]   # Real OCR-derived confidence

        # --- Domain rule validation adjusts confidence up or down ---
        if fn == "village":
            res = validate_village_name(fv)
            if not res["valid"]:
                score *= 0.60          # Village not in master list → penalise
                has_critical_failure = True
            else:
                score = min(1.0, score * res["score"])
                field["field_value"] = res["matched_village"]  # Correct OCR typos

        elif fn == "khasra_number":
            valid_fmt = validate_khasra_format(fv)
            if not valid_fmt:
                score *= 0.50          # Bad format → penalise more heavily
                has_critical_failure = True
            else:
                score = min(1.0, score * 1.05)   # Small boost for valid format

        elif fn == "land_area":
            valid_area = validate_land_area(fv)
            if not valid_area:
                score *= 0.70

        field["confidence_score"] = round(score, 3)
        total_score += score

    # -----------------------------------------------------------------------
    # Guard 1: Too few fields extracted → low confidence
    # -----------------------------------------------------------------------
    if field_count < MIN_FIELDS_FOR_CONFIDENCE:
        overall_confidence = round(total_score / max(field_count, 1), 3) * 0.5
        logger.warning(
            f"Only {field_count} fields extracted (need ≥ {MIN_FIELDS_FOR_CONFIDENCE}). "
            f"Capping confidence."
        )
    else:
        overall_confidence = round(total_score / field_count, 3)

    # -----------------------------------------------------------------------
    # Guard 2: Missing critical fields → cap at 0.50 regardless of score
    # -----------------------------------------------------------------------
    extracted_names = {f["field_name"] for f in extracted_fields}
    missing_critical = CRITICAL_FIELDS - extracted_names
    if missing_critical:
        logger.warning(f"Missing critical fields: {missing_critical}. Capping confidence at 0.50.")
        overall_confidence = min(overall_confidence, 0.50)
        has_critical_failure = True

    # -----------------------------------------------------------------------
    # Guard 3: OCR returned nothing → confidence = 0
    # -----------------------------------------------------------------------
    if not ocr_blocks:
        overall_confidence = 0.0
        has_critical_failure = True

    overall_confidence = round(overall_confidence, 3)

    # Determine document status
    threshold = settings.CONFIDENCE_THRESHOLD_AUTO_VALIDATE
    if overall_confidence >= threshold and not has_critical_failure:
        status = "auto_validated"
    else:
        status = "needs_review"

    logger.info(
        f"Pipeline complete → confidence={overall_confidence}, "
        f"status={status}, fields={field_count}, critical_failure={has_critical_failure}"
    )

    return preprocessed_path, extracted_fields, overall_confidence, status
