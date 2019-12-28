from app.infrastructure.server.http.routes import USER_PATH

from app.infrastructure.server.http.handlers.handler_factory import _valid_query_params


def test_valid_query_params(user_http_adapter):
    user_usecase_class = user_http_adapter.usecase_class
    valid_params = _valid_query_params(user_usecase_class)
    assert valid_params == {
        "id",
        "username",
        "email",
        "is_enabled",
        "created_at",
        "updated_at",
        "limit",
        "offset",
    }


async def test_post_success(http_client, user_post):
    # GET baseline
    response = await http_client.get(USER_PATH)
    response_body = await response.json()
    old_user_count = len(response_body["data"])

    # POST new user
    response = await http_client.post(USER_PATH, json=user_post)
    assert response.status == 200
    response_body = await response.json()
    assert response_body["data"]["username"] == user_post["username"]
    assert response_body["data"]["email"] == user_post["email"]

    # Check new user was created
    response = await http_client.get(USER_PATH)
    response_body = await response.json()
    assert len(response_body["data"]) == old_user_count + 1
