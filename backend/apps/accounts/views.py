from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.core.validators import validate_serializer
from apps.accounts import serializers as acc_sr
from apps.accounts.models import User
from apps.accounts.permissions import IsOwner
from apps.accounts.services import email, token

class UserViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwner]
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

    # Retrieve user details. If the requesting user is the owner, return private details; otherwise, return public details.
    # GET /api/accounts/user/<username>/
    def retrieve(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, username=kwargs['username'])
        is_owner = request.user == user_obj
        if is_owner:
            serializer = acc_sr.PrivateAccountSerializer(user_obj)
        else:
            serializer = acc_sr.PublicAccountSerializer(user_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Update user details (only allowed for the owner)
    # PATCH /api/accounts/user/<username>/
    def partial_update(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, username=kwargs['username'])
        self.check_object_permissions(request, user_obj)
        data = validate_serializer(
            acc_sr.AccountUpdateSerializer, 
            request.data,
            context={'request': request}
        )
        
        if 'username' in data:
            user_obj.username = data['username']
        if 'favorite_team' in data:
            favorite_team_abbreviation = data['favorite_team']
            setattr(user_obj, 'favorite_team_id', favorite_team_abbreviation or None)
        if 'password' in data:
            user_obj.set_password(data['password'])
        user_obj.save()
        serializer = acc_sr.PrivateAccountSerializer(user_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Delete user account (only allowed for the owner)
    # DELETE /api/accounts/user/<username>/
    def destroy(self, request, *args, **kwargs):
        user_obj = get_object_or_404(User, username=kwargs['username'])
        self.check_object_permissions(request, user_obj)
        user_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ActivationViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # Activate a user's account using the provided token.
    # GET /api/accounts/activate/<activation_token>/
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