from fastapi import status

# Because `app` is imported in utils so we do not need to import it
from ..main import app
from ..routers.todos import get_db, get_current_user
# Because `Todos` is imported in utils so we do not need to import it
from ..models import Todos
from .utils import *


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
        'title': 'Learn the python', 'id': 1
    }]


def test_find_one_authenticated(test_todo):
    # Need to param `/1`
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'priority': 4,
        'description': 'Need to watch and practice codes everyday',
        'complete': False,
        'owner_id': 1,
        'title': 'Learn the python', 'id': 1
    }


def test_find_one_authenticated_not_found(test_todo):
    # Need to param `/2`
    response = client.get("/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { "detail": "Todo not found" }


# CREATE
def test_create_todo(test_todo):
    request_data = {
        "title": "new todo",
        "description": "still pending this todo",
        "priority": 5,
        "complete": False,
    }

    # json=request_data is instead of `new_todo` in the endpoint
    response = client.post("/todo/create", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Even though there is not action after creating a todo in the endpoint
    # we can check further like
    db = TestingSessionLocal()
    # `id` should be 2 because `test_todo` already creates the first todo.
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo(test_todo):
    request_data = {
        "title": "Change the current todo 1",
        "description": "Want to change todo item with id 1",
        "priority": 2,
        "complete": False,
    }

    response = client.put("/todo/1", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert model.priority == request_data.get("priority")
    assert model.complete == request_data.get("complete")


def test_update_todo_not_found(test_todo):
    request_data = {
        "title": "Change the current todo 1",
        "description": "Want to change todo item with id 1",
        "priority": 2,
        "complete": False,
    }

    response = client.put("/todo/2", json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { "detail": "Todo not found" }


def test_delete_todo(test_todo):
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { "detail": "Todo not found" }