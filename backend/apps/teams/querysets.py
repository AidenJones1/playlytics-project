from django.db.models import QuerySet

class TeamQuerySet(QuerySet):
    pass

class TeamInjuryReportQuerySet(QuerySet):
    def get_game_injury_report(self, game_obj):
        """Retrieve the injury report for a specific game."""
        home_team_injuries = self.filter(team=game_obj.home_team, week=game_obj.week)
        away_team_injuries = self.filter(team=game_obj.away_team, week=game_obj.week)
        return home_team_injuries, away_team_injuries