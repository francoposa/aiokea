from aiokea.http.handlers import _valid_query_params
from tests.stubs.user.entity import stub_users


def test_valid_query_params(user_http_adapter):
    valid_params = _valid_query_params(user_http_adapter)
    assert valid_params == {
        "id",
        "username",
        "email",
        "is_enabled",
        "created_at",
        "updated_at",
        "page",
        "page_size",
    }


async def test_get_success(http_client):
    # GET baseline
    response = await http_client.get("/api/v1/users")
    response_body = await response.json()
    response_data = response_body["data"]
    assert response.status == 200
    assert len(response_data) == len(stub_users)


async def test_post_success(http_client, user_post):
    # GET baseline
    response = await http_client.get("/api/v1/users")
    response_body = await response.json()
    old_user_count = len(response_body["data"])

    # POST new user
    response = await http_client.post("/api/v1/users", json=user_post)
    assert response.status == 200
    response_body = await response.json()
    assert response_body["data"]["username"] == user_post["username"]
    assert response_body["data"]["email"] == user_post["email"]

    # Check new user was created
    response = await http_client.get("/api/v1/users")
    response_body = await response.json()
    assert len(response_body["data"]) == old_user_count + 1
