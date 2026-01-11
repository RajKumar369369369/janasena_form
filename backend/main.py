import os
import requests
import tempfile

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Person
from crud import create_or_update_person, get_by_aadhaar
from schemas import (
    PersonCreate,
    PersonResponse,
    AadhaarOCRRequest,
    AadhaarOCRResponse
)
from ocr.aadhaar_ocr import run_aadhaar_ocr

# -------------------------------------------------
# App init
# -------------------------------------------------
app = FastAPI(title="Janasena Backend API")

# Create tables
Base.metadata.create_all(bind=engine)

# -------------------------------------------------
# CORS
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# PERSON APIs
# -------------------------------------------------
@app.post("/person/submit", response_model=PersonResponse)
def submit_person(
    data: PersonCreate,
    db: Session = Depends(get_db)
):
    """
    Receives JSON payload from frontend.
    Images must already be uploaded to Cloudinary.
    Stores text fields + image URLs in PostgreSQL.
    """
    try:
        person = create_or_update_person(db, data)
        return person

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/person/by-aadhaar/{aadhaar_number}", response_model=PersonResponse)
def get_person_by_aadhaar(
    aadhaar_number: str,
    db: Session = Depends(get_db)
):
    person = db.query(Person).filter(
        Person.aadhaar_number == aadhaar_number
    ).first()

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person


# -------------------------------------------------
# OCR API (APPLIED LOGIC)
# -------------------------------------------------
@app.post("/ocr/aadhaar", response_model=AadhaarOCRResponse)
def aadhaar_ocr(
    payload: AadhaarOCRRequest,
    owner: str = Query(None),   # "member" | "nominee"
    db: Session = Depends(get_db)
):
    """
    Accepts JSON:
    {
        "image_url": "<cloudinary_url>"
    }

    owner=member  -> always OCR
    owner=nominee -> DB first, OCR fallback
    """

    # 1️⃣ Download image
    try:
        response = requests.get(payload.image_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to download image: {str(e)}"
        )

    tmp_file = None

    try:
        # 2️⃣ Save temporary image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
            f.write(response.content)
            tmp_file = f.name

        # 3️⃣ Run OCR
        ocr_result = run_aadhaar_ocr(tmp_file)
        normalized_aadhaar = ocr_result.get("aadhaar_number", "")

        # 4️⃣ Nominee logic → DB first
        if owner and owner.lower() == "nominee" and normalized_aadhaar:
            person = get_by_aadhaar(db, normalized_aadhaar)
            if person:
                return {
                    "aadhaar_number": person.aadhaar_number or "",
                    "full_name": person.full_name or "",
                    "gender": person.gender or "",
                    "dob": person.dob.isoformat() if person.dob else "",
                    "mobile_number": person.mobile_number or "",
                    "pincode": person.pincode or ""
                }

        # 5️⃣ Fallback → OCR result
        return ocr_result

    finally:
        # 6️⃣ Cleanup temp file
        try:
            if tmp_file and os.path.exists(tmp_file):
                os.remove(tmp_file)
        except Exception:
            pass
