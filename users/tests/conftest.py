from typing import Any, Callable, Dict, Generator

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from djoser.utils import encode_uid
from rest_framework.test import APIClient

from ..models import AuthUser


@pytest.fixture
def api_client() -> APIClient:
    """Api client fixture"""
    return APIClient()


@pytest.fixture
def create_user() -> Callable[..., AuthUser]:
    """Fixture for creating a new user"""

    def _create_user(
        email: str = "test@example.com",
        password: str = "securepassword123",
        **kwargs: Any
    ) -> AuthUser:
        user = AuthUser.objects.create_user(email=email, password=password, **kwargs)
        return user

    return _create_user


@pytest.fixture
def create_superuser(create_user: Callable[..., AuthUser]) -> Callable[..., AuthUser]:
    """Fixture for creating a new superuser"""

    def _create_superuser(
        email: str = "admin@example.com",
        password: str = "securepassword123",
        **kwargs: Any
    ) -> AuthUser:
        superuser = AuthUser.objects.create_superuser(
            email=email, password=password, **kwargs
        )
        return superuser

    return _create_superuser


@pytest.fixture
def activation_data() -> Callable[[AuthUser], Dict[str, str]]:
    def _activation_data(user: AuthUser) -> Dict[str, str]:
        uid = encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        return {"uid": uid, "token": token}

    return _activation_data


@pytest.fixture
def user_endpoints() -> Dict[str, str]:
    return {
        "register": "/api/v1/users/",
        "activation": "/api/v1/users/activation/",
        "login": "/api/v1/jwt/create/",
        "refresh": "/api/v1/jwt/refresh/",
        "password_reset": "/api/v1/users/reset_password/",
        "password_reset_confirm": "/api/v1/users/reset_password_confirm/",
    }


@pytest.fixture
def mail_outbox() -> Generator[list[mail.EmailMessage], None, None]:
    return mail.outbox
