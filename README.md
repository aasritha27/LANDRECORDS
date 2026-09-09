# BhuDrishti — AI-Powered Intelligent Land Record Digitization and Validation System

BhuDrishti is a complete AI-driven prototype system for digitizing scanned and handwritten Indian land records (Khasra, Khatauni, Jamabandi), extracting structured attributes using OCR, Computer Vision, and NLP, validating data via a rules & confidence scoring engine, routing low-confidence extractions to a Human-in-the-Loop (HITL) review UI, storing canonical records in PostGIS, and visualizing parcel spatial boundaries on an interactive GIS map.

---

## 🏗 Architecture & Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python 3.10), Async SQLAlchemy, Uvicorn |
| **Database** | PostgreSQL 15 + PostGIS (Spatial Database) |
| **Computer Vision & OCR** | OpenCV (deskewing, denoising), PyTesseract / PaddleOCR / TrOCR |
| **NLP & Rules Engine** | spaCy, RapidFuzz (fuzzy village matching), Format Regex |
| **Frontend UI** | React 18, Vite, Tailwind CSS (Glassmorphism design), Lucide Icons |
| **GIS Mapping** | Leaflet / OpenLayers parcel spatial boundary layer |
| **Containerization** | Docker & Docker Compose |

---

## 🚀 Quick Start Guide

### Option 1: Docker Compose (Recommended)

Run the full containerized application (PostGIS + FastAPI + React):

```bash
docker-compose up --build
```

- **Frontend Application**: `http://localhost:3000`
- **FastAPI Backend API Docs**: `http://localhost:8000/docs`
- **PostgreSQL / PostGIS**: `localhost:5432`

---

## 📑 Ingestion & Pipeline Workflow

1. **Document Ingestion & Image Preprocessing (`Phase 1`)**:
   - Auto-deskewing, noise reduction, adaptive thresholding via OpenCV.
2. **Layout & OCR Bounding Box Extraction (`Phase 2`)**:
   - Text region segmentation and multi-lingual OCR (English & Hindi).
3. **NLP Field Parsing (`Phase 3`)**:
   - Structured parsing for Khasra No., Khata No., Owner Name, Village, Land Area.
4. **Confidence Engine & Rules Router (`Phase 4`)**:
   - Calculates field confidence $C \in [0.0, 1.0]$. Records with $C \ge 0.85$ are marked `auto_validated`; records with $C < 0.85$ enter `needs_review`.
5. **Human-in-the-Loop Review UI (`Phase 5`)**:
   - Verifier inspects side-by-side scan & field inputs, edits values, and approves record.
6. **Canonical PostGIS Storage (`Phase 6`)**:
   - Verified records committed to `land_records` table with GeoJSON polygon geometry.
7. **GIS Spatial Map (`Phase 7`)**:
   - Interactive parcel layout mapping.
