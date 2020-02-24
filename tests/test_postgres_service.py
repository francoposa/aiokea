from typing import List

import pytest

from aiokea.errors import DuplicateResourceError
from aiokea.filters import Filter, EQ, NE
from tests import pg_setup
from tests.stubs.users.struct import User


async def test_get(psql_db, psql_user_service):
    # Insert a user
    new_user = await psql_user_service.create(
        User(username="test", email="test@test.com")
    )

    # Assert we can retreive user by its id
    retreived_user = await psql_user_service.get(id=new_user.id)
    assert retreived_user == new_user


async def test_get_where(psql_db, psql_user_service):
    # Get baseline
    stub_count = len(pg_setup.stub_users)

    # Get all users by using no filters
    results: List[User] = await psql_user_service.get_where()
    assert len(results) == stub_count

    # Get all users as disjoint sets by using equal to and not equal to
    result_equal_to: List[User] = await psql_user_service.get_where(
        [Filter("username", EQ, "brian")]
    )
    result_not_equal_to: List[User] = await psql_user_service.get_where(
        [Filter("username", NE, "brian")]
    )

    # Assert the total equals the the sum of the two disjoint sets
    assert len(result_equal_to) + len(result_not_equal_to) == stub_count


async def test_get_first_where(psql_db, psql_user_service):
    # Get baseline of all users
    users: List[User] = await psql_user_service.get_where()

    # Use convenience method to get first user
    first_user: User = await psql_user_service.get_first_where()

    # Compare get_first_where user with first get_where user
    assert first_user == users[0]


async def test_insert(psql_db, psql_user_service):
    # Get baseline
    old_user_count = len(await psql_user_service.get_where())

    # Insert a user
    new_user = User(username="test", email="test@test.com")
    inserted_user = await psql_user_service.create(new_user)

    # Assert that the user took the id we generated within the app
    assert inserted_user.id == new_user.id

    # Assert we have one more user in the database
    new_user_count = len(await psql_user_service.get_where())
    assert new_user_count == old_user_count + 1


async def test_insert_duplicate_error(psql_db, psql_user_service):
    # Get baseline
    old_user_count = len(await psql_user_service.get_where())

    # Insert a user
    new_user = User(username="test", email="test@test.com")
    await psql_user_service.create(new_user)

    # Attempt to re-insert the same user
    with pytest.raises(DuplicateResourceError):
        await psql_user_service.create(new_user)

    # Check that only one user was created
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


async def test_partial_update(psql_db, psql_user_service):
    # Get an existing user
    roman: User = await psql_user_service.get_first_where(
        [Filter("username", EQ, "roman")]
    )
    # roman.username = "bigassforehead"
    # Update the user
    await psql_user_service.partial_update(roman.id, username="bigassforehead")

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
