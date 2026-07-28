from typing import cast

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.utils import dates
from apps.elo_ratings.querysets import TeamELORatingQuerySet
from apps.elo_ratings.models import TeamELORating
from apps.elo_ratings.serializers import TeamELORatingProgressionSerializer
from apps.scheduling.querysets import GameQuerySet
from apps.scheduling.models import Game
from apps.scheduling.serializers import WeeklyScheduleSerializer
from apps.stats.querysets import TeamGameStatsQuerySet
from apps.stats.models import TeamGameStats
from apps.teams.models import Team
from apps.teams.serializers import TeamDetailSerializer

class TeamViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # Retrieve a team by its abbreviation, along with its current season games, stats, and ELO rating progression.
    # GET /api/teams/<str:team_abbreviation>/
    def retrieve(self, request, *args, **kwargs):
        team = get_object_or_404(Team, abbreviation=kwargs['team_abbreviation'])

        game_qs = cast(GameQuerySet, Game.objects)
        game = game_qs.by_team_and_season(
            team_abbr=team.abbreviation, 
            season_year=dates.get_current_season_year()
        )

        elo_qs = cast(TeamELORatingQuerySet, TeamELORating.objects)
        elo_rating = elo_qs.by_team_season(
            team.abbreviation,
            season=dates.get_current_season_year()
        )

        stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)
        stats = stats_qs.by_season_and_team(
            team=team, 
            season=dates.get_current_season_year()
        ).agg_season_offense_stats()

        data = {}
        data["team_info"] = TeamDetailSerializer(team).data
        data["season_games"] = WeeklyScheduleSerializer(game, many=True).data
        data["season_stats"] = stats
        data["elo_rating_progression"] = TeamELORatingProgressionSerializer(elo_rating, many=True).data
        return Response(data, status=status.HTTP_200_OK)