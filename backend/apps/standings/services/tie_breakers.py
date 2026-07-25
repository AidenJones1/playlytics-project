from collections import defaultdict
import inspect
from typing import cast

from apps.scheduling.choices import GameStatus
from apps.scheduling.models import Game
from apps.standings.models import TeamStandings
from apps.standings.querysets import TeamStandingsQuerySet


def _winning_percentage(wins, losses, ties):
    total_games = wins + losses + ties
    if total_games == 0:
        return 0.0
    return (wins + (0.5 * ties)) / total_games


def _team_record_from_games(games, team_id, opponents=None):
    wins = 0
    losses = 0
    ties = 0

    for game in games:
        if game.home_team_id == team_id:
            opponent_id = game.away_team_id
            team_score = game.home_score
            opponent_score = game.away_score
        elif game.away_team_id == team_id:
            opponent_id = game.home_team_id
            team_score = game.away_score
            opponent_score = game.home_score
        else:
            continue

        if opponents is not None and opponent_id not in opponents:
            continue

        if team_score > opponent_score:
            wins += 1
        elif team_score < opponent_score:
            losses += 1
        else:
            ties += 1

    return wins, losses, ties


def _build_team_games_map(games, team_ids):
    team_games = {team_id: [] for team_id in team_ids}

    for game in games:
        if game.home_team_id in team_games:
            team_games[game.home_team_id].append(game)
        if game.away_team_id in team_games:
            team_games[game.away_team_id].append(game)

    return team_games


def _build_points_totals(games, team_ids):
    points_for = defaultdict(int)
    points_against = defaultdict(int)
    touchdowns_for = defaultdict(int)
    touchdowns_against = defaultdict(int)

    for team_id in team_ids:
        points_for[team_id] = 0
        points_against[team_id] = 0
        touchdowns_for[team_id] = 0
        touchdowns_against[team_id] = 0

    for game in games:
        home_id = game.home_team_id
        away_id = game.away_team_id

        home_score = game.home_score
        away_score = game.away_score

        if home_id in points_for:
            points_for[home_id] += home_score
            points_against[home_id] += away_score
            touchdowns_for[home_id] += home_score // 7
            touchdowns_against[home_id] += away_score // 7

        if away_id in points_for:
            points_for[away_id] += away_score
            points_against[away_id] += home_score
            touchdowns_for[away_id] += away_score // 7
            touchdowns_against[away_id] += home_score // 7

    return points_for, points_against, touchdowns_for, touchdowns_against


def _opponents_played(team_games, team_id, excluded_team_ids=None):
    opponents = set()

    for game in team_games.get(team_id, []):
        opponent_id = game.away_team_id if game.home_team_id == team_id else game.home_team_id
        if excluded_team_ids and opponent_id in excluded_team_ids:
            continue
        opponents.add(opponent_id)

    return opponents


def _common_opponents(team_games, team_ids):
    opponent_sets = []
    excluded = set(team_ids)

    for team_id in team_ids:
        opponents = _opponents_played(team_games, team_id, excluded_team_ids=excluded)
        if not opponents:
            return set()
        opponent_sets.append(opponents)

    if not opponent_sets:
        return set()

    common = set.intersection(*opponent_sets)
    return common


def _games_against_opponents(team_games, team_id, opponents):
    selected_games = []
    for game in team_games.get(team_id, []):
        opponent_id = game.away_team_id if game.home_team_id == team_id else game.home_team_id
        if opponent_id in opponents:
            selected_games.append(game)
    return selected_games


def _net_points_in_games(games, team_id):
    net = 0
    for game in games:
        if game.home_team_id == team_id:
            net += game.home_score - game.away_score
        elif game.away_team_id == team_id:
            net += game.away_score - game.home_score
    return net


def _combined_rank(team_ids, points_for, points_against):
    points_for_sorted = sorted(team_ids, key=lambda team_id: (-points_for[team_id], team_id))
    points_against_sorted = sorted(team_ids, key=lambda team_id: (points_against[team_id], team_id))

    points_for_rank = {team_id: index + 1 for index, team_id in enumerate(points_for_sorted)}
    points_against_rank = {team_id: index + 1 for index, team_id in enumerate(points_against_sorted)}

    return {
        team_id: points_for_rank[team_id] + points_against_rank[team_id]
        for team_id in team_ids
    }


def _rank_values(values, prefer_lower=False):
    if not values:
        return set(values)

    valid_values = [value for value in values.values() if value is not None]
    if not valid_values:
        return set(values)

    best_value = min(valid_values) if prefer_lower else max(valid_values)
    return {team_id for team_id, value in values.items() if value == best_value}


