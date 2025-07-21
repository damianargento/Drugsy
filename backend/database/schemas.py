from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# Schema for password reset
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Schema for medication
class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str

# Schema for progress note
class ProgressNote(BaseModel):
    date: datetime
    content: str

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

# Schema for creating a new user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for user response
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
# Schema for updating user settings
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    
class TokenRefresh(BaseModel):
    refresh_token: str

# Base Patient Schema
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    medications: Optional[List[Medication]] = None
    chronic_conditions: Optional[str] = None
    progress_notes: Optional[List[ProgressNote]] = None

# Schema for creating a new patient
class PatientCreate(PatientBase):
    pass

# Schema for updating a patient
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    medications: Optional[List[Medication]] = None
    chronic_conditions: Optional[str] = None

# Schema for adding a progress note
class ProgressNoteCreate(BaseModel):
    content: str

# Schema for patient response
class Patient(PatientBase):
    id: int
    doctor_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
