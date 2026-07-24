import re

from rest_framework.serializers import ValidationError

from apps.core.blacklist import BLACKLIST_WORDS

def validate_serializer(serializer_class, data, **kwargs) -> dict:
    serializer = serializer_class(data=data, **kwargs)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data

def is_blacklisted(value: str) -> bool:
    normalized_value = value.lower()
    normalized_blacklist = (word.lower().replace('*', '') for word in BLACKLIST_WORDS)
    return any(word and word in normalized_value for word in normalized_blacklist)

def validate_passwords(value):
    # Must be at least 8 characters
    if len(value) < 8:
        raise ValidationError(
            "Password must be at least 8 characters long."
        )
    # Must only contain ASCII characters
    if not value.isascii():
        raise ValidationError(
            "Password must only contain ASCII characters."
        )
    # Must contain an uppercase letter
    if not re.search(r"[A-Z]", value):
        raise ValidationError(
            "Password must contain at least one uppercase letter."
        )
    # Must contain a number
    if not re.search(r"[0-9]", value):
        raise ValidationError("Password must contain at least one number.")
    # Must contain a special character
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValidationError(
            "Password must contain at least one special character."
        )
    return value