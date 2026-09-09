import cv2
import numpy as np
import os
from app.config import settings


def deskew_image(image: np.ndarray) -> np.ndarray:
    """Deskew image using OpenCV minAreaRect on non-zero pixels."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Cap angle correction to +/- 15 degrees to prevent accidental 90 deg rotation
    if abs(angle) > 15:
        angle = 0.0

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def denoise_and_enhance(image: np.ndarray) -> np.ndarray:
    """
    Apply denoising, CLAHE contrast enhancement, and adaptive binarization.
    Returns a GRAYSCALE image ready for OCR (not BGR).
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 1. Scale up small images so Tesseract has more pixels to work with
    h, w = gray.shape[:2]
    if max(h, w) < 1200:
        scale = 2.0
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 2. Denoise using Non-Local Means (better than bilateral for text)
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # 3. Adaptive Histogram Equalization (CLAHE) to improve contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 4. Adaptive thresholding for clean black-on-white text (best for Tesseract)
    binary = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=10
    )

    # 5. Morphological cleanup: remove tiny noise specks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # Return grayscale (not BGR) — Tesseract reads this much better
    return cleaned


def preprocess_image(input_filepath: str) -> str:
    """
    Main preprocessing entry point: loads scan, deskews, denoises, enhances,
    saves preprocessed copy in PREPROCESSED_DIR and returns path.
    """
    filename = os.path.basename(input_filepath)
    # Use unique hash prefix to avoid stale cached files
    import hashlib
    h = hashlib.md5(input_filepath.encode()).hexdigest()[:8]
    output_filename = f"clean_{h}_{filename}"
    output_filepath = os.path.join(settings.PREPROCESSED_DIR, output_filename)

    # Read image
    img = cv2.imread(input_filepath)
    if img is None:
        return input_filepath

    # Run processing pipeline
    deskewed = deskew_image(img)
    enhanced_gray = denoise_and_enhance(deskewed)

    # Save output as grayscale PNG (lossless — better for OCR than JPEG)
    out_png = output_filepath.rsplit(".", 1)[0] + ".png"
    cv2.imwrite(out_png, enhanced_gray)

    return out_png
