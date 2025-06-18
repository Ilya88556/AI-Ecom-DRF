from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q


class AuthUserManager(BaseUserManager):
    def create_user(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> AuthUser:
        if not email:
            raise ValueError("You can not register without an email address")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> AuthUser:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser should be is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser should be is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class AuthUser(AbstractUser):
    """Custom user model"""

    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=13, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_visited = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=False, db_index=True)

    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AuthUserManager()

    def __str__(self):
        return self.email

    class Meta:
        # Ensures the uniqueness of the phone field at the database level.
        constraints = [
            models.UniqueConstraint(
                fields=["phone"], condition=~Q(phone=""), name="unique_phone_not_empty"
            )
        ]
