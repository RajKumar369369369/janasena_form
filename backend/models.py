from sqlalchemy import Column, Integer, String, Date, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class Person(Base):
    __tablename__ = "person"
    __table_args__ = {"schema": "janasena"}

    person_id = Column(Integer, primary_key=True, index=True)

    aadhaar_number = Column(String, unique=True, nullable=False)
    nominee_id = Column(String)
    jsp_id = Column(String, unique=True, nullable=True)

    full_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String)
    pincode = Column(String)

    constituency = Column(String)
    mandal = Column(String)
    panchayathi = Column(String)
    village = Column(String)
    ward_number = Column(String)

    latitude = Column(Float)
    longitude = Column(Float)

    education = Column(String)
    profession = Column(String)
    religion = Column(String)
    reservation = Column(String)
    caste = Column(String)

    membership = Column(String)
    membership_id = Column(String)

    aadhaar_image_url = Column(String)
    photo_url = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
