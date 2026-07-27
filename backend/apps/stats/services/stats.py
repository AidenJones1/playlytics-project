from typing import cast

from apps.stats.models import TeamGameStats
from apps.stats.querysets import TeamGameStatsQuerySet
from apps.stats.serializer import OffenseStatsSerializer, DefenseStatsSerializer, GameStatsSerializer

def get_game_stats_for_team(team, game):
    stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)
    game_stats = stats_qs.filter(game=game, team=team).first()
    return GameStatsSerializer(game_stats).data

def get_team_seasonal_stats(team, game,):
    stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)

    season_stats = stats_qs.by_season(game.week.season, regular_season_only=False)
    season_off_stats = season_stats.agg_team_seasonal_offense_stats(game=game, team=team)
    season_def_stats = season_stats.agg_team_seasonal_defense_stats(game=game, team=team)

    off_stats_serializer = OffenseStatsSerializer(season_off_stats).data
    def_stats_serializer = DefenseStatsSerializer(season_def_stats).data
    return {
        "offense": off_stats_serializer,
        "defense": def_stats_serializer,
    }

def get_team_rolling_stats(team, game, window):
    stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)

    rolling_off_stats = stats_qs.agg_team_rolling_offense_stats(team=team, game=game, window=window)
    rolling_def_stats = stats_qs.agg_team_rolling_defense_stats(team=team, game=game, window=window)

    off_stats_serializer = OffenseStatsSerializer(rolling_off_stats).data
    def_stats_serializer = DefenseStatsSerializer(rolling_def_stats).data
    return {
        "offense": off_stats_serializer,
        "defense": def_stats_serializer,
    }