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
    
    # GET /api/scheduling/weekly-schedule/
    # Retrieves the weekly schedule for a given season and week
    def list(self, request):
        querysets = self.get_queryset()
        serializer = serializers.WeeklyScheduleSerializer(querysets, many=True)
        data = {}
        data["games"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

class TeamScheduleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]


class GamePreviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
