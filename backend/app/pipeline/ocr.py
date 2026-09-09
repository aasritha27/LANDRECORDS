import cv2
import numpy as np
import re
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tesseract setup — search common Windows install paths
# ---------------------------------------------------------------------------
import pytesseract

POSSIBLE_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
]

TESSERACT_AVAILABLE = False
for _p in POSSIBLE_TESSERACT_PATHS:
    if os.path.exists(_p):
        pytesseract.pytesseract.tesseract_cmd = _p
        TESSERACT_AVAILABLE = True
        logger.info(f"Tesseract found at: {_p}")
        break

if not TESSERACT_AVAILABLE:
    logger.warning(
        "Tesseract binary NOT found. Will use EasyOCR as fallback.\n"
        "To get best results, install Tesseract from:\n"
        "  https://github.com/UB-Mannheim/tesseract/wiki\n"
        "  (choose 'Additional language data' → Telugu + Hindi during setup)"
    )

# ---------------------------------------------------------------------------
# EasyOCR lazy loader — only imported if Tesseract is absent
# ---------------------------------------------------------------------------
_easyocr_reader = None

def _get_easyocr():
    global _easyocr_reader
    if _easyocr_reader is None:
        try:
            import easyocr
            # en = English, hi = Hindi, te = Telugu
            _easyocr_reader = easyocr.Reader(["en", "hi", "te"], gpu=False, verbose=False)
            logger.info("EasyOCR reader initialised (en + hi + te).")
        except ImportError:
            logger.error("EasyOCR not installed. Run: pip install easyocr")
        except Exception as e:
            logger.error(f"EasyOCR init failed: {e}")
    return _easyocr_reader


# ---------------------------------------------------------------------------
# Tesseract OCR — returns real per-word confidence
# ---------------------------------------------------------------------------
def _run_tesseract(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Use pytesseract.image_to_data to get per-word confidence scores.
    Groups words into lines, averaging confidence per line.
    Returns list of {text, confidence, bounding_box}.
    """
    # Try multilingual first, fall back to English only
    for lang in ("eng+hin+tel", "eng+hin", "eng"):
        try:
            data = pytesseract.image_to_data(
                image,
                lang=lang,
                config="--psm 6 --oem 3",   # PSM 6 = uniform text block
                output_type=pytesseract.Output.DICT,
            )
            break
        except Exception as e:
            logger.warning(f"Tesseract lang={lang} failed: {e}")
            data = None

    if data is None:
        return []

    # Group words by line number (block_num + par_num + line_num)
    lines: Dict[tuple, Dict] = {}
    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip()
        conf = int(data["conf"][i])
        if not word or conf < 0:        # conf=-1 means non-text element
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        if key not in lines:
            lines[key] = {
                "words": [],
                "confs": [],
                "x": data["left"][i],
                "y": data["top"][i],
                "w": 0,
                "h": data["height"][i],
            }
        lines[key]["words"].append(word)
        lines[key]["confs"].append(conf)
        lines[key]["w"] = max(lines[key]["w"], data["left"][i] + data["width"][i] - lines[key]["x"])

    results = []
    for key in sorted(lines.keys()):
        ln = lines[key]
        text = " ".join(ln["words"])
        avg_conf = sum(ln["confs"]) / len(ln["confs"]) / 100.0   # 0-1 range
        results.append({
            "text": text,
            "confidence": round(avg_conf, 3),
            "bounding_box": {"x": ln["x"], "y": ln["y"], "w": ln["w"], "h": ln["h"]},
        })

    return results


# ---------------------------------------------------------------------------
# EasyOCR fallback — returns per-line results with real confidence
# ---------------------------------------------------------------------------
def _run_easyocr(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Use EasyOCR as fallback when Tesseract is absent.
    Returns list of {text, confidence, bounding_box}.
    """
    reader = _get_easyocr()
    if reader is None:
        return []

    try:
        raw = reader.readtext(image, detail=1, paragraph=False)
    except Exception as e:
        logger.error(f"EasyOCR readtext failed: {e}")
        return []

    results = []
    for bbox, text, conf in raw:
        text = text.strip()
        if not text:
            continue
        xs = [pt[0] for pt in bbox]
        ys = [pt[1] for pt in bbox]
        x, y = int(min(xs)), int(min(ys))
        w = int(max(xs) - min(xs))
        h = int(max(ys) - min(ys))
        results.append({
            "text": text,
            "confidence": round(float(conf), 3),
            "bounding_box": {"x": x, "y": y, "w": w, "h": h},
        })

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def extract_lines_from_image(image_path: str) -> List[str]:
    """
    Convenience function — returns list of text lines from an image.
    Used by tests / standalone callers.
    """
    blocks = run_ocr(image_path, [])
    return [b["text"] for b in blocks if b.get("text")]


def run_ocr(image_path: str, regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Multilingual OCR Engine (English + Telugu + Hindi).
    Priority:
      1. Tesseract (if binary found) — uses real per-word confidence.
      2. EasyOCR  (if Tesseract absent) — pure-Python, no binary needed.
    Returns list of OCR blocks: {text, confidence, bounding_box}.
    """
    # The preprocessed image is already grayscale (from preprocess.py)
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        # Try reading as colour and converting
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            logger.error(f"Cannot read image: {image_path}")
            return []
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    if TESSERACT_AVAILABLE:
        results = _run_tesseract(img)
        engine = "Tesseract"
    else:
        # EasyOCR can take grayscale or BGR — grayscale is fine
        results = _run_easyocr(img)
        engine = "EasyOCR"

    if results:
        avg_conf = sum(r["confidence"] for r in results) / len(results)
        logger.info(
            f"[OCR:{engine}] {image_path} → {len(results)} lines, "
            f"avg_conf={avg_conf:.2f}"
        )
    else:
        logger.warning(f"[OCR:{engine}] No text extracted from {image_path}")

    return results
