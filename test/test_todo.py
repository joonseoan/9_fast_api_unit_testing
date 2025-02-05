from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
import pytest

# Must use Base from 'database'
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from ..models import Todos, Users

# Set up test database for the endpoint testing

# Creates a new database url
SQLALCHEMY_DATABASE_URL = "postgresql://root:qwer123@localhost/unit_test"

# Creates a new engine with a new SQLALCHEMY_DATABASE_URL for database connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass = StaticPool,
)

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

"""
    [dependency_overrides]
    In FastAPI, `dependency_overrides` is a mechanism that allows  to override the dependencies used 
    in your application during runtime, typically for testing or debugging purposes.
    
    This feature is particularly useful when you want to replace a dependency with a mock or
    a different implementation without modifying the original code.

    How It Works
    Dependencies in FastAPI: FastAPI uses dependency injection to manage dependencies,
    such as database connections, authentication, or other services.
    These dependencies are often defined as functions or classes and injected into route handlers or other dependencies.

    Overriding Dependencies: The dependency_overrides attribute is a dictionary that maps the original dependency 
    (usually a function or class) to a new implementation.
    When you override a dependency, FastAPI will use the new implementation instead of the original one.

    Key Points
    Testing: dependency_overrides is commonly used in unit tests to replace real dependencies 
    (like databases or external APIs) with mock objects or stubs.

    Runtime Override: The overrides are applied at runtime, so you don’t need to modify the original code.

    Scope: The overrides are applied globally for the entire application, 
    so use them carefully to avoid unintended side effects.

    Resetting Overrides
    If you want to reset the overrides (e.g., after a test), you can clear the dependency_overrides dictionary:
    `app.dependency_overrides.clear()`
"""

# get `app` first from `FastAPI` and it has `dependency_overrides dictionary`
# Because it is dictionary, we can map with the function or class name, for instance `get_db`
app.dependency_overrides[get_db] = override_get_db


# [IMPORTANT]
# `get_current_user` is imported into todos.py and then we can directly import here.
# mocking dependency injection `user` in `todos.py`
app.dependency_overrides[get_current_user] = override_get_current_user


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
        title = "Learn the python",
        description = "Need to watch and practice codes everyday",
        priority = 4,
        complete = False,
        # user id which should be matches up with the `id` in `override_get_current_user`
        owner_id = 1,
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

def test_find_all_authenticated(test_todo):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    # Like javascript client
    # [IMPORTANT]
    """
        `==` vs `is`: While [] == [] is True, 
        [] is [] is False. 
        This is because `is` checks for identity (whether two objects are the same object in memory), not value equality.
        Two empty lists are distinct objects in memory, so is returns False.
    """
    # Just we know, python has the same reference [] == []
    print('response.json()',response.json())
    assert response.json() == [{
        'priority': 4,
        'description': 'Need to watch and practice codes everyday',
        'complete': False,
        'owner_id': 1,
        'title': 'Learn the python', 'id': 1}
    ]