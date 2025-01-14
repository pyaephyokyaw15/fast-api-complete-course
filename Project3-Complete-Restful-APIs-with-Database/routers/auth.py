from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm


# app = FastAPI()  # If we use FastAPI() here, we will have two FastAPI instances in the same application
# If there is two API instances, we cannot run main.py with uvicorn main:app, we need to run uvicorn auth:app --reload
# Also, we will not have two app APIs. We will get one app API at a time.
# TO include all apps API, we need router.
# If we use Router(), we don't need to create a new FastAPI instance

router = APIRouter()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(request: CreateUserRequest,
                      db: db_dependency):
    new_user = Users(
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=bcrypt_context.hash(request.password),
        role=request.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    return user
