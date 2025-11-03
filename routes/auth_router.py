from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
# from model import User
from model.models import User

from schemas import UserCreate, UserLogin
from services.auth_services import create_access_token, hash_password, verify_password
# from auth.auth_service import (
#     get_db, hash_password, verify_password, create_access_token
# )

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    role_value = user.role.upper()  

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=role_value
    )   
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully", "user": new_user.email}


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer", "role": db_user.role}

