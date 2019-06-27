import marshmallow
import pytest

from app.usecases import User


def test_mapping_to_usecase_success(user_http_adapter, user_post):
    user = user_http_adapter.mapping_to_usecase(user_post)
    assert user == User(id=user.id, username="test", email="test@test.com")


def test_mapping_to_usecase_invalid_type(user_http_adapter, user_post):
    user_post["username"] = 1738
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.mapping_to_usecase(user_post)


def test_mapping_to_usecase_missing_field(user_http_adapter, user_post):
    del user_post["username"]
    with pytest.raises(marshmallow.exceptions.ValidationError):
        user_http_adapter.mapping_to_usecase(user_post)


def test_usecase_to_mapping_success(user_http_adapter):
    usecase = User(id="1", username="test", email="test@test.com")
    mapping = user_http_adapter.usecase_to_mapping(usecase)
    assert mapping == {
        "id": "1",
        "username": "test",
        "email": "test@test.com",
        "created_at": None,
        "updated_at": None,
    }
