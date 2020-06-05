from typing import Optional, List

import pytest

from aiokea.errors import DuplicateResourceError, ResourceNotFoundError
from aiokea.filters import Filter, EQ, NE
from tests.stubs.user.struct import User, stub_users


async def test_get(aiopg_db, aiopg_user_repo):
    # Insert a user
    new_user = await aiopg_user_repo.create(
        User(username="test", email="test@test.com")
    )

    # Assert we can retrieve user by its id
    retrieved_user = await aiopg_user_repo.get(id=new_user.id)
    assert retrieved_user == new_user


async def test_get_not_found(aiopg_db, aiopg_user_repo):
    # Attempt to retrieve user by nonexistent ID
    with pytest.raises(ResourceNotFoundError):
        _ = await aiopg_user_repo.get(id="xxx")


async def test_get_where(aiopg_db, aiopg_user_repo):
    # Get baseline
    stub_count = len(stub_users)

    # Get all user by using no filters
    results: List[User] = await aiopg_user_repo.get_where()
    assert len(results) == stub_count

    # Get all user as disjoint sets by using equal to and not equal to
    result_equal_to: List[User] = await aiopg_user_repo.get_where(
        [Filter("username", EQ, "brian")]
    )
    result_not_equal_to: List[User] = await aiopg_user_repo.get_where(
        [Filter("username", NE, "brian")]
    )

    # Assert the total equals the the sum of the two disjoint sets
    assert len(result_equal_to) + len(result_not_equal_to) == stub_count


async def test_get_first_where(aiopg_db, aiopg_user_repo):
    # Get baseline of all user
    users: List[User] = await aiopg_user_repo.get_where()

    # Use convenience method to get first user
    first_user: User = await aiopg_user_repo.get_first_where()

    # Compare get_first_where user with first get_where user
    assert first_user == users[0]


async def test_get_first_where_no_results(aiopg_db, aiopg_user_repo):
    # Attempt to retrieve user by nonexistent ID
    user: Optional[User] = await aiopg_user_repo.get_first_where(
        filters=[Filter("id", EQ, "xxx")]
    )

    # Assert None was returned
    assert user is None


async def test_insert(aiopg_db, aiopg_user_repo):
    # Get baseline
    old_user_count = len(stub_users)

    # Insert a user
    new_user = User(username="test", email="test@test.com")
    inserted_user = await aiopg_user_repo.create(new_user)

    # Assert that the user took the id we generated within the app
    assert inserted_user.id == new_user.id

    # Assert we have one more user in the repo
    new_user_count = len(await aiopg_user_repo.get_where())
    assert new_user_count == old_user_count + 1


async def test_create_duplicate_error(aiopg_db, aiopg_user_repo):
    # Get baseline
    old_user_count = len(await aiopg_user_repo.get_where())

    # Create a user
    new_user = User(username="test", email="test@test.com")
    await aiopg_user_repo.create(new_user)

    # Attempt to re-create the same user
    with pytest.raises(DuplicateResourceError):
        await aiopg_user_repo.create(new_user)

    # Check that only one user was created
    new_user_count = len(await aiopg_user_repo.get_where())
    assert new_user_count == old_user_count + 1


async def test_update(aiopg_db, aiopg_user_repo):
    # Get an existing user
    roman: User = await aiopg_user_repo.get_first_where(
        [Filter("username", EQ, "roman")]
    )
    roman.username = "bigassforehead"
    # Update the user
    await aiopg_user_repo.update(roman)

    # Check that the user has been updated
    updated_roman: User = await aiopg_user_repo.get_first_where(
        [Filter("id", EQ, roman.id)]
    )
    assert updated_roman.username == "bigassforehead"


async def test_delete(aiopg_db, aiopg_user_repo):
    # Get baseline
    old_users: List[User] = await aiopg_user_repo.get_where()
    old_user_count = len(await aiopg_user_repo.get_where())

    # Delete a user
    first_old_user = old_users[0]
    deleted_user = await aiopg_user_repo.delete(id=first_old_user.id)

    # Assert that delete returned the deleted user
    assert deleted_user == first_old_user

    # Assert the deleted user is not available from the repo
    new_users: List[User] = await aiopg_user_repo.get_where()
    assert deleted_user not in new_users

    # Assert we have one fewer user in the repo
    new_user_count = len(new_users)
    assert new_user_count == old_user_count - 1


async def test_delete_not_found(aiopg_db, aiopg_user_repo):
    # Attempt to delete user by nonexistent ID
    with pytest.raises(ResourceNotFoundError):
        _ = await aiopg_user_repo.delete(id="xxx")
