import cv2
import numpy as np
from typing import List, Dict, Any

def detect_layout_regions(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect document layout zones (Header, Table, Signature/Owner Details)
    using morphological contour bounding boxes.
    Returns list of region dicts: {"x", "y", "w", "h", "type"}.
    """
    img = cv2.imread(image_path)
    if img is None:
        return [{"x": 0, "y": 0, "w": 1000, "h": 1000, "type": "full_page"}]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h_page, w_page = gray.shape

    # Morphological dilation to group text lines into bounding blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 5))
    thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)[1]
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    for idx, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w > 50 and h > 15: # Filter tiny noise
            region_type = "header" if y < h_page * 0.2 else ("table" if w > w_page * 0.5 else "field_block")
            regions.append({
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "type": region_type
            })

    if not regions:
        regions.append({"x": 0, "y": 0, "w": int(w_page), "h": int(h_page), "type": "full_page"})

    return sorted(regions, key=lambda r: r["y"])
