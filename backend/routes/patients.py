from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import get_db
from database import crud, schemas, auth

router = APIRouter(tags=["Patients"])

@router.get("/patients", response_model=List[schemas.Patient])
def get_patients(current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    patients = crud.get_patients_by_doctor(db=db, doctor_id=current_user.id)
    return patients

@router.post("/patients", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Create a new patient for the current doctor"""
    return crud.create_patient(db=db, patient=patient, doctor_id=current_user.id)

@router.get("/patients/{patient_id}", response_model=schemas.Patient)
def get_patient(patient_id: int, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Get a specific patient by ID"""
    db_patient = crud.get_patient_by_id(db=db, patient_id=patient_id, doctor_id=current_user.id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@router.put("/patients/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient_data: schemas.PatientUpdate, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Update a patient's information"""
    return crud.update_patient(db=db, patient_id=patient_id, doctor_id=current_user.id, patient_data=patient_data)

@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Delete a patient"""
    return crud.delete_patient(db=db, patient_id=patient_id, doctor_id=current_user.id)

@router.post("/patients/{patient_id}/notes", response_model=schemas.Patient)
def add_progress_note(patient_id: int, note: schemas.ProgressNoteCreate, current_user: schemas.User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    """Add a progress note to a patient"""
    return crud.add_progress_note(db=db, patient_id=patient_id, doctor_id=current_user.id, note=note)
