from typing import Any

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from .models import AuthUser
from .validators import validate_unique_phone


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user.

    Validates email for uniqueness and ensures password is write-only
    with length constraints. Uses AuthUser model's create_user method.
    """

    password = serializers.CharField(max_length=30, min_length=6, write_only=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=AuthUser.objects.all())]
    )
    phone = serializers.RegexField(
        regex=r"^\+380\d{9}$",
        required=False,
        allow_blank=True,
        error_messages={"invalid": "Use correct phone number: +380XXXXXXXXX"},
    )

    class Meta:
        model = AuthUser
        fields = ["email", "password", "phone"]

    def validate_phone(self, phone: str) -> str:
        return validate_unique_phone(phone)

    def create(self, validated_data: dict[str, Any]) -> AuthUser:
        try:
            return AuthUser.objects.create_user(**validated_data)
        except IntegrityError:
            raise ValidationError(
                {
                    "phone": "User with this phone already exists, use another phone number"
                }
            )


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating AuthUser data.
    Includes user ID, contact information, names, timestamps, and active status.
    """

    phone = serializers.RegexField(
        regex=r"^\+380\d{9}$",
        required=False,
        allow_blank=True,
        error_messages={
            "invalid": "The phone number should be in format: +380XXXXXXXXX (9 digits)."
        },
    )

    class Meta:
        model = AuthUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "city",
            "phone",
            "time_created",
            "last_visited",
            "is_active",
        ]

    def validate_phone(self, phone: str) -> str:
        return validate_unique_phone(phone, user_id=self.instance.id)

    def update(self, instance: AuthUser, validated_data: dict[str, Any]) -> AuthUser:
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise ValidationError(
                {
                    "phone": "User with this phone already exists, use another phone number"
                }
            )
