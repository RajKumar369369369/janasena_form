from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Literal


class AadhaarOCRRequest(BaseModel):
    image_url: str


class AadhaarOCRResponse(BaseModel):
    aadhaar_number: str
    full_name: str
    gender: str
    dob: str
    mobile_number: str
    pincode: str

class PersonBase(BaseModel):
    aadhaar_number: str
    full_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    mobile_number: Optional[str] = None
    pincode: Optional[str] = None

    constituency: Optional[str] = None
    mandal: Optional[str] = None
    panchayathi: Optional[str] = None
    village: Optional[str] = None
    ward_number: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    

class PersonCreate(PersonBase):
    jsp_id: Optional[str] = None
    education: Optional[str] = None
    profession: Optional[str] = None
    religion: Optional[str] = None
    reservation: Optional[str] = None
    caste: Optional[str] = None
    membership: Optional[str] = None
    membership_id: Optional[str] = None

    aadhaar_image_url: Optional[str] = None
    photo_url: Optional[str] = None
    nominee_id: Optional[str] = None

class PersonResponse(PersonBase):
    person_id: int
    jsp_id: Optional[str] = None
    education: Optional[str] = None
    profession: Optional[str] = None
    religion: Optional[str] = None
    reservation: Optional[str] = None
    caste: Optional[str] = None
    membership: Optional[str] = None
    membership_id: Optional[str] = None
    aadhaar_image_url: Optional[str] = None
    photo_url: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PersonAutoFill(BaseModel):
    aadhaar_number: Optional[str] = None
    full_name: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    mobile_number: Optional[str] = None
    pincode: Optional[str] = None


class OCRResponse(BaseModel):
    source: Literal["db", "ocr"]
    data: PersonAutoFill
