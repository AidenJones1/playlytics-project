from typing import cast

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.validators import validate_serializer
from apps.models.mixins import ModelPerformance
from apps.scheduling.choices import GameStatus
from apps.scheduling.models import Game
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
        serializer = serializers.WeeklyScheduleSerializer(querysets, many=True, context={'request': request})
        perf = ModelPerformance()
        perf.context = {'request': request}
        data = {}
        data["model_performance"] = perf.get_model_performance(querysets)
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
        serializer = serializers.WeeklyScheduleSerializer(queryset, many=True, context={'request': request})
        perf = ModelPerformance()
        perf.context = {'request': request}
        data = {}
        data["model_performance"] = perf.get_model_performance(queryset)
        data["games"] = serializer.data
        return Response(data, status=status.HTTP_200_OK)


class GamePreviewViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    # Retrieves a preview of a specific game, including details about the teams and their previous games
    # GET /api/scheduling/game-preview/<game_id>/
    def retrieve(self, request, *args, **kwargs):
        game_obj = get_object_or_404(Game, pk=kwargs['game_id'])
        ctx = {'request': request}
        perf = ModelPerformance()
        perf.context = ctx
        data = {}
        data['model_performance'] = perf.get_model_performance(game_obj)
        if game_obj.status == GameStatus.COMPLETED:
            data['game'] = serializers.GameResultsSerializer(game_obj, context=ctx).data
        else:
            data['game'] = serializers.GamePreviewSerializer(game_obj, context=ctx).data

        return Response(data, status=status.HTTP_200_OK)