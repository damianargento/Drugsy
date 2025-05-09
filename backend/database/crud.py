from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, status
from typing import Optional

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
    
    # Preparar datos para la creación del usuario
    user_data = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "hashed_password": hashed_password,
    }
    
    # Añadir campos opcionales solo si están presentes
    if user.medications is not None:
        user_data["medications"] = [med.dict() for med in user.medications]
    
    if user.chronic_conditions is not None:
        user_data["chronic_conditions"] = user.chronic_conditions
    
    # Crear el objeto de usuario
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
        if value is not None:  # Solo actualizar campos que no son None
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user
