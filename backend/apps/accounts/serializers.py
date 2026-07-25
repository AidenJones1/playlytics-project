from rest_framework import serializers

from apps.core import validators as v
from apps.accounts.models import User

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=50, validators=[v.is_blacklisted])
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8, validators=[v.validate_passwords])
    password_confirm = serializers.CharField(required=True, write_only=True, min_length=8, validators=[v.validate_passwords])
    favorite_team = serializers.CharField(required=False, allow_null=True, default=None, max_length=100)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_favorite_team(self, value):
        if value is not None:
            v.does_team_exist(value)
        return value

    def validate(self, data):
        v.does_passwords_match(data['password'], data['password_confirm'])
        return data


class AccountUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, max_length=50, validators=[v.is_blacklisted])
    favorite_team = serializers.CharField(required=False, max_length=100)
    password = serializers.CharField(required=False, write_only=True, min_length=8, validators=[v.validate_passwords])
    password_confirm = serializers.CharField(required=False, write_only=True, min_length=8, validators=[v.validate_passwords])

    def validate_username(self, value):
        request = self.context.get('request')
        user_id = request.user.id if request else None
        if User.objects.filter(username=value).exclude(id=user_id).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value
    
    def validate_favorite_team(self, value):
        if value is not None:
            v.does_team_exist(value)
        return value    
    
    def validate(self, data):
        if 'password' in data:
            if 'password_confirm' not in data:
                raise serializers.ValidationError("Password confirmation is required.")
            v.does_passwords_match(data['password'], data['password_confirm'])
        return data


class PublicAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'favorite_team',
            'is_staff',
            'date_joined'
        ]


class PrivateAccountSerializer(PublicAccountSerializer):
    class Meta(PublicAccountSerializer.Meta):
        fields = (
            PublicAccountSerializer.Meta.fields + [
                'email'
            ]
        )


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)


class ResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8, validators=[v.validate_passwords])
    password_confirm = serializers.CharField(required=True, write_only=True, min_length=8, validators=[v.validate_passwords])

    def validate(self, data):
        v.does_passwords_match(data['password'], data['password_confirm'])
        return data