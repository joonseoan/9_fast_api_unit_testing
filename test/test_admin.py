from fastapi import status
from .utils import *
from ..routers.admin import get_db, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_find_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'priority': 4,
        'description': 'Need to watch and practice codes everyday',
        'complete': False,
        'owner_id': 1,
        'title': 'Learn the python', 'id': 1
    }]


def test_admin_delete_todo_authenticated(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_authenticated_not_found(test_todo):
    response = client.delete("/admin/todo/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == { "detail": "Unable to find the todo" }

