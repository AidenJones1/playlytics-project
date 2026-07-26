from typing import cast

from django.db.models import Case, IntegerField, Value, When

from apps.teams.models import Team
from apps.scheduling.models import Game
from apps.standings.models import TeamStandings
from apps.standings.querysets import TeamStandingsQuerySet
from apps.standings.services.tie_breakers import (
    apply_conference_tiebreakers,
    apply_division_tiebreakers,
)


def _default_ranked_team_ids(queryset):
    """Return team ids ordered by the current placeholder ranking rules."""
    return list(queryset.apply_default_ordering().values_list('team', flat=True))


def _conference_ranked_team_ids(queryset):
    """Return conference-ranked team ids using placeholder tie-breakers."""
    return apply_conference_tiebreakers(queryset)


def _division_ranked_team_ids(queryset):
    """Return division-ranked team ids using placeholder tie-breakers."""
    return apply_division_tiebreakers(queryset)


def _rank_from_team_ids(ranked_team_ids, team_obj):
    try:
        return ranked_team_ids.index(team_obj.pk) + 1
    except ValueError:
        return None


def _get_ranked_team_ids_by_scope(standings, scope):
    if scope == 'league':
        return _default_ranked_team_ids(standings)
    if scope == 'conference':
        return _conference_ranked_team_ids(standings)
    if scope == 'division':
        return _division_ranked_team_ids(standings)
    raise ValueError(f"Unsupported ranking scope: {scope}")


def rank_standings_queryset(standings, scope='league'):
    """Return standings queryset ordered by the scope-specific ranking strategy."""
    ranked_team_ids = _get_ranked_team_ids_by_scope(standings, scope)
    if not ranked_team_ids:
        return standings.none()

    rank_order = Case(
        *[
            When(team_id=team_id, then=Value(index))
            for index, team_id in enumerate(ranked_team_ids)
        ],
        output_field=IntegerField(),
    )

    return standings.filter(team_id__in=ranked_team_ids).order_by(rank_order)


def _get_league_rank(standings, team_obj):
    ranked_team_ids = _default_ranked_team_ids(standings)
    return _rank_from_team_ids(ranked_team_ids, team_obj)


def _get_conference_rank(standings, team_obj):
    conference_standings = standings.by_conference(team_obj.conference)
    ranked_team_ids = _conference_ranked_team_ids(conference_standings)
    return _rank_from_team_ids(ranked_team_ids, team_obj)


def _get_division_rank(standings, team_obj):
    division_standings = standings.by_division(team_obj.division)
    ranked_team_ids = _division_ranked_team_ids(division_standings)
    return _rank_from_team_ids(ranked_team_ids, team_obj)


def get_team_pregame_rankings(game_obj, team_obj):
    """
    Get league, conference, and division pre-game rankings for a team.

    Rankings use the standings snapshot from the week leading up to the game.
    For week 1 games, no prior-week standings exist, so this returns None.
    """
    if not isinstance(game_obj, Game):
        raise ValueError("game_obj must be an instance of Game")
    if not isinstance(team_obj, Team):
        raise ValueError("team_obj must be an instance of Team")

    pregame_week = game_obj.week.week - 1
    if pregame_week < 1:
        return None

    # Use the standings snapshot from the week before the game.
    team_standings_qs = cast(TeamStandingsQuerySet, TeamStandings.objects)
    standings = team_standings_qs.by_season_week(
        season=game_obj.week.season.year,
        week=pregame_week
    )

    ordered_standings = standings.apply_default_ordering()
    team_standing = ordered_standings.filter(team=team_obj).first()
    if not team_standing:
        return None

    league_rank = _get_league_rank(standings, team_obj)
    conference_rank = _get_conference_rank(standings, team_obj)
    division_rank = _get_division_rank(standings, team_obj)

    if league_rank is None or conference_rank is None or division_rank is None:
        return None

    return {
        "league_rank": league_rank,
        "conference_rank": conference_rank,
        "division_rank": division_rank,
        "wins": team_standing.wins,
        "losses": team_standing.losses,
        "ties": team_standing.ties,
    }