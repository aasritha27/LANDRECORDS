import json
import os
import re
from rapidfuzz import process, fuzz
from typing import Dict, Any, List

# Load master seed villages
SEED_VILLAGES_PATH = os.path.join("..", "data", "seed", "master_villages.json")
if not os.path.exists(SEED_VILLAGES_PATH):
    SEED_VILLAGES_PATH = os.path.join("data", "seed", "master_villages.json")

MASTER_VILLAGES = []
if os.path.exists(SEED_VILLAGES_PATH):
    with open(SEED_VILLAGES_PATH, "r", encoding="utf-8") as f:
        MASTER_VILLAGES = json.load(f)

def validate_village_name(extracted_village: str) -> Dict[str, Any]:
    """
    Fuzzy match extracted village against master seed list using RapidFuzz.
    """
    if not extracted_village or not MASTER_VILLAGES:
        return {"valid": True, "score": 1.0, "matched_village": extracted_village}

    village_names = [v["village"] for v in MASTER_VILLAGES]
    match = process.extractOne(extracted_village, village_names, scorer=fuzz.ratio)
    
    if match and match[1] >= 70:
        return {
            "valid": True,
            "score": round(match[1] / 100.0, 2),
            "matched_village": match[0]
        }
    else:
        return {
            "valid": False,
            "score": 0.50,
            "matched_village": extracted_village
        }

def validate_khasra_format(khasra_no: str) -> bool:
    """Validate format of khasra number (e.g., '142/1', '504', '88/A', '142/1a')."""
    if not khasra_no:
        return False
    pattern = r"^[0-9]+(\s*/\s*[0-9a-zA-Z]+)?$"
    return bool(re.match(pattern, khasra_no.strip()))

def validate_land_area(area_str: str) -> bool:
    """Validate reasonable positive land area."""
    if not area_str:
        return True
    match = re.search(r"(-?[0-9\.]+)", area_str)
    if match:
        try:
            val = float(match.group(1))
            return 0.001 <= val <= 1000.0
        except ValueError:
            return False
    return True
