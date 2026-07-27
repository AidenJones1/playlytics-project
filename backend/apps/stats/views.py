from typing import cast

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from apps.core.validators import validate_serializer
from apps.stats.models import TeamGameStats
from apps.stats.querysets import TeamGameStatsQuerySet
from apps.stats.serializer import SeasonStatsQuerySerializer

class SeasonStatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(SeasonStatsQuerySerializer, request.query_params)

        stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)
        if params['side'] == 'offense':
            queryset = stats_qs.by_season(params['season']).agg_season_offense_stats()
        else:
            queryset = stats_qs.by_season(params['season']).agg_season_defense_stats()
        return queryset

    # GET /api/season-stats/
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response(queryset, status=status.HTTP_200_OK)