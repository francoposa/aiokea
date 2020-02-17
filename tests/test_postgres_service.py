import pytest

from aiokea.errors import DuplicateResourceError
from aiokea.filters import Filter, EQ, NE
from tests import pg_setup
from tests.stubs.users.struct import User


async def test_get_where(psql_db, psql_user_service):
    stub_count = len(pg_setup.stub_users)
    # No filters
    results = await psql_user_service.get_where()
    assert len(results) == stub_count

    # Filters
    result_equal_to = await psql_user_service.get_where(
        [Filter("username", EQ, "brian")]
    )
    result_not_equal_to = await psql_user_service.get_where(
        [Filter("username", NE, "brian")]
    )
    assert len(result_equal_to) + len(result_not_equal_to) == stub_count


async def test_insert(psql_db, psql_user_service):
    old_user_count = len(await psql_user_service.get_where())

    new_user = User(username="test", email="test")
    inserted_user = await psql_user_service.create(new_user)
    assert inserted_user.id == new_user.id

    new_user_count = len(await psql_user_service.get_where())
    assert new_user_count == old_user_count + 1


async def test_insert_duplicate_error(psql_db, psql_user_service):
    old_user_count = len(await psql_user_service.get_where())

    new_user = User(username="test", email="test")
    await psql_user_service.create(new_user)
    with pytest.raises(DuplicateResourceError):
        await psql_user_service.create(new_user)

    new_user_count = len(await psql_user_service.get_where())
    assert new_user_count == old_user_count + 1


async def test_update(psql_db, psql_user_service):
    # Get an existing user
    roman: User = await psql_user_service.get_first_where(
        [Filter("username", EQ, "roman")]
    )
    roman.username = "bigassforehead"
    # Update the user
    await psql_user_service.update(roman)

    # Check that the user has been updated
    updated_roman: User = await psql_user_service.get_first_where(
        [Filter("id", EQ, roman.id)]
    )
    assert updated_roman.username == "bigassforehead"


async def test_update_where(psql_db, psql_user_service):
    # Get baseline
    user_count = len(await psql_user_service.get_where())
    old_disabled_user_count = len(
        await psql_user_service.get_where([Filter("is_enabled", EQ, False)])
    )
    assert old_disabled_user_count != user_count

    # Update users
    await psql_user_service.update_where(
        filters=[Filter("is_enabled", EQ, True)], is_enabled=False
    )

    # Check all users are now disabled
    new_disabled_user_count = len(
        await psql_user_service.get_where([Filter("is_enabled", EQ, False)])
    )
    assert new_disabled_user_count == user_count
