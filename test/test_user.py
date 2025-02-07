from .utils import *
from ..routers.user import get_current_user, get_db
from fastapi import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_me(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    # Since we set up `test_user`
    user = response.json()
    assert user.get("id") == 1
    assert user.get("id") != 2
    assert user.get("firstname") != "John"


    # It is none because there is no fixture function
    # assert response.json() is None


def test_update_password(test_user):
    request_data = {
        "current_password": "hashpassword",
        "new_password": "testpassword"
    }

    response = client.patch("/user/password_update", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify(request_data.get("new_password"), model.hashed_password)


def test_update_password_invalid_password(test_user):
    request_data = {
        "current_password": "stranger",
        "new_password": "testpassword"
    }

    response = client.patch("/user/password_update", json=request_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == { "detail": "The current password is not identical" }


def test_phone_update_user(test_user):
    request_data = {
        "email": "john@example.com",
        "username": "john",
        "first_name": "Test",
        "last_name": "User",
        "password": bcrypt_context.hash("hashpassword"),
        "role": "admin",
        "phone_number": "2-222-222-2222",
    }

    response = client.put("/user/user_update", json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == request_data.get("phone_number")

