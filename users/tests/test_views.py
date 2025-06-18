import logging
from typing import Callable, Dict, List

import pytest
from django.core.mail import EmailMessage
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.test import APIClient

from users.models import AuthUser

logger = logging.getLogger("project")


@pytest.mark.django_db
def test_user_registration(
    api_client: APIClient,
    user_endpoints: Dict[str, str],
    mail_outbox: List[EmailMessage],
) -> None:
    """Test user registration and email sending."""

    data: Dict[str, str] = {
        "email": "newuser@example.com",
        "password": "securepassword123",
    }

    response = api_client.post(user_endpoints["register"], data, format="json")

    assert response.status_code == HTTP_201_CREATED

    assert len(mail_outbox) == 1
    email = mail_outbox[0]
    assert "newuser@example.com" in email.to
    assert "activation" in email.subject

    user = AuthUser.objects.get(email="newuser@example.com")
    assert user.email == "newuser@example.com"
    assert user.check_password("securepassword123")
    assert not user.is_active


@pytest.mark.django_db
def test_user_activation(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    activation_data: Callable[[AuthUser], Dict[str, str]],
    user_endpoints: Dict[str, str],
) -> None:
    """Test user activation via the activation endpoint."""

    user = create_user(email="activation_user@example.com")
    activation_info = activation_data(user)

    response = api_client.post(
        user_endpoints["activation"], activation_info, format="json"
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_login_with_jwt(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    user_endpoints: Dict[str, str],
) -> None:
    """Test user login with jwt authentication"""

    user = create_user(email="login_user@example.com", password="securepassword123")
    user.is_active = True
    user.save()
    user.refresh_from_db()

    data: Dict[str, str] = {
        "email": user.email,
        "password": "securepassword123",
    }

    response = api_client.post(user_endpoints["login"], data, format="json")

    assert response.status_code == HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_with_inactive_user(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    user_endpoints: Dict[str, str],
) -> None:
    """Test user login with inactive user"""

    user = create_user(email="inactive_user@example.com", password="securepassword123")
    user.save()
    user.refresh_from_db()

    data: Dict[str, str] = {
        "email": user.email,
        "password": "securepassword123",
    }

    response = api_client.post(user_endpoints["login"], data, format="json")

    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert (
        "No active account found with the given credentials" in response.data["detail"]
    )


@pytest.mark.django_db
def test_password_reset_request(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    user_endpoints: Dict[str, str],
    mail_outbox: List[EmailMessage],
) -> None:
    """Test password reset request"""

    user = create_user(email="resetuser@example.com", password="securepassword123")
    user.is_active = True
    user.save()
    user.refresh_from_db()

    data: Dict[str, str] = {"email": user.email}

    response = api_client.post(user_endpoints["password_reset"], data, format="json")

    assert response.status_code == HTTP_204_NO_CONTENT

    assert len(mail_outbox) == 1
    email = mail_outbox[0]
    assert "resetuser@example.com" in email.to
    assert "Password reset" in email.subject


@pytest.mark.django_db
def test_password_reset_confirmation(
    api_client: APIClient,
    create_user: Callable[..., AuthUser],
    user_endpoints: Dict[str, str],
    activation_data: Callable[[AuthUser], Dict[str, str]],
) -> None:
    """Test password reset confirmation"""

    user = create_user(
        "password_confirmation@example.com", password="securepassword123"
    )
    user.is_active = True
    user.save()
    user.refresh_from_db()

    reset_data = activation_data(user)
    reset_data["new_password"] = "newsecurepassword456"

    response = api_client.post(
        user_endpoints["password_reset_confirm"], reset_data, format="json"
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    user.refresh_from_db()

    assert user.check_password("newsecurepassword456")
