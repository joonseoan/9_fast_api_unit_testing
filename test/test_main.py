# We need to install `httpx` to test the endpoint like the client fetches the data
# from the endpoint

# It is just a simple way for us to be able to create a client for out app
from fastapi.testclient import TestClient
# [IMPORTANT]
# Must use the relative path here
# And the files we use for the `app`
from ..main import app
from fastapi import status

# Then we want to connect our client to our `TestClient` with our `app` inside.
# We can say client is equal to TestClient and pass in `app`.
client = TestClient(app)

def test_return_health_check():
    # get "/healthy" endpoint
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == { "status": "Healthy" }