from typing import cast

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.validators import validate_serializer
from apps.standings.models import TeamStandings
from apps.standings.querysets import TeamStandingsQuerySet
from apps.standings.serializers import (
    StandingsSerializer, 
    ConferenceStandingsQuerySerializer, 
    DivisionStandingsQuerySerializer
)

class BaseStandingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    query_serializer_class = SeasonWeekQuerySerializer
    default_ordering = (
        '-percentage',
        '-wins',
        '-point_differential',
        'team',
    )

    def apply_extra_filters(self, queryset, params):
        return queryset

    def apply_ranking(self, queryset):
        return queryset.order_by(*self.default_ordering)

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(self.query_serializer_class, request.query_params)
        standings_qs = cast(TeamStandingsQuerySet, TeamStandings.objects)
        queryset = standings_qs.by_season_week(params['season'], params['week'])
        queryset = self.apply_extra_filters(queryset, params)
        return self.apply_ranking(queryset)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = StandingsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeagueStandingsViewSet(BaseStandingsViewSet):
    # GET /standings/league-standings/
    pass


class ConferenceStandingsViewSet(LeagueStandingsViewSet):
    # GET /standings/conference-standings/
    query_serializer_class = ConferenceStandingsQuerySerializer

    def apply_extra_filters(self, queryset, params):
        return queryset.by_conference(params['conference'])


class DivisionStandingsViewSet(LeagueStandingsViewSet):
    # GET /standings/division-standings/
    query_serializer_class = DivisionStandingsQuerySerializer

    def apply_extra_filters(self, queryset, params):
        return queryset.by_division(params['division'])