def _score_head_to_head(team_ids, team_games):
    scores = {}
    opponent_ids = set(team_ids)

    for team_id in team_ids:
        wins, losses, ties = _team_record_from_games(
            team_games.get(team_id, []),
            team_id,
            opponents=opponent_ids - {team_id},
        )
        scores[team_id] = _winning_percentage(wins, losses, ties)

    return scores, False


def _score_division_percentage(team_ids, standings_map):
    scores = {}
    for team_id in team_ids:
        standing = standings_map.get(team_id)
        if standing is None:
            scores[team_id] = None
            continue
        scores[team_id] = _winning_percentage(
            standing.division_wins,
            standing.division_losses,
            standing.division_ties,
        )

    return scores, False


def _score_common_games(team_ids, team_games):
    common_opponents = _common_opponents(team_games, team_ids)
    if not common_opponents:
        return {team_id: None for team_id in team_ids}, False

    scores = {}
    for team_id in team_ids:
        games = _games_against_opponents(team_games, team_id, common_opponents)
        wins, losses, ties = _team_record_from_games(games, team_id)
        scores[team_id] = _winning_percentage(wins, losses, ties)

    return scores, False


def _score_conference_percentage(team_ids, standings_map):
    scores = {}
    for team_id in team_ids:
        standing = standings_map.get(team_id)
        if standing is None:
            scores[team_id] = None
            continue
        scores[team_id] = _winning_percentage(
            standing.conference_wins,
            standing.conference_losses,
            standing.conference_ties,
        )

    return scores, False


def _score_strength_of_victory(team_ids, team_games, standings_map):
    scores = {}

    for team_id in team_ids:
        total = 0.0
        count = 0
        for game in team_games.get(team_id, []):
            if game.home_team_id == team_id:
                team_score = game.home_score
                opponent_score = game.away_score
                opponent_id = game.away_team_id
            else:
                team_score = game.away_score
                opponent_score = game.home_score
                opponent_id = game.home_team_id

            if team_score <= opponent_score:
                continue

            opponent_standing = standings_map.get(opponent_id)
            if opponent_standing is None:
                continue

            total += _winning_percentage(
                opponent_standing.wins,
                opponent_standing.losses,
                opponent_standing.ties,
            )
            count += 1

        scores[team_id] = (total / count) if count > 0 else 0.0

    return scores, False


def _score_strength_of_schedule(team_ids, team_games, standings_map):
    scores = {}

    for team_id in team_ids:
        total = 0.0
        count = 0
        for game in team_games.get(team_id, []):
            opponent_id = game.away_team_id if game.home_team_id == team_id else game.home_team_id
            opponent_standing = standings_map.get(opponent_id)
            if opponent_standing is None:
                continue

            total += _winning_percentage(
                opponent_standing.wins,
                opponent_standing.losses,
                opponent_standing.ties,
            )
            count += 1

        scores[team_id] = (total / count) if count > 0 else 0.0

    return scores, False


def _score_combined_conference_rank(team_ids, standings_map, points_for, points_against):
    conference_team_ids = [
        standing.team_id
        for standing in standings_map.values()
        if standing.team.conference == standings_map[team_ids[0]].team.conference
    ]

    combined = _combined_rank(conference_team_ids, points_for, points_against)
    return {team_id: combined.get(team_id) for team_id in team_ids}, True


def _score_combined_league_rank(team_ids, standings_map, points_for, points_against):
    league_team_ids = list(standings_map.keys())
    combined = _combined_rank(league_team_ids, points_for, points_against)
    return {team_id: combined.get(team_id) for team_id in team_ids}, True


def _score_net_points_common_games(team_ids, team_games):
    common_opponents = _common_opponents(team_games, team_ids)
    if not common_opponents:
        return {team_id: None for team_id in team_ids}, False

    scores = {}
    for team_id in team_ids:
        games = _games_against_opponents(team_games, team_id, common_opponents)
        scores[team_id] = _net_points_in_games(games, team_id)

    return scores, False


def _score_net_points_all_games(team_ids, standings_map):
    scores = {}
    for team_id in team_ids:
        standing = standings_map.get(team_id)
        scores[team_id] = None if standing is None else standing.point_differential

    return scores, False


def _score_net_touchdowns_all_games(team_ids, touchdowns_for, touchdowns_against):
    return {
        team_id: touchdowns_for[team_id] - touchdowns_against[team_id]
        for team_id in team_ids
    }, False


