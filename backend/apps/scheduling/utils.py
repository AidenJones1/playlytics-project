from typing import cast

from apps.scheduling.models import Game
from apps.scheduling.querysets import GameQuerySet
from apps.teams.models import TeamInjuryReport
from apps.teams.querysets import TeamInjuryReportQuerySet

def get_teams_previous_games(game_obj, games_back=5):
    """Retrieve the previous games for both teams in a given game."""
    game_qs = cast(GameQuerySet, Game.objects)
    home_team_previous_games = game_qs.get_previous_games(game_obj.home_team, game_obj, games_back)
    away_team_previous_games = game_qs.get_previous_games(game_obj.away_team, game_obj, games_back)
    return home_team_previous_games, away_team_previous_games

def get_teams_injury_reports(game_obj):
    """Retrieve the injury reports for both teams in a given game."""
    injury_report_qs = cast(TeamInjuryReportQuerySet, TeamInjuryReport.objects)
    return injury_report_qs.get_game_injury_report(game_obj)

def net_point_differential(team, games):
    """Calculate the net point differential for a team over a list of games."""
    net_diff = 0
    for game in games:
        if game.home_team == team:
            net_diff += (game.home_score or 0) - (game.away_score or 0)
        elif game.away_team == team:
            net_diff += (game.away_score or 0) - (game.home_score or 0)
    return net_diff

def average_points_differential(team, games):
    """Calculate the average point differential for a team over a list of games."""
    if not games:
        return 0
    net_diff = net_point_differential(team, games)
    return net_diff / len(games)

def net_points_scored(team, games):
    """Calculate the net points scored for a team over a list of games."""
    net_points = 0
    for game in games:
        if game.home_team == team:
            net_points += game.home_score or 0
        elif game.away_team == team:
            net_points += game.away_score or 0
    return net_points

def average_points_scored(team, games):
    """Calculate the average points scored for a team over a list of games."""
    if not games:
        return 0
    net_points = net_points_scored(team, games)
    return net_points / len(games)
