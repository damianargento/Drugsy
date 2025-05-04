from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

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

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
