from typing import cast

from django.db.models import Q

from apps.stats.querysets import TeamGameStatsQuerySet
from apps.stats.models import TeamGameStats

def aggregate_team_stats(team, game_objs):
    """Aggregate team stats for a given team and a list of game objects."""
    stats_qs = cast(TeamGameStatsQuerySet, TeamGameStats.objects)
    offense_stats = (
        stats_qs.filter(team=team, game__in=game_objs)
        .agg_season_offense_stats()
    )
    defense_stats = (
        stats_qs.filter(game__in=game_objs)
        .filter(~Q(team=team))
        .agg_season_defense_stats()
    )
    return offense_stats, defense_stats