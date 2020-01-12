import marshmallow
import pytest

from app.entities.resources.user import User


def test_mapping_to_entity_success(user_http_adapter, user_post):
    user = user_http_adapter.mapping_to_entity(user_post)
    assert user == User(id=user.id, username="test", email="test@test.com")


def test_mapping_to_entity_invalid_type(user_http_adapter, user_post):
    user_post["username"] = 1738
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.mapping_to_entity(user_post)


def test_mapping_to_entity_missing_field(user_http_adapter, user_post):
    del user_post["username"]
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.mapping_to_entity(user_post)


def test_entity_to_mapping_success(user_http_adapter):
    entity = User(id="1", username="test", email="test@test.com")
    mapping = user_http_adapter.entity_to_mapping(entity)
    assert mapping == {
        "id": "1",
        "username": "test",
        "email": "test@test.com",
        "is_enabled": True,
        "created_at": None,
        "updated_at": None,
        "record_type": "user",
    }
