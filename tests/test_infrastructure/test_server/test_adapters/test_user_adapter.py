from app.usecases import User


def test_mapping_to_usecase_success(user_http_adapter, user_post):
    user = user_http_adapter.mapping_to_usecase(user_post)
    assert user == User(id=user.id, username="test", email="test@test.com")
