from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/mock-lrms", tags=["Mock Integration Layer"])

@router.get("/validate-owner/{khasra_no}")
async def validate_owner_lrms(khasra_no: str) -> Dict[str, Any]:
    """
    Mock endpoint simulating state LRMS (Land Records Management System)
    registry check for owner verification & mutation status.
    """
    return {
        "status": "success",
        "system": "State DILRMP Cadastral Database",
        "khasra_no": khasra_no,
        "lrms_registered_owner": "Ramesh Chandra Sharma",
        "mutation_history": [
            {"date": "2021-04-12", "type": "Inheritance", "status": "Approved"},
            {"date": "2010-08-05", "type": "Sale Deed", "status": "Approved"}
        ],
        "is_disputed": False,
        "encumbrance_status": "Clear"
    }

@router.get("/gis-parcel/{khasra_no}")
async def get_gis_parcel_geometry(khasra_no: str) -> Dict[str, Any]:
    """
    Mock endpoint serving GeoJSON cadastral geometry polygon for GIS mapping.
    """
    return {
        "type": "Feature",
        "properties": {
            "khasra_no": khasra_no,
            "village": "Rampur",
            "tehsil": "Sadar",
            "district": "Bhopal"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [77.4126, 23.2599],
                    [77.4150, 23.2599],
                    [77.4150, 23.2620],
                    [77.4126, 23.2620],
                    [77.4126, 23.2599]
                ]
            ]
        }
    }
