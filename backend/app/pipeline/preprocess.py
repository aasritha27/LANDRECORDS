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
    """Apply bilateral filtering & CLAHE contrast enhancement."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Denoise
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive Histogram Equalization (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

def preprocess_image(input_filepath: str) -> str:
    """
    Main preprocessing entry point: loads scan, deskews, denoises, enhances,
    saves preprocessed copy in PREPROCESSED_DIR and returns path.
    """
    filename = os.path.basename(input_filepath)
    output_filename = f"clean_{filename}"
    output_filepath = os.path.join(settings.PREPROCESSED_DIR, output_filename)

    # Read image
    img = cv2.imread(input_filepath)
    if img is None:
        # Fallback if non-image format or corrupted
        return input_filepath

    # Run processing pipeline
    deskewed = deskew_image(img)
    enhanced = denoise_and_enhance(deskewed)

    # Save output
    cv2.imwrite(output_filepath, enhanced)

    return output_filepath
