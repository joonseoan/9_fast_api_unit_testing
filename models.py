from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True)
    username = Column(String(100), unique=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=False)
    role = Column(String(100))
    # Just added `phone_number` but does not exist in PostgreSQL DB
    # It does not modify the actual DB table.
    phone_number = Column(String(20))


class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    description = Column(String(255))
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

