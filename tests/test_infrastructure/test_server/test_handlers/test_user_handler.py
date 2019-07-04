from app.infrastructure.server.http.routes import USER_PATH

from app.infrastructure.server.http.handlers.handler_factory import _valid_query_params


def test_valid_query_params(user_http_adapter):
    user_usecase_class = user_http_adapter.usecase_class
    valid_params = _valid_query_params(user_usecase_class)
    assert valid_params == {
        "id",
        "username",
        "email",
        "created_at",
        "updated_at",
        "limit",
        "offset",
    }


# async def test_post_success(web_client, user_post):
#
#     # BASELINE
#     resp = await web_client.get(USER_PATH)
#     response_body = await resp.json()
#     baseline_size = len(response_body["data"])
#
#     # POST
#     resp = await web_client.post(PUBLIC_USER, json=user_post)
#     assert resp.status == 200
#     new_user = (await resp.json())["data"]
#     assert set(new_user) == key_set
#
#     # NEW USER INSERTED
#     resp = await web_client.get(PUBLIC_USER)
#     response_body = await resp.json()
#     assert len(response_body["data"]) == baseline_size + 1
