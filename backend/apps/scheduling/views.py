from typing import cast

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.validators import validate_serializer
from apps.scheduling.models import Season, Week, Game
from apps.scheduling.querysets import GameQuerySet
from apps.scheduling import serializers

class WeeklyScheduleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(serializers.WeeklyScheduleQuerySerializer, request.query_params)

        game_qs = cast(GameQuerySet, Game.objects)
        queryset = game_qs.by_season_and_week(params['season'], params['week'])
        if 'division' in params:
            queryset = queryset.by_division_teams(params['division'])
        elif 'conference' in params:
            queryset = queryset.by_conference_teams(params['conference'])
        return queryset.order_by('game_time')
    
    # Retrieves the weekly schedule for a given season and week
    # GET /api/scheduling/weekly-schedule/
    def list(self, request):
        querysets = self.get_queryset()
        serializer = serializers.WeeklyScheduleSerializer(querysets, many=True)
        data = {}
        data["games"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

class TeamScheduleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(serializers.TeamScheduleQuerySerializer, request.query_params)

        game_qs = cast(GameQuerySet, Game.objects)
        queryset = game_qs.by_team_and_season(params['team'], params['season'])
        if 'division' in params:
            queryset = queryset.by_division_opponents(params['team'], params['division'])
        elif 'conference' in params:
            queryset = queryset.by_conference_opponents(params['team'], params['conference'])
        return queryset.order_by('game_time')

    # Retrieves the schedule for a given team and season.
    # GET /api/scheduling/team-schedule/
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.WeeklyScheduleSerializer(queryset, many=True)
        data = {}
        data["games"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

class GamePreviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
