from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal  # it can be show error due to working directory
from models import Users  # it can be show error due to working directory

from .auth import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['user']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/user_info", status_code=status.HTTP_200_OK)
async def user_info(user: user_dependency,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, old_password: str, new_password: str):
    # instead of using class BaseModel, we can pass parameters directly.
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_record = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if user_record is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(old_password, user_record.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    user_record.hashed_password = bcrypt_context.hash(new_password)
    db.commit()
    return {"message": "Password changed successfully"}
