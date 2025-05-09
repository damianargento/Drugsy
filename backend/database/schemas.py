from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# Esquema para medicación
class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    medications: Optional[List[Medication]] = None
    chronic_conditions: Optional[str] = None

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
    medications: Optional[List[Medication]] = None
    chronic_conditions: Optional[str] = None

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
