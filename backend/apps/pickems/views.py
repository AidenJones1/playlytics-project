from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.validators import validate_serializer
from apps.pickems import permissions
from apps.pickems import serializers as pickems_serializers
from apps.pickems import models as pickems_models
from apps.pickems import choices as pickems_choices
from apps.pickems import paginations as pickems_paginations
from apps.pickems.services.leaderboards import (
    parse_season_years,
    INVALID_SEASON_ERROR_MESSAGE,
    build_global_leaderboard,
    build_group_leaderboard,
    build_requested_user_groups,
    build_requested_user_rank,
)
from apps.teams.models import Team

class PickemGroupViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ["destroy"]:
            permission_classes = [IsAuthenticated, permissions.IsPickemGroupOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Create new pickem group
    # POST /api/pickems/groups/
    def create(self, request, *args, **kwargs):
        data = validate_serializer(pickems_serializers.PickemsGroupCreateSerializer, request.data)
        group_obj = pickems_models.PickemGroup.objects.create(
            name=data["name"],
            is_private=data["is_private"],
            max_members=data["max_members"]
        )
        pickems_models.PickemGroupMember.objects.create(
            group=group_obj,
            user=request.user,
            role=pickems_choices.GroupRole.OWNER
        )
        return Response(
            {"message": "Pickems group created successfully."},
            status=status.HTTP_201_CREATED
        )

    # List all pickem groups the user is a member of
    # GET /api/pickems/groups/
    def list(self, request, *args, **kwargs):
        memberships = pickems_models.PickemGroupMember.objects.filter(user=request.user)
        groups = [membership.group for membership in memberships]
        serializer = pickems_serializers.PickemsGroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Delete a pickem group (only the owner can delete)
    # DELETE /api/pickems/groups/<group_key>/
    def destroy(self, request, *args, **kwargs):
        group_key = kwargs.get("group_key")
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=group_key)
        self.check_object_permissions(request, group_obj)
        group_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PickemsGroupMemberViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ["list", "destroy"]:
            permission_classes = [IsAuthenticated, permissions.IsPickemGroupMember]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # POST /api/pickems/join-group/
    # Join a pickem group using group key and optional invite code
    def create(self, request, *args, **kwargs):
        data = validate_serializer(pickems_serializers.PickemsGroupJoinSerializer, request.data)
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=data["group_key"])
        membership_count = pickems_models.PickemGroupMember.objects.filter(group=group_obj).count()

        if group_obj.is_private and group_obj.invite_code != data.get('invite_code'):
            return Response({"error": "Invalid invite code for private group."}, status=status.HTTP_400_BAD_REQUEST)
        if membership_count >= group_obj.max_members:
            return Response({"error": "Group is full."}, status=status.HTTP_400_BAD_REQUEST)
        if pickems_models.PickemGroupMember.objects.filter(group=group_obj, user=request.user).exists():
            return Response({"error": "You are already a member of this group."}, status=status.HTTP_400_BAD_REQUEST)

        pickems_models.PickemGroupMember.objects.create(
            group=group_obj,
            user=request.user,
            role=pickems_choices.GroupRole.MEMBER
        )

        return Response(
            {"message": "Joined pickems group successfully."},
            status=status.HTTP_201_CREATED
        )

    # GET /api/pickems/groups/<group_key>/members/
    # List all members of a pickem group
    def list(self, request, *args, **kwargs):
        group_key = kwargs.get("group_key")
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=group_key)
        self.check_object_permissions(request, group_obj)
        memberships = pickems_models.PickemGroupMember.objects.filter(group=group_obj)
        serializer = pickems_serializers.PickemsGroupMembershipSerializer(memberships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Endpoint: DELETE /api/pickems/groups/{group_key}/members/
    # Description: Leave a group (only if the authenticated user is a member)
    def destroy(self, request, *args, **kwargs):
        group_key = kwargs.get("group_key")
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=group_key)
        self.check_object_permissions(request, group_obj)

        membership = pickems_models.PickemGroupMember.objects.filter(group=group_obj, user=request.user).first()
        if not membership:
            return Response({"error": "You are not a member of this group."}, status=status.HTTP_400_BAD_REQUEST)
        if membership.role == pickems_choices.GroupRole.OWNER:
            return Response({"error": "Group owner cannot leave the group. Please delete the group or transfer ownership."}, status=status.HTTP_400_BAD_REQUEST)

        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PickemGroupOwnerViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, permissions.IsPickemGroupOwner]

    # Endpoint: PUT /api/pickems/groups/{group_key}/owner/
    # Description: Transfer group ownership to another member (only if the authenticated user is the current owner)
    def update(self, request, *args, **kwargs):
        data = validate_serializer(pickems_serializers.PickemsGroupOwnerSerializer, request.data)
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=kwargs['group_key'])
        self.check_object_permissions(request, group_obj)

        new_owner = get_object_or_404(pickems_models.PickemGroupMember, group=group_obj, user__username=data['user'])
        current_owner = pickems_models.PickemGroupMember.objects.get(group=group_obj, role=pickems_choices.GroupRole.OWNER)
        current_owner.role = pickems_choices.GroupRole.MEMBER
        current_owner.save()
        new_owner.role = pickems_choices.GroupRole.OWNER
        new_owner.save()

        return Response(
            {"message": "Group ownership transferred successfully."},
            status=status.HTTP_200_OK
        )

    # Endpoint: DELETE /api/pickems/groups/{group_key}/remove-member/
    # Description: Remove a member from the group (only if the authenticated user is the owner)
    def destroy(self, request, *args, **kwargs):
        data = validate_serializer(pickems_serializers.PickemsGroupOwnerSerializer, request.data)
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=kwargs['group_key'])
        self.check_object_permissions(request, group_obj)

        member_to_remove = get_object_or_404(pickems_models.PickemGroupMember, group=group_obj, user__username=data['user'])
        if member_to_remove.role == pickems_choices.GroupRole.OWNER:
            return Response({"error": "Cannot remove the group owner."}, status=status.HTTP_400_BAD_REQUEST)

        member_to_remove.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserPickViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Endpoint: POST /api/pickems/user-picks/<game_id>/
    # Description: Submit the authenticated user's pick for a specific game
    def create(self, request, *args, **kwargs):
        data = validate_serializer(
            pickems_serializers.UserPickSubmissionSerializer,
            request.data,
            context={'user': request.user, 'game_id': kwargs.get('game_id')}
        )
        team = Team.objects.filter(abbreviation=data['team']).first()
        game_pickem = pickems_models.GamePickem.objects.filter(game_id=kwargs['game_id']).first()
        pickems_models.UserPick.objects.create(
            pickem=game_pickem,
            user=request.user,
            team=team
        )
        return Response(
            {"message": "User pick created successfully."},
            status=status.HTTP_201_CREATED
        )

class GroupPickemLeaderboardViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, permissions.IsPickemGroupMember]
    pagination_class = pickems_paginations.PickemLeaderboardPagination

    # GET /api/pickems/groups/{group_key}/leaderboard/
    # Description: Get the leaderboard for a specific pickem group
    def list(self, request, *args, **kwargs):
        try:
            season_years = parse_season_years(request.query_params)
        except ValueError:
            return Response(
                {"error": INVALID_SEASON_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )

        group_key = self.kwargs["group_key"]
        group_obj = get_object_or_404(pickems_models.PickemGroup, group_key=group_key)
        self.check_object_permissions(request, group_obj)

        leaderboard = build_group_leaderboard(group_obj, season_years=season_years)
        requested_user_rank = build_requested_user_rank(leaderboard, request.user.username)
        requested_user_groups = build_requested_user_groups(request.user)
        paginated_leaderboard = self.paginate_queryset(leaderboard)
        if paginated_leaderboard is not None:
            response = self.get_paginated_response(paginated_leaderboard)
            response.data["requested_user_rank"] = requested_user_rank
            response.data["requested_user_groups"] = requested_user_groups
            return response

        return Response(
            {
                "count": len(leaderboard),
                "requested_user_rank": requested_user_rank,
                "requested_user_groups": requested_user_groups,
                "results": leaderboard,
            },
            status=status.HTTP_200_OK,
        )

class GlobalPickemLeaderboardViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = pickems_paginations.PickemLeaderboardPagination

    # GET /api/pickems/leaderboard/
    # Description: Get the global leaderboard across all users
    def list(self, request, *args, **kwargs):
        try:
            season_years = parse_season_years(request.query_params)
        except ValueError:
            return Response(
                {"error": INVALID_SEASON_ERROR_MESSAGE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        leaderboard = build_global_leaderboard(season_years=season_years)
        requested_user_rank = build_requested_user_rank(leaderboard, request.user.username)
        paginated_leaderboard = self.paginate_queryset(leaderboard)
        if paginated_leaderboard is not None:
            response = self.get_paginated_response(paginated_leaderboard)
            response.data["requested_user_rank"] = requested_user_rank
            return response

        return Response(
            {
                "count": len(leaderboard),
                "requested_user_rank": requested_user_rank,
                "results": leaderboard,
            },
            status=status.HTTP_200_OK,
        )