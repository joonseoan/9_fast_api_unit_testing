from fastapi import HTTPException
from datetime import timedelta, datetime, timezone
from jose import jwt


from .utils import *
from ..routers.auth import get_db, authenticate_user, create_access_token, ALGORITHM, SECRET_KEY, get_current_user


app.dependency_overrides[get_db] = override_get_db


# [IMPORTANT]
# We can test a common function! without mock
# It is not the endpoint though.
def test_authenticate_user(test_user):
    # To be used as a variable instead of `get_db`
    db = TestingSessionLocal()

    _authenticate_user = authenticate_user(username=test_user.username, password="hashpassword", db=db)
    assert _authenticate_user is not False
    assert _authenticate_user.username == test_user.username

    wrong_username_user = authenticate_user(username="wrong_name", password="hashpassword", db=db)
    assert wrong_username_user is False

    wrong_password_user = authenticate_user(username=test_user.username, password="wrongpassword", db=db)
    assert wrong_password_user is False


def test_create_access_token(test_user):
    _token = create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        role=test_user.role,
        expires_delta=timedelta(minutes=20)
    )

    assert _token is not None

    user = jwt.decode(_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert user.get("id") == test_user.id
    assert user.get("sub") == test_user.username
    assert user.get("role") == test_user.role


# [IMPORTANT]
# Pytest cannot test synchronous functionality. Can't test asynchronous functionality
# Need to install `pip install pytest-asyncio` to test async function
# And, add annotation here
@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {"sub": test_user.username, "id": test_user.id, "role": test_user.role}
    expires = datetime.now(timezone.utc) + timedelta(minutes=20)
    # [IMPORTANT]
    encode.update({"exp": expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # [IMPORTANT]!!!
    # We need to use await in python!!!
    user = await get_current_user(token=token)
    assert user["id"] == test_user.id
    assert user["role"] == test_user.role
    assert user["username"] == test_user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid(test_user):
    encode = {"role": test_user.role}
    # expires = datetime.now(timezone.utc) + timedelta(minutes=20)
    # encode.update({"exp": expires})
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    # [IMPORTANT]
    with pytest.raises(HTTPException) as excinfig:
        await get_current_user(token=token)
        assert excinfig.value.status_code == 401
        assert excinfig.value.detail == "Could not validate the user"