from rest_framework.exceptions import ValidationError

from .models import AuthUser


def validate_unique_phone(phone: str | None, user_id: int | None = None) -> str | None:
    if phone in ("", None):
        return phone

    qs = AuthUser.objects.filter(phone=phone)

    if user_id is not None:
        qs = qs.exclude(id=user_id)

    if qs.exists():
        raise ValidationError(
            "User with this phone already exists, use another phone number"
        )

    return phone
