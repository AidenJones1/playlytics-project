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