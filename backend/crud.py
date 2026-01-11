import re
from sqlalchemy.orm import Session
from models import Person
from schemas import PersonCreate

def normalize_aadhaar(aadhaar: str) -> str:
    if not aadhaar:
        return ""
    return re.sub(r"\D", "", aadhaar)

def get_by_aadhaar(db: Session, aadhaar: str):
    aad = normalize_aadhaar(aadhaar)
    return db.query(Person).filter(Person.aadhaar_number == aad).first()

def get_by_jsp_id(db: Session, jsp_id: str):
    return db.query(Person).filter(Person.jsp_id == jsp_id).first()

def create_or_update_person(db: Session, data: PersonCreate):
    person = get_by_aadhaar(db, data.aadhaar_number)

    if person:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(person, key, value)
    else:
        person = Person(**data.dict())
        db.add(person)

    db.commit()
    db.refresh(person)
    return person
