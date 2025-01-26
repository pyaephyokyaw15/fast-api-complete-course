from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal  # it can be show error due to working directory
from models import Todos  # it can be show error due to working directory

from .auth import get_current_user


router = APIRouter(
    tags=['admin'],
    prefix='/admin'
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return db.query(Todos).all()


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_todo_id(user: user_dependency,db: db_dependency,  todo_id: Annotated[int, Path(gt=0)]):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_item is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo_item)
    db.commit()