from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, status
from typing import Optional, List, Any
from datetime import datetime, timedelta, date
import secrets
import json

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

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

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete all patients associated with this user
    patients = get_patients_by_doctor(db, user_id)
    for patient in patients:
        db.delete(patient)
    
    # Delete the user
    db.delete(db_user)
    db.commit()
    return {"message": "User account and all associated data deleted successfully"}


def create_password_reset_token(db: Session, email: str) -> Optional[str]:
    """Create a password reset token for a user"""
    # Find the user by email
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Generate a secure token
    token = secrets.token_urlsafe(32)
    
    # Set token expiration (24 hours)
    expiration = datetime.now() + timedelta(hours=24)
    
    # Save token to user record
    user.reset_token = token
    user.reset_token_expires = expiration
    db.commit()
    
    return token


def verify_reset_token(db: Session, token: str) -> Optional[models.User]:
    """Verify a password reset token and return the user if valid"""
    # Find user with this token
    user = db.query(models.User).filter(models.User.reset_token == token).first()
    
    # Check if token exists and is not expired
    if not user or not user.reset_token_expires or user.reset_token_expires < datetime.now():
        return None
    
    return user


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """Reset a user's password using a valid token"""
    # Verify token and get user
    user = verify_reset_token(db, token)
    if not user:
        return False
    
    # Update password
    user.hashed_password = models.User.get_password_hash(new_password)
    
    # Clear reset token
    user.reset_token = None
    user.reset_token_expires = None
    
    db.commit()
    return True

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
        # Convert datetime objects in progress notes to JSON-serializable format
        patient_data['progress_notes'] = json.loads(
            json.dumps(patient_data['progress_notes'], cls=DateTimeEncoder)
        )
    
    # Convert medications to the right format if provided
    if patient_data.get('medications'):
        patient_data['medications'] = [med.dict() for med in patient_data['medications']]
    
    # Handle date_of_birth - convert string to date object if provided
    if patient_data.get('date_of_birth') is not None:
        try:
            # If it's already a date object, keep it as is
            if not isinstance(patient_data['date_of_birth'], date):
                # Try to parse the date string in ISO format (YYYY-MM-DD)
                patient_data['date_of_birth'] = date.fromisoformat(patient_data['date_of_birth'])
        except (ValueError, TypeError) as e:
            # If date parsing fails, log the error
            print(f"Error parsing date_of_birth: {e}")
            # Don't create the patient if we can't parse the date_of_birth
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date format for date_of_birth: {patient_data['date_of_birth']}"
            )
    
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
    
    # Handle progress notes if provided
    if update_data.get('progress_notes') is not None:
        # Handle empty list case
        if len(update_data['progress_notes']) == 0:
            update_data['progress_notes'] = []
        else:
            # Check if progress notes are already dictionaries or Pydantic models
            if hasattr(update_data['progress_notes'][0], 'dict'):
                update_data['progress_notes'] = [note.dict() for note in update_data['progress_notes']]
            
            # Convert progress_notes to JSON-serializable format using our custom DateTimeEncoder
            update_data['progress_notes'] = json.loads(
                json.dumps(update_data['progress_notes'], cls=DateTimeEncoder)
            )
    
    # Handle date_of_birth - convert string to date object if provided
    if update_data.get('date_of_birth') is not None:
        try:
            # If it's already a date object, keep it as is
            if not isinstance(update_data['date_of_birth'], date):
                # Try to parse the date string in ISO format (YYYY-MM-DD)
                update_data['date_of_birth'] = date.fromisoformat(update_data['date_of_birth'])
        except (ValueError, TypeError) as e:
            # If date parsing fails, log the error and keep the original value
            print(f"Error parsing date_of_birth: {e}")
            # Don't update the field if we can't parse it
            del update_data['date_of_birth']
    
    # Apply all updates at once after processing all fields
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
