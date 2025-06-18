import pytest
from rest_framework.exceptions import ValidationError

from ..models import AuthUser
from ..validators import validate_unique_phone


@pytest.mark.django_db
def test_validate_unique_phone_returns_empty_and_none() -> None:
    """
    Test that validate_unique_phone returns the same value
    when phone is empty string or None.
    """

    assert validate_unique_phone("") == ""
    assert validate_unique_phone(None) is None


@pytest.mark.django_db
def test_validate_unique_phone_allows_new_phone() -> None:
    """
    Test that validate_unique_phone returns the phone
    when it does not exist in the database.
    """

    phone = "+380633332211"
    assert validate_unique_phone(phone) == phone


@pytest.mark.django_db
def test_validate_unique_phone_raises_for_duplicate_phone(create_user) -> None:
    """
    Test that validate_unique_phone raises ValidationError
    if another user already has the same phone.
    """

    create_user(phone="+380633332211")
    with pytest.raises(ValidationError, match="User with this phone already exists"):
        validate_unique_phone("+380633332211")


@pytest.mark.django_db
def test_validate_unique_phone_allows_same_user(create_user) -> None:
    """
    Test that validate_unique_phone allows the same phone
    for the user identified by user_id.
    """
    user: AuthUser = create_user(phone="+380633332211")

    assert validate_unique_phone("+380633332211", user_id=user.id) == "+380633332211"
