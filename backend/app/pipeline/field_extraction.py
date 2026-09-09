import re
from typing import List, Dict, Any

# Multilingual Key Aliases (Telugu, Hindi, English)
KEY_ALIASES = {
    "khasra_number": [
        r"khasra\s*(?:no|num|number)?", r"survey\s*(?:no|num|number)?", r"plot\s*(?:no|num|number)?",
        r"ఖస్రా\s*(?:నంబరు|నెం|నం)?", r"సర్వే\s*(?:నంబరు|నెం|నం)?",
        r"खसरा\s*(?:संख्या|नंबर|नं)?", r"सर्वे\s*(?:नंबर|नं)?"
    ],
    "khata_number": [
        r"khata\s*(?:no|num|number)?", r"khatauni\s*(?:no|num|number)?", r"patta\s*(?:no|num|number)?",
        r"ఖాతా\s*(?:నంబరు|నెం|నం)?", r"పట్టా\s*(?:నంబరు|నెం|నం)?",
        r"खाता\s*(?:संख्या|नंबर|नं)?", r"खतौनी\s*(?:संख्या|नंबर)?"
    ],
    "survey_number": [
        r"survey\s*(?:no|num|number)?",
        r"సర్వే\s*(?:నంబరు|నెం|నం)?",
        r"सर्वे\s*(?:नंबर|नं)?"
    ],
    "owner_name": [
        r"(?:land\s*)?owner\s*(?:name)?", r"pattadar\s*(?:name)?", r"swami\s*name", r"name",
        r"పట్టాదారు\s*పేరు", r"యజమాని\s*పేరు", r"భూమి\s*యజమాని", r"ఖాతాదారు\s*పేరు", r"పేరు",
        r"भूमिस्वामी\s*(?:का\s*नाम)?", r"खातेदार\s*(?:का\s*नाम)?", r"स्वामी\s*(?:का\s*नाम)?"
    ],
    "father_husband_name": [
        r"father\s*(?:name)?", r"husband\s*(?:name)?", r"s/o", r"w/o", r"d/o",
        r"తండ్రి\s*పేరు", r"భర్త\s*పేరు", r"తండ్రి/భర్త",
        r"पिता/पति\s*(?:का\s*नाम)?", r"संरक्षक\s*(?:का\s*नाम)?"
    ],
    "village": [
        r"village", r"gram",
        r"గ్రామం", r"గ్రామము", r"గ్రామ\s*పేరు",
        r"ग्राम", r"गाँव", r"ज़िला"
    ],
    "tehsil": [
        r"tehsil", r"mandal", r"taluk",
        r"మండలం", r"మండలము", r"తాలూకా",
        r"तहसील"
    ],
    "district": [
        r"district", r"zila",
        r"జిల్లా",
        r"ज़िला", r"जिला"
    ],
    "land_area": [
        r"(?:land\s*)?area", r"extent",
        r"విస్తీర్ణం", r"వైశాల్యం",
        r"क्षेत्रफल", r"रकबा"
    ],
    "land_type": [
        r"land\s*type", r"classification",
        r"భూమి\s*రకం", r"భూమి\s*వర్గీకరణ",
        r"भूमि\s*का\s*प्रकार"
    ],
    "mutation_details": [
        r"mutation\s*(?:details)?", r"transaction",
        r"మ్యుటేషన్", r"హక్కుల\s*మార్పు",
        r"नामांतरण"
    ]
}

def extract_fields(ocr_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Dynamic multilingual key-value extractor for English, Telugu, and Hindi land record scans.
    Parses exact values appearing after colons/separators on lines in the uploaded document image.
    """
    lines = [b["text"] for b in ocr_blocks if b.get("text")]
    full_text = "\n".join(lines)
    
    extracted_fields = []
    found_field_names = set()

    # 1. Line-by-line key-value parsing
    for line in lines:
        if ":" in line or "-" in line:
            parts = re.split(r"[:\-]", line, maxsplit=1)
            if len(parts) == 2:
                key_candidate = parts[0].strip().lower()
                val_candidate = parts[1].strip()

                if not val_candidate:
                    continue

                # Match key_candidate against alias patterns
                matched_field = None
                for f_name, alias_regexes in KEY_ALIASES.items():
                    for alias in alias_regexes:
                        if re.search(r"\b" + alias + r"\b", key_candidate, re.IGNORECASE):
                            matched_field = f_name
                            break
                    if matched_field:
                        break

                if matched_field and matched_field not in found_field_names:
                    found_field_names.add(matched_field)
                    extracted_fields.append({
                        "field_name": matched_field,
                        "field_value": val_candidate,
                        "confidence_score": 0.95,
                        "bounding_box": {"x": 40, "y": 50, "w": 400, "h": 30}
                    })

    # 2. Fallback regex search for unparsed target fields
    for f_name, alias_regexes in KEY_ALIASES.items():
        if f_name not in found_field_names:
            for alias in alias_regexes:
                pattern = r"(?:" + alias + r")[:\s\-]*([^\n,;\(\)]+)"
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match and match.group(1):
                    val = match.group(1).strip()
                    if val:
                        found_field_names.add(f_name)
                        extracted_fields.append({
                            "field_name": f_name,
                            "field_value": val,
                            "confidence_score": 0.88,
                            "bounding_box": {"x": 40, "y": 80, "w": 400, "h": 30}
                        })
                        break

    # 3. Direct pattern extraction for numbers & area if missing
    if "khasra_number" not in found_field_names:
        k_match = re.search(r"\b([0-9]+\s*/\s*[0-9]+[a-zA-Z]?)\b", full_text)
        if k_match:
            extracted_fields.append({
                "field_name": "khasra_number",
                "field_value": k_match.group(1).strip(),
                "confidence_score": 0.85,
                "bounding_box": {"x": 40, "y": 40, "w": 200, "h": 30}
            })

    if "land_area" not in found_field_names:
        a_match = re.search(r"\b([0-9\.]+\s*(?:Hectares|Acres|హెక్టార్లు|ఎకరాలు|Hec|Ac))\b", full_text, re.IGNORECASE)
        if a_match:
            extracted_fields.append({
                "field_name": "land_area",
                "field_value": a_match.group(1).strip(),
                "confidence_score": 0.85,
                "bounding_box": {"x": 40, "y": 160, "w": 200, "h": 30}
            })

    return extracted_fields
