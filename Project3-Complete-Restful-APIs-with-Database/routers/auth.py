from fastapi import APIRouter
from datetime import timedelta, datetime, timezone
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


# app = FastAPI()  # If we use FastAPI() here, we will have two FastAPI instances in the same application
# If there is two API instances, we cannot run main.py with uvicorn main:app, we need to run uvicorn auth:app --reload
# Also, we will not have two app APIs. We will get one app API at a time.
# TO include all apps API, we need router.
# If we use Router(), we don't need to create a new FastAPI instance

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRETE_KEY = "bc6f9b6076919a68ffae12cf2e0a8b4a70a68c83cd36e4a7424a5b62ce208e09"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

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

def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    payload = {"sub": username, "user_id": user_id, "role": role, "exp": datetime.now(timezone.utc) + expires_delta}
    token = jwt.encode(payload, SECRETE_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user credentials")
        return {"username": username, "user_id": user_id, "role": role}
    except JWTError as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user credentials") from ex


@router.post("/users", status_code=status.HTTP_201_CREATED)
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


@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=15))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(username: str, new_password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.hashed_password = bcrypt_context.hash(new_password)
    db.commit()
    return {"message": "Password reset successful"}
