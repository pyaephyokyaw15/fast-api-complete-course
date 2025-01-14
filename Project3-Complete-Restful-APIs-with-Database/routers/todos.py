from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import SessionLocal  # it can be show error due to working directory
from models import Todos  # it can be show error due to working directory


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    # title: str
    # description: str
    # priority: int
    # completed: bool
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    completed: bool = Field(default=False)


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_todo_id(db: db_dependency, todo_id: Annotated[int, Path(gt=0)]):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_item is not None:
        return todo_item
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_new_todo(todo: TodoRequest, db: db_dependency):
    new_todo = Todos(**todo.model_dump())
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.put("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo_by_todo_id(todo_id: int, todo: TodoRequest, db: db_dependency):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_item is not None:
        for key, value in todo.model_dump().items():
            setattr(todo_item, key, value)  # nice way to update the object
            # todo_item.title = todo.title
            # todo_item.description = todo.description
            # todo_item.priority = todo.priority
            # todo_item.completed = todo.completed
            # db.add(todo_item)  # if we use setattr, we don't need to add the object again
        db.commit()
        db.refresh(todo_item)
        return todo_item
    raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/todos/{todo_id}", status_code=status.HTTP_200_OK)
async def delete_todo_by_todo_id(todo_id: int, db: db_dependency):
    todo_item = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_item is not None:
        db.delete(todo_item)
        db.commit()
        return todo_item
    raise HTTPException(status_code=404, detail="Todo not found")