def _coin_toss(team_ids, standings_map):
    scores = {
        team_id: standings_map[team_id].team.abbreviation
        for team_id in team_ids
    }
    return scores, True


def _apply_step(step, team_ids, context):
    step_signature = inspect.signature(step)
    accepted_kwargs = {
        key: value
        for key, value in context.items()
        if key in step_signature.parameters
    }
    scores, prefer_lower = step(team_ids, **accepted_kwargs)
    best_teams = _rank_values(scores, prefer_lower=prefer_lower)
    if not best_teams:
        return set(team_ids)
    return best_teams


def _select_division_winner(team_ids, context):
    candidates = set(team_ids)

    two_team_steps = [
        _score_head_to_head,
        _score_division_percentage,
        _score_common_games,
        _score_conference_percentage,
        _score_strength_of_victory,
        _score_strength_of_schedule,
        _score_combined_conference_rank,
        _score_combined_league_rank,
        _score_net_points_common_games,
        _score_net_points_all_games,
        _score_net_touchdowns_all_games,
        _coin_toss,
    ]

    multi_team_steps = [
        _score_head_to_head,
        _score_division_percentage,
        _score_common_games,
        _score_conference_percentage,
        _score_strength_of_victory,
        _score_strength_of_schedule,
        _score_combined_conference_rank,
        _score_combined_league_rank,
        _score_net_points_common_games,
        _score_net_points_all_games,
        _score_net_touchdowns_all_games,
        _coin_toss,
    ]

    while len(candidates) > 1:
        steps = two_team_steps if len(candidates) == 2 else multi_team_steps
        reduced = False

        for step in steps:
            best_teams = _apply_step(step, list(candidates), context)
            if len(best_teams) == 1:
                return next(iter(best_teams))

            if 1 < len(best_teams) < len(candidates):
                candidates = best_teams
                reduced = True
                break

        if not reduced:
            tied = sorted(
                candidates,
                key=lambda team_id: context['standings_map'][team_id].team.abbreviation,
            )
            return tied[0]

    return next(iter(candidates))


def _resolve_division_tie_group(team_ids, context):
    remaining = list(team_ids)
    ordered = []

    while remaining:
        winner = _select_division_winner(remaining, context)
        ordered.append(winner)
        remaining = [team_id for team_id in remaining if team_id != winner]

    return ordered


def _build_division_context(standings):
    if not standings.exists():
        return None

    sample = standings.select_related('week__season').first()
    season = sample.week.season.year
    week = sample.week.week

    team_standings_qs = cast(TeamStandingsQuerySet, TeamStandings.objects)
    all_standings = team_standings_qs.by_season_week(season=season, week=week).select_related('team')
    standings_map = {standing.team_id: standing for standing in all_standings}

    games = list(
        Game.objects.filter(
            week__season__year=season,
            week__week__lte=week,
            status=GameStatus.COMPLETED,
            home_score__isnull=False,
            away_score__isnull=False,
        ).select_related('home_team', 'away_team')
    )

    team_ids = list(standings_map.keys())
    team_games = _build_team_games_map(games, team_ids)
    points_for, points_against, touchdowns_for, touchdowns_against = _build_points_totals(games, team_ids)

    return {
        'standings_map': standings_map,
        'team_games': team_games,
        'points_for': points_for,
        'points_against': points_against,
        'touchdowns_for': touchdowns_for,
        'touchdowns_against': touchdowns_against,
    }


def default_ordering_tiebreakers(standings):
    ordered_standings = standings.select_related('team').order_by(
        '-percentage',
        '-wins',
        '-point_differential',
    )
    return list(ordered_standings.values_list('team_id', flat=True))


def apply_conference_tiebreakers(standings):
    return default_ordering_tiebreakers(standings)


def apply_division_tiebreakers(standings):
    ordered_standings = list(standings.select_related('team').apply_default_ordering())
    if not ordered_standings:
        return []

    context = _build_division_context(standings)
    if context is None:
        return []

    grouped = defaultdict(list)
    for standing in ordered_standings:
        tie_key = round(_winning_percentage(standing.wins, standing.losses, standing.ties), 6)
        grouped[tie_key].append(standing.team_id)

    ranked_team_ids = []
    for tie_key in sorted(grouped.keys(), reverse=True):
        group_team_ids = grouped[tie_key]
        if len(group_team_ids) == 1:
            ranked_team_ids.extend(group_team_ids)
            continue

        resolved = _resolve_division_tie_group(group_team_ids, context)
        ranked_team_ids.extend(resolved)

    return ranked_team_ids
