from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = models.User.get_password_hash(user.password)
    
    # Prepare data for user creation
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "hashed_password": hashed_password,
    }
    
    # Create user object
    db_user = models.User(**user_data)
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not models.User.verify_password(password, user.hashed_password):
        return None
    return user

def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user data
    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:  # Only update fields that are not None
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Patient CRUD operations
def get_patients_by_doctor(db: Session, doctor_id: int) -> List[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.doctor_id == doctor_id).all()

def get_patient_by_id(db: Session, patient_id: int, doctor_id: int):
    return db.query(models.Patient).filter(
        models.Patient.id == patient_id,
        models.Patient.doctor_id == doctor_id
    ).first()

def create_patient(db: Session, patient: schemas.PatientCreate, doctor_id: int):
    # Prepare patient data
    patient_data = patient.dict()
    
    # Convert progress_notes to the right format if provided
    if patient_data.get('progress_notes'):
        patient_data['progress_notes'] = [note.dict() for note in patient_data['progress_notes']]
    
    # Convert medications to the right format if provided
    if patient_data.get('medications'):
        patient_data['medications'] = [med.dict() for med in patient_data['medications']]
    
    # Create patient object
    db_patient = models.Patient(**patient_data, doctor_id=doctor_id)
    
    # Add to database
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, doctor_id: int, patient_data: schemas.PatientUpdate):
    db_patient = get_patient_by_id(db, patient_id, doctor_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Update patient data
    update_data = patient_data.dict(exclude_unset=True)
    
    # Handle medications if provided
    if update_data.get('medications') is not None:
        # Handle empty list case
        if len(update_data['medications']) == 0:
            update_data['medications'] = []
        else:
            # Check if medications are already dictionaries or Pydantic models
            if hasattr(update_data['medications'][0], 'dict'):
                update_data['medications'] = [med.dict() for med in update_data['medications']]
            # If they're already dictionaries, leave them as is
    for key, value in update_data.items():
        if value is not None:  # Only update fields that are not None
            setattr(db_patient, key, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int, doctor_id: int):
    db_patient = get_patient_by_id(db, patient_id, doctor_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    db.delete(db_patient)
    db.commit()
    return {"message": "Patient deleted successfully"}

def add_progress_note(db: Session, patient_id: int, doctor_id: int, note: schemas.ProgressNoteCreate):
    db_patient = get_patient_by_id(db, patient_id, doctor_id)
    if not db_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create new progress note
    new_note = {
        "date": datetime.now(),
        "content": note.content
    }
    
    # Add note to patient's progress notes
    if db_patient.progress_notes is None:
        db_patient.progress_notes = [new_note]
    else:
        db_patient.progress_notes.append(new_note)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient
