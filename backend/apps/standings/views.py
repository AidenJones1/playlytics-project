from typing import cast

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers import SeasonWeekQuerySerializer
from apps.core.validators import validate_serializer
from apps.standings.models import TeamStandings
from apps.standings.querysets import TeamStandingsQuerySet
from apps.standings.services.rankings import rank_standings_queryset
from apps.standings.serializers import (
    StandingsSerializer, 
    LeagueStandingsQuerySerializer,
    ConferenceStandingsQuerySerializer, 
    DivisionStandingsQuerySerializer
)

class BaseStandingsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    query_serializer_class = SeasonWeekQuerySerializer
    ranking_scope = 'league'

    def apply_extra_filters(self, queryset, params):
        return queryset

    def apply_ranking(self, queryset):
        return rank_standings_queryset(queryset, scope=self.ranking_scope)

    def get_latest_snapshot_queryset(self, standings_qs):
        latest_snapshot = standings_qs.values_list(
            'week__season__year',
            'week__week',
        ).first()
        if not latest_snapshot:
            return standings_qs.none()

        season, week = latest_snapshot
        return standings_qs.by_season_week(season, week)

    def get_queryset(self):
        request = cast(Request, self.request)
        params = validate_serializer(self.query_serializer_class, request.query_params)
        standings_qs = cast(TeamStandingsQuerySet, TeamStandings.objects)
        queryset = standings_qs.by_season_week(params['season'], params['week'])

        # If defaults resolve to a season/week with no data, fallback to latest available.
        season_was_explicit = 'season' in request.query_params
        week_was_explicit = 'week' in request.query_params
        if not season_was_explicit and not week_was_explicit and not queryset.exists():
            queryset = self.get_latest_snapshot_queryset(standings_qs)

        queryset = self.apply_extra_filters(queryset, params)
        return self.apply_ranking(queryset)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = StandingsSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LeagueStandingsViewSet(BaseStandingsViewSet):
    # GET /standings/league-standings/
    query_serializer_class = LeagueStandingsQuerySerializer


class ConferenceStandingsViewSet(LeagueStandingsViewSet):
    # GET /standings/conference-standings/
    query_serializer_class = ConferenceStandingsQuerySerializer
    ranking_scope = 'conference'

    def apply_extra_filters(self, queryset, params):
        return queryset.by_conference(params['conference'])


class DivisionStandingsViewSet(LeagueStandingsViewSet):
    # GET /standings/division-standings/
    query_serializer_class = DivisionStandingsQuerySerializer
    ranking_scope = 'division'

    def apply_extra_filters(self, queryset, params):
        return queryset.by_division(params['division'])