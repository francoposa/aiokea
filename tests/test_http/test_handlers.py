from aiokea.http.handlers import _valid_query_params
from tests.stubs.user.struct import stub_users


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


async def test_get_success(http_client,):
    # GET baseline
    response = await http_client.get("/api/v1/user")
    response_body = await response.json()
    response_data = response_body["data"]
    assert response.status == 200
    assert len(response_data) == len(stub_users)
