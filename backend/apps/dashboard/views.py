from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.utils import dates
from apps.dashboard.models import GameOfTheWeek
from apps.dashboard.serializers import GameOfTheWeekSerializer

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Retrieves the dashboard page data
    # GET /api/dashboard/game-of-the-week/
    def list(self, request, *args, **kwargs):
        season = dates.get_current_season_year()
        week = dates.get_current_week_number()

        game_of_the_week = get_object_or_404(GameOfTheWeek, week__season__year=season, week__week=week)
        data = {
            "game_of_the_week": GameOfTheWeekSerializer(game_of_the_week.game, context={'request': request}).data,
        }
        return Response(data, status=status.HTTP_200_OK)
