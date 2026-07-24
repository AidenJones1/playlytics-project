from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.validators import validate_serializer
from apps.accounts.services import email, token
from apps.accounts import serializers as acc_sr
from apps.accounts.models import User

class UserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Register a new user
    # POST /api/accounts/register/
    def create(self, request, *args, **kwargs):
        data = validate_serializer(acc_sr.RegistrationSerializer, data=request.data)
        user_obj = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            favorite_team_id=data.get('favorite_team'),
            is_active=False
        )

        email.send_activation_email(user_obj)

        return Response(
            {"message": "User registered successfully. Please check your email to activate your account."},
            status=status.HTTP_201_CREATED
        )

class ActivationViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # GET /api/accounts/activate/<activation_token>/
    # Activate a user's account using the provided token.
    def retrieve(self, request, activation_token=None):
        user_pk = token.get_user_pk_from_token(activation_token)
        if not user_pk:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_obj = User.objects.get(pk=user_pk)
        if user_obj.is_active:
            return Response({"message": "Account is already activated."}, status=status.HTTP_200_OK)
        user_obj.is_active = True
        user_obj.save()

        return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)