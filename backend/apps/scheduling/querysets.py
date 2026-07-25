from django.db.models import QuerySet, Q

class GameQuerySet(QuerySet):
    def by_season_and_week(self, season, week):
        return self.filter(
            week__season__year=season,
            week__week=week
        )

    def by_division_teams(self, division):
        return self.filter(
            Q(home_team__division=division) | Q(away_team__division=division)
        )

    def by_conference_teams(self, conference):
        return self.filter(
            Q(home_team__conference=conference) | Q(away_team__conference=conference)
        )

    def by_team_and_season(self, team_abbr, season_year):
        return self.filter(
            Q(home_team__abbreviation=team_abbr) | Q(away_team__abbreviation=team_abbr),
            week__season__year=season_year
        )

    def by_division_opponents(self, team_obj, division):
        return self.filter(
            Q(home_team=team_obj, away_team__division=division) |
            Q(away_team=team_obj, home_team__division=division)
        )
    
    def by_conference_opponents(self, team_obj, conference):
        return self.filter(
            Q(home_team=team_obj, away_team__conference=conference) |
            Q(away_team=team_obj, home_team__conference=conference)
        )