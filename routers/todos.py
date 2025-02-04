from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..models import Todos
from ..database import SessionLocal
from ..dtos.todo import TodoDto
from .auth import get_current_user


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
def find_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed in find_all")

    return (db.query(Todos)
            .filter(Todos.owner_id == user.get("id"))
            .all())


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
def find_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed in find_todo")

    todo_model = (db.query(Todos)
                  .filter(Todos.id == todo_id)
                  .filter(Todos.owner_id == user.get("id"))
                  .first())

    if todo_model is not None:
        return todo_model

    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo/create", status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependency, db: db_dependency, new_todo: TodoDto):
    if user is None:
        raise HTTPException(status_code=401, detail="You are not authorized to create todo.")

    todo_model = Todos(**new_todo.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_todo(user: user_dependency, db: db_dependency, new_todo: TodoDto, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed in update_todo")

    existing_model = (db.query(Todos)
                      .filter(Todos.id == todo_id)
                      .filter(Todos.owner_id == user.get("id"))
                      .first())

    if existing_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    existing_model.title = new_todo.title
    existing_model.description = new_todo.description
    existing_model.priority = new_todo.priority
    existing_model.complete = new_todo.complete

    db.add(existing_model)
    db.commit()


# [IMPORTANT] HTTP_204_NO_CONTENT return nothing because it is `no_content`
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed in update_todo")

    existing_model = (db.query(Todos)
                      .filter(Todos.id == todo_id)
                      .filter(Todos.owner_id == user.get("id"))
                      .first())

    if existing_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    (db.query(Todos)
     .filter(Todos.id == todo_id)
     .filter(Todos.owner_id == user.get("id"))
     .delete())

    db.commit()
