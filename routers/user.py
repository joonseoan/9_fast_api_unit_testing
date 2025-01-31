from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from models import Todos, Users
from database import SessionLocal
from .auth import get_current_user
from dtos.user_password import UserPassword
from dtos.user import UserDto
from passlib.context import CryptContext


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
def me(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="You are not logged in now")

    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.patch("/password_update", status_code=status.HTTP_204_NO_CONTENT)
def update_password(user: user_dependency, db: db_dependency, updated_password: UserPassword):
    if user is None:
        raise HTTPException(status_code=401, detail="not possible to change password")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(updated_password.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="The current password is not identical")

    current_user.hashed_password = bcrypt_context.hash(updated_password.new_password)

    db.add(current_user)
    db.commit()


@router.put("/user_update", status_code=status.HTTP_204_NO_CONTENT)
def update_user(user: user_dependency, db: db_dependency, user_update: UserDto):
    if user is None:
        raise HTTPException(status_code=401, detail="You are not authorized to update phone_number")

    current_user = db.query(Users).filter(Users.id == user.get("id")).first()
    current_user.phone_number = user_update.phone_number

    db.add(current_user)
    db.commit()
