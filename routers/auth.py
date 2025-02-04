from datetime import timedelta, datetime, timezone
from typing import Annotated
from starlette import status
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from ..models import Users
from ..database import SessionLocal
from ..dtos.user import UserDto
from ..dtos.token import Token


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "AFJLAJFLADafdafalc"
ALGORITHM = "HS256"


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: db_dependency) -> Users | bool:
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: str, role: str, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate the user",
            )

        return {
            "username": username,
            "id": user_id,
            "role": user_role,
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency, create_user_request: UserDto):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
        phone_number=create_user_request.phone_number,
    )

    db.add(create_user_model)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to validate the user"
        )

    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer",
    }
