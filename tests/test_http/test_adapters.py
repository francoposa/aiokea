import pytest

from aiokea.errors import ValidationError
from tests.stubs.user.entity import User


def test_load_to_entity_success(user_http_adapter, user_post):
    user = user_http_adapter.to_entity(user_post)
    assert user == User(id=user.id, username="test", email="test@test.com")


def test_load_to_entity_invalid_type(user_http_adapter, user_post):
    user_post["username"] = 1738
    with pytest.raises(ValidationError):
        user_http_adapter.to_entity(user_post)


def test_load_to_entity_missing_field(user_http_adapter, user_post):
    del user_post["username"]
    with pytest.raises(ValidationError):
        user_http_adapter.to_entity(user_post)


def test_dump_from_entity_success(user_http_adapter):
    usecase = User(id="1", username="test", email="test@test.com")
    mapping = user_http_adapter.from_entity(usecase)
    assert mapping == {
        "id": "1",
        "username": "test",
        "email": "test@test.com",
        "is_enabled": True,
        "created_at": None,
        "updated_at": None,
    }
