from rest_framework import serializers

from apps.core.validators import is_blacklisted, validate_passwords
from apps.accounts.models import User

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=50, validators=[is_blacklisted])
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8, validators=[validate_passwords])
    password_confirm = serializers.CharField(required=True, write_only=True, min_length=8, validators=[validate_passwords])
    favorite_team = serializers.CharField(required=False, allow_null=True, default=None, max_length=100)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data