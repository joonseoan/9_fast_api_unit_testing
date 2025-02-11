from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text
from fastapi.testclient import TestClient
import pytest

from ..main import app

# Must use Base from 'database'
from ..database import Base
from ..models import Todos, Users
from ..routers.user import bcrypt_context


# Set up test database for the endpoint testing

# Separately
# Creates a new database url
SQLALCHEMY_DATABASE_URL = "postgresql://root:qwer123@localhost/unit_test"


# Separately
# Creates a new engine with a new SQLALCHEMY_DATABASE_URL for database connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass = StaticPool,
)


# Separately
# be able to create a fully separate testing session that is isolated frm our production database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Easy way to update, delete and recreate the `unit_test`
# Since it moves to fixture function below for testing
# Base.metadata.create_all(bind=engine)


# override `def get_db():` in `todos.py`
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# mock (not override) a function of `get_current_user`
def override_get_current_user():
    return {
        "username": "john",
        "id": 1,
        "role": "admin"
    }


# Then we want to connect our client to our `TestClient` with our `app` inside.
# Then, this `app` has now the replacement with overriden and mocked function
client = TestClient(app)


"""
    fixture. This fixture is something that happens before the function is called
"""


@pytest.fixture
def test_todo():
    db = TestingSessionLocal()

    # Dropping current database
    Base.metadata.drop_all(bind=engine)
    # For easy connection to database
    Base.metadata.create_all(bind=engine)

    user = Users(
        email="john@example.com",
        username="john",
        first_name="Test",
        last_name="User",
        hashed_password="hashedpassword",
        is_active=True,
        role="admin",
        id=1
    )

    db.add(user)
    # Must commit first than todo
    db.commit()

    todo = Todos(
        title="Learn the python",
        description="Need to watch and practice codes everyday",
        priority=4,
        complete=False,
        # user id which should be matches up with the `id` in `override_get_current_user`
        owner_id=1,
    )

    # We do not need to implement dependency injection here
    # So we can directly use `TestingSessionLocal`
    db.add(todo)
    db.commit()

    # return todo
    yield todo

    # [IMPORTANT]
    # engine.connect is from engine. In this case `engine.connect` is working
    # no matter what the session life cycle is.
    """
    Why Not Use `db` to Delete the todos?
    The reason the fixture doesn't use `db` to delete the todos is related to `database session lifecycle` and
    `isolation between tests`.

    Database Session Lifecycle:
    The `db` object (TestingSessionLocal()) is a SQLAlchemy session that is created during the setup phase 
    of the fixture.

    # [IMPORTANT]
    Once the fixture yields the todo object, the session (db) is no longer in use.
    If you try to use db in the teardown phase, it might not work as expected because the session
    could already be closed or in an invalid state.

    Isolation Between Tests:
    Using engine.connect() to delete all rows in the todos table ensures that the database is cleaned up completely, 
    regardless of the state of the db session.

    This approach guarantees that each test starts with a clean database, which is critical for test isolation.
    """
    with engine.connect() as connection:
        # delete all rows
        connection.execute(text("DELETE FROM todos;"))
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        email="john@example.com",
        username="john",
        first_name="Test",
        last_name="User",
        hashed_password=bcrypt_context.hash("hashpassword"),
        is_active=True,
        role="admin",
        phone_number="1-111-111-1111",
        id=1,
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()