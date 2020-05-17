import marshmallow
import pytest

from tests.stubs.user.struct import User


def test_load_to_struct_success(user_http_adapter, user_post):
    user = user_http_adapter.load_to_struct(user_post)
    assert user == User(id=user.id, username="test", email="test@test.com")


def test_load_to_struct_invalid_type(user_http_adapter, user_post):
    user_post["username"] = 1738
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.load_to_struct(user_post)


def test_load_to_struct_missing_field(user_http_adapter, user_post):
    del user_post["username"]
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.load_to_struct(user_post)


def test_dump_from_struct_success(user_http_adapter):
    usecase = User(id="1", username="test", email="test@test.com")
    mapping = user_http_adapter.dump_from_struct(usecase)
    assert mapping == {
        "id": "1",
        "username": "test",
        "email": "test@test.com",
        "is_enabled": True,
        "created_at": None,
        "updated_at": None,
    }
